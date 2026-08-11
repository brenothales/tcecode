# Instalador do tcecode — Windows (PowerShell).
#
# Uso:
#   irm https://bitbucket.org/tcesc-git/tcecode/raw/main/scripts/install.ps1 | iex
#
# Instala o CLI `tcecode` (via pipx, direto do repositório) e o engine
# tcecode-agent (binário publicado em Bitbucket Downloads pelo bitbucket-pipelines.yml).

$ErrorActionPreference = "Stop"

$RepoSsh = "git+ssh://git@bitbucket.org/tcesc-git/tcecode.git#subdirectory=cli"
$RepoHttps = "git+https://bitbucket.org/tcesc-git/tcecode.git#subdirectory=cli"

Write-Host "==> Instalando tcecode..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python nao encontrado. Instale Python 3.10+ (https://python.org) antes de continuar."
    exit 1
}

if (-not (Get-Command pipx -ErrorAction SilentlyContinue)) {
    Write-Host "==> pipx nao encontrado, instalando..."
    python -m pip install --user pipx
    python -m pipx ensurepath
    Write-Host "Reabra o terminal se o comando 'pipx' nao for encontrado no proximo passo."
}

Write-Host "==> Instalando o CLI tcecode (via pipx)..."
$sshOk = $false
try {
    $sshTest = ssh -T git@bitbucket.org 2>&1
    if ($sshTest -match "authenticated|logged in") { $sshOk = $true }
} catch {}

if ($sshOk) {
    pipx install $RepoSsh
} else {
    Write-Host "Aviso: SSH para bitbucket.org nao configurado - tentando HTTPS (pode pedir usuario/senha ou app password)."
    pipx install $RepoHttps
}

Write-Host "==> Instalando o engine (tcecode-agent)..."
try {
    tcecode update
} catch {
    Write-Host ""
    Write-Host "Nao foi possivel baixar o engine automaticamente."
    Write-Host "Se o repositorio for privado, configure credenciais do Bitbucket"
    Write-Host "(usuario + App Password) e rode: tcecode update"
    exit 1
}

Write-Host ""
Write-Host "==> tcecode instalado! Rode 'tcecode login' para autenticar e 'tcecode configure' para configurar sua squad."
