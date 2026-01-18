# ============================================
# Installation de la config Claude Code
# ============================================

param(
    [switch]$Force,
    [switch]$SkipScripts,
    [switch]$SkipSounds
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Config Claude Code" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$CLAUDE_DIR = "$env:USERPROFILE\.claude"

# Vérifier que Claude Code est installé
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "ERREUR: Claude Code n'est pas installé." -ForegroundColor Red
    Write-Host "Installez-le d'abord: https://claude.ai/code" -ForegroundColor Yellow
    exit 1
}

# Créer le dossier .claude si nécessaire
if (-not (Test-Path $CLAUDE_DIR)) {
    New-Item -ItemType Directory -Path $CLAUDE_DIR -Force | Out-Null
}

# 1. settings.json
Write-Host "[1/5] Installation de settings.json..." -ForegroundColor Yellow
$settingsDest = "$CLAUDE_DIR\settings.json"
if ((Test-Path $settingsDest) -and -not $Force) {
    Write-Host "  ATTENTION: settings.json existe déjà" -ForegroundColor Yellow
    $response = Read-Host "  Voulez-vous le remplacer? (o/N)"
    if ($response -eq 'o' -or $response -eq 'O') {
        $backup = "$settingsDest.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $settingsDest $backup
        Write-Host "  Backup: $backup" -ForegroundColor Gray
        Copy-Item "$SCRIPT_DIR\settings.json" $settingsDest -Force
        Write-Host "  OK" -ForegroundColor Green
    } else {
        Write-Host "  SKIP" -ForegroundColor Gray
    }
} else {
    Copy-Item "$SCRIPT_DIR\settings.json" $settingsDest -Force
    Write-Host "  OK" -ForegroundColor Green
}

# 2. CLAUDE.md
Write-Host "[2/5] Installation de CLAUDE.md..." -ForegroundColor Yellow
Copy-Item "$SCRIPT_DIR\CLAUDE.md" "$CLAUDE_DIR\CLAUDE.md" -Force
Write-Host "  OK" -ForegroundColor Green

# 3. Statusline
Write-Host "[3/5] Installation du script statusline..." -ForegroundColor Yellow
Copy-Item "$SCRIPT_DIR\statusline-git.ps1" "$CLAUDE_DIR\statusline-git.ps1" -Force
Write-Host "  OK" -ForegroundColor Green

# 4. Scripts (hooks)
if (-not $SkipScripts) {
    Write-Host "[4/5] Installation des scripts (hooks)..." -ForegroundColor Yellow

    $scriptsDir = "$CLAUDE_DIR\scripts"
    if (-not (Test-Path $scriptsDir)) {
        New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
    }

    # command-validator
    if (Test-Path "$SCRIPT_DIR\scripts\command-validator") {
        Copy-Item "$SCRIPT_DIR\scripts\command-validator" "$scriptsDir\" -Recurse -Force
        Write-Host "  command-validator OK" -ForegroundColor Green

        # Installer les dépendances
        Push-Location "$scriptsDir\command-validator"
        if (Get-Command bun -ErrorAction SilentlyContinue) {
            Write-Host "  Installation des dépendances (bun)..." -ForegroundColor Gray
            bun install 2>$null
        }
        Pop-Location
    }

    # quality-checks
    if (Test-Path "$SCRIPT_DIR\scripts\quality-checks") {
        Copy-Item "$SCRIPT_DIR\scripts\quality-checks" "$scriptsDir\" -Recurse -Force
        Write-Host "  quality-checks OK" -ForegroundColor Green

        Push-Location "$scriptsDir\quality-checks"
        if (Get-Command bun -ErrorAction SilentlyContinue) {
            Write-Host "  Installation des dépendances (bun)..." -ForegroundColor Gray
            bun install 2>$null
        }
        Pop-Location
    }
} else {
    Write-Host "[4/5] Installation des scripts... SKIP" -ForegroundColor Gray
}

# 5. Rules
Write-Host "[5/5] Installation des rules..." -ForegroundColor Yellow
$rulesDir = "$CLAUDE_DIR\rules"
if (-not (Test-Path $rulesDir)) {
    New-Item -ItemType Directory -Path $rulesDir -Force | Out-Null
}
if (Test-Path "$SCRIPT_DIR\rules\delegator") {
    Copy-Item "$SCRIPT_DIR\rules\delegator" "$rulesDir\" -Recurse -Force
    Write-Host "  delegator OK" -ForegroundColor Green
}

# 6. Sons (bonus)
if (-not $SkipSounds) {
    Write-Host "[Bonus] Installation des sons..." -ForegroundColor Yellow
    $songDir = "$CLAUDE_DIR\song"
    if (-not (Test-Path $songDir)) {
        New-Item -ItemType Directory -Path $songDir -Force | Out-Null
    }
    if (Test-Path "$SCRIPT_DIR\song") {
        Copy-Item "$SCRIPT_DIR\song\*" "$songDir\" -Force
        Write-Host "  OK" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation terminée !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration installée:" -ForegroundColor Cyan
Write-Host "  - settings.json (permissions, hooks, plugins)" -ForegroundColor White
Write-Host "  - CLAUDE.md (instructions globales)" -ForegroundColor White
Write-Host "  - statusline-git.ps1 (barre de statut)" -ForegroundColor White
Write-Host "  - Scripts de validation (hooks)" -ForegroundColor White
Write-Host "  - Rules de délégation GPT" -ForegroundColor White
Write-Host "  - Sons de notification" -ForegroundColor White
Write-Host ""
Write-Host "Redémarrez Claude Code pour appliquer." -ForegroundColor Yellow
