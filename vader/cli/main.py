import sys
import os
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from vader import __version__
from vader.config import config_manager
from vader.cli.terminal import console, print_banner, print_panel, print_markdown, print_diff
from vader.cli.setup import run_setup_wizard
from vader.providers.manager import ProviderManager
from vader.providers.ollama import OllamaProvider
from vader.providers.quantized import QuantizedProvider
from vader.orchestration.engine import VaderEngine
from vader.skills.manager import skill_manager
from vader.workflows.engine import WorkflowEngine
from vader.cron.scheduler import cron_scheduler

KNOWN_COMMANDS = {"setup", "doctor", "diff", "skill", "workflow", "cron", "code", "--help", "-h", "--version", "-v"}

def preprocess_argv():
    if len(sys.argv) > 1:
        non_flags = [a for a in sys.argv[1:] if not a.startswith("-")]
        if non_flags and non_flags[0] not in KNOWN_COMMANDS:
            sys.argv.insert(1, "code")

preprocess_argv()

@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show Vader version.")
@click.pass_context
def cli(ctx, version):
    """
    Vader: Autonomous Agentic Development Platform for Vibe-Coding.
    """
    if version:
        console.print(f"[bold cyan]Vader[/bold cyan] version [green]{__version__}[/green]")
        sys.exit(0)

    if ctx.invoked_subcommand is None:
        interactive_repl()

@cli.command("code")
@click.option("--provider", "-p", default=None, help="LLM provider: ollama, quantized, openai, anthropic, deepseek, mock.")
@click.option("--model", "-m", default=None, help="Model identifier.")
@click.argument("prompt", nargs=-1, required=False)
def code_cmd(provider, model, prompt):
    """Execute a vibe-coding task or launch interactive REPL."""
    if prompt:
        user_prompt = " ".join(prompt)
        execute_single_prompt(user_prompt, provider=provider, model=model)
    else:
        interactive_repl(provider=provider, model=model)

def execute_single_prompt(user_prompt: str, provider: str = None, model: str = None, show_banner: bool = True):
    prov_inst = ProviderManager.get_provider(provider_name=provider, model_name=model)
    model_name = getattr(prov_inst, "model", config_manager.get("model"))
    prov_name = provider or config_manager.get("provider")
    if show_banner:
        print_banner(model_name, prov_name)
    console.print(f"[bold green]Executing task:[/bold green] {user_prompt}\n")
    
    def on_event(ev, data):
        if ev == "phase":
            console.print(f"[bold cyan]> {data.get('msg')}[/bold cyan]")
        elif ev == "plan_created":
            print_panel(data.get("plan", ""), title="Architect Execution Plan", style="blue")
        elif ev == "files_written":
            files = data.get("files", [])
            if files:
                console.print(f"[green]Written {len(files)} files:[/green] {', '.join(files)}")
        elif ev == "self_healing":
            console.print(f"[yellow]Self-healing iteration {data.get('iteration')} triggered...[/yellow]")
        elif ev == "complete":
            if data.get("success", False):
                console.print("[bold green]Task completed successfully![/bold green]")
            else:
                console.print("[yellow]Task completed with warnings/incomplete state.[/yellow]")
        elif ev == "error":
            console.print(f"[bold red]Execution Error:[/bold red] {data.get('msg')}")

    engine = VaderEngine(provider=prov_inst, on_event=on_event)
    engine.plan_and_execute(user_prompt)

def interactive_repl(provider: str = None, model: str = None):
    prov_inst = ProviderManager.get_provider(provider_name=provider, model_name=model)
    model_name = getattr(prov_inst, "model", config_manager.get("model"))
    prov_name = provider or config_manager.get("provider")
    # Print banner ONCE when REPL session starts
    print_banner(model_name, prov_name)
    console.print("[dim]Type your prompt or [bold]/help[/bold] for commands. Press Ctrl+C to exit.[/dim]\n")
    
    while True:
        try:
            user_input = console.input("[bold cyan]vader > [/bold cyan]").strip()
            if not user_input:
                continue
            
            if user_input.startswith("/"):
                handle_slash_command(user_input)
                continue

            # Run task without re-printing the banner
            try:
                execute_single_prompt(user_input, provider=provider, model=model, show_banner=False)
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")
                console.print("[dim]Vader is ready for your next prompt. Type /help for options.[/dim]")
            console.print()
        except KeyboardInterrupt:
            console.print("\n[dim]Action cancelled. Type /exit to quit or continue entering prompts.[/dim]\n")
        except EOFError:
            console.print("\n[dim]Exiting Vader. Keep vibe-coding![/dim]")
            break
