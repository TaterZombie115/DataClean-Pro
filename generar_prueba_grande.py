
from pathlib import Path
import pandas as pd

carpeta = Path("datos_ejemplo")
carpeta.mkdir(exist_ok=True)

registros = []

for i in range(45000):
    registros.append({
        "Producto": f"Producto_{i % 100}",
        "Cantidad": "" if i % 20 == 0 else str((i % 10) + 1),
        "Precio": "" if i % 30 == 0 else str(100 + i),
        "Cliente": f"Cliente_{i}"
    })

# Agregar 5,000 duplicados exactos
registros.extend(registros[:5000].copy())

datos = pd.DataFrame(registros)

ruta = carpeta / "prueba_50000.csv"
datos.to_csv(ruta, index=False, encoding="utf-8-sig")

print("Archivo de prueba generado correctamente.")
print(f"Registros: {len(datos)}")
print(f"Ubicación: {ruta.resolve()}")
