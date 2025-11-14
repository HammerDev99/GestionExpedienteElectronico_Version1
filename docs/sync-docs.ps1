<#
.SYNOPSIS
    Script de sincronización de documentación para AgilEx
.DESCRIPTION
    Construye la documentación con MkDocs y genera archivos necesarios para despliegue en Easypanel
.NOTES
    Autor: HammerDev99
    Versión: 2.0
    Ejecutar desde: docs/sync-docs.ps1
#>

#Requires -Version 5.1

# Configuración de manejo de errores
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

#region Funciones auxiliares

function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Type = "Info"
    )

    $emoji = switch ($Type) {
        "Success" { "✅"; $color = "Green" }
        "Error"   { "❌"; $color = "Red" }
        "Warning" { "⚠️ "; $color = "Yellow" }
        "Info"    { "ℹ️ "; $color = "Cyan" }
        "Progress"{ "🔨"; $color = "Cyan" }
        default   { "📍"; $color = "Gray" }
    }

    Write-Host "$emoji $Message" -ForegroundColor $color
}

function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

#endregion

#region Validaciones iniciales

try {
    Write-ColorMessage "Ubicación actual: $PWD" "Default"

    # Validar que MkDocs está instalado
    if (-not (Test-CommandExists "mkdocs")) {
        Write-ColorMessage "MkDocs no está instalado. Instálalo con: pip install mkdocs-material" "Error"
        exit 1
    }

    # Configurar rutas
    $projectRoot = Split-Path -Parent $PSScriptRoot
    $deployPath = Join-Path $projectRoot "docs\deploy-docs"
    $mkdocsYaml = Join-Path $projectRoot "mkdocs.yml"

    # Validar que existe mkdocs.yml
    if (-not (Test-Path $mkdocsYaml)) {
        Write-ColorMessage "No se encontró mkdocs.yml en: $projectRoot" "Error"
        exit 1
    }

    # Cambiar al directorio raíz del proyecto
    Push-Location $projectRoot

    #endregion

    #region Construcción de documentación

    Write-ColorMessage "Construyendo documentación con MkDocs..." "Progress"

    # Ejecutar mkdocs build con captura de salida
    $buildOutput = & mkdocs build 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-ColorMessage "Error al construir documentación" "Error"
        Write-Host $buildOutput -ForegroundColor Red
        exit 1
    }

    Write-ColorMessage "Documentación construida exitosamente en docs/deploy-docs/" "Success"

    #endregion

    #region Validación de repositorio Git

    if (-not (Test-Path "$deployPath\.git")) {
        Write-ColorMessage "docs\deploy-docs no está inicializado como repositorio Git" "Warning"
        Write-Host "`n   Ejecuta primero:" -ForegroundColor Yellow
        Write-Host "   cd docs\deploy-docs" -ForegroundColor Gray
        Write-Host "   git init" -ForegroundColor Gray
        Write-Host "   git branch -M main" -ForegroundColor Gray
        Write-Host "   git remote add origin https://github.com/TU_USUARIO/AgilEx-Docs.git" -ForegroundColor Gray
        Write-ColorMessage "`nNOTA: Se continuará con la generación de archivos..." "Warning"
    }

    #endregion

    #region Generación de archivos para despliegue

    Write-ColorMessage "Generando archivos de despliegue..." "Progress"

    # Crear Dockerfile optimizado para Nginx
    $dockerfile = @"
# Dockerfile para servir documentación estática con Nginx
# Optimizado para MkDocs Material y mejores prácticas de seguridad

FROM nginx:alpine

# Etiquetas de metadata
LABEL maintainer="HammerDev99" \
      description="Documentación estática de AgilEx con Nginx" \
      version="1.0"

# Copiar archivos estáticos al directorio de Nginx
COPY . /usr/share/nginx/html

