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
        self.empleados = {} # Diccionario para almacenar empleados
        self.time_options = self._generate_time_options() # Genera la lista de opciones de hora

        # Variable para almacenar el nombre del empleado seleccionado para edición
        self._selected_employee_name_for_edit = None 

        self._crear_widgets_iniciales()
        # Puedes descomentar la siguiente línea si quieres precargar datos de ejemplo para pruebas
        # self._precargar_datos_ejemplo() 

    def _generate_time_options(self):
        """Genera una lista de todas las horas del día en formato HH:MM AM/PM."""
        options = []
        for hour in range(24):
            for minute in [0, 30]: # Opciones cada 30 minutos, puedes ajustar a 0, 15, 30, 45 si quieres más granularidad
                time_obj = datetime.time(hour, minute)
                options.append(time_obj.strftime('%I:%M %p')) # Formato 01:00 AM, 02:30 PM, etc.
        return options

    def _crear_widgets_iniciales(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # Pestaña 1: Registro de Jornadas
        self.frame_jornadas = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_jornadas, text="Registro de Jornadas")
        self._setup_jornadas_tab()

        # Pestaña 2: Gestión de Empleados (Nueva)
        self.frame_gestion_empleados = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_gestion_empleados, text="Gestión de Empleados")
        self._setup_gestion_empleados_tab()

        # Pestaña 3: Reportes
        self.frame_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_reportes, text="Reportes")
        self._setup_reportes_tab()

        # Pestaña 4: Gestión de Festivos
        self.frame_festivos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_festivos, text="Gestión de Festivos")
        self._setup_festivos_tab()

        # Pestaña 5: Configuración
        self.frame_config = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_config, text="Configuración")
        self._setup_config_tab()

        # Asegurarse de que todos los combobox y listas existan antes de intentar actualizarlos
        self._actualizar_lista_empleados()
        self._actualizar_lista_gestion_empleados() # Actualizar la nueva lista al inicio


    def _setup_jornadas_tab(self):
        tk.Label(self.frame_jornadas, text="--- Gestión de Empleados ---", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, pady=5)
        
        tk.Label(self.frame_jornadas, text="Nombre del Empleado:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nombre_empleado = tk.Entry(self.frame_jornadas)
        self.entry_nombre_empleado.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.frame_jornadas, text="Salario Mensual:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_salario_empleado = tk.Entry(self.frame_jornadas)
        self.entry_salario_empleado.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.frame_jornadas, text="Horas Diarias Estándar:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_standard_daily_hours = tk.Entry(self.frame_jornadas)
        self.entry_standard_daily_hours.insert(0, "8") # Valor por defecto: 8 horas
        self.entry_standard_daily_hours.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.btn_crear_empleado = tk.Button(self.frame_jornadas, text="Crear Empleado", command=self._crear_empleado)
        self.btn_crear_empleado.grid(row=4, column=0, columnspan=2, pady=10)

        self.empleados_combobox = ttk.Combobox(self.frame_jornadas, state="readonly")
        self.empleados_combobox.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.empleados_combobox.bind("<<ComboboxSelected>>", self._on_empleado_selected)
        tk.Label(self.frame_jornadas, text="Seleccionar Empleado:").grid(row=5, column=0, padx=5, pady=5, sticky="w")

        tk.Label(self.frame_jornadas, text="--- Registro de Jornada (Horas Reales) ---", font=("Arial", 10, "bold")).grid(row=6, column=0, columnspan=3, pady=10)

        tk.Label(self.frame_jornadas, text="Fecha (YYYY-MM-DD):").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.entry_fecha_jornada = tk.Entry(self.frame_jornadas)
        self.entry_fecha_jornada.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.frame_jornadas, text="Hora Entrada:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.combo_hora_entrada = ttk.Combobox(self.frame_jornadas, values=self.time_options, state="readonly")
        self.combo_hora_entrada.grid(row=8, column=1, padx=5, pady=5, sticky="ew")
        self.combo_hora_entrada.set("08:00 AM") # Valor por defecto

        tk.Label(self.frame_jornadas, text="Hora Salida:").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        self.combo_hora_salida = ttk.Combobox(self.frame_jornadas, values=self.time_options, state="readonly")
        self.combo_hora_salida.grid(row=9, column=1, padx=5, pady=5, sticky="ew")
        self.combo_hora_salida.set("05:00 PM") # Valor por defecto

        self.btn_registrar_jornada = tk.Button(self.frame_jornadas, text="Registrar Jornada", command=self._registrar_jornada)
        self.btn_registrar_jornada.grid(row=10, column=0, columnspan=2, pady=10)
        
    def _setup_gestion_empleados_tab(self):
        tk.Label(self.frame_gestion_empleados, text="--- Gestión de Registros de Empleados ---", font=("Arial", 10, "bold")).pack(pady=10)

        # Lista de empleados
        tk.Label(self.frame_gestion_empleados, text="Seleccionar Empleado:").pack(pady=5)
        self.empleados_listbox = tk.Listbox(self.frame_gestion_empleados, width=50, height=10)
        self.empleados_listbox.pack(pady=5, padx=10, fill="both", expand=True)
        self.empleados_listbox.bind("<<ListboxSelect>>", self._seleccionar_empleado_para_edicion)

        # Controles de edición
        edit_frame = ttk.LabelFrame(self.frame_gestion_empleados, text="Editar/Eliminar Empleado")
        edit_frame.pack(pady=10, padx=10, fill="x", expand=False)

        tk.Label(edit_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.edit_nombre_empleado = tk.Entry(edit_frame)
        self.edit_nombre_empleado.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(edit_frame, text="Salario Mensual:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.edit_salario_empleado = tk.Entry(edit_frame)
        self.edit_salario_empleado.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(edit_frame, text="Horas Diarias Estándar:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.edit_standard_daily_hours = tk.Entry(edit_frame)
        self.edit_standard_daily_hours.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # Botones de acción
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.btn_guardar_cambios = tk.Button(button_frame, text="Guardar Cambios", command=self._guardar_cambios_empleado)
        self.btn_guardar_cambios.pack(side="left", padx=5)

        self.btn_eliminar_empleado = tk.Button(button_frame, text="Eliminar Empleado", command=self._eliminar_empleado_gui)
        self.btn_eliminar_empleado.pack(side="left", padx=5)

        edit_frame.columnconfigure(1, weight=1) # Permite que el campo de entrada se expanda

        self._actualizar_lista_gestion_empleados() # Cargar la lista al inicio de la pestaña

    def _actualizar_lista_gestion_empleados(self):
        """Actualiza la Listbox de la pestaña de gestión de empleados."""
        self.empleados_listbox.delete(0, tk.END)
        for nombre in sorted(self.empleados.keys()):
            empleado = self.empleados[nombre]
            self.empleados_listbox.insert(tk.END, f"{empleado.nombre} (Salario: ${empleado.salario_mensual:,.0f}, Horas Est.: {empleado.standard_daily_hours}h)")

    def _seleccionar_empleado_para_edicion(self, event=None):
        """Carga los datos del empleado seleccionado en los campos de edición."""
        selected_indices = self.empleados_listbox.curselection()
        if not selected_indices:
            self._limpiar_campos_edicion_empleado()
            self._selected_employee_name_for_edit = None
            return

        selected_name_display = self.empleados_listbox.get(selected_indices[0])
        # Extraer el nombre real del empleado (antes del paréntesis)
        original_name = selected_name_display.split('(')[0].strip()
        
        empleado = self.empleados.get(original_name)
        if empleado:
            self._selected_employee_name_for_edit = original_name # Guardar el nombre original para la edición
            self.edit_nombre_empleado.delete(0, tk.END)
            self.edit_nombre_empleado.insert(0, empleado.nombre)
            self.edit_salario_empleado.delete(0, tk.END)
            self.edit_salario_empleado.insert(0, str(empleado.salario_mensual))
            self.edit_standard_daily_hours.delete(0, tk.END)
            self.edit_standard_daily_hours.insert(0, str(empleado.standard_daily_hours))
        else:
            self._limpiar_campos_edicion_empleado()
            self._selected_employee_name_for_edit = None

    def _limpiar_campos_edicion_empleado(self):
        """Limpia los campos de entrada de la sección de edición de empleado."""
        self.edit_nombre_empleado.delete(0, tk.END)
        self.edit_salario_empleado.delete(0, tk.END)
        self.edit_standard_daily_hours.delete(0, tk.END)

    def _guardar_cambios_empleado(self):
        """Guarda los cambios de un empleado editado."""
        if not self._selected_employee_name_for_edit:
            messagebox.showwarning("Advertencia", "Seleccione un empleado para guardar cambios.")
            return

        original_name = self._selected_employee_name_for_edit
        new_name = self.edit_nombre_empleado.get().strip()
        new_salario_str = self.edit_salario_empleado.get().strip()
        new_standard_hours_str = self.edit_standard_daily_hours.get().strip()

        if not new_name or not new_salario_str or not new_standard_hours_str:
            messagebox.showerror("Error", "Todos los campos del empleado deben estar llenos.")
            return

        try:
            new_salario = float(new_salario_str)
            if new_salario <= 0:
                raise ValueError("El salario debe ser un número positivo.")
            new_standard_hours = int(new_standard_hours_str)
            if new_standard_hours <= 0:
                raise ValueError("Las horas diarias estándar deben ser un número entero positivo.")
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}\nPor favor, ingrese números válidos.")
            return

        if new_name != original_name and new_name in self.empleados:
            messagebox.showerror("Error", f"El nombre '{new_name}' ya existe para otro empleado.")
            return

        # Actualizar o recrear el empleado
        if new_name == original_name:
            # Actualizar el empleado existente
            empleado = self.empleados[original_name]
            empleado.salario_mensual = new_salario
            empleado.standard_daily_hours = new_standard_hours
            messagebox.showinfo("Éxito", f"Empleado '{new_name}' actualizado con éxito.")
        else:
            # Crear un nuevo empleado con el nuevo nombre y transferir las jornadas
            old_empleado = self.empleados.pop(original_name) # Eliminar el viejo
            new_empleado = Empleado(new_name, new_salario, new_standard_hours, old_empleado.tipo_contrato)
            new_empleado.jornadas_registradas = old_empleado.jornadas_registradas # Transferir jornadas
            self.empleados[new_name] = new_empleado # Añadir el nuevo
            messagebox.showinfo("Éxito", f"Empleado '{original_name}' renombrado a '{new_name}' y actualizado con éxito.")
        
        self._limpiar_campos_edicion_empleado()
        self._selected_employee_name_for_edit = None
        self._actualizar_todas_las_listas_empleados() # Actualizar todos los combobox y listbox

    def _eliminar_empleado_gui(self):
        """Elimina un empleado seleccionado."""
        selected_indices = self.empleados_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Advertencia", "Seleccione un empleado para eliminar.")
            return

        selected_name_display = self.empleados_listbox.get(selected_indices[0])
        original_name = selected_name_display.split('(')[0].strip()

        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar al empleado '{original_name}' y todas sus jornadas?"):
            if original_name in self.empleados:
                del self.empleados[original_name]
                messagebox.showinfo("Éxito", f"Empleado '{original_name}' eliminado con éxito.")
                self._limpiar_campos_edicion_empleado()
                self._selected_employee_name_for_edit = None
                self._actualizar_todas_las_listas_empleados() # Actualizar todos los combobox y listbox
            else:
                messagebox.showerror("Error", "Empleado no encontrado.")


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
        self.entry_festivo_fecha = tk.Entry(self.frame_festivos) 
        self.entry_festivo_fecha.pack(pady=5)

        self.btn_agregar_festivo = tk.Button(self.frame_festivos, text="Agregar Festivo", command=self._agregar_festivo_gui)
        self.btn_agregar_festivo.pack(pady=5)

        self.btn_eliminar_festivo = tk.Button(self.frame_festivos, text="Eliminar Festivo", command=self._eliminar_festivo_gui)
        self.btn_eliminar_festivo.pack(pady=5) # Corregido el nombre del atributo
        
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

        tk.Label(self.frame_config, text=f"Hora Ordinaria Nocturna (Actual: {self.calculadora.PORCENTAJE_HORA_ORDINARIA_NOCTURNA*100:.0f}%):").pack(pady=2)
        self.entry_ordinaria_nocturna_config = tk.Entry(self.frame_config)
        self.entry_ordinaria_nocturna_config.insert(0, str(self.calculadora.PORCENTAJE_HORA_ORDINARIA_NOCTURNA * 100))
        self.entry_ordinaria_nocturna_config.pack(pady=2)

        self.btn_actualizar_porcentajes = tk.Button(self.frame_config, text="Actualizar Porcentajes", command=self._actualizar_porcentajes_gui)
        self.btn_actualizar_porcentajes.pack(pady=10)


    def _crear_empleado(self):
        nombre = self.entry_nombre_empleado.get().strip()
        salario_str = self.entry_salario_empleado.get().strip()
        standard_daily_hours_str = self.entry_standard_daily_hours.get().strip()

        if not nombre or not salario_str or not standard_daily_hours_str:
            messagebox.showerror("Error", "Todos los campos del empleado son obligatorios.")
            return

        try:
            salario = float(salario_str)
            if salario <= 0:
                raise ValueError("El salario debe ser un número positivo.")
            standard_daily_hours = int(standard_daily_hours_str)
            if standard_daily_hours <= 0:
                raise ValueError("Las horas diarias estándar deben ser un número entero positivo.")
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}\nPor favor, ingrese números válidos.")
            return

        if nombre in self.empleados:
            messagebox.showwarning("Advertencia", f"El empleado '{nombre}' ya existe.")
            return

        nuevo_empleado = Empleado(nombre, salario, standard_daily_hours)
        self.empleados[nombre] = nuevo_empleado
        messagebox.showinfo("Éxito", f"Empleado '{nombre}' creado con éxito (Horas diarias estándar: {standard_daily_hours}h).")
        
        self.entry_nombre_empleado.delete(0, tk.END)
        self.entry_salario_empleado.delete(0, tk.END)
        self.entry_standard_daily_hours.delete(0, tk.END)
        self.entry_standard_daily_hours.insert(0, "8") # Restablecer valor por defecto
        self._actualizar_todas_las_listas_empleados() # Actualizar todas las listas y comboboxes


    def _actualizar_lista_empleados(self):
        """Actualiza los Combobox de selección de empleado en las pestañas de registro y reportes."""
        nombres_empleados = sorted(list(self.empleados.keys()))
        self.empleados_combobox['values'] = nombres_empleados
        if nombres_empleados:
            # Intentar mantener la selección si es posible, o seleccionar el primero
            current_selection = self.empleados_combobox.get()
            if current_selection not in nombres_empleados:
                self.empleados_combobox.set(nombres_empleados[0])
            
            if hasattr(self, 'reporte_empleado_combobox'): 
                self.reporte_empleado_combobox['values'] = nombres_empleados
                current_report_selection = self.reporte_empleado_combobox.get()
                if current_report_selection not in nombres_empleados:
                    self.reporte_empleado_combobox.set(nombres_empleados[0])
        else:
            self.empleados_combobox.set("") # Limpiar si no hay empleados
            if hasattr(self, 'reporte_empleado_combobox'):
                self.reporte_empleado_combobox.set("")

    def _actualizar_todas_las_listas_empleados(self):
        """Llama a todos los métodos de actualización de listas y comboboxes de empleados."""
        self._actualizar_lista_empleados() # Para los combobox de registro y reportes
        self._actualizar_lista_gestion_empleados() # Para la listbox de gestión


    def _on_empleado_selected(self, event=None):
        pass

    def _registrar_jornada(self):
        nombre_empleado = self.empleados_combobox.get()
        fecha_str = self.entry_fecha_jornada.get().strip()
        hora_entrada_str = self.combo_hora_entrada.get().strip() 
        hora_salida_str = self.combo_hora_salida.get().strip()   

        if not nombre_empleado:
            messagebox.showerror("Error", "Seleccione un empleado.")
            return
        if not fecha_str or not hora_entrada_str or not hora_salida_str:
            messagebox.showerror("Error", "Todos los campos de la jornada son obligatorios.")
            return

        try:
            fecha = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora_entrada = datetime.datetime.strptime(hora_entrada_str, '%I:%M %p').time()
            hora_salida = datetime.datetime.strptime(hora_salida_str, '%I:%M %p').time()

        except ValueError as e:
            messagebox.showerror("Error", f"Error en el formato de fecha/hora: {e}\nAsegúrese que la fecha es YYYY-MM-DD y las horas son HH:MM AM/PM.")
            return

        empleado = self.empleados[nombre_empleado]
        mensaje = empleado.registrar_jornada(fecha, hora_entrada, hora_salida)
        messagebox.showinfo("Registro Exitoso", mensaje)
        
        self.entry_fecha_jornada.delete(0, tk.END)


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
        if selected_tab == "Registro de Jornadas" or selected_tab == "Reportes":
            self._actualizar_lista_empleados()
        elif selected_tab == "Gestión de Empleados": # Nueva condición para la pestaña de gestión
            self._actualizar_lista_gestion_empleados()
            self._limpiar_campos_edicion_empleado() # Limpiar campos al entrar a la pestaña
        elif selected_tab == "Gestión de Festivos":
            self._actualizar_lista_festivos()
        elif selected_tab == "Configuración":
            self.entry_dominical_config.delete(0, tk.END)
            self.entry_dominical_config.insert(0, str(self.calculadora.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO * 100))
            self.entry_extra_diurna_config.delete(0, tk.END)
            self.entry_extra_diurna_config.insert(0, str(self.calculadora.PORCENTAJE_HORA_EXTRA_DIURNA * 100))
            self.entry_extra_nocturna_config.delete(0, tk.END)
            self.entry_extra_nocturna_config.insert(0, str(self.calculadora.PORCENTAJE_HORA_EXTRA_NOCTURNA * 100))
            self.entry_ordinaria_nocturna_config.delete(0, tk.END) 
            self.entry_ordinaria_nocturna_config.insert(0, str(self.calculadora.PORCENTAJE_HORA_ORDINARIA_NOCTURNA * 100))


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
        nuevo_ordinaria_nocturna = self.entry_ordinaria_nocturna_config.get().strip() 

        try:
            p_dom = float(nuevo_dom) if nuevo_dom else None
            p_extra_diurna = float(nuevo_extra_diurna) if nuevo_extra_diurna else None
            p_extra_nocturna = float(nuevo_extra_nocturna) if nuevo_extra_nocturna else None
            p_ordinaria_nocturna = float(nuevo_ordinaria_nocturna) if nuevo_ordinaria_nocturna else None 

            if (p_dom is not None and (p_dom < 0 or p_dom > 100)) or \
               (p_extra_diurna is not None and (p_extra_diurna < 0 or p_extra_diurna > 100)) or \
               (p_extra_nocturna is not None and (p_extra_nocturna < 0 or p_extra_nocturna > 100)) or \
               (p_ordinaria_nocturna is not None and (p_ordinaria_nocturna < 0 or p_ordinaria_nocturna > 100)): 
                raise ValueError("Los porcentajes deben estar entre 0 y 100.")

            mensaje = self.calculadora.actualizar_porcentajes_recargo(
                nuevo_porcentaje_dominical=p_dom,
                nuevo_porcentaje_extra_diurna=p_extra_diurna,
                nuevo_porcentaje_extra_nocturna=p_extra_nocturna,
                nuevo_porcentaje_ordinaria_nocturna=p_ordinaria_nocturna 
            )
            messagebox.showinfo("Configuración", mensaje)
            
            self._on_tab_change(None)
        except ValueError as e:
            messagebox.showerror("Error", f"Valores de porcentaje inválidos: {e}\nIngrese números entre 0 y 100.")

    def _precargar_datos_ejemplo(self):
        """
        Este método está comentado por defecto. Descoméntalo y úsalo si necesitas
        precargar datos de ejemplo al iniciar la aplicación para pruebas.
        """
        empleado1 = Empleado("Ana Pérez", 1_300_000, 8, "indefinido") # 8 horas estándar
        empleado2 = Empleado("Juan García", 2_500_000, 8, "término fijo") # 8 horas estándar
        empleado3 = Empleado("Pedro López", 1_000_000, 6, "obra o labor") # 6 horas estándar

        self.empleados["Ana Pérez"] = empleado1
        self.empleados["Juan García"] = empleado2
        self.empleados["Pedro López"] = empleado3

        # Jornadas de ejemplo para probar la categorización:
        # Domingo (2025-07-13) - 8 horas: Deberían ser 8h ordinarias D/F
        empleado1.registrar_jornada(datetime.date(2025, 7, 13), datetime.time(8, 0), datetime.time(16, 0)) 
        # Festivo (2025-07-20) - 10 horas: 8h ordinarias D/F, 2h extras diurnas D/F
        empleado2.registrar_jornada(datetime.date(2025, 7, 20), datetime.time(7, 0), datetime.time(17, 0))
        # Día regular (2025-07-14, lunes) - 10 horas: 8h ordinarias, 2h extras diurnas
        empleado3.registrar_jornada(datetime.date(2025, 7, 14), datetime.time(9, 0), datetime.time(19, 0))
        # Día regular (2025-07-15, martes) - 12 horas (incluye nocturnas): 8h ord, 2h ext diurnas, 2h ext nocturnas
        empleado1.registrar_jornada(datetime.date(2025, 7, 15), datetime.time(18, 0), datetime.time(6, 0)) # Turno de noche
        # Día regular (2025-07-16, miércoles) - 8 horas nocturnas: 8h ordinarias nocturnas
        empleado2.registrar_jornada(datetime.date(2025, 7, 16), datetime.time(22, 0), datetime.time(6, 0)) 


        self._actualizar_todas_las_listas_empleados() # Actualizar todas las listas y comboboxes

if __name__ == "__main__":
    root = tk.Tk()
    app = RecargosApp(root)
    root.mainloop()