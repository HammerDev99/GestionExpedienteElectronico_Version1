# Script de sincronización de documentación
# Construye los docs con MkDocs y los sincroniza con el subproyecto en docs/deploy-docs

Write-Host "🔨 Construyendo documentación con MkDocs..." -ForegroundColor Cyan

# Construir documentación
mkdocs build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir documentación" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Documentación construida exitosamente" -ForegroundColor Green

# Verificar que existe docs/deploy-docs
if (-not (Test-Path "docs\deploy-docs\.git")) {
    Write-Host "⚠️  WARNING: docs\deploy-docs no está inicializado como repositorio Git" -ForegroundColor Yellow
    Write-Host "   Ejecuta primero:" -ForegroundColor Yellow
    Write-Host "   cd docs\deploy-docs" -ForegroundColor Gray
    Write-Host "   git init" -ForegroundColor Gray
    Write-Host "   git branch -M main" -ForegroundColor Gray
    Write-Host "   git remote add origin https://github.com/TU_USUARIO/AgilEx-Docs.git" -ForegroundColor Gray
    exit 1
}

# Limpiar docs/deploy-docs (excepto .git)
Write-Host "🧹 Limpiando docs\deploy-docs..." -ForegroundColor Cyan
Get-ChildItem -Path "docs\deploy-docs" -Exclude ".git" | Remove-Item -Recurse -Force

# Copiar contenido de site/ a docs/deploy-docs/
Write-Host "📦 Copiando archivos a docs\deploy-docs..." -ForegroundColor Cyan
Copy-Item -Path "site\*" -Destination "docs\deploy-docs\" -Recurse -Force

# Crear .gitignore en docs/deploy-docs
$gitignore = @"
# Archivos del sistema
.DS_Store
Thumbs.db
desktop.ini

# Temporales
*.tmp
*.bak
"@
Set-Content -Path "docs\deploy-docs\.gitignore" -Value $gitignore

# Crear README.md en docs/deploy-docs
$readme = @"
# AgilEx by Marduk - Documentación

Documentación estática generada con MkDocs Material.

**URL de producción**: https://docs.agilex.sprintjudicial.com

## 🔄 Actualización Automática

Esta documentación se genera automáticamente desde el proyecto principal:
- Repositorio fuente: [GestionExpedienteElectronico_Version1](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1)
- Generador: MkDocs Material
- Deploy: Easypanel con webhook de GitHub

## 📝 Para actualizar

En el proyecto principal:
``````powershell
# Construir y sincronizar
.\sync-docs.ps1

# Hacer commit y push (ver opciones en el script)
``````

---
*Última actualización: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")*
"@
Set-Content -Path "docs\deploy-docs\README.md" -Value $readme

Write-Host "✅ Archivos sincronizados en docs\deploy-docs" -ForegroundColor Green

# Mostrar estadísticas
$fileCount = (Get-ChildItem -Path "docs\deploy-docs" -Recurse -File | Measure-Object).Count
$totalSize = (Get-ChildItem -Path "docs\deploy-docs" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "📊 Total archivos: $fileCount" -ForegroundColor Yellow
Write-Host "📊 Tamaño total: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Yellow

# Preguntar si hacer commit
Write-Host "`n¿Deseas hacer commit y push ahora? (S/N)" -ForegroundColor Yellow
$respuesta = Read-Host

if ($respuesta -eq "S" -or $respuesta -eq "s") {
    Push-Location "docs\deploy-docs"

    # Ver estado
    git status

    Write-Host "`n📝 Ingresa el mensaje del commit (Enter para usar mensaje automático):" -ForegroundColor Cyan
    $commitMessage = Read-Host

    if ([string]::IsNullOrWhiteSpace($commitMessage)) {
        $commitMessage = "Actualiza documentación - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }

    # Commit
    git add .
    git commit -m $commitMessage

    # Push
    Write-Host "`n🚀 Haciendo push a GitHub..." -ForegroundColor Cyan
    git push origin main

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Push exitoso! Webhook de Easypanel se activará automáticamente" -ForegroundColor Green
        Write-Host "🌐 Documentación estará disponible en: https://docs.agilex.sprintjudicial.com" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Error al hacer push" -ForegroundColor Red
    }

    Pop-Location
} else {
    Write-Host "`n💡 Puedes hacer commit manualmente:" -ForegroundColor Yellow
    Write-Host "   cd docs\deploy-docs" -ForegroundColor Gray
    Write-Host "   git add ." -ForegroundColor Gray
    Write-Host "   git commit -m 'Actualiza documentación'" -ForegroundColor Gray
    Write-Host "   git push origin main" -ForegroundColor Gray
}

Write-Host "`n🎉 ¡Proceso completado!" -ForegroundColor Green
