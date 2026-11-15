
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import os
import sys
import subprocess

from limpiador import limpiar_archivo


class DataCleanApp:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("DataClean Pro | Limpieza de Datos")
        self.ventana.geometry("850x700")
        self.ventana.minsize(750, 650)
        self.ventana.configure(bg="#101827")

        self.archivo_seleccionado = None
        self.archivo_generado = None

        self.crear_interfaz()

    def crear_interfaz(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Accion.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=12
        )

        contenedor = tk.Frame(
            self.ventana,
            bg="#101827",
            padx=35,
            pady=25
        )
        contenedor.pack(fill="both", expand=True)

        tk.Label(
            contenedor,
            text="DataClean Pro",
            font=("Segoe UI", 26, "bold"),
            fg="#38BDF8",
            bg="#101827"
        ).pack(pady=(5, 5))

        tk.Label(
            contenedor,
            text="Automatización y limpieza de archivos Excel y CSV",
            font=("Segoe UI", 11),
            fg="#CBD5E1",
            bg="#101827"
        ).pack(pady=(0, 30))

        ttk.Button(
            contenedor,
            text="Seleccionar archivo Excel o CSV",
            style="Accion.TButton",
            command=self.seleccionar_archivo
        ).pack(fill="x", pady=8)

        self.etiqueta_archivo = tk.Label(
            contenedor,
            text="Ningún archivo seleccionado",
            font=("Segoe UI", 10),
            fg="#94A3B8",
            bg="#101827",
            wraplength=600
        )
        self.etiqueta_archivo.pack(pady=10)

        self.boton_limpiar = ttk.Button(
            contenedor,
            text="Iniciar limpieza de datos",
            style="Accion.TButton",
            command=self.ejecutar_limpieza
        )
        self.boton_limpiar.pack(fill="x", pady=15)

        self.estado = tk.Label(
            contenedor,
            text="Esperando archivo...",
            font=("Segoe UI", 11),
            fg="#FACC15",
            bg="#101827"
        )
        self.estado.pack(pady=10)

        self.resultados = tk.Text(
            contenedor,
            height=10,
            font=("Consolas", 11),
            bg="#1E293B",
            fg="#E2E8F0",
            relief="flat",
            padx=15,
            pady=15,
            state="disabled"
        )
        self.resultados.pack(fill="both", expand=True, pady=10)

        self.boton_abrir = ttk.Button(
            contenedor,
            text="Abrir archivo generado",
            style="Accion.TButton",
            command=self.abrir_resultado,
            state="disabled"
        )
        self.boton_abrir.pack(fill="x", pady=10)

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Archivos Excel y CSV", "*.xlsx *.csv"),
                ("Excel", "*.xlsx"),
                ("CSV", "*.csv")
            ]
        )

        if archivo:
            self.archivo_seleccionado = archivo
            self.archivo_generado = None
            self.boton_abrir.config(state="disabled")
            self.etiqueta_archivo.config(
                text=Path(archivo).name
            )
            self.estado.config(
                text="Archivo listo para procesar",
                fg="#38BDF8"
            )
            self.mostrar_resultados("")

    def ejecutar_limpieza(self):
        if not self.archivo_seleccionado:
            messagebox.showwarning(
                "Archivo requerido",
                "Selecciona primero un archivo Excel o CSV."
            )
            return

        self.boton_limpiar.config(state="disabled")
        self.boton_abrir.config(state="disabled")
        self.estado.config(
            text="Procesando archivo...",
            fg="#FACC15"
        )
        self.ventana.update_idletasks()

        try:
            resultado = limpiar_archivo(
                self.archivo_seleccionado
            )

            self.archivo_generado = resultado["archivo_limpio"]

            texto = (
                "LIMPIEZA COMPLETADA\n"
                "------------------------------\n"
                f"Registros originales: {resultado['filas_originales']}\n"
                f"Duplicados eliminados: {resultado['duplicados_eliminados']}\n"
                f"Registros finales: {resultado['filas_finales']}\n"
                f"Celdas vacías detectadas: {resultado['errores_detectados']}\n"
                "\nArchivo generado correctamente."
            )

            self.mostrar_resultados(texto)
            self.estado.config(
                text="Proceso completado",
                fg="#4ADE80"
            )
            self.boton_abrir.config(state="normal")

        except Exception as error:
            self.estado.config(
                text="Error durante el procesamiento",
                fg="#F87171"
            )
            messagebox.showerror(
                "Error",
                str(error)
            )

        finally:
            self.boton_limpiar.config(state="normal")

    def mostrar_resultados(self, texto):
        self.resultados.config(state="normal")
        self.resultados.delete("1.0", tk.END)
        self.resultados.insert(tk.END, texto)
        self.resultados.config(state="disabled")

    def abrir_resultado(self):
        if not self.archivo_generado:
            return

        ruta = Path(self.archivo_generado)

        if not ruta.is_file():
            messagebox.showerror(
                "Archivo no encontrado",
                "No se encontró el archivo generado."
            )
            return

        try:
            if sys.platform == "win32":
                os.startfile(str(ruta))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(ruta)])
            else:
                subprocess.Popen(["xdg-open", str(ruta)])

        except Exception as error:
            messagebox.showerror(
                "No se pudo abrir el archivo",
                str(error)
            )


if __name__ == "__main__":
    ventana = tk.Tk()
    aplicacion = DataCleanApp(ventana)
    ventana.mainloop()
