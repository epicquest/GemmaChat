from __future__ import annotations

import sys
from typing import Iterator

import ollama
from ollama import ResponseError
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

MODEL = "gemma4:e2b"
console = Console()


def render_user_message(content: str) -> None:
    console.print(
        Panel(content, title="[bold cyan]You[/bold cyan]", border_style="cyan")
    )


def stream_assistant_response(
    history: list[dict[str, str]],
) -> str:
    stream: Iterator[ollama.ChatResponse] = ollama.chat(
        model=MODEL,
        messages=history,
        stream=True,
    )

    full_response = ""
    buffer = ""

    with Live(console=console, refresh_per_second=20, vertical_overflow="visible") as live:
        for chunk in stream:
            token: str = chunk.message.content or ""
            full_response += token
            buffer += token
            live.update(
                Panel(
                    Markdown(full_response),
                    title="[bold green]Gemma[/bold green]",
                    border_style="green",
                )
            )

    return full_response


def handle_command(command: str, history: list[dict[str, str]]) -> bool:
    """
    Process a slash command.
    Returns True if the chat loop should continue, False if it should exit.
    """
    cmd = command.strip().lower()
    if cmd == "/exit":
        console.print("[bold yellow]Goodbye![/bold yellow]")
        return False
    if cmd == "/clear":
        history.clear()
        console.print("[bold yellow]Chat history cleared.[/bold yellow]")
        return True
    console.print(f"[bold red]Unknown command:[/bold red] {command}")
    return True


def chat_loop() -> None:
    history: list[dict[str, str]] = []

    console.print(
        Panel(
            Text.from_markup(
                f"[bold]Model:[/bold] [cyan]{MODEL}[/cyan]\n"
                "[bold]Commands:[/bold] [yellow]/clear[/yellow] · [yellow]/exit[/yellow]"
            ),
            title="[bold magenta]GemmaChat[/bold magenta]",
            border_style="magenta",
        )
    )

    while True:
        try:
            user_input: str = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input.startswith("/"):
            if not handle_command(user_input, history):
                break
            continue

        render_user_message(user_input)
        history.append({"role": "user", "content": user_input})

        try:
            assistant_content = stream_assistant_response(history)
        except ollama.ResponseError as exc:
            if "model" in str(exc).lower() and "not found" in str(exc).lower():
                console.print(
                    f"[bold red]Error:[/bold red] Model '[cyan]{MODEL}[/cyan]' was not found. "
                    f"Run [yellow]`ollama pull {MODEL}`[/yellow] to download it."
                )
            else:
                console.print(f"[bold red]Ollama error:[/bold red] {exc}")
            history.pop()
            continue
        except ConnectionError:
            console.print(
                "[bold red]Connection error:[/bold red] Cannot reach the Ollama server. "
                "Make sure Ollama is running ([yellow]`ollama serve`[/yellow])."
            )
            history.pop()
            continue
        except Exception as exc:  # noqa: BLE001
            error_text = str(exc)
            if "connection" in error_text.lower() or "refused" in error_text.lower():
                console.print(
                    "[bold red]Connection error:[/bold red] Cannot reach the Ollama server. "
                    "Make sure Ollama is running ([yellow]`ollama serve`[/yellow])."
                )
            else:
                console.print(f"[bold red]Unexpected error:[/bold red] {exc}")
            history.pop()
            continue

        history.append({"role": "assistant", "content": assistant_content})


def main() -> None:
    chat_loop()


if __name__ == "__main__":
    main()
