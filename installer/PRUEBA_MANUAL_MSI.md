# Prueba manual del instalador MSI

> Estos pasos requieren una consola **PowerShell ejecutada como administrador**.
> La instalación per-machine escribe en `Program Files` y en `HKLM`, por lo que
> Windows exige elevación UAC.
>
> Verifique que el título de la ventana diga **"Administrador: Windows PowerShell"**.
> Si no lo dice, ciérrela y ábrala con clic derecho → *Ejecutar como administrador*.

Cada bloque es autocontenido: incluye el `cd` y las variables que necesita, para
que pueda copiarse y pegarse sin depender de lo que se ejecutó antes.

---

## 0. Preparación (obligatorio antes de todo)

Este paso evita los dos errores más comunes: que `wix` no se encuentre, y que se
pruebe un MSI antiguo sin darse cuenta.

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1

# WiX se instala como herramienta global de dotnet, pero su carpeta no siempre
# queda en el PATH permanente. Esta linea la agrega solo para esta consola.
$env:PATH = "$env:USERPROFILE\.dotnet\tools;$env:PATH"

# Verificar que wix responde (debe imprimir la version, p. ej. 6.0.1+...)
wix --version
```

**Si `wix --version` falla:** ejecute `dotnet tool list --global`. Si `wix` aparece
en la lista, el problema es solo el PATH — repita la línea `$env:PATH` de arriba.
Si no aparece, instálelo con `dotnet tool install --global wix --version 6.0.1`.

### 0.1 Confirmar la plataforma del MSI

**Este es el paso que más problemas evita.** Un MSI compilado sin `-arch x64` se
instala en `Program Files (x86)` aunque el sistema sea de 64 bits, porque Windows
Installer redirige `ProgramFiles64Folder` automáticamente. El resultado es que las
verificaciones posteriores dan `False` sin explicar la causa.

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1

$wi = New-Object -ComObject WindowsInstaller.Installer
$db = $wi.GetType().InvokeMember("OpenDatabase","InvokeMethod",$null,$wi,@("$PWD\dist\AgilEx_test.msi",0))
$si = $db.GetType().InvokeMember("SummaryInformation","GetProperty",$null,$db,@(0))
$si.GetType().InvokeMember("Property","GetProperty",$null,$si,@(7))
```

**Esperado:** `x64;1034`

**Si imprime `Intel;1034` o cualquier otra cosa:** el MSI es antiguo. Regenérelo
con el bloque de la sección 6.1 antes de continuar.

### 0.2 Partir de un equipo limpio

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1

# Desinstalar cualquier residuo de pruebas anteriores (no falla si no hay nada)
Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test.msi','/qn' -Wait -ErrorAction SilentlyContinue
Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test_152.msi','/qn' -Wait -ErrorAction SilentlyContinue

# Confirmar que no queda nada registrado
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -like "*AgilEx*" } |
    Select-Object DisplayName, DisplayVersion
```

**Esperado:** sin resultados (ninguna fila).

---

## 1. Instalación silenciosa

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1

Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test.msi','/qn','/l*v','dist\install.log' -Wait

Write-Host "--- Ejecutable en Program Files ---"
Test-Path "$env:ProgramFiles\AgilEx by Marduk\AgilEx_by_Marduk.exe"
Write-Host "--- Acceso directo escritorio ---"
Test-Path "$env:PUBLIC\Desktop\AgilEx by Marduk.lnk"
Write-Host "--- Acceso directo menu inicio ---"
Test-Path "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\AgilEx by Marduk\AgilEx by Marduk.lnk"
```

**Esperado:** los tres devuelven `True`.

**Si el primero da `False`:** ejecute lo siguiente para ver dónde quedó realmente.

```powershell
Get-ChildItem "C:\Program Files","C:\Program Files (x86)" -Filter "AgilEx*" -ErrorAction SilentlyContinue |
    Select-Object FullName
```

Si aparece bajo `Program Files (x86)`, el MSI no era x64 — vuelva al paso 0.1.

