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

## Prerequisitos

| Herramienta | Cómo instalarla |
|---|---|
| Windows SDK (signtool) | Componente "Signing Tools" del Windows SDK |
| WiX Toolset v6 | `dotnet tool install --global wix --version 6.0.1` |
| WinRAR | Opcional. Si falta, el proceso deja el MSI firmado sin comprimir |

> **Si el script reporta "No se encontró la herramienta wix" pese a haberla instalado:**
> ejecute `dotnet tool list --global` para confirmar que aparece en la lista. Si aparece,
> el problema es que `%USERPROFILE%\.dotnet\tools` no está en el PATH del usuario — agréguelo
> y abra una consola nueva. Si no aparece, instálela con el comando de la tabla anterior.

`dotnet tool install --global wix` sin versión instala v7 por defecto (requiere aceptar un EULA distinto) y el script está probado contra 6.0.1 con las extensiones pinneadas a esa misma versión.

Se necesita el certificado de firma de código institucional **instalado en el almacén de Windows** (`Cert:\CurrentUser\My` o `Cert:\LocalMachine\My`), no como archivo suelto. El script nunca recibe ni transporta la llave privada: solo referencia el certificado por su huella (thumbprint) una vez que ya está en el almacén.

### Cómo poner el certificado en el almacén

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

1. Descomprimir el paquete completo en una carpeta local.
2. Obtener la huella del certificado:

   ```powershell
   Get-ChildItem Cert:\CurrentUser\My | Format-List Subject, Thumbprint, NotAfter
   ```

3. Ejecutar:

   ```powershell
   .\build-signed-msi.ps1 -Thumbprint "HUELLA_DEL_CERTIFICADO"
   ```

El script no requiere privilegios de administrador ni accede a internet salvo al servicio de sellado de tiempo (`http://timestamp.digicert.com`, configurable con `-TimestampUrl`).

## Qué hace, paso a paso

| Etapa | Acción |
|---|---|
| 0 | Verifica herramientas (signtool, wix, opcionalmente Rar.exe) y el certificado (vigencia, EKU de firma de código) |
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
| 30 | Firma exe | `signtool` falló o el estado de la firma es inesperado |
| 40 | MSI | `wix build` falló (revise que el icono viaja junto al `.wxs`) |
| 50 | Firma MSI | `signtool` falló sobre el MSI |
| 99 | Error no controlado | Situación no prevista por el script — revise `transcript.log` en la carpeta de salida y contacte al desarrollador |

Ante cualquier fallo, la carpeta de salida contiene `transcript.log` con la traza completa.

## Nota sobre el hash y el incidente 804977

Este trabajo responde al incidente `RJ-MDE-MAL-ALERT-002` / ID `804977`, en el que Microsoft XDR marcó el ejecutable como `Malgent`.

**El SHA256 del ejecutable cambia al firmarlo.** El hash documentado previamente ante el SOC corresponde al binario firmado con el certificado autofirmado del desarrollador. Tras la firma institucional será distinto, y esa diferencia es esperada — no indica alteración. `REPORTE_FIRMA.txt` registra ambos valores.

Una vez firmado con el certificado institucional, es posible crear una regla de AppLocker/WDAC **por publisher** que confíe en ese certificado. Una sola regla cubre esta versión y todas las futuras sin intervención adicional.

## Contacto

Daniel Arbeláez Álvarez — darbelaal@cendoj.ramajudicial.gov.co