def handle_slash_command(cmd: str):
    parts = cmd.split()
    root_cmd = parts[0].lower()

    if root_cmd in ["/help", "/h"]:
        console.print(Panel(
            "[bold]Vader Interactive Slash Commands:[/bold]\n"
            "  [cyan]/help[/cyan]          Show this help cheatsheet\n"
            "  [cyan]/diff[/cyan]          View active git changes\n"
            "  [cyan]/model[/cyan]         Show or switch active LLM\n"
            "  [cyan]/skills[/cyan]        List installed skills\n"
            "  [cyan]/doctor[/cyan]        Run environment diagnostics\n"
            "  [cyan]/setup[/cyan]         Re-run setup wizard\n"
            "  [cyan]/exit[/cyan]          Exit interactive session",
            border_style="cyan"
        ))
    elif root_cmd == "/diff":
        engine = VaderEngine()
        print_diff(engine.harness.get_git_diff())
    elif root_cmd == "/model":
        console.print(f"Current Provider: [cyan]{config_manager.get('provider')}[/cyan]")
        console.print(f"Active Model: [green]{config_manager.get('model')}[/green]")
    elif root_cmd == "/skills":
        skills = skill_manager.list_skills()
        console.print(f"Installed skills: {len(skills)}")
        for s in skills:
            console.print(f"  - [cyan]{s.name}[/cyan]: {s.description}")
    elif root_cmd == "/doctor":
        run_doctor()
    elif root_cmd == "/setup":
        run_setup_wizard()
    elif root_cmd in ["/exit", "/quit"]:
        sys.exit(0)
    else:
        console.print(f"[yellow]Unknown command: {root_cmd}. Type /help for available commands.[/yellow]")

@cli.command("setup")
def setup_cmd():
    """Run interactive setup wizard for model providers and endpoints."""
    run_setup_wizard()

@cli.command("doctor")
def doctor_cmd():
    """Inspect environment, Ollama connectivity, Git status, and model health."""
    run_doctor()

