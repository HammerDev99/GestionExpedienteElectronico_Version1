
import sys
import subprocess
import os

executable = os.path.join(os.path.dirname(sys.argv[0]), "AgilEx_by_Marduk.exe")
try:
    result = subprocess.run([executable], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error al ejecutar la aplicación:")
        print(result.stderr)
        input("Presiona Enter para cerrar...")
except Exception as e:
    print(f"Error al iniciar: {str(e)}")
    input("Presiona Enter para cerrar...")
