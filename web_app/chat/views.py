from __future__ import annotations

import json
import logging
from collections.abc import Iterator

import ollama
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from application.chat_service import ChatService
from domain.entities import Conversation, Message
from infrastructure.ollama_gateway import OllamaGateway

logger = logging.getLogger(__name__)

# Dependency wired at module level – swap OllamaGateway for any ChatGateway impl.
_service = ChatService(OllamaGateway())

_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


# ── Helpers ───────────────────────────────────────────────────────────────────


def _load_history(request: HttpRequest) -> Conversation:
    return Conversation.from_session(request.session.get("history", []))


def _save_history(request: HttpRequest, conversation: Conversation) -> None:
    request.session["history"] = conversation.to_session()
    request.session.save()


def _validate_image(image_file) -> tuple[bytes | None, str | None]:
    """Return (bytes, None) on success or (None, error_message) on failure."""
    if image_file.content_type not in _ALLOWED_IMAGE_TYPES:
        return None, f"Unsupported image type: {image_file.content_type}"
    data = image_file.read()
    if len(data) > _MAX_IMAGE_BYTES:
        return None, "Image exceeds 10 MB limit."
    return data, None


# ── Views ─────────────────────────────────────────────────────────────────────


@require_GET
def chat_page(request: HttpRequest):
    history = request.session.get("history", [])
    return render(request, "chat/index.html", {"history": history})


@require_POST
def stream_chat(request: HttpRequest):
    text: str = request.POST.get("message", "").strip()
    image_file = request.FILES.get("image")

    if not text and not image_file:
        return JsonResponse({"error": "Message cannot be empty."}, status=400)

    images: list[bytes] = []
    if image_file:
        data, err = _validate_image(image_file)
        if err:
            return JsonResponse({"error": err}, status=400)
        images = [data]

    user_message = Message(role="user", content=text, images=images)

    # Persist user message before streaming so a page reload shows it.
    conversation = _load_history(request)
    history_snapshot = list(conversation.messages)  # copy for the generator
    conversation.add(user_message)
    _save_history(request, conversation)

    def generate() -> Iterator[bytes]:
        full_response = ""
        try:
            for token in _service.send(history_snapshot, user_message):
                full_response += token
                yield (f"data: {json.dumps({'token': token})}\n\n").encode()
        except ollama.ResponseError as exc:
            logger.error("Ollama error: %s", exc)
            yield (f"data: {json.dumps({'error': str(exc)})}\n\n").encode()
        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected error: %s", exc)
            yield (f"data: {json.dumps({'error': 'An unexpected error occurred.'})}\n\n").encode()
        finally:
            # Persist the assistant reply after the stream is exhausted.
            if full_response:
                hist = request.session.get("history", [])
                hist.append({"role": "assistant", "content": full_response})
                request.session["history"] = hist
                request.session.save()
            yield b"data: [DONE]\n\n"

    response = StreamingHttpResponse(generate(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # disable nginx buffering
    return response


@require_POST
def clear_history(request: HttpRequest):
    request.session["history"] = []
    request.session.save()
    return JsonResponse({"ok": True})