Si falla por otra razón, busque el punto exacto del error en el log:

```powershell
Select-String -Path "dist\install.log" -Pattern "return value 3" -Context 5,2 | Select-Object -First 1
```

---

## 2. Metadatos en Agregar o quitar programas

```powershell
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\* |
    Where-Object { $_.DisplayName -like "*AgilEx*" } |
    Select-Object DisplayName, DisplayVersion, Publisher, Contact, InstallLocation |
    Format-List
```

**Esperado:**

| Campo | Valor |
|---|---|
| DisplayName | AgilEx by Marduk - Gestión de Expediente Electrónico |
| DisplayVersion | 1.5.1 |
| Publisher | Daniel Arbelaez Alvarez |
| InstallLocation | C:\Program Files\AgilEx by Marduk\ |

---

## 3. Apertura desde los accesos directos

Abra la aplicación con doble clic en el acceso directo del **escritorio**, y
después desde el **menú inicio**.

**Esperado:** la ventana de AgilEx abre en ambos casos.

Esta es la validación real de la Fase A: la aplicación está en `Program Files`, un
directorio de solo lectura. Antes de la corrección del logger, aquí habría muerto
con `PermissionError` antes de mostrar la ventana.

Con la aplicación abierta, confirme que los logs se escriben fuera del directorio
de instalación:

```powershell
Write-Host "--- Logs recientes en LOCALAPPDATA ---"
Get-ChildItem "$env:LOCALAPPDATA\AgilEx\logs" | Sort-Object LastWriteTime -Descending |
    Select-Object -First 3 Name, LastWriteTime

Write-Host "--- Contenido del directorio de instalacion ---"
Get-ChildItem "$env:ProgramFiles\AgilEx by Marduk"
```

**Esperado:** hay logs recientes en `LOCALAPPDATA`, y en `Program Files` está
**únicamente** `AgilEx_by_Marduk.exe` — ningún archivo nuevo.

---

## 4. Desinstalación con la aplicación abierta

**Deje AgilEx abierto** y ejecute:

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1

Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test.msi','/qb','/l*v','dist\uninstall_abierto.log' -Wait
```

**Esperado:** el instalador detecta la aplicación en uso y **pide cerrarla**, sin
exigir reiniciar el equipo.

Este escenario motivó incluir `util:CloseApplication` en el instalador: el
bootloader onefile de PyInstaller deja un proceso hijo que retiene el ejecutable.
Sin esa detección, Windows Installer pediría reinicio — inaceptable en un
despliegue por GPO a cientos de equipos.

Verifique en el log que no se exigió reinicio:

```powershell
Select-String -Path "dist\uninstall_abierto.log" -Pattern "REBOOT REQUIRED|ForceReboot|Reinicie el equipo"
```

**Esperado:** sin coincidencias.

> **Nota sobre falsos positivos en esta búsqueda:** las líneas
> `MsiSystemRebootPending`, `RESTART MANAGER: Session opened` y
> `Scheduling file ... for deletion during post-install cleanup (not post-reboot)`
> son normales y **no** indican que se pida reinicio. `MsiSystemRebootPending`
> refleja un reinicio pendiente de Windows por otra causa ajena a esta instalación.

---

## 5. Desinstalación limpia

Si el paso 4 dejó la aplicación instalada, desinstale con todo cerrado:

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1

Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test.msi','/qn' -Wait

Test-Path "$env:ProgramFiles\AgilEx by Marduk"
Test-Path "$env:PUBLIC\Desktop\AgilEx by Marduk.lnk"
```

**Esperado:** ambos devuelven `False` — sin residuos ni accesos directos huérfanos.

---

## 6. Actualización sin entradas duplicadas

Esta es la prueba que valida el `UpgradeCode`, **la decisión no corregible una vez
distribuida**. Si falla, debe corregirse antes de entregar el paquete.

