import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime 

# Importar las clases de tu archivo de lógica
from recargos_logic import Empleado, CalculadoraRecargos

class RecargosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Recargos Dominicales y Festivos")
        self.calculadora = CalculadoraRecargos() # Instancia de la lógica
        self.empleados = {}

        self._crear_widgets_iniciales()
        # Línea comentada: NO SE PRECARGAN DATOS DE EJEMPLO AL INICIO
        # self._precargar_datos_ejemplo() 

    def _crear_widgets_iniciales(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        self.frame_jornadas = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_jornadas, text="Registro de Jornadas")
        self._setup_jornadas_tab()

        self.frame_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_reportes, text="Reportes")
        self._setup_reportes_tab()

        self.frame_festivos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_festivos, text="Gestión de Festivos")
        self._setup_festivos_tab()

        self.frame_config = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_config, text="Configuración")
        self._setup_config_tab()

        # Actualiza la lista de empleados al inicio (estará vacía si no hay precarga)
        self._actualizar_lista_empleados()


    def _setup_jornadas_tab(self):
        tk.Label(self.frame_jornadas, text="--- Gestión de Empleados ---", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, pady=5)
        
        tk.Label(self.frame_jornadas, text="Nombre del Empleado:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nombre_empleado = tk.Entry(self.frame_jornadas)
        self.entry_nombre_empleado.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.frame_jornadas, text="Salario Mensual:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_salario_empleado = tk.Entry(self.frame_jornadas)
        self.entry_salario_empleado.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.btn_crear_empleado = tk.Button(self.frame_jornadas, text="Crear Empleado", command=self._crear_empleado)
        self.btn_crear_empleado.grid(row=3, column=0, columnspan=2, pady=10)

        self.empleados_combobox = ttk.Combobox(self.frame_jornadas, state="readonly")
        self.empleados_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.empleados_combobox.bind("<<ComboboxSelected>>", self._on_empleado_selected)
        tk.Label(self.frame_jornadas, text="Seleccionar Empleado:").grid(row=4, column=0, padx=5, pady=5, sticky="w")

        tk.Label(self.frame_jornadas, text="--- Registro de Jornada ---", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=3, pady=10)

        tk.Label(self.frame_jornadas, text="Fecha (YYYY-MM-DD):").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.entry_fecha_jornada = tk.Entry(self.frame_jornadas)
        self.entry_fecha_jornada.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.frame_jornadas, text="Horas Ordinarias D/F:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.entry_horas_ord = tk.Entry(self.frame_jornadas)
        self.entry_horas_ord.insert(0, "0")
        self.entry_horas_ord.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.frame_jornadas, text="Horas Extras Diurnas D/F:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.entry_horas_extra_diurna = tk.Entry(self.frame_jornadas)
        self.entry_horas_extra_diurna.insert(0, "0")
        self.entry_horas_extra_diurna.grid(row=8, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.frame_jornadas, text="Horas Extras Nocturnas D/F:").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        self.entry_horas_extra_nocturna = tk.Entry(self.frame_jornadas)
        self.entry_horas_extra_nocturna.insert(0, "0")
        self.entry_horas_extra_nocturna.grid(row=9, column=1, padx=5, pady=5, sticky="ew")

        self.btn_registrar_jornada = tk.Button(self.frame_jornadas, text="Registrar Jornada", command=self._registrar_jornada)
        self.btn_registrar_jornada.grid(row=10, column=0, columnspan=2, pady=10)
        

    def _setup_reportes_tab(self):
        tk.Label(self.frame_reportes, text="--- Reportes de Recargos ---", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(self.frame_reportes, text="Seleccionar Empleado para Reporte:").pack(pady=5)
        self.reporte_empleado_combobox = ttk.Combobox(self.frame_reportes, state="readonly")
        self.reporte_empleado_combobox.pack(pady=5)
        self.btn_generar_reporte_empleado = tk.Button(self.frame_reportes, text="Generar Reporte por Empleado", command=self._generar_reporte_empleado_gui)
        self.btn_generar_reporte_empleado.pack(pady=5)

        tk.Label(self.frame_reportes, text="--- Reporte Consolidado (Opcional: Por Período) ---").pack(pady=5)
        tk.Label(self.frame_reportes, text="Fecha Inicio (YYYY-MM-DD):").pack(pady=2)
        self.entry_periodo_inicio = tk.Entry(self.frame_reportes)
        self.entry_periodo_inicio.pack(pady=2)
        tk.Label(self.frame_reportes, text="Fecha Fin (YYYY-MM-DD):").pack(pady=2)
        self.entry_periodo_fin = tk.Entry(self.frame_reportes)
        self.entry_periodo_fin.pack(pady=2)
        self.btn_generar_reporte_consolidado = tk.Button(self.frame_reportes, text="Generar Reporte Consolidado", command=self._generar_reporte_consolidado_gui)
        self.btn_generar_reporte_consolidado.pack(pady=10)

        self.report_area = scrolledtext.ScrolledText(self.frame_reportes, width=80, height=20, wrap=tk.WORD)
        self.report_area.pack(pady=10, padx=10, expand=True, fill="both")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _setup_festivos_tab(self):
        tk.Label(self.frame_festivos, text="--- Gestión de Días Festivos ---", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(self.frame_festivos, text="Fecha Festivo (YYYY-MM-DD):").pack(pady=5)
        # CORRECCIÓN DE ERROR: Usar self.frame_festivos como padre
        self.entry_festivo_fecha = tk.Entry(self.frame_festivos) 
        self.entry_festivo_fecha.pack(pady=5)

        self.btn_agregar_festivo = tk.Button(self.frame_festivos, text="Agregar Festivo", command=self._agregar_festivo_gui)
        self.btn_agregar_festivo.pack(pady=5)

        self.btn_eliminar_festivo = tk.Button(self.frame_festivos, text="Eliminar Festivo", command=self._eliminar_festivo_gui)
        self.btn_eliminar_festivo.pack(pady=5)
        
        tk.Label(self.frame_festivos, text="Días Festivos Actuales:").pack(pady=5)
        self.festivos_listbox = tk.Listbox(self.frame_festivos, width=30, height=10)
        self.festivos_listbox.pack(pady=5)
        self._actualizar_lista_festivos()

    def _setup_config_tab(self):
        tk.Label(self.frame_config, text="--- Configuración de Porcentajes ---", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(self.frame_config, text=f"Recargo Dominical/Festivo (Actual: {self.calculadora.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO*100:.0f}%):").pack(pady=2)
        self.entry_dominical_config = tk.Entry(self.frame_config)
        self.entry_dominical_config.insert(0, str(self.calculadora.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO * 100))
        self.entry_dominical_config.pack(pady=2)

        tk.Label(self.frame_config, text=f"Hora Extra Diurna (Actual: {self.calculadora.PORCENTAJE_HORA_EXTRA_DIURNA*100:.0f}%):").pack(pady=2)
        self.entry_extra_diurna_config = tk.Entry(self.frame_config)
        self.entry_extra_diurna_config.insert(0, str(self.calculadora.PORCENTAJE_HORA_EXTRA_DIURNA * 100))
        self.entry_extra_diurna_config.pack(pady=2)

        tk.Label(self.frame_config, text=f"Hora Extra Nocturna (Actual: {self.calculadora.PORCENTAJE_HORA_EXTRA_NOCTURNA*100:.0f}%):").pack(pady=2)
        self.entry_extra_nocturna_config = tk.Entry(self.frame_config)
        self.entry_extra_nocturna_config.insert(0, str(self.calculadora.PORCENTAJE_HORA_EXTRA_NOCTURNA * 100))
        self.entry_extra_nocturna_config.pack(pady=2)

        self.btn_actualizar_porcentajes = tk.Button(self.frame_config, text="Actualizar Porcentajes", command=self._actualizar_porcentajes_gui)
        self.btn_actualizar_porcentajes.pack(pady=10)


    def _crear_empleado(self):
        nombre = self.entry_nombre_empleado.get().strip()
        salario_str = self.entry_salario_empleado.get().strip()

        if not nombre or not salario_str:
            messagebox.showerror("Error", "El nombre y el salario son obligatorios.")
            return

        try:
            salario = float(salario_str)
            if salario <= 0:
                raise ValueError("El salario debe ser un número positivo.")
        except ValueError:
            messagebox.showerror("Error", "Salario inválido. Por favor, ingrese un número.")
            return

        if nombre in self.empleados:
            messagebox.showwarning("Advertencia", f"El empleado '{nombre}' ya existe.")
            return

        nuevo_empleado = Empleado(nombre, salario)
        self.empleados[nombre] = nuevo_empleado
        messagebox.showinfo("Éxito", f"Empleado '{nombre}' creado con éxito.")
        
        self.entry_nombre_empleado.delete(0, tk.END)
        self.entry_salario_empleado.delete(0, tk.END)
        self._actualizar_lista_empleados()

    def _actualizar_lista_empleados(self):
        nombres_empleados = sorted(list(self.empleados.keys()))
        self.empleados_combobox['values'] = nombres_empleados
        if hasattr(self, 'reporte_empleado_combobox'): 
            self.reporte_empleado_combobox['values'] = nombres_empleados
        if nombres_empleados:
            self.empleados_combobox.set(nombres_empleados[0])
            if hasattr(self, 'reporte_empleado_combobox'): 
                self.reporte_empleado_combobox.set(nombres_empleados[0])

    def _on_empleado_selected(self, event=None):
        pass

    def _registrar_jornada(self):
        nombre_empleado = self.empleados_combobox.get()
        fecha_str = self.entry_fecha_jornada.get().strip()
        horas_ord_str = self.entry_horas_ord.get().strip()
        horas_extra_diurna_str = self.entry_horas_extra_diurna.get().strip()
        horas_extra_nocturna_str = self.entry_horas_extra_nocturna.get().strip() 

        if not nombre_empleado:
            messagebox.showerror("Error", "Seleccione un empleado.")
            return
        if not fecha_str:
            messagebox.showerror("Error", "Ingrese una fecha.")
            return

        try:
            fecha = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            horas_ord = int(horas_ord_str)
            horas_extra_diurna = int(horas_extra_diurna_str)
            horas_extra_nocturna = int(horas_extra_nocturna_str)

            if any(h < 0 for h in [horas_ord, horas_extra_diurna, horas_extra_nocturna]):
                raise ValueError("Las horas no pueden ser negativas.")

        except ValueError as e:
            messagebox.showerror("Error", f"Error en los datos de la jornada: {e}\nAsegúrese que la fecha es YYYY-MM-DD y las horas son números enteros.")
            return

        empleado = self.empleados[nombre_empleado]
        mensaje = empleado.registrar_jornada(fecha, horas_ord, horas_extra_diurna, horas_extra_nocturna)
        messagebox.showinfo("Registro Exitoso", mensaje)
        
        self.entry_fecha_jornada.delete(0, tk.END)
        self.entry_horas_ord.delete(0, tk.END)
        self.entry_horas_extra_diurna.delete(0, tk.END)
        self.entry_horas_extra_nocturna.delete(0, tk.END)
        self.entry_horas_ord.insert(0, "0")
        self.entry_horas_extra_diurna.insert(0, "0")
        self.entry_horas_extra_nocturna.insert(0, "0")


    def _generar_reporte_empleado_gui(self):
        nombre_empleado = self.reporte_empleado_combobox.get()
        if not nombre_empleado:
            messagebox.showerror("Error", "Seleccione un empleado para generar el reporte.")
            return

        empleado = self.empleados.get(nombre_empleado)
        if empleado:
            reporte = self.calculadora.generar_reporte_empleado(empleado)
            self.report_area.delete(1.0, tk.END) 
            self.report_area.insert(tk.END, reporte)
        else:
            messagebox.showerror("Error", "Empleado no encontrado.")

    def _generar_reporte_consolidado_gui(self):
        fecha_inicio_str = self.entry_periodo_inicio.get().strip()
        fecha_fin_str = self.entry_periodo_fin.get().strip()
        
        periodo_inicio = None
        periodo_fin = None

        if fecha_inicio_str:
            try:
                periodo_inicio = datetime.datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha de inicio inválido (YYYY-MM-DD).")
                return
        
        if fecha_fin_str:
            try:
                periodo_fin = datetime.datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha de fin inválido (YYYY-MM-DD).")
                return
        
        if periodo_inicio and periodo_fin and periodo_inicio > periodo_fin:
            messagebox.showerror("Error", "La fecha de inicio no puede ser posterior a la fecha de fin.")
            return

        lista_empleados = list(self.empleados.values())
        if not lista_empleados:
            self.report_area.delete(1.0, tk.END)
            self.report_area.insert(tk.END, "No hay empleados registrados para generar un reporte consolidado.")
            return

        reporte = self.calculadora.generar_reporte_consolidado(lista_empleados, periodo_inicio, periodo_fin)
        self.report_area.delete(1.0, tk.END) 
        self.report_area.insert(tk.END, reporte)


    def _on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Reportes":
            self._actualizar_lista_empleados()
        elif selected_tab == "Gestión de Festivos":
            self._actualizar_lista_festivos()
        elif selected_tab == "Configuración":
            self.entry_dominical_config.delete(0, tk.END)
            self.entry_dominical_config.insert(0, str(self.calculadora.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO * 100))
            self.entry_extra_diurna_config.delete(0, tk.END)
            self.entry_extra_diurna_config.insert(0, str(self.calculadora.PORCENTAJE_HORA_EXTRA_DIURNA * 100))
            self.entry_extra_nocturna_config.delete(0, tk.END)
            self.entry_extra_nocturna_config.insert(0, str(self.calculadora.PORCENTAJE_HORA_EXTRA_NOCTURNA * 100))

    def _agregar_festivo_gui(self):
        fecha_str = self.entry_festivo_fecha.get().strip()
        if not fecha_str:
            messagebox.showerror("Error", "Ingrese una fecha para el festivo (YYYY-MM-DD).")
            return
        try:
            fecha_festivo = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            mensaje = self.calculadora.agregar_dia_festivo(fecha_festivo)
            messagebox.showinfo("Gestión de Festivos", mensaje)
            self.entry_festivo_fecha.delete(0, tk.END)
            self._actualizar_lista_festivos()
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")

    def _eliminar_festivo_gui(self):
        fecha_str = self.entry_festivo_fecha.get().strip()
        if not fecha_str:
            messagebox.showerror("Error", "Ingrese una fecha para eliminar (YYYY-MM-DD).")
            return
        try:
            fecha_festivo = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            mensaje = self.calculadora.eliminar_dia_festivo(fecha_festivo)
            messagebox.showinfo("Gestión de Festivos", mensaje)
            self.entry_festivo_fecha.delete(0, tk.END)
            self._actualizar_lista_festivos()
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")

    def _actualizar_lista_festivos(self):
        self.festivos_listbox.delete(0, tk.END)
        for fecha in sorted(self.calculadora.dias_festivos):
            self.festivos_listbox.insert(tk.END, fecha.strftime('%Y-%m-%d'))


    def _actualizar_porcentajes_gui(self):
        nuevo_dom = self.entry_dominical_config.get().strip()
        nuevo_extra_diurna = self.entry_extra_diurna_config.get().strip()
        nuevo_extra_nocturna = self.entry_extra_nocturna_config.get().strip()

        try:
            p_dom = float(nuevo_dom) if nuevo_dom else None
            p_extra_diurna = float(nuevo_extra_diurna) if nuevo_extra_diurna else None
            p_extra_nocturna = float(nuevo_extra_nocturna) if nuevo_extra_nocturna else None

            if (p_dom is not None and (p_dom < 0 or p_dom > 100)) or \
               (p_extra_diurna is not None and (p_extra_diurna < 0 or p_extra_diurna > 100)) or \
               (p_extra_nocturna is not None and (p_extra_nocturna < 0 or p_extra_nocturna > 100)):
                raise ValueError("Los porcentajes deben estar entre 0 y 100.")

            mensaje = self.calculadora.actualizar_porcentajes_recargo(
                nuevo_porcentaje_dominical=p_dom,
                nuevo_porcentaje_extra_diurna=p_extra_diurna,
                nuevo_porcentaje_extra_nocturna=p_extra_nocturna
            )
            messagebox.showinfo("Configuración", mensaje)
            
            self._on_tab_change(None)
        except ValueError as e:
            messagebox.showerror("Error", f"Valores de porcentaje inválidos: {e}\nIngrese números entre 0 y 100.")

    

if __name__ == "__main__":
    root = tk.Tk()
    app = RecargosApp(root)
    root.mainloop()