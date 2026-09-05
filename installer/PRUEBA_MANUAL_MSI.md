# Prueba manual del instalador MSI

> Estos pasos requieren una consola **PowerShell ejecutada como administrador**.
> La instalación per-machine escribe en `Program Files` y en `HKLM`, por lo que
> Windows exige elevación UAC.
>
> El MSI a probar es `dist\AgilEx_test.msi` (sin firmar; la firma la aplica el
> área de Seguridad Informática en el flujo definitivo).

Abre PowerShell como administrador y sitúate en la raíz del proyecto:

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1
```

---

## 1. Instalación silenciosa

```powershell
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test.msi','/qn','/l*v','dist\install.log' -Wait
```

**Esperado:** termina sin interacción y sin error.

Verifica el resultado:

```powershell
Test-Path "$env:ProgramFiles\AgilEx by Marduk\AgilEx_by_Marduk.exe"
Test-Path "$env:PUBLIC\Desktop\AgilEx by Marduk.lnk"
Test-Path "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\AgilEx by Marduk\AgilEx by Marduk.lnk"
```

**Esperado:** los tres devuelven `True`.

Si alguno falla, revisa `dist\install.log` (busca "return value 3", que marca el punto de error).

---

## 2. Metadatos en Agregar o quitar programas

```powershell
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\* |
    Where-Object { $_.DisplayName -like "*AgilEx*" } |
    Select-Object DisplayName, DisplayVersion, Publisher, Contact
```

**Esperado:**

| Campo | Valor |
|---|---|
| DisplayName | AgilEx by Marduk - Gestión de Expediente Electrónico |
| DisplayVersion | 1.5.1 |
| Publisher | Daniel Arbelaez Alvarez |
| Contact | darbelaal@cendoj.ramajudicial.gov.co |

---

## 3. Apertura desde los accesos directos

Abre la aplicación con doble clic en el acceso directo del **escritorio**, y después
desde el **menú inicio**.

**Esperado:** la ventana de AgilEx abre en ambos casos.

Esta es la validación real de la Fase A: la aplicación está en `Program Files`, un
directorio de solo lectura. Antes de la corrección del logger, aquí habría muerto
con `PermissionError` antes de mostrar la ventana.

Confirma que los logs se escriben fuera del directorio de instalación:

```powershell
Get-ChildItem "$env:LOCALAPPDATA\AgilEx\logs" | Select-Object -Last 3 Name, LastWriteTime
Get-ChildItem "$env:ProgramFiles\AgilEx by Marduk"
```

**Esperado:** hay logs recientes en `LOCALAPPDATA`, y en `Program Files` está
**únicamente** `AgilEx_by_Marduk.exe` — ningún archivo nuevo.

---

## 4. Desinstalación con la aplicación abierta (Ruling G)

**Deja AgilEx abierto** y ejecuta:

```powershell
Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test.msi','/qb','/l*v','dist\uninstall_abierto.log' -Wait
```

**Esperado:** el instalador detecta la aplicación en uso y **pide cerrarla**, sin
exigir reiniciar el equipo.

Este es el escenario que motivó añadir `util:CloseApplication`: el bootloader onefile
de PyInstaller deja un proceso hijo que retiene el ejecutable. Sin esa detección,
Windows Installer pediría reinicio — inaceptable en un despliegue por GPO a cientos
de equipos.

Comprueba en el log que no se solicitó reinicio:

```powershell
Select-String -Path "dist\uninstall_abierto.log" -Pattern "REBOOT|Restart|reinici" | Select-Object -First 5
```

**Esperado:** sin coincidencias que indiquen reinicio obligatorio.

---

## 5. Desinstalación limpia

Si el paso 4 dejó la aplicación instalada, desinstala con todo cerrado:

```powershell
Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test.msi','/qn' -Wait
Test-Path "$env:ProgramFiles\AgilEx by Marduk"
Test-Path "$env:PUBLIC\Desktop\AgilEx by Marduk.lnk"
```

**Esperado:** ambos devuelven `False` — sin residuos ni accesos directos huérfanos.

---

## 6. Actualización sin entradas duplicadas

Esta es la prueba que valida el `UpgradeCode`, la decisión no corregible a posteriori.

```powershell
# Instala 1.5.1
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test.msi','/qn' -Wait

# Genera un MSI 1.5.2 con el mismo ejecutable
cd installer\wix
wix build Product.wxs `
  -ext WixToolset.UI.wixext/6.0.1 `
  -ext WixToolset.Util.wixext/6.0.1 `
  -d ExeSourcePath="C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1\dist\AgilEx_by_Marduk.exe" `
  -d ProductVersion="1.5.2" `
  -o "C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1\dist\AgilEx_test_152.msi"
cd ..\..

# Instala 1.5.2 encima
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test_152.msi','/qn' -Wait

# Debe haber UNA sola entrada, en version 1.5.2
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\* |
    Where-Object { $_.DisplayName -like "*AgilEx*" } |
    Select-Object DisplayName, DisplayVersion
```

**Esperado:** exactamente **una** entrada, con `DisplayVersion` = `1.5.2`.

Dos entradas indicarían un `UpgradeCode` mal configurado — se corrige antes de
distribuir, porque una vez desplegado no tiene arreglo remoto.

Limpieza final:

```powershell
Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test_152.msi','/qn' -Wait
```

---

## 7. Bloqueo de downgrade

```powershell
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test_152.msi','/qn' -Wait
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test.msi','/qb' -Wait
```

**Esperado:** el instalador rechaza la versión anterior con el mensaje
"Ya está instalada una versión más reciente de AgilEx by Marduk."

Limpieza:

```powershell
Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test_152.msi','/qn' -Wait
```

---

## Registro de resultados

Anota el resultado de cada paso en
`scripts\certificacion_firma_digital\evidencias\validacion_msi.txt`.

| # | Prueba | Resultado |
|---|---|---|
| 1 | Instalación silenciosa + accesos directos | |
| 2 | Metadatos ARP | |
| 3 | Apertura desde ambos accesos directos + logs en LOCALAPPDATA | |
| 4 | Desinstalación con la app abierta, sin reinicio | |
| 5 | Desinstalación limpia | |
| 6 | Actualización 1.5.1 → 1.5.2 con una sola entrada | |
| 7 | Bloqueo de downgrade | |

Si algún paso falla, guarda el `.log` correspondiente: contiene la causa exacta.
