
from pathlib import Path
import pandas as pd
from estilos_excel import aplicar_estilos_excel

def limpiar_archivo(ruta_archivo):
    ruta = Path(ruta_archivo)

    if not ruta.is_file():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    extension = ruta.suffix.lower()

    if extension == ".xlsx":
        datos = pd.read_excel(ruta, dtype=str)
    elif extension == ".csv":
        datos = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
    else:
        raise ValueError("Solo se admiten archivos .xlsx y .csv")

    if datos.empty:
        raise ValueError("El archivo no contiene registros para procesar.")

    filas_originales = len(datos)

    # Limpiar encabezados
    datos.columns = datos.columns.str.strip()

    # Limpiar espacios en los textos
    for columna in datos.columns:
        datos[columna] = datos[columna].map(
            lambda valor: valor.strip()
            if isinstance(valor, str)
            else valor
        )

    # Convertir cadenas vacías en valores faltantes
    datos = datos.replace(r"^\s*$", pd.NA, regex=True)

    
    # Identificar duplicados exactos
    mascara_duplicados = datos.duplicated()

    # Guardar los registros duplicados antes de eliminarlos
    reporte_duplicados = datos.loc[mascara_duplicados].copy()

    # Conservar la fila original del archivo
    reporte_duplicados.insert(
    0,
    "Fila original",
    reporte_duplicados.index + 2
    )

    # Contar duplicados
    duplicados = int(mascara_duplicados.sum())

    # Eliminar duplicados del conjunto principal
    datos = datos.loc[~mascara_duplicados].copy()

    

    # Detectar celdas vacías
    mascara_vacios = datos.isna()

    # Obtener únicamente las posiciones con valores vacíos
    posiciones = mascara_vacios.stack()
    posiciones = posiciones[posiciones].index

    # Crear reporte conservando las filas originales
    reporte_errores = pd.DataFrame(
        [
            {
                "Fila original": indice + 2,
                "Columna": columna,
                "Problema": "Valor vacío"
            }
            for indice, columna in posiciones
        ],
        columns=["Fila original", "Columna", "Problema"]
    )

    # Contar errores detectados
    errores = reporte_errores
    # Generar resumen de procesamiento
    resumen = pd.DataFrame({
        "Indicador": [
            "Registros originales",
            "Duplicados eliminados",
            "Registros finales",
            "Celdas vacías detectadas",
            "Columnas procesadas",
            "Registros con datos incompletos",
        ],
        "Resultado": [
            filas_originales,
            duplicados,
            len(datos),
            len(errores),
            len(datos.columns),
            int(datos.isna().any(axis=1).sum()),
        ],
    })

    # Crear registro de acciones realizadas
    registros_incompletos = int(datos.isna().any(axis=1).sum())

    registro_acciones = pd.DataFrame({
        "Acción": [
            "Limpieza de espacios",
            "Eliminación de duplicados",
            "Detección de celdas vacías",
            "Conservación de registros incompletos",
        ],
        "Resultados": [
            "Aplicada a encabezados y textos",
            f"{duplicados} registros eliminados",
            f"{len(errores)} celdas detectadas",
            f"{registros_incompletos} registros conservados",
        ],
        })


    # Crear carpeta de resultados
    carpeta_resultados = ruta.parent / "resultados"
    carpeta_resultados.mkdir(exist_ok=True)

    ruta_salida = carpeta_resultados / f"{ruta.stem}_limpio.xlsx"

    # Generar archivo con dos hojas
    with pd.ExcelWriter(ruta_salida, engine="openpyxl") as escritor:
        datos.to_excel(
            escritor,
            sheet_name="Datos_Limpios",
            index=False
        )

        reporte_errores.to_excel(
            escritor,
            sheet_name="Errores",
            index=False
        )

        resumen.to_excel(
            escritor,
            sheet_name="Resumen",
            index=False
        )


        reporte_duplicados.to_excel(
            escritor,
            sheet_name="Duplicados_Eliminados",
            index=False
        )

        registro_acciones.to_excel(
            escritor,
            sheet_name="Registro_Acciones",
            index=False
        )

        aplicar_estilos_excel(escritor.book)


    return {
        "archivo_original": str(ruta),
        "archivo_limpio": str(ruta_salida),
        "filas_originales": filas_originales,
        "duplicados_eliminados": duplicados,
        "filas_finales": len(datos),
        "errores_detectados": len(errores),
    }