### 6.1 Generar un MSI de versión 1.5.2

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1
$env:PATH = "$env:USERPROFILE\.dotnet\tools;$env:PATH"

Push-Location installer\wix
wix build Product.wxs `
  -arch x64 `
  -ext WixToolset.UI.wixext/6.0.1 `
  -ext WixToolset.Util.wixext/6.0.1 `
  -d ExeSourcePath="C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1\dist\AgilEx_by_Marduk.exe" `
  -d ProductVersion="1.5.2" `
  -o "C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1\dist\AgilEx_test_152.msi"
Write-Host "EXIT: $LASTEXITCODE"
Pop-Location
```

**Esperado:** `EXIT: 0` y el archivo `dist\AgilEx_test_152.msi` creado.

**No continúe si este paso falla.** Si `wix` no se reconoce, vuelva al paso 0. Si
omite este bloque, el paso siguiente instalaría un archivo inexistente o antiguo y
la prueba daría un resultado falso.

Confirme que el archivo existe y es reciente:

```powershell
Get-ChildItem dist\AgilEx_test_152.msi | Select-Object Name, Length, LastWriteTime
```

### 6.2 Instalar 1.5.1 y actualizar a 1.5.2

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1

# Instalar la version base
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test.msi','/qn' -Wait

# Instalar la version superior encima
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test_152.msi','/qn' -Wait

# Debe haber UNA sola entrada, en version 1.5.2
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\* |
    Where-Object { $_.DisplayName -like "*AgilEx*" } |
    Select-Object DisplayName, DisplayVersion
```

**Esperado:** exactamente **una** fila, con `DisplayVersion` = `1.5.2`.

**Si aparecen dos filas** (1.5.1 y 1.5.2 por separado): el `UpgradeCode` está mal
configurado. Detenga la prueba y repórtelo — es un defecto que no tiene arreglo
remoto una vez que el paquete se distribuya.

**Si aparece una sola fila pero dice `1.5.1`:** el MSI 1.5.2 no se generó
correctamente en el paso 6.1. Repítalo verificando que `EXIT: 0`.

Limpieza:

```powershell
Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test_152.msi','/qn' -Wait
```

---

## 7. Bloqueo de downgrade

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1

# Instalar la version superior
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test_152.msi','/qn' -Wait

# Intentar instalar la anterior encima (con interfaz, para ver el mensaje)
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test.msi','/qb' -Wait
```

**Esperado:** el instalador rechaza la versión anterior con el mensaje
*"Ya está instalada una versión más reciente de AgilEx by Marduk."*

---

## 8. Limpieza final

```powershell
cd C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1

Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test_152.msi','/qn' -Wait -ErrorAction SilentlyContinue
Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test.msi','/qn' -Wait -ErrorAction SilentlyContinue

Write-Host "--- Debe quedar todo en False y sin filas ---"
Test-Path "$env:ProgramFiles\AgilEx by Marduk"
Test-Path "$env:PUBLIC\Desktop\AgilEx by Marduk.lnk"
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -like "*AgilEx*" } |
    Select-Object DisplayName, DisplayVersion
```

---

## Registro de resultados

Anote el resultado de cada paso en
`scripts\certificacion_firma_digital\evidencias\validacion_msi.txt`
(**cree el archivo**, aún no existe).

| # | Prueba | Resultado |
|---|---|---|
| 0.1 | MSI declarado como `x64;1034` | |
| 1 | Instalación silenciosa en `Program Files` + accesos directos | |
| 2 | Metadatos ARP correctos | |
| 3 | Apertura desde ambos accesos directos + logs en LOCALAPPDATA | |
| 4 | Desinstalación con la app abierta, sin exigir reinicio | |
| 5 | Desinstalación limpia | |
| 6 | Actualización 1.5.1 → 1.5.2 con una sola entrada | |
| 7 | Bloqueo de downgrade | |
| 8 | Limpieza final sin residuos | |

Si algún paso falla, guarde el `.log` correspondiente de `dist\`: contiene la
causa exacta.
