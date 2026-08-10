"""tcecode CLI — ponto de entrada."""

import os
import subprocess
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .agent import agent_ok, agent_path, install_agent, installed_version, APPROVED_VERSION
from .auth import clear_token, get_valid_token, load_token, password_login, save_token
from .config import TceCodeConfig, load_config, save_config, write_agent_config, GATEWAY_URL, KEYCLOAK_URL

app = typer.Typer(
    name="tcecode",
    help="TCE Code — Institutional AI Coding Agent",
    no_args_is_help=False,
)
console = Console()


def _ensure_agent() -> None:
    if not agent_ok():
        console.print("[yellow]Engine não instalado.[/yellow] Instalando agora...")
        install_agent()


@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Modelo lógico institucional"),
) -> None:
    """Inicia uma sessão de coding com o agente institucional."""
    if ctx.invoked_subcommand is not None:
        return

    cfg = load_config()
    realm_url = cfg.keycloak_url or KEYCLOAK_URL

    # JWT: identidade do desenvolvedor (quem está usando)
    jwt = get_valid_token(realm_url)

    # Virtual key: credencial de acesso ao LiteLLM (por squad)
    api_key = cfg.virtual_key

    if not jwt and not api_key:
        console.print(
            "[yellow]Não autenticado.[/yellow] "
            "Execute [bold]tcecode login[/bold] para autenticar."
        )
        raise typer.Exit(1)

    if not api_key:
        console.print(
            "[yellow]Virtual key não configurada.[/yellow] "
            "Execute [bold]tcecode configure[/bold] ou peça ao AI_SQUAD_ADMIN."
        )
        raise typer.Exit(1)

    _ensure_agent()
    effective_model = model or cfg.default_model
    write_agent_config(cfg, api_key=api_key)

    auth_method = "JWT+" if jwt else "virtual-key"
    console.print(
        f"[green]TCE Code[/green] "
        f"squad=[bold]{cfg.squad or '?'}[/bold] "
        f"modelo=[bold]{effective_model}[/bold] "
        f"auth=[dim]{auth_method}[/dim]"
    )
    env = os.environ.copy()
    env["OPENCODE_DISABLE_AUTOUPDATE"] = "1"
    env["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"
    subprocess.run([str(agent_path())], check=False, env=env)


@app.command()
def login(
    username: str = typer.Option(..., "--username", "-u", prompt="Usuário institucional"),
    password: str = typer.Option(..., "--password", "-p", prompt=True, hide_input=True),
) -> None:
    """Autenticar com credenciais institucionais via Keycloak."""
    cfg = load_config()
    realm_url = cfg.keycloak_url or KEYCLOAK_URL

    console.print(f"Autenticando em [cyan]{realm_url}[/cyan]...")

    try:
        token = password_login(realm_url, username, password)
    except RuntimeError as exc:
        console.print(f"[red]Falha na autenticação:[/red] {exc}")
        raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[red]Erro ao conectar ao Keycloak:[/red] {exc}")
        raise typer.Exit(1)

    save_token(token)
    console.print(f"[green]Autenticado![/green] Sessão válida por {token.get('expires_in', 300)//60} min.")

    _ensure_agent()
    if cfg.virtual_key:
        write_agent_config(cfg, api_key=cfg.virtual_key)
        console.print("Engine configurado.")
    else:
        console.print("[yellow]Virtual key não configurada.[/yellow] Execute [bold]tcecode configure[/bold].")


@app.command()
def logout() -> None:
    """Encerrar sessão e remover token local."""
    clear_token()
    console.print("[green]Sessão encerrada.[/green] Execute [bold]tcecode login[/bold] para autenticar novamente.")


@app.command()
def configure(
    gateway_url: str = typer.Option(GATEWAY_URL, "--gateway", help="URL do AI Gateway"),
    squad: str = typer.Option(..., "--squad", prompt="Squad"),
    virtual_key: str = typer.Option(..., "--key", prompt="Virtual key (fornecida pelo AI_SQUAD_ADMIN)", hide_input=True),
    model: str = typer.Option("institutional-coding", "--model", help="Modelo padrão"),
) -> None:
    """Configura o tcecode (Fase 1 — virtual key)."""
    cfg = TceCodeConfig(gateway_url=gateway_url, squad=squad, virtual_key=virtual_key, default_model=model)
    save_config(cfg)
    console.print(f"[green]Configurado.[/green] Squad: [bold]{squad}[/bold], Modelo: [bold]{model}[/bold]")


@app.command()
def update() -> None:
    """Instala ou atualiza o engine para a versão aprovada pela plataforma."""
    current = installed_version()
    if current == APPROVED_VERSION:
        console.print(f"[green]Engine já está na versão aprovada ({APPROVED_VERSION}).[/green]")
        return
    if current:
        console.print(f"Atualizando engine {current} → {APPROVED_VERSION}...")
    install_agent(APPROVED_VERSION)


@app.command()
def models() -> None:
    """Lista os modelos institucionais disponíveis no gateway."""
    import json, ssl, urllib.request, urllib.error

    cfg = load_config()
    api_key = cfg.virtual_key

    if not api_key:
        console.print("[yellow]Virtual key não configurada.[/yellow] Execute [bold]tcecode configure[/bold].")
        raise typer.Exit(1)

    url = cfg.gateway_url.rstrip("/").removesuffix("/v1") + "/v1/models"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        console.print(f"[red]Erro ao buscar modelos:[/red] {exc.code} {exc.reason}")
        raise typer.Exit(1)
    except OSError as exc:
        console.print(f"[red]Gateway inacessível:[/red] {exc}")
        raise typer.Exit(1)

    model_ids = [m["id"] for m in data.get("data", [])]
    if not model_ids:
        console.print("[yellow]Nenhum modelo disponível no gateway.[/yellow]")
        return

    table = Table(title="Modelos Institucionais — TCE Code")
    table.add_column("Modelo", style="cyan bold")
    for mid in model_ids:
        table.add_row(mid)
    console.print(table)


@app.command()
def status() -> None:
    """Exibe configuração e verifica conectividade com o gateway."""
    import urllib.request, urllib.error

    cfg = load_config()
    console.print(f"Gateway:       [cyan]{cfg.gateway_url}[/cyan]")
    console.print(f"Squad:         [cyan]{cfg.squad or '(não configurado)'}[/cyan]")
    console.print(f"Modelo padrão: [cyan]{cfg.default_model}[/cyan]")
    console.print(f"Virtual key:   {'[green]configurada[/green]' if cfg.virtual_key else '[red]não configurada[/red]'}")
    console.print(f"Engine:        [cyan]{installed_version() or 'não instalado'}[/cyan] (aprovado: {APPROVED_VERSION})")

    # JWT status
    jwt = get_valid_token(cfg.keycloak_url or KEYCLOAK_URL)
    if jwt:
        console.print("Auth (JWT):    [green]ativo[/green]")
    else:
        token = load_token()
        if token:
            console.print("Auth (JWT):    [yellow]expirado — execute tcecode login[/yellow]")
        else:
            console.print("Auth (JWT):    [dim]não autenticado (Fase 1: virtual key)[/dim]")

    base_url = cfg.gateway_url.rstrip("/").removesuffix("/v1")
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        urllib.request.urlopen(f"{base_url}/health", timeout=5, context=ctx)
        console.print("Gateway:       [green]online[/green]")
    except (urllib.error.URLError, OSError):
        console.print("Gateway:       [red]offline ou inacessível[/red]")


def main() -> None:
    app()
