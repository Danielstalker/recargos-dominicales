import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime 
from tkcalendar import Calendar # Importar el widget de calendario (Asegúrate de instalarlo: pip install tkcalendar)

# Importar las clases y las funciones de guardado/carga de tu archivo de lógica
from recargos_logic import Empleado, CalculadoraRecargos, save_app_data, load_app_data

class RecargosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Recargos Dominicales y Festivos")
        
        # Cargar datos al inicio de la aplicación
        self.empleados, self.calculadora = load_app_data() 

        self.time_options = self._generate_time_options() 

        # Variable para almacenar el nombre del empleado seleccionado para edición/visualización de jornadas
        self._selected_employee_name_for_edit = None 
        # Variable para almacenar el índice de la jornada seleccionada para edición
        self._selected_jornada_index_for_edit = None

        # Variable para el checkbox de día compensatorio
        self.es_dia_compensatorio = tk.BooleanVar(value=False)
        self.es_dia_compensatorio.trace_add("write", self._on_dia_compensatorio_toggle)


        self._crear_widgets_iniciales()
        
        # Configurar el protocolo de cierre de ventana para guardar datos
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

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

        # Pestaña 6: Acumulados de Horas (Nueva)
        self.frame_acumulados = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_acumulados, text="Acumulados de Horas")
        self._setup_acumulados_tab()

        # NUEVA PESTAÑA: Recargos Detallados
        self.frame_recargos_detallados = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_recargos_detallados, text="Recargos Detallados")
        self._setup_recargos_detallados_tab()


        # Asegurarse de que todos los combobox y listas existan antes de intentar actualizarlos
        self._actualizar_lista_empleados()
        self._actualizar_lista_gestion_empleados() # Actualizar la nueva lista al inicio
        
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)


    def _setup_jornadas_tab(self):
        tk.Label(self.frame_jornadas, text="--- Creación de Empleados ---", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, pady=5)
        
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

        # CAMBIO: Campo de fecha con botón de calendario
        tk.Label(self.frame_jornadas, text="Fecha (YYYY-MM-DD):").grid(row=7, column=0, padx=5, pady=5, sticky="w") 
        self.entry_fecha_jornada = tk.Entry(self.frame_jornadas, state="readonly") # Hacerlo de solo lectura
        self.entry_fecha_jornada.grid(row=7, column=1, padx=5, pady=5, sticky="ew") 
        # CORRECCIÓN: Usar lambda para pasar el argumento target_entry
        self.btn_seleccionar_fecha = tk.Button(self.frame_jornadas, text="Seleccionar", command=lambda: self._open_calendar_dialog(self.entry_fecha_jornada))
        self.btn_seleccionar_fecha.grid(row=7, column=2, padx=5, pady=5) # Botón para abrir el calendario

        # Nuevo Checkbutton para Día Compensatorio
        self.check_dia_compensatorio = tk.Checkbutton(self.frame_jornadas, text="Día Compensatorio (8h Ordinarias)", variable=self.es_dia_compensatorio)
        self.check_dia_compensatorio.grid(row=11, column=0, columnspan=3, pady=5, sticky="w") # Ajustar fila

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

        # Sección de selección y edición de empleado
        empleado_selection_frame = ttk.LabelFrame(self.frame_gestion_empleados, text="Seleccionar y Editar Empleado")
        empleado_selection_frame.pack(pady=5, padx=10, fill="x", expand=False)

        tk.Label(empleado_selection_frame, text="Lista de Empleados:").pack(pady=2)
        self.empleados_listbox = tk.Listbox(empleado_selection_frame, width=60, height=8)
        self.empleados_listbox.pack(pady=2, padx=5, fill="both", expand=True)
        self.empleados_listbox.bind("<<ListboxSelect>>", self._seleccionar_empleado_para_edicion)

        edit_empleado_frame = ttk.Frame(empleado_selection_frame)
        edit_empleado_frame.pack(pady=5, padx=5, fill="x", expand=True)

        tk.Label(edit_empleado_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.edit_nombre_empleado = tk.Entry(edit_empleado_frame)
        self.edit_nombre_empleado.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(edit_empleado_frame, text="Salario Mensual:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.edit_salario_empleado = tk.Entry(edit_empleado_frame)
        self.edit_salario_empleado.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(edit_empleado_frame, text="Horas Diarias Estándar:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.edit_standard_daily_hours = tk.Entry(edit_empleado_frame)
        self.edit_standard_daily_hours.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        button_frame_empleado = ttk.Frame(empleado_selection_frame)
        button_frame_empleado.pack(pady=5)

        self.btn_guardar_cambios = tk.Button(button_frame_empleado, text="Guardar Cambios Empleado", command=self._guardar_cambios_empleado)
        self.btn_guardar_cambios.pack(side="left", padx=5)

        self.btn_eliminar_empleado = tk.Button(button_frame_empleado, text="Eliminar Empleado", command=self._eliminar_empleado_gui)
        self.btn_eliminar_empleado.pack(side="left", padx=5)

        edit_empleado_frame.columnconfigure(1, weight=1)

        # Sección de registro de jornadas del empleado seleccionado
        jornadas_empleado_frame = ttk.LabelFrame(self.frame_gestion_empleados, text="Jornadas del Empleado Seleccionado")
        jornadas_empleado_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Treeview para mostrar las jornadas
        self.jornadas_treeview = ttk.Treeview(jornadas_empleado_frame, columns=("Fecha", "Entrada", "Salida"), show="headings")
        self.jornadas_treeview.heading("Fecha", text="Fecha")
        self.jornadas_treeview.heading("Entrada", text="Hora Entrada")
        self.jornadas_treeview.heading("Salida", text="Hora Salida")
        self.jornadas_treeview.column("Fecha", width=100, anchor="center")
        self.jornadas_treeview.column("Entrada", width=100, anchor="center")
        self.jornadas_treeview.column("Salida", width=100, anchor="center")
        self.jornadas_treeview.pack(pady=5, padx=5, fill="both", expand=True)
        self.jornadas_treeview.bind("<<TreeviewSelect>>", self._seleccionar_jornada_para_edicion)

        # Controles de edición de jornada
        edit_jornada_frame = ttk.LabelFrame(jornadas_empleado_frame, text="Editar/Eliminar Jornada")
        edit_jornada_frame.pack(pady=10, padx=5, fill="x", expand=False)

        # CAMBIO: Campo de fecha con botón de calendario para edición de jornada
        tk.Label(edit_jornada_frame, text="Fecha:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.edit_jornada_fecha = tk.Entry(edit_jornada_frame, state="readonly") # Hacerlo de solo lectura
        self.edit_jornada_fecha.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        # CORRECCIÓN: Usar lambda para pasar el argumento target_entry
        self.btn_seleccionar_fecha_edit = tk.Button(edit_jornada_frame, text="Seleccionar", command=lambda: self._open_calendar_dialog(self.edit_jornada_fecha))
        self.btn_seleccionar_fecha_edit.grid(row=0, column=2, padx=5, pady=2)


        tk.Label(edit_jornada_frame, text="Hora Entrada:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.edit_jornada_hora_entrada = ttk.Combobox(edit_jornada_frame, values=self.time_options, state="readonly")
        self.edit_jornada_hora_entrada.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(edit_jornada_frame, text="Hora Salida:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.edit_jornada_hora_salida = ttk.Combobox(edit_jornada_frame, values=self.time_options, state="readonly")
        self.edit_jornada_hora_salida.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        button_frame_jornada = ttk.Frame(edit_jornada_frame)
        button_frame_jornada.grid(row=3, column=0, columnspan=3, pady=10) # Ajuste de columnspan

        self.btn_guardar_cambios_jornada = tk.Button(button_frame_jornada, text="Guardar Cambios Jornada", command=self._guardar_cambios_jornada)
        self.btn_guardar_cambios_jornada.pack(side="left", padx=5)

        self.btn_eliminar_jornada = tk.Button(button_frame_jornada, text="Eliminar Jornada", command=self._eliminar_jornada_gui)
        self.btn_eliminar_jornada.pack(side="left", padx=5)

        edit_jornada_frame.columnconfigure(1, weight=1)

        self._actualizar_lista_gestion_empleados() # Cargar la lista de empleados al inicio de la pestaña

    def _actualizar_lista_gestion_empleados(self):
        """Actualiza la Listbox de la pestaña de gestión de empleados."""
        self.empleados_listbox.delete(0, tk.END)
        for nombre in sorted(self.empleados.keys()):
            empleado = self.empleados[nombre]
            self.empleados_listbox.insert(tk.END, f"{empleado.nombre} (Salario: ${empleado.salario_mensual:,.0f}, Horas Est.: {empleado.standard_daily_hours}h)")

    def _seleccionar_empleado_para_edicion(self, event=None):
        """Carga los datos del empleado seleccionado en los campos de edición y sus jornadas."""
        selected_indices = self.empleados_listbox.curselection()
        if not selected_indices:
            self._limpiar_campos_edicion_empleado()
            self._selected_employee_name_for_edit = None
            self._actualizar_lista_jornadas_empleado_seleccionado(None) # Limpiar jornadas
            return

        selected_name_display = self.empleados_listbox.get(selected_indices[0])
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
            
            self._actualizar_lista_jornadas_empleado_seleccionado(empleado) # Cargar las jornadas
            self._limpiar_campos_edicion_jornada() # Limpiar campos de edición de jornada
        else:
            self._limpiar_campos_edicion_empleado()
            self._selected_employee_name_for_edit = None
            self._actualizar_lista_jornadas_empleado_seleccionado(None)

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
        self._actualizar_lista_jornadas_empleado_seleccionado(None) # Limpiar jornadas después de editar/renombrar empleado
        save_app_data(self.empleados, self.calculadora) # Guardar datos después de la modificación

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
                self._actualizar_lista_jornadas_empleado_seleccionado(None) # Limpiar jornadas
                save_app_data(self.empleados, self.calculadora) # Guardar datos después de la modificación
            else:
                messagebox.showerror("Error", "Empleado no encontrado.")

    def _actualizar_lista_jornadas_empleado_seleccionado(self, empleado):
        """Actualiza el Treeview con las jornadas del empleado seleccionado."""
        self.jornadas_treeview.delete(*self.jornadas_treeview.get_children()) # Limpiar Treeview
        self._selected_jornada_index_for_edit = None # Resetear selección de jornada
        self._limpiar_campos_edicion_jornada() # Limpiar campos de edición de jornada

        if empleado:
            # Usamos el índice de la jornada como iid para facilitar la edición/eliminación
            for i, jornada in enumerate(empleado.jornadas_registradas):
                self.jornadas_treeview.insert("", "end", iid=str(i), values=(
                    jornada["fecha"].strftime('%Y-%m-%d'),
                    jornada["hora_entrada"].strftime('%I:%M %p'),
                    jornada["hora_salida"].strftime('%I:%M %p')
                ))

    def _seleccionar_jornada_para_edicion(self, event=None):
        """Carga los datos de la jornada seleccionada en los campos de edición."""
        selected_item_id = self.jornadas_treeview.focus()
        if not selected_item_id:
            self._limpiar_campos_edicion_jornada()
            self._selected_jornada_index_for_edit = None
            return

        # El iid es el índice de la jornada en la lista del empleado
        self._selected_jornada_index_for_edit = int(selected_item_id) 

        empleado = self.empleados.get(self._selected_employee_name_for_edit)
        if empleado and 0 <= self._selected_jornada_index_for_edit < len(empleado.jornadas_registradas):
            jornada = empleado.jornadas_registradas[self._selected_jornada_index_for_edit]
            
            # Habilitar el entry para insertar la fecha
            self.edit_jornada_fecha.config(state="normal")
            self.edit_jornada_fecha.delete(0, tk.END)
            self.edit_jornada_fecha.insert(0, jornada["fecha"].strftime('%Y-%m-%d'))
            self.edit_jornada_fecha.config(state="readonly") # Volver a solo lectura
            
            self.edit_jornada_hora_entrada.set(jornada["hora_entrada"].strftime('%I:%M %p'))
            self.edit_jornada_hora_salida.set(jornada["hora_salida"].strftime('%I:%M %p'))
        else:
            self._limpiar_campos_edicion_jornada()
            self._selected_jornada_index_for_edit = None

    def _limpiar_campos_edicion_jornada(self):
        """Limpia los campos de entrada de la sección de edición de jornada."""
        self.edit_jornada_fecha.config(state="normal") # Habilitar para limpiar
        self.edit_jornada_fecha.delete(0, tk.END)
        self.edit_jornada_fecha.config(state="readonly") # Volver a solo lectura

        self.edit_jornada_hora_entrada.set("08:00 AM") # Resetear a valor por defecto
        self.edit_jornada_hora_salida.set("05:00 PM") # Resetear a valor por defecto

    def _guardar_cambios_jornada(self):
        """Guarda los cambios de una jornada editada."""
        if self._selected_employee_name_for_edit is None or self._selected_jornada_index_for_edit is None:
            messagebox.showwarning("Advertencia", "Seleccione un empleado y una jornada para guardar cambios.")
            return

        empleado = self.empleados.get(self._selected_employee_name_for_edit)
        if not empleado:
            messagebox.showerror("Error", "Empleado no encontrado.")
            return

        new_fecha_str = self.edit_jornada_fecha.get().strip()
        new_hora_entrada_str = self.edit_jornada_hora_entrada.get().strip()
        new_hora_salida_str = self.edit_jornada_hora_salida.get().strip()

        if not new_fecha_str or not new_hora_entrada_str or not new_hora_salida_str:
            messagebox.showerror("Error", "Todos los campos de la jornada deben estar llenos.")
            return

        try:
            new_fecha = datetime.datetime.strptime(new_fecha_str, '%Y-%m-%d').date()
            new_hora_entrada = datetime.datetime.strptime(new_hora_entrada_str, '%I:%M %p').time()
            new_hora_salida = datetime.datetime.strptime(new_hora_salida_str, '%I:%M %p').time()

        except ValueError as e:
            messagebox.showerror("Error", f"Error en el formato de fecha/hora: {e}\nAsegúrese que la fecha es YYYY-MM-DD y las horas son HH:MM AM/PM.")
            return

        # Actualizar la jornada en la lista del empleado
        empleado.jornadas_registradas[self._selected_jornada_index_for_edit] = {
            "fecha": new_fecha,
            "hora_entrada": new_hora_entrada,
            "hora_salida": new_hora_salida
        }
        messagebox.showinfo("Éxito", f"Jornada actualizada con éxito para {empleado.nombre}.")
        
        self._actualizar_lista_jornadas_empleado_seleccionado(empleado) # Refrescar el Treeview
        self._limpiar_campos_edicion_jornada() # Limpiar campos de edición de jornada
        self._selected_jornada_index_for_edit = None # Resetear selección
        save_app_data(self.empleados, self.calculadora) # Guardar datos después de la modificación

    def _eliminar_jornada_gui(self):
        """Elimina una jornada seleccionada de un empleado."""
        if self._selected_employee_name_for_edit is None or self._selected_jornada_index_for_edit is None:
            messagebox.showwarning("Advertencia", "Seleccione un empleado y una jornada para eliminar.")
            return

        empleado = self.empleados.get(self._selected_employee_name_for_edit)
        if not empleado:
            messagebox.showerror("Error", "Empleado no encontrado.")
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar esta jornada?"):
            if 0 <= self._selected_jornada_index_for_edit < len(empleado.jornadas_registradas):
                del empleado.jornadas_registradas[self._selected_jornada_index_for_edit]
                messagebox.showinfo("Éxito", "Jornada eliminada con éxito.")
                self._actualizar_lista_jornadas_empleado_seleccionado(empleado) # Refrescar el Treeview
                self._limpiar_campos_edicion_jornada() # Limpiar campos de edición de jornada
                self._selected_jornada_index_for_edit = None # Resetear selección
                save_app_data(self.empleados, self.calculadora) # Guardar datos después de la modificación
            else:
                messagebox.showerror("Error", "Jornada no encontrado.")


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

    def _setup_festivos_tab(self):
        tk.Label(self.frame_festivos, text="--- Gestión de Días Festivos ---", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(self.frame_festivos, text="Fecha Festivo (YYYY-MM-DD):").pack(pady=5)
        # CAMBIO: Campo de fecha con botón de calendario para festivos
        self.entry_festivo_fecha = tk.Entry(self.frame_festivos, state="readonly")
        self.entry_festivo_fecha.pack(pady=5)
        # CORRECCIÓN: Usar lambda para pasar el argumento target_entry
        self.btn_seleccionar_fecha_festivo = tk.Button(self.frame_festivos, text="Seleccionar", command=lambda: self._open_calendar_dialog(self.entry_festivo_fecha))
        self.btn_seleccionar_fecha_festivo.pack(pady=5)


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

        # Horas Extras (se muestran como porcentaje TOTAL)
        tk.Label(self.frame_config, text=f"Hora Extra Diurna (% Total):").pack(pady=2)
        self.entry_extra_diurna_config = tk.Entry(self.frame_config)
        self.entry_extra_diurna_config.insert(0, str(round(self.calculadora.MULTIPLIER_HORA_EXTRA_DIURNA * 100)))
        self.entry_extra_diurna_config.pack(pady=2)

        tk.Label(self.frame_config, text=f"Horas Extras Nocturnas (% Total):").pack(pady=2)
        self.entry_extra_nocturna_config = tk.Entry(self.frame_config)
        self.entry_extra_nocturna_config.insert(0, str(round(self.calculadora.MULTIPLIER_HORA_EXTRA_NOCTURNA * 100)))
        self.entry_extra_nocturna_config.pack(pady=2)

        tk.Label(self.frame_config, text=f"Horas Extras Diurnas Dom./Fest. (% Total):").pack(pady=2)
        self.entry_extra_diurna_domingofestivo_config = tk.Entry(self.frame_config)
        self.entry_extra_diurna_domingofestivo_config.insert(0, str(round(self.calculadora.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO * 100)))
        self.entry_extra_diurna_domingofestivo_config.pack(pady=2)

        tk.Label(self.frame_config, text=f"Horas Extras Noctur Dom o Festivas (% Total):").pack(pady=2)
        self.entry_extra_nocturna_domingofestivo_config = tk.Entry(self.frame_config)
        self.entry_extra_nocturna_domingofestivo_config.insert(0, str(round(self.calculadora.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO * 100)))
        self.entry_extra_nocturna_domingofestivo_config.pack(pady=2)

        # Recargos (se muestran como porcentaje ADICIONAL)
        tk.Label(self.frame_config, text=f"Recargo Nocturno (% Adicional):").pack(pady=2)
        self.entry_ordinaria_nocturna_config = tk.Entry(self.frame_config)
        self.entry_ordinaria_nocturna_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA * 100)))
        self.entry_ordinaria_nocturna_config.pack(pady=2)

        tk.Label(self.frame_config, text=f"Recargo Dominical o Festivo Diurno Base (% Adicional):").pack(pady=2) 
        self.entry_domingofestivo_base_config = tk.Entry(self.frame_config)
        self.entry_domingofestivo_base_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE * 100)))
        self.entry_domingofestivo_base_config.pack(pady=2)

        tk.Label(self.frame_config, text=f"Recargo Nocturno Dominical o festivo (% Adicional):").pack(pady=2)
        self.entry_ordinaria_nocturna_domingofestivo_config = tk.Entry(self.frame_config)
        self.entry_ordinaria_nocturna_domingofestivo_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO * 100)))
        self.entry_ordinaria_nocturna_domingofestivo_config.pack(pady=2)

        tk.Label(self.frame_config, text=f"Recargo Dom./Fest. Diurno Jornada Larga (% Adicional):").pack(pady=2) 
        self.entry_domingofestivo_diurno_larga_jornada_config = tk.Entry(self.frame_config) # Corrected name
        self.entry_domingofestivo_diurno_larga_jornada_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA * 100)))
        self.entry_domingofestivo_diurno_larga_jornada_config.pack(pady=2)

        tk.Label(self.frame_config, text=f"Recargo Dom./Fest. Nocturno Jornada Larga (% Adicional):").pack(pady=2) 
        self.entry_domingofestivo_nocturno_larga_jornada_config = tk.Entry(self.frame_config)
        self.entry_domingofestivo_nocturno_larga_jornada_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA * 100)))
        self.entry_domingofestivo_nocturno_larga_jornada_config.pack(pady=2)

        self.btn_actualizar_porcentajes = tk.Button(self.frame_config, text="Actualizar Porcentajes de Recargo", command=self._actualizar_porcentajes_gui)
        self.btn_actualizar_porcentajes.pack(pady=10)

    def _setup_acumulados_tab(self):
        tk.Label(self.frame_acumulados, text="--- Acumulados de Horas por Categoría ---", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(self.frame_acumulados, text="Seleccionar Empleado:").pack(pady=5)
        self.acumulados_empleado_combobox = ttk.Combobox(self.frame_acumulados, state="readonly")
        self.acumulados_empleado_combobox.pack(pady=5)

        # Nuevos campos para selección de período
        periodo_frame = ttk.LabelFrame(self.frame_acumulados, text="Filtrar por Período (Opcional)")
        periodo_frame.pack(pady=5, padx=10, fill="x", expand=False)

        tk.Label(periodo_frame, text="Fecha Inicio (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.entry_acumulados_periodo_inicio = tk.Entry(periodo_frame, state="readonly")
        self.entry_acumulados_periodo_inicio.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.btn_seleccionar_fecha_acum_inicio = tk.Button(periodo_frame, text="Seleccionar", command=lambda: self._open_calendar_dialog(self.entry_acumulados_periodo_inicio))
        self.btn_seleccionar_fecha_acum_inicio.grid(row=0, column=2, padx=5, pady=2)

        tk.Label(periodo_frame, text="Fecha Fin (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.entry_acumulados_periodo_fin = tk.Entry(periodo_frame, state="readonly")
        self.entry_acumulados_periodo_fin.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.btn_seleccionar_fecha_acum_fin = tk.Button(periodo_frame, text="Seleccionar", command=lambda: self._open_calendar_dialog(self.entry_acumulados_periodo_fin))
        self.btn_seleccionar_fecha_acum_fin.grid(row=1, column=2, padx=5, pady=2)

        periodo_frame.columnconfigure(1, weight=1) # Permite que el campo de entrada se expanda

        self.btn_mostrar_acumulados = tk.Button(self.frame_acumulados, text="Mostrar Acumulados", command=self._mostrar_acumulados_empleado)
        self.btn_mostrar_acumulados.pack(pady=5)

        self.acumulados_report_area = scrolledtext.ScrolledText(self.frame_acumulados, width=80, height=20, wrap=tk.WORD)
        self.acumulados_report_area.pack(pady=10, padx=10, expand=True, fill="both")

    def _setup_recargos_detallados_tab(self):
        tk.Label(self.frame_recargos_detallados, text="--- Recargos Detallados por Empleado ---", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(self.frame_recargos_detallados, text="Seleccionar Empleado:").pack(pady=5)
        self.detallados_empleado_combobox = ttk.Combobox(self.frame_recargos_detallados, state="readonly")
        self.detallados_empleado_combobox.pack(pady=5)

        # Campos para selección de período (opcional)
        periodo_detallado_frame = ttk.LabelFrame(self.frame_recargos_detallados, text="Filtrar por Período (Opcional)")
        periodo_detallado_frame.pack(pady=5, padx=10, fill="x", expand=False)

        tk.Label(periodo_detallado_frame, text="Fecha Inicio (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.entry_detallados_periodo_inicio = tk.Entry(periodo_detallado_frame, state="readonly")
        self.entry_detallados_periodo_inicio.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.btn_seleccionar_fecha_detallados_inicio = tk.Button(periodo_detallado_frame, text="Seleccionar", command=lambda: self._open_calendar_dialog(self.entry_detallados_periodo_inicio))
        self.btn_seleccionar_fecha_detallados_inicio.grid(row=0, column=2, padx=5, pady=2)

        tk.Label(periodo_detallado_frame, text="Fecha Fin (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.entry_detallados_periodo_fin = tk.Entry(periodo_detallado_frame, state="readonly")
        self.entry_detallados_periodo_fin.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.btn_seleccionar_fecha_detallados_fin = tk.Button(periodo_detallado_frame, text="Seleccionar", command=lambda: self._open_calendar_dialog(self.entry_detallados_periodo_fin))
        self.btn_seleccionar_fecha_detallados_fin.grid(row=1, column=2, padx=5, pady=2)

        periodo_detallado_frame.columnconfigure(1, weight=1)

        self.btn_generar_recargos_detallados = tk.Button(self.frame_recargos_detallados, text="Generar Reporte Detallado", command=self._generar_recargos_detallados_gui)
        self.btn_generar_recargos_detallados.pack(pady=5)

        self.detallados_report_area = scrolledtext.ScrolledText(self.frame_recargos_detallados, width=80, height=20, wrap=tk.WORD)
        self.detallados_report_area.pack(pady=10, padx=10, expand=True, fill="both")


    def _mostrar_acumulados_empleado(self):
        nombre_empleado = self.acumulados_empleado_combobox.get()
        if not nombre_empleado:
            messagebox.showerror("Error", "Seleccione un empleado para ver los acumulados.")
            return

        original_empleado = self.empleados.get(nombre_empleado)
        if not original_empleado:
            messagebox.showerror("Error", "Empleado no encontrado.")
            return

        fecha_inicio_str = self.entry_acumulados_periodo_inicio.get().strip()
        fecha_fin_str = self.entry_acumulados_periodo_fin.get().strip()
        
        periodo_inicio = None
        periodo_fin = None
        report_period_info = ""

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
        
        jornadas_to_process = []
        if periodo_inicio and periodo_fin:
            # Filtrar jornadas por el período seleccionado
            for jornada in original_empleado.jornadas_registradas:
                if periodo_inicio <= jornada["fecha"] <= periodo_fin:
                    jornadas_to_process.append(jornada)
            report_period_info = f"Período: {periodo_inicio.strftime('%Y-%m-%d')} a {periodo_fin.strftime('%Y-%m-%d')}"
        elif periodo_inicio or periodo_fin: # Si solo se ingresa una fecha, es un error de uso
             messagebox.showwarning("Advertencia", "Por favor, ingrese AMBAS fechas de inicio y fin para filtrar por período, o deje AMBAS vacías para el acumulado total.")
             return
        else:
            # Si no se selecciona período, procesar todas las jornadas registradas
            jornadas_to_process = original_empleado.jornadas_registradas
            report_period_info = "Todas las jornadas registradas"


        # Crear un objeto Empleado temporal con las jornadas filtradas para usar la lógica existente
        # Esto evita modificar la lista original de jornadas del empleado y permite reutilizar CalculadoraRecargos
        temp_empleado = Empleado(original_empleado.nombre, original_empleado.salario_mensual, original_empleado.standard_daily_hours, original_empleado.tipo_contrato)
        temp_empleado.jornadas_registradas = jornadas_to_process

        # Obtener los acumulados usando la lógica existente
        acum_horas, _, _ = self.calculadora.get_accumulated_hours_and_surcharges(temp_empleado)

        reporte_str = f"--- Acumulados de Horas para {original_empleado.nombre} ({report_period_info}) ---\n"
        reporte_str += f"Horas Diarias Estándar: {original_empleado.standard_daily_hours} horas\n\n"

        display_names = {
            "horas_ordinarias_diurnas": "Horas Ordinarias Diurnas",
            "horas_ordinarias_nocturnas": "Horas Ordinarias Nocturnas",
            "horas_extras_diurnas": "Horas Extras Diurnas",
            "horas_extras_nocturnas": "Horas Extras Nocturnas",
            "horas_ordinarias_diurnas_domingo": "Horas Ordinarias Diurnas Domingo",
            "horas_ordinarias_nocturnas_domingo": "Horas Ordinarias Nocturnas Domingo",
            "horas_extras_diurnas_domingo": "Horas Extras Diurnas Domingo",
            "horas_extras_nocturnas_domingo": "Horas Extras Nocturnas Domingo",
            "horas_ordinarias_diurnas_festivo": "Horas Ordinarias Diurnas Festivo",
            "horas_ordinarias_nocturnas_festivo": "Horas Ordinarias Nocturnas Festivo",
            "horas_extras_diurnas_festivo": "Horas Extras Diurnas Festivo",
            "horas_extras_nocturnas_festivo": "Horas Extras Nocturnas Festivo",
        }

        # Sección para horas y recargos regulares
        reporte_str += "--- Horas Regulares ---\n"
        regular_keys = [
            "horas_ordinarias_diurnas",
            "horas_ordinarias_nocturnas",
            "horas_extras_diurnas",
            "horas_extras_nocturnas",
        ]
        total_horas_regulares_con_recargo = 0.0
        for key in regular_keys:
            hours = acum_horas.get(key, 0.0)
            if hours > 0:
                reporte_str += f"- {display_names[key]}: {hours:.2f}h\n"
                if key != "horas_ordinarias_diurnas":
                    total_horas_regulares_con_recargo += hours
        
        # Sección para horas de Domingo (Separadas)
        reporte_str += "\n--- Horas (Domingos) ---\n"
        domingo_keys = [
            "horas_ordinarias_diurnas_domingo",
            "horas_ordinarias_nocturnas_domingo",
            "horas_extras_diurnas_domingo",
            "horas_extras_nocturnas_domingo",
        ]
        total_horas_domingo_con_recargo = 0.0
        for key in domingo_keys:
            hours = acum_horas.get(key, 0.0)
            if hours > 0:
                reporte_str += f"- {display_names[key]}: {hours:.2f}h\n"
                total_horas_domingo_con_recargo += hours

        # Sección para horas de Festivo (Separadas)
        reporte_str += "\n--- Horas (Festivos) ---\n"
        festivo_keys = [
            "horas_ordinarias_diurnas_festivo",
            "horas_ordinarias_nocturnas_festivo",
            "horas_extras_diurnas_festivo",
            "horas_extras_nocturnas_festivo",
        ]
        total_horas_festivo_con_recargo = 0.0
        for key in festivo_keys:
            hours = acum_horas.get(key, 0.0)
            if hours > 0:
                reporte_str += f"- {display_names[key]}: {hours:.2f}h\n"
                total_horas_festivo_con_recargo += hours

        # NUEVA SECCIÓN: Horas Acumuladas Domingos y Festivos (Combinadas)
        reporte_str += "\n--- Horas Acumuladas Domingos y Festivos (Combinadas) ---\n"
        
        total_ord_diurnas_df = acum_horas.get("horas_ordinarias_diurnas_domingo", 0.0) + acum_horas.get("horas_ordinarias_diurnas_festivo", 0.0)
        if total_ord_diurnas_df > 0:
            reporte_str += f"- Horas Ordinarias Diurnas D/F: {total_ord_diurnas_df:.2f}h\n"

        total_ord_nocturnas_df = acum_horas.get("horas_ordinarias_nocturnas_domingo", 0.0) + acum_horas.get("horas_ordinarias_nocturnas_festivo", 0.0)
        if total_ord_nocturnas_df > 0:
            reporte_str += f"- Horas Ordinarias Nocturnas D/F: {total_ord_nocturnas_df:.2f}h\n"

        total_ext_diurnas_df = acum_horas.get("horas_extras_diurnas_domingo", 0.0) + acum_horas.get("horas_extras_diurnas_festivo", 0.0)
        if total_ext_diurnas_df > 0:
            reporte_str += f"- Horas Extras Diurnas D/F: {total_ext_diurnas_df:.2f}h\n"

        total_ext_nocturnas_df = acum_horas.get("horas_extras_nocturnas_domingo", 0.0) + acum_horas.get("horas_extras_nocturnas_festivo", 0.0)
        if total_ext_nocturnas_df > 0:
            reporte_str += f"- Horas Extras Nocturnas D/F: {total_ext_nocturnas_df:.2f}h\n"

        # Calcular el total general de horas con recargo
        total_general_horas_con_recargo = 0.0
        for key, hours in acum_horas.items():
            if key != "horas_ordinarias_diurnas": # Excluir horas ordinarias diurnas que no tienen recargo adicional
                total_general_horas_con_recargo += hours

        # Calcular el total general de todas las horas (recargo + ordinarias diurnas)
        total_todas_las_horas_acumuladas = sum(acum_horas.values())

        reporte_str += f"\nTotal de Horas Acumuladas con Recargo (Todas las Categorías): {total_general_horas_con_recargo:.2f}h\n"
        reporte_str += f"Total de Todas las Horas Acumuladas (Recargo + Ordinarias): {total_todas_las_horas_acumuladas:.2f}h\n"
        reporte_str += "-----------------------------------------------------\n"

        self.acumulados_report_area.delete(1.0, tk.END)
        self.acumulados_report_area.insert(tk.END, reporte_str)

    def _generar_recargos_detallados_gui(self):
        nombre_empleado = self.detallados_empleado_combobox.get()
        if not nombre_empleado:
            messagebox.showerror("Error", "Seleccione un empleado para generar el reporte detallado.")
            return

        original_empleado = self.empleados.get(nombre_empleado)
        if not original_empleado:
            messagebox.showerror("Error", "Empleado no encontrado.")
            return

        fecha_inicio_str = self.entry_detallados_periodo_inicio.get().strip()
        fecha_fin_str = self.entry_detallados_periodo_fin.get().strip()
        
        periodo_inicio = None
        periodo_fin = None
        report_period_info = ""

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
        
        jornadas_to_process = []
        if periodo_inicio and periodo_fin:
            for jornada in original_empleado.jornadas_registradas:
                if periodo_inicio <= jornada["fecha"] <= periodo_fin:
                    jornadas_to_process.append(jornada)
            report_period_info = f"Período: {periodo_inicio.strftime('%Y-%m-%d')} a {periodo_fin.strftime('%Y-%m-%d')}"
        elif periodo_inicio or periodo_fin:
             messagebox.showwarning("Advertencia", "Por favor, ingrese AMBAS fechas de inicio y fin para filtrar por período, o deje AMBAS vacías para el acumulado total.")
             return
        else:
            jornadas_to_process = original_empleado.jornadas_registradas
            report_period_info = "Todas las jornadas registradas"

        temp_empleado = Empleado(original_empleado.nombre, original_empleado.salario_mensual, original_empleado.standard_daily_hours, original_empleado.tipo_contrato)
        temp_empleado.jornadas_registradas = jornadas_to_process

        acum_horas, acum_surcharge_values, total_gross_value = self.calculadora.get_accumulated_hours_and_surcharges(temp_empleado)

        reporte_str = f"--- Recargos Detallados para {original_empleado.nombre} ({report_period_info}) ---\n"
        reporte_str += f"Salario Mensual: ${original_empleado.salario_mensual:,.2f}\n"
        reporte_str += f"Horas Diarias Estándar: {original_empleado.standard_daily_hours} horas\n\n"
        reporte_str += "Detalle de Horas y Recargos:\n"

        display_names = {
            "horas_ordinarias_diurnas": "Horas Ordinarias Diurnas",
            "horas_ordinarias_nocturnas": "Horas Ordinarias Nocturnas",
            "horas_extras_diurnas": "Horas Extras Diurnas",
            "horas_extras_nocturnas": "Horas Extras Nocturnas",
            "horas_ordinarias_diurnas_domingo": "Horas Ordinarias Diurnas Domingo",
            "horas_ordinarias_nocturnas_domingo": "Horas Ordinarias Nocturnas Domingo",
            "horas_extras_diurnas_domingo": "Horas Extras Diurnas Domingo",
            "horas_extras_nocturnas_domingo": "Horas Extras Nocturnas Domingo",
            "horas_ordinarias_diurnas_festivo": "Horas Ordinarias Diurnas Festivo",
            "horas_ordinarias_nocturnas_festivo": "Horas Ordinarias Nocturnas Festivo",
            "horas_extras_diurnas_festivo": "Horas Extras Diurnas Festivo",
            "horas_extras_nocturnas_festivo": "Horas Extras Nocturnas Festivo",
        }

        # Ordenar las claves para una presentación consistente
        ordered_keys = [
            "horas_ordinarias_diurnas",
            "horas_ordinarias_nocturnas",
            "horas_extras_diurnas",
            "horas_extras_nocturnas",
        ]

        # Sección para horas regulares
        reporte_str += "--- Horas Regulares ---\n"
        for key in ordered_keys:
            hours = acum_horas.get(key, 0.0)
            if hours > 0:
                if key == "horas_ordinarias_diurnas":
                    # Horas Ordinarias Diurnas no tienen recargo adicional, solo valor base
                    valor_base = hours * original_empleado.obtener_valor_hora_ordinaria()
                    reporte_str += f"- {display_names[key]}: {hours:.2f}h (Valor Base: ${valor_base:,.2f})\n"
                else:
                    porcentaje = self.calculadora._get_percentage_for_hour_type(key)
                    surcharge_value = acum_surcharge_values.get(key, 0.0)
                    # El valor total es el valor base de esas horas más el recargo
                    valor_total_tipo_hora = (hours * original_empleado.obtener_valor_hora_ordinaria()) + surcharge_value
                    reporte_str += f"- {display_names[key]} ({porcentaje}%): {hours:.2f}h (Recargo: ${surcharge_value:,.2f} | Total: ${valor_total_tipo_hora:,.2f})\n"
        
        # Sección para horas de Domingo (Separadas)
        reporte_str += "\n--- Horas (Domingos) ---\n"
        domingo_keys = [
            "horas_ordinarias_diurnas_domingo",
            "horas_ordinarias_nocturnas_domingo",
            "horas_extras_diurnas_domingo",
            "horas_extras_nocturnas_domingo",
        ]
        for key in domingo_keys:
            hours = acum_horas.get(key, 0.0)
            if hours > 0:
                porcentaje = self.calculadora._get_percentage_for_hour_type(key)
                surcharge_value = acum_surcharge_values.get(key, 0.0)
                valor_total_tipo_hora = (hours * original_empleado.obtener_valor_hora_ordinaria()) + surcharge_value
                reporte_str += f"- {display_names[key]} ({porcentaje}%): {hours:.2f}h (Recargo: ${surcharge_value:,.2f} | Total: ${valor_total_tipo_hora:,.2f})\n"

        # Sección para horas de Festivo (Separadas)
        reporte_str += "\n--- Horas (Festivos) ---\n"
        festivo_keys = [
            "horas_ordinarias_diurnas_festivo",
            "horas_ordinarias_nocturnas_festivo",
            "horas_extras_diurnas_festivo",
            "horas_extras_nocturnas_festivo",
        ]
        for key in festivo_keys:
            hours = acum_horas.get(key, 0.0)
            if hours > 0:
                porcentaje = self.calculadora._get_percentage_for_hour_type(key)
                surcharge_value = acum_surcharge_values.get(key, 0.0)
                valor_total_tipo_hora = (hours * original_empleado.obtener_valor_hora_ordinaria()) + surcharge_value
                reporte_str += f"- {display_names[key]} ({porcentaje}%): {hours:.2f}h (Recargo: ${surcharge_value:,.2f} | Total: ${valor_total_tipo_hora:,.2f})\n"

        # NUEVA SECCIÓN: Horas Acumuladas Domingos y Festivos (Combinadas)
        reporte_str += "\n--- Horas Acumuladas Domingos y Festivos (Combinadas) ---\n"
        
        # Horas Ordinarias Diurnas D/F Combinadas
        total_ord_diurnas_df_hours = acum_horas.get("horas_ordinarias_diurnas_domingo", 0.0) + acum_horas.get("horas_ordinarias_diurnas_festivo", 0.0)
        total_ord_diurnas_df_surcharge = acum_surcharge_values.get("horas_ordinarias_diurnas_domingo", 0.0) + acum_surcharge_values.get("horas_ordinarias_diurnas_festivo", 0.0)
        # Asumimos que el porcentaje para ambas es el mismo (180%)
        porcentaje_ord_diurnas_df = self.calculadora._get_percentage_for_hour_type("horas_ordinarias_diurnas_domingo") 
        if total_ord_diurnas_df_hours > 0:
            valor_total_ord_diurnas_df = (total_ord_diurnas_df_hours * original_empleado.obtener_valor_hora_ordinaria()) + total_ord_diurnas_df_surcharge
            reporte_str += f"- Horas Ordinarias Diurnas D/F ({porcentaje_ord_diurnas_df}%): {total_ord_diurnas_df_hours:.2f}h (Recargo: ${total_ord_diurnas_df_surcharge:,.2f} | Total: ${valor_total_ord_diurnas_df:,.2f})\n"

        # Horas Ordinarias Nocturnas D/F Combinadas
        total_ord_nocturnas_df_hours = acum_horas.get("horas_ordinarias_nocturnas_domingo", 0.0) + acum_horas.get("horas_ordinarias_nocturnas_festivo", 0.0)
        total_ord_nocturnas_df_surcharge = acum_surcharge_values.get("horas_ordinarias_nocturnas_domingo", 0.0) + acum_surcharge_values.get("horas_ordinarias_nocturnas_festivo", 0.0)
        porcentaje_ord_nocturnas_df = self.calculadora._get_percentage_for_hour_type("horas_ordinarias_nocturnas_domingo")
        if total_ord_nocturnas_df_hours > 0:
            valor_total_ord_nocturnas_df = (total_ord_nocturnas_df_hours * original_empleado.obtener_valor_hora_ordinaria()) + total_ord_nocturnas_df_surcharge
            reporte_str += f"- Horas Ordinarias Nocturnas D/F ({porcentaje_ord_nocturnas_df}%): {total_ord_nocturnas_df_hours:.2f}h (Recargo: ${total_ord_nocturnas_df_surcharge:,.2f} | Total: ${valor_total_ord_nocturnas_df:,.2f})\n"

        # Horas Extras Diurnas D/F Combinadas
        total_ext_diurnas_df_hours = acum_horas.get("horas_extras_diurnas_domingo", 0.0) + acum_horas.get("horas_extras_diurnas_festivo", 0.0)
        total_ext_diurnas_df_surcharge = acum_surcharge_values.get("horas_extras_diurnas_domingo", 0.0) + acum_surcharge_values.get("horas_extras_diurnas_festivo", 0.0)
        porcentaje_ext_diurnas_df = self.calculadora._get_percentage_for_hour_type("horas_extras_diurnas_domingo")
        if total_ext_diurnas_df_hours > 0:
            valor_total_ext_diurnas_df = (total_ext_diurnas_df_hours * original_empleado.obtener_valor_hora_ordinaria()) + total_ext_diurnas_df_surcharge
            reporte_str += f"- Horas Extras Diurnas D/F ({porcentaje_ext_diurnas_df}%): {total_ext_diurnas_df_hours:.2f}h (Recargo: ${total_ext_diurnas_df_surcharge:,.2f} | Total: ${valor_total_ext_diurnas_df:,.2f})\n"

        # Horas Extras Nocturnas D/F Combinadas
        total_ext_nocturnas_df_hours = acum_horas.get("horas_extras_nocturnas_domingo", 0.0) + acum_horas.get("horas_extras_nocturnas_festivo", 0.0)
        total_ext_nocturnas_df_surcharge = acum_surcharge_values.get("horas_extras_nocturnas_domingo", 0.0) + acum_surcharge_values.get("horas_extras_nocturnas_festivo", 0.0)
        porcentaje_ext_nocturnas_df = self.calculadora._get_percentage_for_hour_type("horas_extras_nocturnas_domingo")
        if total_ext_nocturnas_df_hours > 0:
            valor_total_ext_nocturnas_df = (total_ext_nocturnas_df_hours * original_empleado.obtener_valor_hora_ordinaria()) + total_ext_nocturnas_df_surcharge
            reporte_str += f"- Horas Extras Nocturnas D/F ({porcentaje_ext_nocturnas_df}%): {total_ext_nocturnas_df_hours:.2f}h (Recargo: ${total_ext_nocturnas_df_surcharge:,.2f} | Total: ${valor_total_ext_nocturnas_df:,.2f})\n"


        reporte_str += f"\nTotal Valor Bruto Acumulado: ${total_gross_value:,.2f}\n"
        reporte_str += "-----------------------------------------------------\n"

        self.detallados_report_area.delete(1.0, tk.END)
        self.detallados_report_area.insert(tk.END, reporte_str)


    def _open_calendar_dialog(self, target_entry):
        """Abre un diálogo de calendario para seleccionar una fecha."""
        top = tk.Toplevel(self.root)
        top.title("Seleccionar Fecha")
        
        # Centrar la ventana del calendario
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (top.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (top.winfo_height() // 2)
        top.geometry(f"+{x}+{y}")

        # Obtener la fecha actual o la fecha del entry si ya hay una
        try:
            current_date_str = target_entry.get()
            if current_date_str:
                current_date = datetime.datetime.strptime(current_date_str, '%Y-%m-%d').date()
            else:
                current_date = datetime.date.today()
        except ValueError:
            current_date = datetime.date.today()

        cal = Calendar(top, selectmode='day',
                       year=current_date.year, month=current_date.month, day=current_date.day,
                       date_pattern='yyyy-mm-dd')
        cal.pack(pady=20)

        def set_date():
            selected_date = cal.selection_get()
            target_entry.config(state="normal") # Habilitar para escribir
            target_entry.delete(0, tk.END)
            target_entry.insert(0, selected_date.strftime('%Y-%m-%d'))
            target_entry.config(state="readonly") # Volver a solo lectura
            top.destroy()

        ttk.Button(top, text="Seleccionar Fecha", command=set_date).pack(pady=10)


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
        messagebox.showinfo("Éxito", f"Empleado '{nombre}' creado con éxito (Horas diarias estándar: {standard_daily_hours}h).") # Eliminado salario del mensaje
        
        self.entry_nombre_empleado.delete(0, tk.END)
        self.entry_salario_empleado.delete(0, tk.END) 
        self.entry_standard_daily_hours.delete(0, tk.END)
        self.entry_standard_daily_hours.insert(0, "8") # Restablecer valor por defecto
        self._actualizar_todas_las_listas_empleados() # Actualizar todos los combobox y listbox
        save_app_data(self.empleados, self.calculadora) # Guardar datos después de la modificación


    def _actualizar_lista_empleados(self):
        """Actualiza los Combobox de selección de empleado en las pestañas de registro y reportes."""
        nombres_empleados = sorted(list(self.empleados.keys()))
        self.empleados_combobox['values'] = nombres_empleados
        if nombres_empleados:
            current_selection = self.empleados_combobox.get()
            if current_selection not in nombres_empleados:
                self.empleados_combobox.set(nombres_empleados[0])
            
            if hasattr(self, 'reporte_empleado_combobox'): 
                self.reporte_empleado_combobox['values'] = nombres_empleados
                current_report_selection = self.reporte_empleado_combobox.get()
                if current_report_selection not in nombres_empleados:
                    self.reporte_empleado_combobox.set(nombres_empleados[0])
            
            if hasattr(self, 'acumulados_empleado_combobox'):
                self.acumulados_empleado_combobox['values'] = nombres_empleados
                current_acum_selection = self.acumulados_empleado_combobox.get()
                if current_acum_selection not in nombres_empleados:
                    self.acumulados_empleado_combobox.set(nombres_empleados[0])
            
            # NUEVO: Actualizar el combobox de la pestaña de recargos detallados
            if hasattr(self, 'detallados_empleado_combobox'):
                self.detallados_empleado_combobox['values'] = nombres_empleados
                current_detallados_selection = self.detallados_empleado_combobox.get()
                if current_detallados_selection not in nombres_empleados:
                    self.detallados_empleado_combobox.set(nombres_empleados[0])

        else:
            self.empleados_combobox.set("") 
            if hasattr(self, 'reporte_empleado_combobox'):
                self.reporte_empleado_combobox.set("")
            if hasattr(self, 'acumulados_empleado_combobox'):
                self.acumulados_empleado_combobox.set("")
            if hasattr(self, 'detallados_empleado_combobox'):
                self.detallados_empleado_combobox.set("")


    def _actualizar_todas_las_listas_empleados(self):
        """Llama a todos los métodos de actualización de listas y comboboxes de empleados."""
        self._actualizar_lista_empleados() # Para los combobox de registro y reportes
        self._actualizar_lista_gestion_empleados() # Para la listbox de gestión


    def _on_empleado_selected(self, event=None):
        pass

    def _on_dia_compensatorio_toggle(self, *args):
        """Maneja el estado del checkbox de día compensatorio."""
        if self.es_dia_compensatorio.get():
            # Si es día compensatorio, fijar las horas y deshabilitar los combobox
            self.combo_hora_entrada.set("08:00 AM")
            self.combo_hora_salida.set("04:00 PM") # 8 horas de trabajo
            self.combo_hora_entrada.config(state="disabled")
            self.combo_hora_salida.config(state="disabled")
            # Opcional: Puedes pre-seleccionar la fecha actual si lo deseas, o dejar que el usuario la elija
            # self.entry_fecha_jornada.config(state="normal")
            # self.entry_fecha_jornada.delete(0, tk.END)
            # self.entry_fecha_jornada.insert(0, datetime.date.today().strftime('%Y-%m-%d'))
            # self.entry_fecha_jornada.config(state="readonly")
        else:
            # Si no es día compensatorio, habilitar los combobox y limpiar la fecha
            self.combo_hora_entrada.config(state="readonly")
            self.combo_hora_salida.config(state="readonly")
            # self.entry_fecha_jornada.config(state="normal")
            # self.entry_fecha_jornada.delete(0, tk.END)
            # self.entry_fecha_jornada.config(state="readonly")


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
        
        # Limpiar el campo de fecha usando el nuevo método de limpieza para Entry de solo lectura
        self.entry_fecha_jornada.config(state="normal")
        self.entry_fecha_jornada.delete(0, tk.END)
        self.entry_fecha_jornada.config(state="readonly")

        # Desactivar el checkbox de día compensatorio después de registrar
        self.es_dia_compensatorio.set(False)

        save_app_data(self.empleados, self.calculadora) # Guardar datos después de la modificación


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
        if selected_tab == "Registro de Jornadas" or selected_tab == "Reportes" or selected_tab == "Acumulados de Horas" or selected_tab == "Recargos Detallados":
            self._actualizar_lista_empleados()
        elif selected_tab == "Gestión de Empleados": 
            self._actualizar_lista_gestion_empleados()
            self._limpiar_campos_edicion_empleado() 
            self._actualizar_lista_jornadas_empleado_seleccionado(None) 
            self._limpiar_campos_edicion_jornada() 
        elif selected_tab == "Gestión de Festivos":
            self._actualizar_lista_festivos()
            # Limpiar el campo de fecha de festivos al cambiar a la pestaña
            self.entry_festivo_fecha.config(state="normal")
            self.entry_festivo_fecha.delete(0, tk.END)
            self.entry_festivo_fecha.config(state="readonly")
        elif selected_tab == "Configuración":
            # Actualizar campos de porcentajes al entrar a la pestaña
            # Horas Extras (se muestran como porcentaje TOTAL)
            self.entry_extra_diurna_config.delete(0, tk.END)
            self.entry_extra_diurna_config.insert(0, str(round(self.calculadora.MULTIPLIER_HORA_EXTRA_DIURNA * 100)))

            self.entry_extra_nocturna_config.delete(0, tk.END)
            self.entry_extra_nocturna_config.insert(0, str(round(self.calculadora.MULTIPLIER_HORA_EXTRA_NOCTURNA * 100)))

            self.entry_extra_diurna_domingofestivo_config.delete(0, tk.END)
            self.entry_extra_diurna_domingofestivo_config.insert(0, str(round(self.calculadora.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO * 100)))

            self.entry_extra_nocturna_domingofestivo_config.delete(0, tk.END)
            self.entry_extra_nocturna_domingofestivo_config.insert(0, str(round(self.calculadora.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO * 100)))

            # Recargos (se muestran como porcentaje ADICIONAL)
            self.entry_ordinaria_nocturna_config.delete(0, tk.END)
            self.entry_ordinaria_nocturna_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA * 100)))

            self.entry_domingofestivo_base_config.delete(0, tk.END)
            self.entry_domingofestivo_base_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE * 100)))

            self.entry_ordinaria_nocturna_domingofestivo_config.delete(0, tk.END)
            self.entry_ordinaria_nocturna_domingofestivo_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO * 100)))

            self.entry_domingofestivo_diurno_larga_jornada_config.delete(0, tk.END)
            self.entry_domingofestivo_diurno_larga_jornada_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA * 100)))

            self.entry_domingofestivo_nocturno_larga_jornada_config.delete(0, tk.END)
            self.entry_domingofestivo_nocturno_larga_jornada_config.insert(0, str(round(self.calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA * 100)))


    def _agregar_festivo_gui(self):
        fecha_str = self.entry_festivo_fecha.get().strip()
        if not fecha_str:
            messagebox.showerror("Error", "Ingrese una fecha para el festivo (YYYY-MM-DD).")
            return
        try:
            fecha_festivo = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            mensaje = self.calculadora.agregar_dia_festivo(fecha_festivo)
            messagebox.showinfo("Gestión de Festivos", mensaje)
            
            self.entry_festivo_fecha.config(state="normal") # Habilitar para limpiar
            self.entry_festivo_fecha.delete(0, tk.END)
            self.entry_festivo_fecha.config(state="readonly") # Volver a solo lectura

            self._actualizar_lista_festivos()
            save_app_data(self.empleados, self.calculadora) # Guardar datos después de la modificación
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
            
            self.entry_festivo_fecha.config(state="normal") # Habilitar para limpiar
            self.entry_festivo_fecha.delete(0, tk.END) # Corregido: usar self.entry_festivo_fecha
            self.entry_festivo_fecha.config(state="readonly") # Volver a solo lectura

            self._actualizar_lista_festivos()
            save_app_data(self.empleados, self.calculadora) # Guardar datos después de la modificación
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")

    def _actualizar_lista_festivos(self):
        self.festivos_listbox.delete(0, tk.END)
        for fecha in sorted(self.calculadora.dias_festivos):
            self.festivos_listbox.insert(tk.END, fecha.strftime('%Y-%m-%d'))


    def _actualizar_porcentajes_gui(self):
        # Obtener valores de los campos de entrada
        # Horas Extras (se esperan como porcentaje TOTAL)
        nuevo_extra_diurna_str = self.entry_extra_diurna_config.get().strip()
        nuevo_extra_nocturna_str = self.entry_extra_nocturna_config.get().strip()
        nuevo_extra_diurna_domingofestivo_str = self.entry_extra_diurna_domingofestivo_config.get().strip()
        nuevo_extra_nocturna_domingofestivo_str = self.entry_extra_nocturna_domingofestivo_config.get().strip()
        
        # Recargos (se esperan como porcentaje ADICIONAL)
        nuevo_ordinaria_nocturna_recargo_str = self.entry_ordinaria_nocturna_config.get().strip()
        nuevo_recargo_domingofestivo_diurno_base_recargo_str = self.entry_domingofestivo_base_config.get().strip()
        nuevo_ordinaria_nocturna_domingofestivo_recargo_str = self.entry_ordinaria_nocturna_domingofestivo_config.get().strip()
        nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo_str = self.entry_domingofestivo_diurno_larga_jornada_config.get().strip()
        nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo_str = self.entry_domingofestivo_nocturno_larga_jornada_config.get().strip()

        try:
            # Convertir a float. Si el campo está vacío, None.
            p_extra_diurna = float(nuevo_extra_diurna_str) if nuevo_extra_diurna_str else None
            p_extra_nocturna = float(nuevo_extra_nocturna_str) if nuevo_extra_nocturna_str else None
            p_extra_diurna_domingofestivo = float(nuevo_extra_diurna_domingofestivo_str) if nuevo_extra_diurna_domingofestivo_str else None
            p_extra_nocturna_domingofestivo = float(nuevo_extra_nocturna_domingofestivo_str) if nuevo_extra_nocturna_domingofestivo_str else None
            
            p_ordinaria_nocturna_recargo = float(nuevo_ordinaria_nocturna_recargo_str) if nuevo_ordinaria_nocturna_recargo_str else None
            p_recargo_domingofestivo_diurno_base_recargo = float(nuevo_recargo_domingofestivo_diurno_base_recargo_str) if nuevo_recargo_domingofestivo_diurno_base_recargo_str else None
            p_ordinaria_nocturna_domingofestivo_recargo = float(nuevo_ordinaria_nocturna_domingofestivo_recargo_str) if nuevo_ordinaria_nocturna_domingofestivo_recargo_str else None
            p_recargo_domingofestivo_diurno_larga_jornada_recargo = float(nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo_str) if nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo_str else None
            p_recargo_domingofestivo_nocturno_larga_jornada_recargo = float(nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo_str) if nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo_str else None

            # Validar rangos para porcentajes
            max_percentage = 350.0 # Un porcentaje total máximo razonable
            max_additional_percentage = 300.0 # Un porcentaje adicional máximo razonable

            # Validar porcentajes TOTALES (para extras)
            if (p_extra_diurna is not None and (p_extra_diurna < 0 or p_extra_diurna > max_percentage)) or \
               (p_extra_nocturna is not None and (p_extra_nocturna < 0 or p_extra_nocturna > max_percentage)) or \
               (p_extra_diurna_domingofestivo is not None and (p_extra_diurna_domingofestivo < 0 or p_extra_diurna_domingofestivo > max_percentage)) or \
               (p_extra_nocturna_domingofestivo is not None and (p_extra_nocturna_domingofestivo < 0 or p_extra_nocturna_domingofestivo > max_percentage)):
                raise ValueError(f"Los porcentajes 'Total' deben estar entre 0 y {max_percentage}.")

            # Validar porcentajes ADICIONALES (para recargos)
            if (p_ordinaria_nocturna_recargo is not None and (p_ordinaria_nocturna_recargo < 0 or p_ordinaria_nocturna_recargo > max_additional_percentage)) or \
               (p_recargo_domingofestivo_diurno_base_recargo is not None and (p_recargo_domingofestivo_diurno_base_recargo < 0 or p_recargo_domingofestivo_diurno_base_recargo > max_additional_percentage)) or \
               (p_ordinaria_nocturna_domingofestivo_recargo is not None and (p_ordinaria_nocturna_domingofestivo_recargo < 0 or p_ordinaria_nocturna_domingofestivo_recargo > max_additional_percentage)) or \
               (p_recargo_domingofestivo_diurno_larga_jornada_recargo is not None and (p_recargo_domingofestivo_diurno_larga_jornada_recargo < 0 or p_recargo_domingofestivo_diurno_larga_jornada_recargo > max_additional_percentage)) or \
               (p_recargo_domingofestivo_nocturno_larga_jornada_recargo is not None and (p_recargo_domingofestivo_nocturno_larga_jornada_recargo < 0 or p_recargo_domingofestivo_nocturno_larga_jornada_recargo > max_additional_percentage)):
                raise ValueError(f"Los porcentajes 'Adicional' deben estar entre 0 y {max_additional_percentage}.")


            mensaje = self.calculadora.actualizar_porcentajes_recargo(
                nuevo_extra_diurna=p_extra_diurna,
                nuevo_extra_nocturna=p_extra_nocturna,
                nuevo_extra_diurna_domingofestivo=p_extra_diurna_domingofestivo,
                nuevo_extra_nocturna_domingofestivo=p_extra_nocturna_domingofestivo,
                nuevo_ordinaria_nocturna_recargo=p_ordinaria_nocturna_recargo,
                nuevo_recargo_domingofestivo_diurno_base_recargo=p_recargo_domingofestivo_diurno_base_recargo,
                nuevo_ordinaria_nocturna_domingofestivo_recargo=p_ordinaria_nocturna_domingofestivo_recargo,
                nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo=p_recargo_domingofestivo_diurno_larga_jornada_recargo,
                nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo=p_recargo_domingofestivo_nocturno_larga_jornada_recargo
            )
            messagebox.showinfo("Configuración", mensaje)
            
            self._on_tab_change(None) # Refrescar la pestaña de configuración para mostrar los nuevos valores
            save_app_data(self.empleados, self.calculadora) # Guardar datos después de la modificación
        except ValueError as e:
            messagebox.showerror("Error", f"Valores de porcentaje inválidos: {e}")

    def _on_closing(self):
        """Maneja el evento de cierre de la ventana para guardar datos."""
        if messagebox.askokcancel("Salir", "¿Desea guardar los cambios y salir de la aplicación?"):
            save_app_data(self.empleados, self.calculadora)
            self.root.destroy()
        else:
            self.root.destroy() # Si no quiere guardar, igual cierra la app

    def _precargar_datos_ejemplo(self):
        """
        Este método está comentado por defecto. Descoméntalo y úsalo si necesitas
        precargar datos de ejemplo al iniciar la aplicación para pruebas.
        """
        # Ajustado el salario para que el valor de la hora ordinaria sea 6470
        empleado1 = Empleado("Ana Pérez", 1_423_400, 8, "indefinido") 
        empleado2 = Empleado("Juan García", 2_500_000, 8, "término fijo") 
        empleado3 = Empleado("Pedro López", 1_000_000, 6, "obra o labor") 

        self.empleados["Ana Pérez"] = empleado1
        self.empleados["Juan García"] = empleado2
        self.empleados["Pedro López"] = empleado3

        # Jornadas de ejemplo para probar la categorización:
        # Domingo (2025-07-13) - 8 horas: Deberían ser 8h ordinarias Domingo Diurnas
        empleado1.registrar_jornada(datetime.date(2025, 7, 13), datetime.time(8, 0), datetime.time(16, 0)) 
        # Festivo (2025-07-20) - 10 horas: 8h ordinarias Festivo Diurnas, 2h extras diurnas Festivo
        empleado2.registrar_jornada(datetime.date(2025, 7, 20), datetime.time(7, 0), datetime.time(17, 0))
        # Día regular (2025-07-14, lunes) - 10 horas: 8h ordinarias diurnas, 2h extras diurnas
        empleado3.registrar_jornada(datetime.date(2025, 7, 14), datetime.time(9, 0), datetime.time(19, 0))
        # Día regular (2025-07-15, martes) - 12 horas (incluye nocturnas): 8h ord diurnas, 2h ext diurnas, 2h ext nocturnas
        empleado1.registrar_jornada(datetime.date(2025, 7, 15), datetime.time(18, 0), datetime.time(6, 0)) # Turno de noche
        # Día regular (2025-07-16, miércoles) - 8 horas nocturnas: 8h ordinarias nocturnas
        empleado2.registrar_jornada(datetime.date(2025, 7, 16), datetime.time(22, 0), datetime.time(6, 0)) 
        # Domingo/Festivo Nocturno (2025-12-25, Navidad, asumiendo que cae en Festivo)
        empleado3.registrar_jornada(datetime.date(2025, 12, 25), datetime.time(22, 0), datetime.time(6, 0)) # 8h ordinarias nocturnas festivo
        # Jornada larga en domingo/festivo diurno (2025-07-27, domingo) - 24 horas continuas
        empleado1.registrar_jornada(datetime.date(2025, 7, 27), datetime.time(0, 0), datetime.time(0, 0)) # 24 horas en Domingo
        # Jornada de 7 horas en Domingo Diurno para probar 0.80
        empleado1.registrar_jornada(datetime.date(2025, 7, 28), datetime.time(8, 0), datetime.time(15, 0)) # 7 horas en Domingo
        # Jornada de 22 horas en Domingo Diurno para probar 0.80
        empleado2.registrar_jornada(datetime.date(2025, 7, 29), datetime.time(6, 0), datetime.time(4, 0)) # 22 horas en Domingo (6am a 4am del día siguiente)
        # Jornada de 24 horas en Festivo Nocturno para probar 215%
        empleado2.registrar_jornada(datetime.date(2025, 12, 25), datetime.time(21, 0), datetime.time(21, 0) + datetime.timedelta(days=1)) # 24 horas en Festivo, nocturnas

        self._actualizar_todas_las_listas_empleados() 
        self._actualizar_lista_festivos()
        save_app_data(self.empleados, self.calculadora) # Guardar los datos de ejemplo

if __name__ == "__main__":
    root = tk.Tk()
    app = RecargosApp(root)
    root.mainloop()