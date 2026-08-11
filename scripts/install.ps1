# Instalador do tcecode — Windows (PowerShell).
#
# Uso:
#   irm https://bitbucket.org/tcesc-git/tcecode/raw/master/scripts/install.ps1 | iex
#
# Clona o repositório institucional (CLI + fork do OpenCode) e builda o
# tcecode-agent localmente com Bun. Não depende de binário pré-buildado —
# o build leva alguns minutos na primeira instalação.

$ErrorActionPreference = "Stop"

$RepoSsh = "git@bitbucket.org:tcesc-git/tcecode.git"
$RepoHttps = "https://bitbucket.org/tcesc-git/tcecode.git"
$ForkSsh = "git@github.com:brenothales/opencode.git"
$ForkHttps = "https://github.com/brenothales/opencode.git"
$ForkBranch = "dev"

# O agent.py resolve o caminho do fork relativo ao proprio clone (import
# editavel) - por isso mantemos um clone persistente em vez de pip solto.
$InstallDir = if ($env:TCECODE_SRC_DIR) { $env:TCECODE_SRC_DIR } else { "$env:LOCALAPPDATA\tcecode-src" }

Write-Host "==> Instalando tcecode em $InstallDir..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python nao encontrado. Instale Python 3.10+ (https://python.org) antes de continuar."
    exit 1
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git nao encontrado. Instale o Git for Windows antes de continuar."
    exit 1
}

if (-not (Get-Command pipx -ErrorAction SilentlyContinue)) {
    Write-Host "==> pipx nao encontrado, instalando..."
    python -m pip install --user pipx
    python -m pipx ensurepath
}

$sshOk = $false
try {
    $sshTest = ssh -T git@bitbucket.org -o BatchMode=yes -o ConnectTimeout=5 2>&1
    if ($sshTest -match "authenticated|logged in") { $sshOk = $true }
} catch {}

if ($sshOk) {
    $RepoUrl = $RepoSsh
    $ForkUrl = $ForkSsh
} else {
    Write-Host "Aviso: SSH para bitbucket.org nao configurado - usando HTTPS (pode pedir credenciais)."
    $RepoUrl = $RepoHttps
    $ForkUrl = $ForkHttps
}

Write-Host "==> Clonando/atualizando $RepoUrl..."
if (Test-Path "$InstallDir\.git") {
    git -C $InstallDir pull --ff-only
} else {
    git clone $RepoUrl $InstallDir
}

Write-Host "==> Clonando/atualizando o fork do OpenCode ($ForkBranch)..."
$ForkDir = "$InstallDir\opencode"
if (Test-Path "$ForkDir\.git") {
    git -C $ForkDir pull --ff-only
} else {
    git clone --branch $ForkBranch --depth 1 $ForkUrl $ForkDir
}

if (-not (Get-Command bun -ErrorAction SilentlyContinue)) {
    Write-Host "==> Bun nao encontrado, instalando..."
    irm https://bun.sh/install.ps1 | iex
    $env:Path = "$env:USERPROFILE\.bun\bin;$env:Path"
}

Write-Host "==> Buildando tcecode-agent (isso pode levar alguns minutos na primeira vez)..."
Push-Location "$ForkDir\packages\opencode"
try {
    bun install
    bun run script/build.ts --single --skip-embed-web-ui
} finally {
    Pop-Location
}

Write-Host "==> Instalando o CLI tcecode (editavel, via pipx)..."
pipx install --force -e "$InstallDir\cli"

tcecode update

Write-Host ""
Write-Host "==> tcecode instalado! Rode 'tcecode login' para autenticar e 'tcecode configure' para configurar sua squad."
