"""tce-ai CLI — ponto de entrada principal."""

import subprocess
import shutil
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .config import load_config, save_config, write_opencode_config, TceAiConfig, GATEWAY_URL

app = typer.Typer(
    name="tce-ai",
    help="Institutional AI Engineering Platform — Tribunal de Contas",
    no_args_is_help=False,
)
console = Console()


def _require_opencode() -> str:
    path = shutil.which("opencode")
    if not path:
        console.print(
            "[red]OpenCode não encontrado.[/red] "
            "Execute [bold]tce-ai install[/bold] para instalar.",
        )
        raise typer.Exit(1)
    return path


@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Modelo lógico institucional"),
) -> None:
    """Inicia uma sessão de coding com o agente institucional."""
    if ctx.invoked_subcommand is not None:
        return

    cfg = load_config()

    if not cfg.virtual_key:
        console.print(
            "[yellow]Nenhuma chave configurada.[/yellow] "
            "Execute [bold]tce-ai configure[/bold] para configurar.",
        )
        raise typer.Exit(1)

    effective_model = model or cfg.default_model
    write_opencode_config(cfg, api_key=cfg.virtual_key)

    opencode_bin = _require_opencode()
    console.print(
        f"[green]Iniciando sessão[/green] "
        f"modelo=[bold]{effective_model}[/bold] "
        f"gateway=[dim]{cfg.gateway_url}[/dim]"
    )
    subprocess.run([opencode_bin], check=False)


@app.command()
def configure(
    gateway_url: str = typer.Option(GATEWAY_URL, "--gateway", help="URL do AI Gateway"),
    squad: str = typer.Option(..., "--squad", prompt="Nome da squad"),
    virtual_key: str = typer.Option(..., "--key", prompt="Virtual key (fornecida pelo AI_SQUAD_ADMIN)", hide_input=True),
    model: str = typer.Option("institutional-coding", "--model", help="Modelo padrão"),
) -> None:
    """Configura o tce-ai com a virtual key da squad (Fase 1)."""
    cfg = TceAiConfig(
        gateway_url=gateway_url,
        squad=squad,
        virtual_key=virtual_key,
        default_model=model,
    )
    save_config(cfg)
    console.print(f"[green]Configurado.[/green] Squad: [bold]{squad}[/bold], Modelo: [bold]{model}[/bold]")


@app.command()
def models() -> None:
    """Lista os modelos lógicos institucionais disponíveis."""
    table = Table(title="Modelos Institucionais")
    table.add_column("Nome lógico", style="cyan bold")
    table.add_column("Uso indicado")
    table.add_column("Provider atual")

    rows = [
        ("institutional-coding", "Coding primário — alta qualidade", "Anthropic Claude 3.5"),
        ("institutional-reasoning", "Raciocínio complexo, arquitetura", "OpenAI o3"),
        ("institutional-fast", "Tarefas rápidas, autocompletion", "Google Gemini Flash"),
        ("institutional-local", "Código sensível, air-gapped", "Ollama / vLLM on-prem"),
    ]
    for name, use, provider in rows:
        table.add_row(name, use, provider)

    console.print(table)


@app.command()
def status() -> None:
    """Exibe a configuração atual e verifica conectividade com o gateway."""
    import urllib.request
    import urllib.error

    cfg = load_config()
    console.print(f"Gateway: [cyan]{cfg.gateway_url}[/cyan]")
    console.print(f"Squad: [cyan]{cfg.squad or '(não configurado)'}[/cyan]")
    console.print(f"Modelo padrão: [cyan]{cfg.default_model}[/cyan]")
    console.print(f"Virtual key: {'[green]configurada[/green]' if cfg.virtual_key else '[red]não configurada[/red]'}")

    # health está na raiz do gateway, não dentro de /v1
    base_url = cfg.gateway_url.rstrip("/").removesuffix("/v1")
    try:
        urllib.request.urlopen(f"{base_url}/health", timeout=5)
        console.print("Gateway: [green]online[/green]")
    except (urllib.error.URLError, OSError):
        console.print("Gateway: [red]offline ou inacessível[/red]")


@app.command()
def install() -> None:
    """Instala ou atualiza o OpenCode (coding agent)."""
    console.print("Instalando OpenCode...")
    # Fase 1: instrução manual; Fase 3+ terá download automático versionado
    console.print(
        "Acesse [link=https://github.com/sst/opencode]https://github.com/sst/opencode[/link] "
        "e siga as instruções de instalação para o seu sistema operacional."
    )
    console.print("Após instalar, execute [bold]tce-ai status[/bold] para verificar.")


def main() -> None:
    app()
