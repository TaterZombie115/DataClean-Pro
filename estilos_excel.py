
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def aplicar_estilos_excel(workbook):
    """Aplica estilos optimizados a los reportes Excel."""

    azul_oscuro = "17365D"
    blanco = "FFFFFF"
    gris = "F3F6FA"
    rojo_claro = "FCE8E6"

    # Crear los estilos una sola vez
    fuente_encabezado = Font(
        name="Calibri",
        size=11,
        bold=True,
        color=blanco
    )

    fuente_normal = Font(
        name="Calibri",
        size=11
    )

    fuente_resumen = Font(
        name="Calibri",
        size=12,
        bold=True,
        color=azul_oscuro
    )

    fondo_encabezado = PatternFill(
        fill_type="solid",
        fgColor=azul_oscuro
    )

    fondo_alternado = PatternFill(
        fill_type="solid",
        fgColor=gris
    )

    fondo_error = PatternFill(
        fill_type="solid",
        fgColor=rojo_claro
    )

    alineacion_centro = Alignment(
        horizontal="center",
        vertical="center"
    )

    alineacion_normal = Alignment(
        vertical="center"
    )

    for hoja in workbook.worksheets:

        if hoja.max_row < 1:
            continue

        # 1. Encabezados
        for celda in hoja[1]:
            celda.fill = fondo_encabezado
            celda.font = fuente_encabezado
            celda.alignment = alineacion_centro

        hoja.row_dimensions[1].height = 28
        hoja.freeze_panes = "A2"

        # 2. Estilos de registros
        for fila in hoja.iter_rows(min_row=2):

            numero_fila = fila[0].row

            for celda in fila:
                celda.font = fuente_normal
                celda.alignment = alineacion_normal

                if hoja.title == "Errores":
                    celda.fill = fondo_error

                elif numero_fila % 2 == 0:
                    celda.fill = fondo_alternado

        # 3. Ancho de columnas usando una muestra
        limite = min(hoja.max_row, 200)

        for columna in hoja.iter_cols(
            min_row=1,
            max_row=limite
        ):
            letra = get_column_letter(columna[0].column)

            longitud = max(
                (
                    len(str(celda.value))
                    if celda.value is not None
                    else 0
                )
                for celda in columna
            )

            hoja.column_dimensions[letra].width = min(
                max(longitud + 4, 15),
                45
            )

        # 4. Filtros
        if hoja.max_row > 1:
            hoja.auto_filter.ref = hoja.dimensions

        # 5. Indicadores del resumen
        if hoja.title == "Resumen":
            for celda in hoja["B"][1:]:
                celda.font = fuente_resumen
                celda.alignment = alineacion_centro

    return workbook
