
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import os
import threading 
import queue
import multiprocessing as mp
from trabajador import ejecutar_limpieza
from instancia_unica import obtener_instancia_unica, liberar_instancia
from limpiador import limpiar_archivo
import webbrowser
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DataCleanPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DataClean Pro | Limpieza Inteligente")
        self.geometry("960x760")

         # Configurar icono de la ventana
        self.iconbitmap(
            str(Path(__file__).resolve().parent / "DataCleanPro.ico")
        )
        
        self.minsize(850, 700)

        self.archivo_seleccionado = None
        self.archivo_generado = None

        self.cola_resultados = mp.Queue()
        self.proceso_limpieza = None
        self.procesando = False

        self.configure(fg_color="#0B1120")
        self.crear_interfaz()
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def crear_tarjeta(self, padre, titulo, columna):
        tarjeta = ctk.CTkFrame(
            padre,
            fg_color="#1E293B",
            corner_radius=12
        )
        tarjeta.grid(
            row=0,
            column=columna,
            padx=6,
            pady=8,
            sticky="nsew"
        )

        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            font=("Segoe UI", 13),
            text_color="#CBD5E1"
        ).pack(pady=(15, 5))

        valor = ctk.CTkLabel(
            tarjeta,
            text="—",
            font=("Segoe UI", 28, "bold"),
            text_color="#38BDF8"
        )
        valor.pack(pady=(0, 15))

        return valor

    def crear_interfaz(self):
        contenedor = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        contenedor.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        ctk.CTkLabel(
            contenedor,
            text="DataClean Pro",
            font=("Segoe UI", 32, "bold"),
            text_color="#38BDF8"
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            contenedor,
            text="Automatización y limpieza profesional de Excel y CSV",
            font=("Segoe UI", 14),
            text_color="#94A3B8"
        ).pack(pady=(0, 25))

        panel_archivo = ctk.CTkFrame(
            contenedor,
            fg_color="#111C30",
            corner_radius=15
        )
        panel_archivo.pack(fill="x", pady=10)

        ctk.CTkLabel(
            panel_archivo,
            text="Archivo de entrada",
            font=("Segoe UI", 17, "bold")
        ).pack(pady=(20, 10))

        self.etiqueta_archivo = ctk.CTkLabel(
            panel_archivo,
            text="Ningún archivo seleccionado",
            text_color="#94A3B8",
            wraplength=700
        )
        self.etiqueta_archivo.pack(pady=5)

        ctk.CTkButton(
            panel_archivo,
            text="Seleccionar Excel o CSV",
            height=42,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=("Segoe UI", 14, "bold"),
            command=self.seleccionar_archivo
        ).pack(padx=25, pady=(10, 20), fill="x")

        self.boton_procesar = ctk.CTkButton(
            contenedor,
            text="Iniciar limpieza de datos",
            height=48,
            fg_color="#0891B2",
            hover_color="#0E7490",
            font=("Segoe UI", 15, "bold"),
            command=self.iniciar_procesamiento
        )
        self.boton_procesar.pack(fill="x", pady=15)

        self.progreso = ctk.CTkProgressBar(
            contenedor,
            progress_color="#38BDF8"
        )
        self.progreso.pack(fill="x", pady=8)
        self.progreso.set(0)

        self.estado = ctk.CTkLabel(
            contenedor,
            text="Esperando archivo...",
            font=("Segoe UI", 13),
            text_color="#FACC15"
        )
        self.estado.pack(pady=10)

        panel_estadisticas = ctk.CTkFrame(
            contenedor,
            fg_color="transparent"
        )
        panel_estadisticas.pack(fill="x", pady=15)

        for columna in range(4):
            panel_estadisticas.grid_columnconfigure(
                columna,
                weight=1,
                uniform="estadisticas"
            )

        self.valor_originales = self.crear_tarjeta(
            panel_estadisticas, "Originales", 0
        )
        self.valor_duplicados = self.crear_tarjeta(
            panel_estadisticas, "Duplicados", 1
        )
        self.valor_finales = self.crear_tarjeta(
            panel_estadisticas, "Finales", 2
        )
        self.valor_errores = self.crear_tarjeta(
            panel_estadisticas, "Celdas vacías", 3
        )

        ctk.CTkLabel(
            contenedor,
            text="Resumen del procesamiento",
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", pady=(10, 5))

        self.cuadro_resultados = ctk.CTkTextbox(
            contenedor,
            height=145,
            fg_color="#1E293B",
            font=("Consolas", 12)
        )
        self.cuadro_resultados.pack(
            fill="x",
            pady=10
        )
        self.mostrar_resultados(
            "Selecciona un archivo para comenzar."
        )

        # Botón para abrir el archivo generado
        self.boton_abrir = ctk.CTkButton(
            contenedor,
            text="Abrir archivo generado",
            height=45,
            fg_color="#16A34A",
            hover_color="#15803D",
            font=("Segoe UI", 14, "bold"),
            state="disabled",
            command=self.abrir_archivo
        )
        self.boton_abrir.pack(fill="x", pady=15)
        
        # Botón de información del programa
        self.boton_acerca = ctk.CTkButton(
            contenedor,
            text="Acerca de DataClean Pro",
            height=35,
            fg_color="#1E293B",
            hover_color="#334155",
            font=("Segoe UI", 12),
            command=self.mostrar_acerca_de
        )
        self.boton_acerca.pack(pady=(5, 10))

        # Información del desarrollador
        ctk.CTkLabel(
            contenedor,
            text=(
                "DataClean Pro v1.0.0\n"
                "Desarrollado por Emmanuel Hernández Morales\n"
                "Python | Automatización y limpieza de datos\n"
                "GitHub: TaterZombie115"
            ),
            font=("Segoe UI", 11),
            text_color="#64748B",
            justify="center"
        ).pack(pady=10)

    
    def mostrar_acerca_de(self):
        # Evitar abrir varias ventanas de información
        if hasattr(self, "ventana_acerca"):
            if self.ventana_acerca.winfo_exists():
                self.ventana_acerca.focus()
                return

        self.ventana_acerca = ctk.CTkToplevel(self)
        self.ventana_acerca.configure(fg_color="#0B1120")
        self.ventana_acerca.title("Acerca de DataClean Pro")
        self.ventana_acerca.geometry("460x540")
        self.ventana_acerca.resizable(False, False)
        self.ventana_acerca.transient(self)

        # Fondo de la ventana
        self.ventana_acerca.configure(fg_color="#0B1120")

        # Logotipo de DataClean Pro
        ruta_logo = Path(__file__).resolve().parent / "DataCleanPro.png"

        imagen_logo = ctk.CTkImage(
            light_image=Image.open(ruta_logo),
            dark_image=Image.open(ruta_logo),
            size=(85, 85)
        )

        ctk.CTkLabel(
            self.ventana_acerca,
            image=imagen_logo,
            text=""
        ).pack(pady=(15, 0))


        # Título
        ctk.CTkLabel(
            self.ventana_acerca,
            text="DataClean Pro",
            font=("Segoe UI", 26, "bold"),
            text_color="#38BDF8"
        ).pack(pady=(25, 5))

        # Versión
        ctk.CTkLabel(
            self.ventana_acerca,
            text="Versión 1.0.0",
            font=("Segoe UI", 13),
            text_color="#94A3B8"
        ).pack(pady=5)

        # Información del desarrollador
        ctk.CTkLabel(
            self.ventana_acerca,
            text=(
                "Desarrollado por\n"
                "Emmanuel Hernández Morales\n\n"
                "Automatización y limpieza de datos\n\n"
                "Tecnologías utilizadas:\n"
                "Python | Pandas | OpenPyXL | CustomTkinter\n\n"
                "© 2026"
            ),
            font=("Segoe UI", 13),
            justify="center",
            text_color="#E2E8F0"
        ).pack(pady=15)

        # Botón de GitHub
        ctk.CTkButton(
            self.ventana_acerca,
            text="Visitar mi GitHub",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=lambda: webbrowser.open(
                "https://github.com/TaterZombie115"
            )
        ).pack(pady=10)

        # Botón para cerrar
        ctk.CTkButton(
            self.ventana_acerca,
            text="Cerrar",
            fg_color="#334155",
            hover_color="#475569",
            command=self.ventana_acerca.destroy
        ).pack(pady=10)

    def mostrar_resultados(self, texto):
        self.cuadro_resultados.configure(state="normal")
        self.cuadro_resultados.delete("1.0", "end")
        self.cuadro_resultados.insert("end", texto)
        self.cuadro_resultados.configure(state="disabled")

    def reiniciar_estadisticas(self):
        for etiqueta in (
            self.valor_originales,
            self.valor_duplicados,
            self.valor_finales,
            self.valor_errores
        ):
            etiqueta.configure(text="—")

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Excel y CSV", "*.xlsx *.csv"),
                ("Excel", "*.xlsx"),
                ("CSV", "*.csv")
            ]
        )

        if archivo:
            self.archivo_seleccionado = archivo
            self.archivo_generado = None

            self.etiqueta_archivo.configure(
                text=Path(archivo).name
            )
            self.estado.configure(
                text="Archivo listo para procesar",
                text_color="#38BDF8"
            )

            self.progreso.set(0)
            self.boton_abrir.configure(state="disabled")
            self.reiniciar_estadisticas()
            self.mostrar_resultados(
                "Archivo seleccionado:\n" + archivo
            )

    def iniciar_procesamiento(self):
        if not self.archivo_seleccionado:
            messagebox.showwarning(
                "Archivo requerido",
                "Selecciona primero un archivo."
            )
            return
        self.boton_procesar.configure(state="disabled")
        self.boton_abrir.configure(state="disabled")
        self.archivo_generado = None

        self.estado.configure(
            text="Procesando archivo...",
            text_color="#FACC15"
        )

        self.progreso.configure(mode="indeterminate")
        self.progreso.start()

        self._esperas_resultados = 0

        self.proceso_limpieza = mp.Process(
            target=ejecutar_limpieza,
            args=(
                self.archivo_seleccionado,
                self.cola_resultados
            ),
            daemon=True
        )

        self.proceso_limpieza.start()

        self.after(100, self.revisar_resultados)

    def procesar_archivo(self):
        try:
            resultado = limpiar_archivo(
                self.archivo_seleccionado
            )

            self.cola_resultados.put(("exito", resultado))

        except Exception as error:
            self.cola_resultados.put(("error", str(error)))

    def revisar_resultados(self):
        try:
            tipo, contenido = self.cola_resultados.get_nowait()

        except queue.Empty:
            proceso = self.proceso_limpieza

            if proceso is not None and not proceso.is_alive():
                # Dar un pequeño margen para recibir el último mensaje
                if not hasattr(self, "_esperas_resultado"):
                    self._esperas_resultado = 0

                self._esperas_resultado += 1

                if self._esperas_resultado >= 20:
                    self.progreso.stop()
                    self.progreso.configure(mode="determinate")
                    self.progreso.set(0)

                    self.estado.configure(
                        text="El procesamiento terminó sin entregar resultados",
                        text_color="#F87171"
                    )

                    self.boton_procesar.configure(state="normal")
                    self.boton_abrir.configure(state="disabled")

                    messagebox.showerror(
                        "Error de procesamiento",
                        f"El proceso terminó sin enviar resultados."
                        f"Código de salida: {proceso.exitcode}"
                    )
                    return
            self.after(100, self.revisar_resultados)
            return

        self.progreso.stop()
        self.progreso.configure(mode="determinate")

        if tipo == "exito":
            resultado = contenido

            self.archivo_generado = resultado["archivo_limpio"]

            self.valor_originales.configure(
                text=str(resultado["filas_originales"])
            )
            self.valor_duplicados.configure(
                text=str(resultado["duplicados_eliminados"])
            )
            self.valor_finales.configure(
                text=str(resultado["filas_finales"])
            )
            self.valor_errores.configure(
                text=str(resultado["errores_detectados"])
            )

            self.mostrar_resultados(
                "LIMPIEZA COMPLETADA\n"
                "--------------------------------\n"
                f"Originales: {resultado['filas_originales']}\n"
                f"Duplicados: {resultado['duplicados_eliminados']}\n"
                f"Finales: {resultado['filas_finales']}\n"
                f"Celdas vacías: {resultado['errores_detectados']}\n\n"
                f"Archivo:\n{self.archivo_generado}"
            )

            self.progreso.set(1)

            self.estado.configure(
                text="Proceso completado correctamente",
                text_color="#4ADE80"
            )

            self.boton_abrir.configure(state="normal")

        else:
            self.progreso.set(0)

            self.estado.configure(
                text="Error durante el procesamiento",
                text_color="#F87171"
            )

            messagebox.showerror(
                "Error",
                contenido
            )

        self.boton_procesar.configure(state="normal")

    def cerrar_aplicacion(self):
        proceso = self.proceso_limpieza

        if proceso is not None and proceso.is_alive():
            messagebox.showwarning(
                "Procesamiento en curso",
                "Espera a que termine la limpieza antes de cerrar DataClean Pro."
            )
            return
        self.destroy()

    def abrir_archivo(self):
        if self.archivo_generado:
            ruta = Path(self.archivo_generado)

            if ruta.is_file():
                try:
                    os.startfile(str(ruta))
                except OSError as error:
                    messagebox.showerror(
                        "Error al abrir",
                        str(error)
                    )
            else:
                messagebox.showerror(
                    "Archivo no encontrado",
                    "No se encontró el archivo generado."
                )


if __name__ == "__main__":
    mp.freeze_support()

    instancia = obtener_instancia_unica()

    if instancia is None:
        messagebox.showwarning(
            "DataClean Pro",
            "DataClean Pro ya está abierto.\n"
            "No se permite iniciar otra instancia."
        )
    else:
        try:
            app = DataCleanPro()
            app.mainloop()
        finally:
            liberar_instancia(instancia)
