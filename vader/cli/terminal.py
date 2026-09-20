import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

console = Console(highlight=False)

ASCII_BANNER = r"""[bold cyan]
__      __     _____  ______ _____  
\ \    / /\   |  __ \|  ____|  __ \ 
 \ \  / /  \  | |  | | |__  | |__) |
  \ \/ / /\ \ | |  | |  __| |  _  / 
   \  / ____ \| |__| | |____| | \ \ 
    \/_/    \_\_____/|______|_|  \_\
[/bold cyan][dim white]Autonomous Agentic Development Platform (Vibe-Coder)[/dim white]
"""

def print_banner(model_name: str = "qwen2.5-coder:7b", provider: str = "ollama"):
    console.print(ASCII_BANNER)
    console.print(f"[dim]• Engine: [cyan]{provider}[/cyan] | Active Model: [green]{model_name}[/green] | Type [bold]/help[/bold] for commands[/dim]\n")

def print_panel(content: str, title: str = "", style: str = "cyan"):
    console.print(Panel(content, title=title, border_style=style, expand=False))

def print_markdown(content: str):
    console.print(Markdown(content))

def print_diff(diff_text: str):
    if not diff_text.strip():
        console.print("[dim]No uncommitted git changes.[/dim]")
        return
    syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="[bold]Active Repository Diff[/bold]", border_style="yellow"))
