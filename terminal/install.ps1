#Requires -RunAsAdministrator
# ============================================
# Installation complète du terminal
# ============================================
# Exécuter en tant qu'administrateur :
# powershell -ExecutionPolicy Bypass -File install.ps1
# ============================================

param(
    [switch]$SkipTools,      # Passer l'installation des outils CLI
    [switch]$SkipModules,    # Passer l'installation des modules PowerShell
    [switch]$SkipProfile,    # Passer la copie du profil
    [switch]$SkipSTT,        # Passer l'installation du STT
    [switch]$Force           # Forcer le remplacement du profil existant
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Terminal Amar" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPO_ROOT = Split-Path -Parent $SCRIPT_DIR

# ============================================
# 1. Installation des outils CLI via winget
# ============================================
if (-not $SkipTools) {
    Write-Host "[1/4] Installation des outils CLI..." -ForegroundColor Yellow

    $tools = @(
        @{ Name = "Starship"; Id = "Starship.Starship" },
        @{ Name = "zoxide"; Id = "ajeetdsouza.zoxide" },
        @{ Name = "fzf"; Id = "junegunn.fzf" },
        @{ Name = "Git"; Id = "Git.Git" }
    )

    foreach ($tool in $tools) {
        Write-Host "  Vérification de $($tool.Name)..." -NoNewline
        $installed = winget list --id $tool.Id 2>$null | Select-String $tool.Id
        if ($installed) {
            Write-Host " déjà installé" -ForegroundColor Green
        } else {
            Write-Host " installation..." -ForegroundColor Yellow
            winget install --id $tool.Id --silent --accept-package-agreements --accept-source-agreements
            if ($LASTEXITCODE -eq 0) {
                Write-Host "    OK" -ForegroundColor Green
            } else {
                Write-Host "    ERREUR" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "[1/4] Installation des outils CLI... SKIP" -ForegroundColor Gray
}

# ============================================
# 2. Installation des modules PowerShell
# ============================================
if (-not $SkipModules) {
    Write-Host ""
    Write-Host "[2/4] Installation des modules PowerShell..." -ForegroundColor Yellow

    $modules = @("PSFzf", "PSReadLine")

    foreach ($module in $modules) {
        Write-Host "  Vérification de $module..." -NoNewline
        if (Get-Module -ListAvailable -Name $module) {
            Write-Host " déjà installé" -ForegroundColor Green
        } else {
            Write-Host " installation..." -ForegroundColor Yellow
            Install-Module -Name $module -Force -Scope CurrentUser -AllowClobber
            Write-Host "    OK" -ForegroundColor Green
        }
    }
} else {
    Write-Host "[2/4] Installation des modules PowerShell... SKIP" -ForegroundColor Gray
}

# ============================================
# 3. Installation du profil PowerShell
# ============================================
if (-not $SkipProfile) {
    Write-Host ""
    Write-Host "[3/4] Installation du profil PowerShell..." -ForegroundColor Yellow

    $profileSource = Join-Path $SCRIPT_DIR "Microsoft.PowerShell_profile.ps1"
    $profileDest = $PROFILE
    $profileDir = Split-Path -Parent $profileDest

    # Créer le dossier si nécessaire
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }

    # Vérifier si un profil existe déjà
    if ((Test-Path $profileDest) -and -not $Force) {
        Write-Host "  ATTENTION: Un profil existe déjà à $profileDest" -ForegroundColor Yellow
        $response = Read-Host "  Voulez-vous le remplacer? (o/N)"
        if ($response -ne 'o' -and $response -ne 'O') {
            Write-Host "  SKIP - Profil non remplacé" -ForegroundColor Gray
        } else {
            # Backup
            $backup = "$profileDest.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
            Copy-Item $profileDest $backup
            Write-Host "  Backup créé: $backup" -ForegroundColor Gray
            Copy-Item $profileSource $profileDest -Force
            Write-Host "  OK - Profil installé" -ForegroundColor Green
        }
    } else {
        if (Test-Path $profileDest) {
            $backup = "$profileDest.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
            Copy-Item $profileDest $backup
            Write-Host "  Backup créé: $backup" -ForegroundColor Gray
        }
        Copy-Item $profileSource $profileDest -Force
        Write-Host "  OK - Profil installé à $profileDest" -ForegroundColor Green
    }
} else {
    Write-Host "[3/4] Installation du profil PowerShell... SKIP" -ForegroundColor Gray
}

# ============================================
# 4. Installation du STT GUI
# ============================================
if (-not $SkipSTT) {
    Write-Host ""
    Write-Host "[4/4] Installation du STT GUI..." -ForegroundColor Yellow

    $sttInstaller = Join-Path $REPO_ROOT "stt\install.ps1"
    if (Test-Path $sttInstaller) {
        & $sttInstaller -SkipPluginInstall:$false
    } else {
        Write-Host "  ERREUR: Script STT non trouvé à $sttInstaller" -ForegroundColor Red
    }
} else {
    Write-Host "[4/4] Installation du STT GUI... SKIP" -ForegroundColor Gray
}

# ============================================
# Résumé
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation terminée !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Outils installés:" -ForegroundColor Cyan
Write-Host "  - Starship    (prompt moderne)" -ForegroundColor White
Write-Host "  - zoxide      (navigation intelligente, utiliser 'z')" -ForegroundColor White
Write-Host "  - fzf + PSFzf (fuzzy finder, Ctrl+F / Ctrl+R)" -ForegroundColor White
Write-Host "  - PSReadLine  (autocomplétion améliorée)" -ForegroundColor White
Write-Host ""
Write-Host "Commandes STT:" -ForegroundColor Cyan
Write-Host "  - stt         (lancer le GUI)" -ForegroundColor White
Write-Host "  - sttstop     (arrêter)" -ForegroundColor White
Write-Host ""
Write-Host "Alias utiles:" -ForegroundColor Cyan
Write-Host "  - gs, gp, gf, gl, gd  (Git shortcuts)" -ForegroundColor White
Write-Host "  - .., ..., ....       (navigation rapide)" -ForegroundColor White
Write-Host "  - ll                  (ls détaillé)" -ForegroundColor White
Write-Host "  - e                   (ouvrir explorer)" -ForegroundColor White
Write-Host "  - ff <pattern>        (recherche fichiers)" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Redémarrez votre terminal pour appliquer les changements." -ForegroundColor Yellow
Write-Host ""