def run_doctor():
    console.print(Panel("[bold]Vader System Diagnostics[/bold]", border_style="cyan"))
    table = Table(title="System & Component Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    table.add_row("Python", "[green]OK[/green]", f"Python {py_ver}")

    # Git
    engine = VaderEngine()
    git_stat = engine.harness.get_git_status()
    table.add_row("Git Repository", "[green]Active[/green]" if git_stat is not None else "[yellow]Not Found[/yellow]", 
                  f"{len(git_stat.splitlines())} modified files" if git_stat else "Clean workspace")

    # Ollama
    ollama_prov = OllamaProvider()
    if ollama_prov.health_check():
        models = ollama_prov.list_models()
        table.add_row("Ollama Service", "[green]Online[/green]", f"{len(models)} local models installed ({ollama_prov.endpoint})")
    else:
        table.add_row("Ollama Service", "[yellow]Offline[/yellow]", f"Cannot reach {ollama_prov.endpoint}")

    # Quantized
    quant_prov = QuantizedProvider()
    ggufs = quant_prov.list_local_gguf_files()
    table.add_row("Local GGUF Models", f"[cyan]{len(ggufs)} Found[/cyan]", f"Models dir: {quant_prov.models_dir}")

    # Active configuration
    table.add_row("Active Provider", "[green]Configured[/green]", config_manager.get("provider"))
    table.add_row("Active Model", "[green]Configured[/green]", config_manager.get("model"))

    # Skills
    skills = skill_manager.list_skills()
    table.add_row("Skills", f"[green]{len(skills)} Available[/green]", ", ".join([s.name for s in skills[:3]]) or "None")

    console.print(table)

@cli.group("skill")
def skill_group():
    """Manage developer skills."""
    pass

@skill_group.command("list")
def skill_list():
    """List all installed skills."""
    skills = skill_manager.list_skills()
    if not skills:
        console.print("[dim]No skills installed yet. Use 'vader skill install <path>' to add one.[/dim]")
        return
    table = Table(title="Installed Vader Skills")
    table.add_column("Skill Name", style="bold cyan")
    table.add_column("Description")
    table.add_column("Source Path", style="dim")
    for s in skills:
        table.add_row(s.name, s.description, str(s.path))
    console.print(table)

@skill_group.command("install")
@click.argument("source")
def skill_install(source):
    """Install a skill from a local folder or git repository."""
    try:
        skill = skill_manager.install_skill(source)
        console.print(f"[bold green]Successfully installed skill:[/bold green] [cyan]{skill.name}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Failed to install skill:[/bold red] {e}")

@cli.group("workflow")
def workflow_group():
    """Manage and run multi-step agentic workflows."""
    pass

@workflow_group.command("run")
@click.argument("file_path")
def workflow_run(file_path):
    """Execute a YAML workflow pipeline."""
    engine = WorkflowEngine()
    try:
        wf = engine.load_workflow(file_path)
        console.print(f"[bold cyan]Running workflow:[/bold cyan] {wf.name} ({len(wf.steps)} steps)")
        
        def on_step(step, status):
            icon = "[WAIT]" if status == "running" else ("[OK]" if status == "completed" else "[FAIL]")
            color = "yellow" if status == "running" else ("green" if status == "completed" else "red")
            console.print(f"[{color}]{icon} [{step.type.upper()}] {step.name}...[/{color}]")

        success = engine.execute(wf, on_step_update=on_step)
        if success:
            console.print(f"\n[bold green]Workflow '{wf.name}' executed successfully![/bold green]")
        else:
            console.print(f"\n[bold red]Workflow '{wf.name}' failed at some step.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error running workflow:[/bold red] {e}")

@workflow_group.command("list")
def workflow_list():
    """List available workflows."""
    table = Table(title="Available Workflows")
    table.add_column("Workflow", style="bold cyan")
    table.add_column("Location")
    candidates = list(Path("workflows").glob("*.yaml")) + list((Path(".vader") / "workflows").glob("*.yaml"))
    for c in candidates:
        table.add_row(c.name, str(c))
    console.print(table)

@cli.group("cron")
def cron_group():
    """Manage scheduled automated tasks."""
    pass

@cron_group.command("list")
def cron_list():
    """List scheduled background cron jobs."""
    jobs = cron_scheduler.list_jobs()
    if not jobs:
        console.print("[dim]No cron jobs scheduled. Use 'vader cron add' to schedule one.[/dim]")
        return
    table = Table(title="Scheduled Cron Tasks")
    table.add_column("ID", style="bold cyan")
    table.add_column("Schedule", style="yellow")
    table.add_column("Type")
    table.add_column("Payload", style="dim")
    for j in jobs:
        table.add_row(j.id, j.schedule, j.task_type, j.payload)
    console.print(table)

@cron_group.command("add")
@click.option("--id", "job_id", required=True, help="Unique job ID")
@click.option("--schedule", required=True, help="Cron expression (e.g. '*/30 * * * *')")
@click.option("--type", "task_type", default="prompt", type=click.Choice(["prompt", "workflow", "command"]))
@click.argument("payload")
def cron_add(job_id, schedule, task_type, payload):
    """Add a new scheduled cron job."""
    try:
        job = cron_scheduler.add_job(job_id, schedule, task_type, payload)
        console.print(f"[bold green]Added cron job:[/bold green] [cyan]{job.id}[/cyan] ({job.schedule})")
    except Exception as e:
        console.print(f"[bold red]Failed to add cron job:[/bold red] {e}")

@cron_group.command("remove")
@click.argument("job_id")
def cron_remove(job_id):
    """Remove a scheduled cron job."""
    if cron_scheduler.remove_job(job_id):
        console.print(f"[green]Removed job {job_id}[/green]")
    else:
        console.print(f"[yellow]Job {job_id} not found[/yellow]")

@cli.command("diff")
def diff_cmd():
    """Display uncommitted git diffs."""
    engine = VaderEngine()
    print_diff(engine.harness.get_git_diff())

if __name__ == "__main__":
    cli()
