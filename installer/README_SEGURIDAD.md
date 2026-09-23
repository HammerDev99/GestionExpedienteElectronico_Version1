# AgilEx by Marduk — Instrucciones de firma y empaquetado

## Qué es este paquete

AgilEx by Marduk es una herramienta de automatización que genera índices electrónicos de expedientes judiciales conforme al Acuerdo PCSJA20-11567 de 2020. Lleva 3.5 años en operación en la Rama Judicial.

Este paquete contiene el ejecutable **sin firmar** junto con las herramientas para que el área de Seguridad Informática lo firme con el certificado institucional, lo empaquete como MSI y lo prepare para distribución.

## Por qué se firman dos archivos

| Artefacto | Qué protege |
|---|---|
| `AgilEx_by_Marduk.exe` | El uso diario. Es el archivo que se ejecuta cada vez que un funcionario abre la aplicación, y el que evalúan Defender/ASR/AppLocker |
| `AgilEx_..._firmado.msi` | La instalación. Es lo que se distribuye y se despliega por GPO/SCCM |

El orden es obligatorio: primero el `.exe`, luego el `.msi`. Un MSI firmado es inmutable, por lo que su contenido debe estar firmado antes de empaquetarlo.

## Qué certificado se necesita

El certificado debe tener el **EKU de firma de código** (`Code Signing`, OID `1.3.6.1.5.5.7.3.3`), con validación **OV** o **EV**.

Un certificado **TLS de servidor** (OID `1.3.6.1.5.5.7.3.1`), como el que protege los sitios web institucionales, **no sirve para este proceso** aunque sea de la entidad y esté vigente. Son emisiones distintas ante la autoridad certificadora.

Con el parámetro `/u` de `signtool` es posible aplicar la firma con un certificado TLS, pero `/u` solo cambia lo que `signtool` acepta al firmar, no lo que Windows exige al verificar. El resultado:

- Windows reporta la firma como *no válida para el uso solicitado*.
- AppLocker no reconoce ningún editor, así que no se puede crear una regla por editor.
- En equipos con Control de aplicaciones activo (por ejemplo, Smart App Control), el ejecutable firmado **queda bloqueado**, mientras que el mismo ejecutable sin firmar se ejecuta.

Por eso el script no admite `/u`: detecta el certificado TLS en el preflight y se detiene con código 10 antes de tocar el ejecutable.

Para verificar un certificado antes de usarlo:

```powershell
$c = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Thumbprint -eq "HUELLA" }
$c.Extensions | Where-Object { $_.Oid.Value -eq "2.5.29.37" } |
    ForEach-Object { $_.EnhancedKeyUsages } |
    Format-Table Value, FriendlyName
```

Debe aparecer `1.3.6.1.5.5.7.3.3` en la lista.

## Modos de firma

El script admite dos modos, según dónde viva la llave privada.

| Modo | Cuándo usarlo | La llave privada |
|---|---|---|
| **Azure Key Vault** | La entidad ya opera un Key Vault | Nunca sale del vault |
| **Almacén local** | Certificado en archivo PFX o token físico/HSM | Se instala en el almacén de Windows, o vive en el token |

**Se recomienda Azure Key Vault** cuando esté disponible: la firma ocurre de forma remota, no hay material sensible que transportar por correo ni que instalar en la estación de firma, y el vault deja registro de auditoría de cada operación de firma.

## Prerequisitos

| Herramienta | Cómo instalarla | Modo |
|---|---|---|
| WiX Toolset v6 | `dotnet tool install --global wix --version 6.0.1` | Ambos |
| AzureSignTool | `dotnet tool install --global AzureSignTool` | Key Vault |
| Windows SDK (signtool) | Componente "Signing Tools" del Windows SDK | Almacén local |
| WinRAR | Opcional. Si falta, el proceso deja el MSI firmado sin comprimir | Ambos |

> **Si el script reporta "No se encontró la herramienta wix" pese a haberla instalado:**
> ejecute `dotnet tool list --global` para confirmar que aparece en la lista. Si aparece,
> el problema es que `%USERPROFILE%\.dotnet\tools` no está en el PATH del usuario — agréguelo
> y abra una consola nueva. Si no aparece, instálela con el comando de la tabla anterior.

`dotnet tool install --global wix` sin versión instala v7 por defecto (requiere aceptar un EULA distinto) y el script está probado contra 6.0.1 con las extensiones pinneadas a esa misma versión.

### Modo almacén local: cómo poner el certificado en el almacén

En este modo el certificado debe estar **instalado en el almacén de Windows** (`Cert:\CurrentUser\My` o `Cert:\LocalMachine\My`), no como archivo suelto. El script nunca recibe ni transporta la llave privada: solo referencia el certificado por su huella (thumbprint) una vez que ya está en el almacén.

**Si el certificado institucional llega como archivo `.pfx` (con contraseña):**

