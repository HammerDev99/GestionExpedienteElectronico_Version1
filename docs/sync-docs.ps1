# Script de sincronización de documentación
# Construye los docs con MkDocs directamente en docs/deploy-docs/
# Ejecutar desde: docs/sync-docs.ps1

Write-Host "📍 Ubicación actual: $PWD" -ForegroundColor Gray

# Ir al directorio raíz del proyecto (un nivel arriba)
$projectRoot = Split-Path -Parent $PSScriptRoot
$deployPath = Join-Path $projectRoot "docs\deploy-docs"

Push-Location $projectRoot

Write-Host "🔨 Construyendo documentación con MkDocs..." -ForegroundColor Cyan

# Construir documentación (MkDocs la genera directamente en docs/deploy-docs/)
mkdocs build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir documentación" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "✅ Documentación construida exitosamente en docs/deploy-docs/" -ForegroundColor Green

# Verificar que existe docs/deploy-docs
if (-not (Test-Path "$deployPath\.git")) {
    Write-Host "⚠️  WARNING: docs\deploy-docs no está inicializado como repositorio Git" -ForegroundColor Yellow
    Write-Host "   Ejecuta primero:" -ForegroundColor Yellow
    Write-Host "   cd docs\deploy-docs" -ForegroundColor Gray
    Write-Host "   git init" -ForegroundColor Gray
    Write-Host "   git branch -M main" -ForegroundColor Gray
    Write-Host "   git remote add origin https://github.com/TU_USUARIO/AgilEx-Docs.git" -ForegroundColor Gray
    Pop-Location
    exit 1
}

# Crear Dockerfile para Nginx
<# $dockerfile = @"
# Dockerfile para servir documentación estática con Nginx
# Optimizado para MkDocs Material

FROM nginx:alpine

# Copiar archivos estáticos al directorio de Nginx
COPY . /usr/share/nginx/html

# Configuración personalizada de Nginx para docs
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Habilitar compresión gzip \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json; \
    \
    # Cache de recursos estáticos \
    location ~* \.(?:css|js|jpg|jpeg|gif|png|ico|svg|woff|woff2|ttf|eot)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
    \
    # Manejar rutas para documentación \
    location / { \
        try_files $uri $uri/ =404; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80
"@
Set-Content -Path "$deployPath\Dockerfile" -Value $dockerfile

# Crear .dockerignore
$dockerignore = @"
# Excluir archivos innecesarios del build de Docker
.git
.gitignore
README.md
"@
Set-Content -Path "$deployPath\.dockerignore" -Value $dockerignore

# Crear .gitignore
$gitignore = @"
# Archivos del sistema
.DS_Store
Thumbs.db
desktop.ini

# Temporales
*.tmp
*.bak
"@
Set-Content -Path "$deployPath\.gitignore" -Value $gitignore #>

# Crear README.md
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

En el proyecto principal (desde la carpeta docs/):
``````powershell
# Construir y sincronizar
.\sync-docs.ps1

# Hacer commit manualmente en deploy-docs/
cd deploy-docs
git add .
git commit -m "Actualiza documentación"
git push origin main
``````

---
*Última actualización: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")*
"@
Set-Content -Path "$deployPath\README.md" -Value $readme

Write-Host "✅ Archivos sincronizados en deploy-docs/" -ForegroundColor Green

# Mostrar estadísticas
$fileCount = (Get-ChildItem -Path $deployPath -Recurse -File | Measure-Object).Count
$totalSize = (Get-ChildItem -Path $deployPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "📊 Total archivos: $fileCount" -ForegroundColor Yellow
Write-Host "📊 Tamaño total: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Yellow

# Volver al directorio original
Pop-Location

Write-Host "`n✅ Sincronización completada!" -ForegroundColor Green
Write-Host "`n💡 Para publicar los cambios:" -ForegroundColor Cyan
Write-Host "   cd deploy-docs" -ForegroundColor Gray
Write-Host "   git add ." -ForegroundColor Gray
Write-Host "   git commit -m 'Actualiza documentación v1.5.0'" -ForegroundColor Gray
Write-Host "   git push origin main" -ForegroundColor Gray
Write-Host "`n🌐 Una vez pusheado, Easypanel actualizará automáticamente:" -ForegroundColor Cyan
Write-Host "   https://docs.agilex.sprintjudicial.com" -ForegroundColor Blue
Write-Host "`n🎉 ¡Listo!" -ForegroundColor Green
