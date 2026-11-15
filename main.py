
from limpiador import limpiar_archivo

ruta = input("Introduce la ruta del archivo Excel o CSV: ").strip().strip('"')

try:
    resultado = limpiar_archivo(ruta)

    print("\n=== RESULTADO DE LIMPIEZA ===")
    print(f"Registros originales: {resultado['filas_originales']}")
    print(f"Duplicados eliminados: {resultado['duplicados_eliminados']}")
    print(f"Registros finales: {resultado['filas_finales']}")
    print(f"Celdas vacías detectadas: {resultado['errores_detectados']}")
    print(f"Archivo generado: {resultado['archivo_limpio']}")

except Exception as error:
    print(f"\nError: {error}")
