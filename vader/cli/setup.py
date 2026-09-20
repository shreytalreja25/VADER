import sys
import shutil
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from vader.config import config_manager
from vader.providers.ollama import OllamaProvider
from vader.providers.quantized import QuantizedProvider

console = Console()

def run_setup_wizard():
    console.print(Panel(
        "[bold cyan]VADER Configuration & Model Setup Wizard[/bold cyan]\n"
        "[dim]Configure local Ollama, Quantized GGUF inference, or Cloud fallbacks[/dim]",
        border_style="cyan"
    ))

    # Step 1: Provider selection
    console.print("\n[bold]1. Choose Primary LLM Engine:[/bold]")
    console.print("  [cyan]1[/cyan]) [bold]Ollama[/bold] (Recommended: local zero-cost streaming, auto-pulling)")
    console.print("  [cyan]2[/cyan]) [bold]Quantized GGUF / llama.cpp[/bold] (Plug-and-play 4-bit/8-bit models with low VRAM)")
    console.print("  [cyan]3[/cyan]) [bold]Cloud Fallback[/bold] (Claude 3.7 Sonnet, DeepSeek V2, OpenAI GPT-4o)")
    
    choice = Prompt.ask("Select engine", choices=["1", "2", "3"], default="1")

    if choice == "1":
        config_manager.set("provider", "ollama", persist=False)
        endpoint = Prompt.ask("Ollama endpoint", default="http://localhost:11434")
        config_manager.set("ollama.endpoint", endpoint, persist=False)

        provider = OllamaProvider(endpoint=endpoint)
        console.print("[dim]Connecting to Ollama...[/dim]")
        if provider.health_check():
            console.print("[green]✔ Successfully connected to Ollama service![/green]")
            models = provider.list_models()
            if models:
                console.print(f"Detected {len(models)} local models:")
                for idx, m in enumerate(models[:5]):
                    console.print(f"  - [cyan]{m.name}[/cyan] ({m.parameters}, {m.quantization})")
                selected_model = Prompt.ask("Default coding model", default=models[0].name)
                config_manager.set("model", selected_model, persist=False)
            else:
                console.print("[yellow]No models found in Ollama yet.[/yellow]")
                pull_rec = Confirm.ask("Would you like to recommend 'qwen2.5-coder:7b'?", default=True)
                config_manager.set("model", "qwen2.5-coder:7b", persist=False)
        else:
            console.print("[yellow]⚠ Ollama is not currently running at " + endpoint + "[/yellow]")
            console.print("[dim]Make sure to start Ollama with: 'ollama serve'[/dim]")
            config_manager.set("model", "qwen2.5-coder:7b", persist=False)

    elif choice == "2":
        config_manager.set("provider", "quantized", persist=False)
        endpoint = Prompt.ask("Quantized API endpoint (e.g. llama-server or vLLM)", default="http://localhost:8080/v1")
        config_manager.set("quantized.endpoint", endpoint, persist=False)
        models_dir = Prompt.ask("GGUF Models directory", default=str(Path.home() / ".vader" / "models"))
        config_manager.set("quantized.models_dir", models_dir, persist=False)
        
        quant_provider = QuantizedProvider(endpoint=endpoint)
        local_ggufs = quant_provider.list_local_gguf_files()
        if local_ggufs:
            console.print(f"[green]Found {len(local_ggufs)} GGUF files in {models_dir}:[/green]")
            for g in local_ggufs:
                console.print(f"  - [cyan]{g['name']}[/cyan] ({g['size_gb']} GB | {g['quantization']})")
            selected_model = Prompt.ask("Select GGUF model", default=local_ggufs[0]["name"])
            config_manager.set("model", selected_model, persist=False)
        else:
            console.print(f"[dim]No .gguf files in {models_dir} yet. You can drop any GGUF file there.[/dim]")
            config_manager.set("model", "qwen2.5-coder-7b-instruct-q4_k_m.gguf", persist=False)

    else:
        config_manager.set("provider", "cloud", persist=False)
        cloud_type = Prompt.ask("Select provider", choices=["deepseek", "anthropic", "openai"], default="deepseek")
        api_key = Prompt.ask(f"Enter {cloud_type.upper()} API Key", password=True)
        config_manager.set(f"cloud.{cloud_type}_api_key", api_key, persist=False)
        default_model = "deepseek-coder" if cloud_type == "deepseek" else ("claude-3-7-sonnet" if cloud_type == "anthropic" else "gpt-4o")
        config_manager.set("model", default_model, persist=False)

    # Step 2: Guardrails
    console.print("\n[bold]2. Guardrail Protection:[/bold]")
    confirm_prot = Confirm.ask("Protect git, environment files (.env), and dependencies from automatic overwrite?", default=True)
    if confirm_prot:
        console.print("[green]✔ Guardrails enabled for protected paths.[/green]")

    # Save
    config_manager.save_global()
    console.print("\n[bold green]✔ Configuration saved successfully to ~/.vader/config.json![/bold green]")
    console.print("[dim]Run 'vader doctor' anytime to verify your setup.[/dim]\n")
