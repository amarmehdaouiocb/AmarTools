# ============================================
# Installation du STT GUI
# ============================================
# Exécuter en tant qu'administrateur si nécessaire
# ============================================

param(
    [switch]$SkipPluginInstall,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation STT GUI pour Claude Code" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Chemins
$STT_DIR = "$env:USERPROFILE\.claude\plugins\claude-stt"
$PLUGIN_CACHE = "$env:USERPROFILE\.claude\plugins\cache\jarrodwatts-claude-stt\claude-stt\0.1.0"
$HOOKS_FILE = "$PLUGIN_CACHE\hooks\hooks.json"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Vérifier que le plugin claude-stt est installé
Write-Host "[1/5] Vérification du plugin claude-stt..." -ForegroundColor Yellow
if (-not (Test-Path $PLUGIN_CACHE)) {
    if ($SkipPluginInstall) {
        Write-Host "ERREUR: Le plugin claude-stt n'est pas installé." -ForegroundColor Red
        Write-Host "Installez-le d'abord avec: claude plugin install jarrodwatts/claude-stt" -ForegroundColor Red
        exit 1
    }
    Write-Host "Le plugin n'est pas installé. Installation..." -ForegroundColor Yellow
    & claude plugin install jarrodwatts/claude-stt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Impossible d'installer le plugin." -ForegroundColor Red
        exit 1
    }
}
Write-Host "  OK - Plugin trouvé" -ForegroundColor Green

# 2. Créer le dossier STT config
Write-Host "[2/5] Création du dossier de configuration..." -ForegroundColor Yellow
if (-not (Test-Path $STT_DIR)) {
    New-Item -ItemType Directory -Path $STT_DIR -Force | Out-Null
}
Write-Host "  OK - $STT_DIR" -ForegroundColor Green

# 3. Copier le GUI
Write-Host "[3/5] Installation du GUI STT..." -ForegroundColor Yellow
$guiSource = Join-Path $SCRIPT_DIR "stt_gui.pyw"
$guiDest = Join-Path $STT_DIR "stt_gui.pyw"
if (Test-Path $guiSource) {
    Copy-Item $guiSource $guiDest -Force
    Write-Host "  OK - stt_gui.pyw installé" -ForegroundColor Green
} else {
    Write-Host "  ERREUR: stt_gui.pyw non trouvé dans $SCRIPT_DIR" -ForegroundColor Red
    exit 1
}

# 4. Désactiver le hook de démarrage automatique
Write-Host "[4/5] Désactivation du démarrage automatique du daemon..." -ForegroundColor Yellow
if (Test-Path $HOOKS_FILE) {
    $hooksContent = '{ "hooks": {} }'
    Set-Content -Path $HOOKS_FILE -Value $hooksContent -Encoding UTF8
    Write-Host "  OK - Hook SessionStart désactivé" -ForegroundColor Green
} else {
    Write-Host "  SKIP - Fichier hooks.json non trouvé" -ForegroundColor Yellow
}

# 5. Ajouter les fonctions au profil PowerShell
Write-Host "[5/5] Configuration du profil PowerShell..." -ForegroundColor Yellow
$profilePath = $PROFILE
$profileDir = Split-Path -Parent $profilePath

if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

# Vérifier si les fonctions STT sont déjà dans le profil
$profileContent = ""
if (Test-Path $profilePath) {
    $profileContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
}

if ($profileContent -like "*Start-STTGUI*" -and -not $Force) {
    Write-Host "  SKIP - Fonctions STT déjà présentes dans le profil" -ForegroundColor Yellow
} else {
    # Lire les fonctions à ajouter
    $functionsFile = Join-Path $SCRIPT_DIR "profile-functions.ps1"
    if (Test-Path $functionsFile) {
        $functionsContent = Get-Content $functionsFile -Raw

        # Supprimer les anciennes définitions si -Force
        if ($Force -and $profileContent) {
            # Pattern pour supprimer l'ancien bloc STT
            $profileContent = $profileContent -replace '(?s)# ={10,}\s*# Claude STT.*?Set-Alias -Name sttstatus -Value Get-STTStatus\s*', ''
        }

        # Ajouter les nouvelles fonctions
        if ($profileContent) {
            $newContent = $profileContent.TrimEnd() + "`n`n" + $functionsContent
        } else {
            $newContent = $functionsContent
        }

        Set-Content -Path $profilePath -Value $newContent -Encoding UTF8
        Write-Host "  OK - Fonctions ajoutées à $profilePath" -ForegroundColor Green
    } else {
        Write-Host "  ERREUR: profile-functions.ps1 non trouvé" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation terminée !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Commandes disponibles (après redémarrage du terminal):" -ForegroundColor Cyan
Write-Host "  stt        - Lancer le GUI STT" -ForegroundColor White
Write-Host "  sttstop    - Arrêter tous les processus STT" -ForegroundColor White
Write-Host "  sttdaemon  - Lancer le daemon (hotkey global)" -ForegroundColor White
Write-Host "  sttstatus  - Afficher le statut" -ForegroundColor White
Write-Host ""
Write-Host "Redémarrez votre terminal pour appliquer les changements." -ForegroundColor Yellow