```powershell
Import-PfxCertificate -FilePath "C:\ruta\al\certificado.pfx" `
    -CertStoreLocation Cert:\CurrentUser\My `
    -Password (Read-Host -AsSecureString "Contraseña del PFX")
```

También puede hacerse con doble clic en el `.pfx` y siguiendo el asistente de importación de Windows (elegir el almacén "Personal").

**Si el certificado institucional vive en un token físico o HSM:** no requiere importación — el software del proveedor del token ya lo expone automáticamente en el almacén de Windows al conectarlo.

En ambos casos, una vez instalado, verifíquelo con el paso siguiente.

## Ejecución

Descomprimir el paquete completo en una carpeta local y ejecutar según el modo elegido.

### Modo Azure Key Vault

```powershell
az login
.\build-signed-msi.ps1 -KeyVaultUrl "https://NOMBRE-DEL-VAULT.vault.azure.net" `
    -KeyVaultCertificate "NOMBRE-DEL-CERTIFICADO"
```

La identidad autenticada necesita permiso **Get** sobre certificados y **Sign** sobre llaves en el vault.

Para automatización desatendida puede usarse un service principal con `-KeyVaultClientId`, `-KeyVaultTenantId` y `-KeyVaultClientSecret`. Se recomienda preferir `az login` o una identidad administrada: el secret pasado por línea de comandos queda en el historial de la consola y en el `transcript.log`.

### Modo almacén local

1. Obtener la huella del certificado:

   ```powershell
   Get-ChildItem Cert:\CurrentUser\My | Format-List Subject, Thumbprint, NotAfter
   ```

2. Ejecutar:

   ```powershell
   .\build-signed-msi.ps1 -Thumbprint "HUELLA_DEL_CERTIFICADO"
   ```

Los dos modos son excluyentes: PowerShell rechaza la invocación si se combinan parámetros de ambos.

El script no requiere privilegios de administrador. Accede a internet para el sellado de tiempo (`http://timestamp.digicert.com`, configurable con `-TimestampUrl`) y, en modo Key Vault, al vault de Azure.

## Qué hace, paso a paso

| Etapa | Acción |
|---|---|
| 0 | Verifica herramientas (signtool o AzureSignTool, wix, opcionalmente Rar.exe) y, en modo local, el certificado (vigencia, EKU de firma de código) |
| 1 | Compara el SHA256 del ejecutable con el declarado en `MANIFIESTO.txt` |
| 2 | Firma el ejecutable con SHA256 y sellado de tiempo RFC 3161 |
| 3 | Empaqueta el MSI con WiX |
| 4 | Firma el MSI |
| 5 | Comprime el MSI en RAR (si `Rar.exe` no está disponible, continúa sin comprimir) |
| 6 | Genera `REPORTE_FIRMA.txt` |

La etapa 1 permite confirmar que se está firmando exactamente el binario que el desarrollador declaró, sin alteraciones en tránsito.

## Salida

Todo queda en la subcarpeta `salida\`:

- `AgilEx_by_Marduk_v<version>_firmado.msi` — instalador firmado
- `AgilEx_v<version>_firmado.rar` — comprimido para distribución
- `REPORTE_FIRMA.txt` — evidencia con hashes, certificado y sellos de tiempo
- `transcript.log` — traza completa de la ejecución

## Códigos de error

| Código | Etapa | Significado |
|---|---|---|
| 10 | Preflight | Falta una herramienta, el certificado no existe/está vencido/no sirve para firma de código, falta un archivo del paquete, o la ruta de `-OutputDir` no es accesible |
| 20 | Integridad | El SHA256 no coincide. **No firmar**: solicitar reenvío del paquete |
| 30 | Firma exe | `signtool`/`AzureSignTool` falló o el estado de la firma es inesperado |
| 40 | MSI | `wix build` falló (revise que el icono viaja junto al `.wxs`) |
| 50 | Firma MSI | `signtool`/`AzureSignTool` falló sobre el MSI |
| 99 | Error no controlado | Situación no prevista por el script — revise `transcript.log` en la carpeta de salida y contacte al desarrollador |

Ante cualquier fallo, la carpeta de salida contiene `transcript.log` con la traza completa.

## Nota sobre el hash y el incidente 804977

Este trabajo responde al incidente `RJ-MDE-MAL-ALERT-002` / ID `804977`, en el que Microsoft XDR marcó el ejecutable como `Malgent`.

**El SHA256 del ejecutable cambia al firmarlo.** El hash documentado previamente ante el SOC corresponde al binario firmado con el certificado autofirmado del desarrollador. Tras la firma institucional será distinto, y esa diferencia es esperada — no indica alteración. `REPORTE_FIRMA.txt` registra ambos valores.

Una vez firmado con el certificado institucional, es posible crear una regla de AppLocker/WDAC **por publisher** que confíe en ese certificado. Una sola regla cubre esta versión y todas las futuras sin intervención adicional.

## Contacto

Daniel Arbeláez Álvarez — darbelaal@cendoj.ramajudicial.gov.co