# Configuración optimizada de Nginx
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Configuración de charset \
    charset utf-8; \
    \
    # Habilitar compresión gzip \
    gzip on; \
    gzip_vary on; \
    gzip_proxied any; \
    gzip_comp_level 6; \
    gzip_min_length 1024; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json application/x-javascript application/xml image/svg+xml; \
    \
    # Cache de recursos estáticos (1 año) \
    location ~* \.(?:css|js|jpg|jpeg|gif|png|ico|cur|gz|svg|svgz|mp4|ogg|ogv|webm|htc|woff|woff2|ttf|eot|webp)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
        access_log off; \
    } \
    \
    # Cache para HTML (sin cache para actualizaciones inmediatas) \
    location ~* \.(?:html)$ { \
        expires -1; \
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0"; \
    } \
    \
    # Manejar rutas para documentación \
    location / { \
        try_files `$uri `$uri/ `$uri/index.html =404; \
    } \
    \
    # Headers de seguridad \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    add_header Referrer-Policy "strict-origin-when-cross-origin" always; \
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always; \
    \
    # Ocultar versión de Nginx \
    server_tokens off; \
    \
    # Logging personalizado \
    access_log /var/log/nginx/access.log; \
    error_log /var/log/nginx/error.log warn; \
}' > /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80

# Healthcheck para validar que Nginx está respondiendo
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1
"@

    # Crear .dockerignore mejorado
    $dockerignore = @"
# Excluir archivos innecesarios del build de Docker

# Control de versiones
.git
.gitignore
.gitattributes
.github

# Documentación
README.md
*.md
!index.md

# Archivos del sistema
.DS_Store
Thumbs.db
desktop.ini
*.swp
*.swo
*~

# Temporales y backup
*.tmp
*.bak
*.log
*.cache

# IDE
.vscode
.idea
*.sublime-*

# Python
__pycache__
*.pyc
*.pyo
.pytest_cache

# Node
node_modules
npm-debug.log
"@

    # Crear .gitignore mejorado
    $gitignore = @"
# Archivos del sistema
.DS_Store
Thumbs.db
desktop.ini
*.swp
*.swo
*~

# Temporales y logs
*.tmp
*.bak
*.log
*.cache

# IDE
.vscode/
.idea/
*.sublime-*

# Build artifacts (si aplica)
*.zip
*.tar.gz
"@

    # Crear README.md mejorado
    $currentDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $readme = @"
# AgilEx by Marduk - Documentación Oficial

[![Deploy Status](https://img.shields.io/badge/deploy-easypanel-blue)](https://docs.agilex.sprintjudicial.com)
[![MkDocs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://squidfunk.github.io/mkdocs-material/)
[![Nginx](https://img.shields.io/badge/server-nginx--alpine-green)](https://nginx.org/)

Documentación estática generada automáticamente con **MkDocs Material**.

## 🌐 URL de Producción

**https://docs.agilex.sprintjudicial.com**

## 📁 Estructura

Este repositorio contiene únicamente los archivos estáticos compilados de la documentación:

- ``index.html`` - Página principal
- ``assets/`` - Recursos estáticos (CSS, JS, imágenes)
- ``search/`` - Índice de búsqueda
- Páginas de documentación en HTML

## 🔄 Actualización Automática

Esta documentación se genera automáticamente desde el proyecto principal:

- **Repositorio fuente**: [GestionExpedienteElectronico_Version1](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1)
- **Generador**: MkDocs Material
- **Deploy**: Easypanel con auto-deploy desde GitHub
- **Stack**: Nginx Alpine + Dockerfile optimizado

## 📝 Flujo de Actualización

### 1. Generar documentación (en el proyecto principal)

``````powershell
# Desde la carpeta docs/
cd docs
.\sync-docs.ps1
``````

### 2. Commit y push

``````bash
cd deploy-docs
git add .
git commit -m "docs: actualiza documentación v1.5.0"
git push origin main
``````

### 3. Deploy automático

Easypanel detecta el push y despliega automáticamente vía webhook de GitHub.

## 🐳 Docker

El despliegue utiliza un contenedor Nginx Alpine optimizado:

- **Imagen base**: ``nginx:alpine``
- **Puerto**: 80
- **Compresión**: gzip mejorado (nivel 6, tipos MIME extendidos)
- **Cache**: Headers optimizados diferenciados (estáticos: 1 año, HTML: sin cache)
- **Seguridad**: Headers HTTP de seguridad configurados
- **Healthcheck**: Verificación automática cada 30s
- **Charset**: UTF-8

## 🔒 Seguridad

- Headers de seguridad HTTP completos
- Sin exposición de versión de Nginx (server_tokens off)
- Permissions-Policy restrictivo
- X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- Referrer-Policy configurado

## 📊 Información del Build

- **Última actualización**: $currentDate
- **Generado por**: sync-docs.ps1 v2.0

---

**Nota**: Este repositorio es generado automáticamente. No edites archivos directamente aquí.
Todos los cambios deben hacerse en el [repositorio fuente](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1).
"@

    # Escribir archivos con encoding UTF-8
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false

    [System.IO.File]::WriteAllText("$deployPath\Dockerfile", $dockerfile, $utf8NoBom)
    [System.IO.File]::WriteAllText("$deployPath\.dockerignore", $dockerignore, $utf8NoBom)
    [System.IO.File]::WriteAllText("$deployPath\.gitignore", $gitignore, $utf8NoBom)
    [System.IO.File]::WriteAllText("$deployPath\README.md", $readme, $utf8NoBom)

    Write-ColorMessage "Archivos de despliegue generados exitosamente" "Success"

    #endregion

    #region Estadísticas

    Write-Host ""
    Write-ColorMessage "Generando estadísticas..." "Progress"

    $files = Get-ChildItem -Path $deployPath -Recurse -File -ErrorAction SilentlyContinue
    $fileCount = ($files | Measure-Object).Count
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum / 1MB

    Write-Host "📊 Total archivos: $fileCount" -ForegroundColor Yellow
    Write-Host "📊 Tamaño total: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Yellow

    #endregion

    #region Instrucciones finales

    Write-Host ""
    Write-ColorMessage "Sincronización completada!" "Success"
    Write-Host ""
    Write-ColorMessage "Para publicar los cambios:" "Info"
    Write-Host "   cd deploy-docs" -ForegroundColor Gray
    Write-Host "   git add ." -ForegroundColor Gray
    Write-Host "   git commit -m 'docs: actualiza documentación v1.5.0'" -ForegroundColor Gray
    Write-Host "   git push origin main" -ForegroundColor Gray
    Write-Host ""
    Write-ColorMessage "Una vez pusheado, Easypanel actualizará automáticamente:" "Info"
    Write-Host "   https://docs.agilex.sprintjudicial.com" -ForegroundColor Blue
    Write-Host ""
    Write-ColorMessage "¡Listo!" "Success"

    #endregion

} catch {
    Write-ColorMessage "Error durante la ejecución del script" "Error"
    Write-Host "Detalles: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Línea: $($_.InvocationInfo.ScriptLineNumber)" -ForegroundColor Red
    exit 1
} finally {
    # Asegurar que volvemos al directorio original
    Pop-Location -ErrorAction SilentlyContinue
}
