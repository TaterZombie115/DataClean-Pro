
from limpiador import limpiar_archivo


def ejecutar_limpieza(ruta_archivo, cola):
    """Procesa el archivo en un proceso independiente."""
    try:
        resultado = limpiar_archivo(ruta_archivo)
        cola.put(("exito", resultado))

    except Exception as error:
        cola.put(("error", str(error)))
