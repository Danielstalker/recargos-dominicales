import datetime

class Empleado:
    """
    Representa a un empleado con su información básica, tipo de contrato y horario estándar.
    """
    def __init__(self, nombre, salario_mensual, standard_daily_hours=8, tipo_contrato="indefinido"):
        self.nombre = nombre
        self.salario_mensual = salario_mensual
        self.standard_daily_hours = standard_daily_hours # Horas diarias estándar de trabajo
        self.tipo_contrato = tipo_contrato
        self.jornadas_registradas = [] # Lista de diccionarios para registrar jornadas (fecha, hora_entrada, hora_salida)

    def obtener_valor_hora_ordinaria(self):
        """Calcula el valor de la hora ordinaria basándose en el salario mensual."""
        # Se asume un mes laboral de 30 días y una jornada de 8 horas diarias (240 horas/mes)
        horas_mes = 30 * 8
        return self.salario_mensual / horas_mes

    def registrar_jornada(self, fecha, hora_entrada, hora_salida):
        """
        Registra una jornada laboral en un día específico con horas de entrada y salida.
        """
        self.jornadas_registradas.append({
            "fecha": fecha,
            "hora_entrada": hora_entrada,
            "hora_salida": hora_salida
        })
        return f"Jornada registrada para {self.nombre} el {fecha.strftime('%Y-%m-%d')} de {hora_entrada.strftime('%H:%M')} a {hora_salida.strftime('%H:%M')}."

class CalculadoraRecargos:
    """
    Clase para manejar la lógica de cálculo de recargos dominicales y festivos,
    así como la gestión de días festivos.
    """
    def __init__(self):
        # Porcentajes de recargo según la ley colombiana
        self.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO = 0.75
        self.PORCENTAJE_HORA_EXTRA_DIURNA = 0.25 # Recargo adicional sobre la hora ordinaria
        self.PORCENTAJE_HORA_EXTRA_NOCTURNA = 0.75 # Recargo adicional sobre la hora ordinaria (entre 9pm y 6am)
        self.PORCENTAJE_HORA_ORDINARIA_NOCTURNA = 0.35 # Para horas ordinarias nocturnas (no aplica en domingo/festivo)

        # Días festivos de Colombia (pueden ser actualizados manualmente o desde una API externa)
        # Formato: datetime.date(año, mes, día)
        self.dias_festivos = [
            datetime.date(2025, 1, 1), # Año Nuevo
            datetime.date(2025, 1, 6), # Día de Reyes Magos
            datetime.date(2025, 3, 24), # Día de San José
            datetime.date(2025, 4, 17), # Jueves Santo
            datetime.date(2025, 4, 18), # Viernes Santo
            datetime.date(2025, 5, 1), # Día del Trabajo
            datetime.date(2025, 6, 2), # Día de la Ascensión
            datetime.date(2025, 6, 23), # Corpus Christi
            datetime.date(2025, 6, 30), # Sagrado Corazón de Jesús
            datetime.date(2025, 7, 20), # Día de la Independencia
            datetime.date(2025, 8, 7), # Batalla de Boyacá
            datetime.date(2025, 8, 18), # Asunción de la Virgen
            datetime.date(2025, 10, 13), # Día de la Raza
            datetime.date(2025, 11, 3), # Día de Todos los Santos
            datetime.date(2025, 11, 17), # Independencia de Cartagena
            datetime.date(2025, 12, 8), # Día de la Inmaculada Concepción
            datetime.date(2025, 12, 25) # Navidad
        ]
        self.dias_festivos.sort()

    def es_festivo_o_domingo(self, fecha):
        """Verifica si una fecha dada es domingo o un día festivo."""
        # 6 es domingo (Monday=0, Sunday=6)
        return fecha.weekday() == 6 or fecha in self.dias_festivos

    def _categorize_shift_hours(self, empleado, fecha, hora_entrada, hora_salida):
        """
        Categoriza las horas de una jornada en ordinarias, extras, diurnas, nocturnas,
        y si son en domingo/festivo, basándose en el horario estándar del empleado.
        """
        dt_entrada = datetime.datetime.combine(fecha, hora_entrada)
        dt_salida = datetime.datetime.combine(fecha, hora_salida)

        # Manejar turnos que cruzan la medianoche
        if dt_salida < dt_entrada:
            dt_salida += datetime.timedelta(days=1)

        is_domingo_festivo = self.es_festivo_o_domingo(fecha)
        standard_daily_minutes = empleado.standard_daily_hours * 60

        categorized_minutes = {
            "horas_ordinarias": 0, # Día regular, horas ordinarias (diurnas)
            "horas_ordinarias_nocturnas": 0, # Día regular, horas ordinarias (nocturnas)
            "horas_extras_diurnas": 0, # Día regular, horas extras (diurnas)
            "horas_extras_nocturnas": 0, # Día regular, horas extras (nocturnas)
            "horas_ordinarias_domingo_festivo": 0, # Domingo/Festivo, horas ordinarias
            "horas_extras_diurnas_domingo_festivo": 0, # Domingo/Festivo, horas extras (diurnas)
            "horas_extras_nocturnas_domingo_festivo": 0 # Domingo/Festivo, horas extras (nocturnas)
        }

        current_dt = dt_entrada
        minutes_processed = 0

        while current_dt < dt_salida:
            minutes_processed += 1
            
            current_time = current_dt.time()
            # Determinar si este minuto es nocturno (entre 9 PM y 6 AM)
            is_nocturnal = (current_time >= datetime.time(21, 0) or current_time < datetime.time(6, 0))

            if is_domingo_festivo:
                if minutes_processed <= standard_daily_minutes: 
                    # Horas ordinarias en domingo/festivo (no se distingue diurna/nocturna para esta categoría base)
                    categorized_minutes["horas_ordinarias_domingo_festivo"] += 1
                else: 
                    # Horas extras en domingo/festivo
                    if is_nocturnal:
                        categorized_minutes["horas_extras_nocturnas_domingo_festivo"] += 1
                    else:
                        categorized_minutes["horas_extras_diurnas_domingo_festivo"] += 1
            else: # Día regular (no domingo/festivo)
                if minutes_processed <= standard_daily_minutes: 
                    # Horas ordinarias en día regular
                    if is_nocturnal:
                        categorized_minutes["horas_ordinarias_nocturnas"] += 1
                    else:
                        categorized_minutes["horas_ordinarias"] += 1
                else: 
                    # Horas extras en día regular
                    if is_nocturnal:
                        categorized_minutes["horas_extras_nocturnas"] += 1
                    else:
                        categorized_minutes["horas_extras_diurnas"] += 1
            
            current_dt += datetime.timedelta(minutes=1)

        # Convertir minutos a horas
        for key in categorized_minutes:
            categorized_minutes[key] /= 60.0

        return categorized_minutes

    def calcular_recargos_jornada(self, empleado, jornada):
        """
        Calcula el recargo total para una jornada específica de un empleado.
        Ahora utiliza la categorización de horas.
        """
        fecha = jornada["fecha"]
        hora_entrada = jornada["hora_entrada"]
        hora_salida = jornada["hora_salida"]

        # Obtener las horas categorizadas de la nueva función auxiliar
        categorized_hours = self._categorize_shift_hours(empleado, fecha, hora_entrada, hora_salida)

        valor_hora_ordinaria = empleado.obtener_valor_hora_ordinaria()
        recargo_total_jornada = 0.0
        horas_con_recargo_jornada = 0.0 # Usar float para acumular horas

        # Calcular recargos basados en las horas categorizadas
        
        # 1. Horas ordinarias nocturnas (días regulares)
        horas_ord_noct = categorized_hours["horas_ordinarias_nocturnas"]
        recargo_ord_noct = horas_ord_noct * valor_hora_ordinaria * self.PORCENTAJE_HORA_ORDINARIA_NOCTURNA
        recargo_total_jornada += recargo_ord_noct
        horas_con_recargo_jornada += horas_ord_noct

        # 2. Horas extras diurnas (días regulares)
        horas_ext_diur = categorized_hours["horas_extras_diurnas"]
        recargo_ext_diur = horas_ext_diur * valor_hora_ordinaria * self.PORCENTAJE_HORA_EXTRA_DIURNA
        recargo_total_jornada += recargo_ext_diur
        horas_con_recargo_jornada += horas_ext_diur

        # 3. Horas extras nocturnas (días regulares)
        horas_ext_noct = categorized_hours["horas_extras_nocturnas"]
        recargo_ext_noct = horas_ext_noct * valor_hora_ordinaria * self.PORCENTAJE_HORA_EXTRA_NOCTURNA
        recargo_total_jornada += recargo_ext_noct
        horas_con_recargo_jornada += horas_ext_noct

        # 4. Horas ordinarias en domingo/festivo
        horas_ord_df = categorized_hours["horas_ordinarias_domingo_festivo"]
        recargo_ord_df = horas_ord_df * valor_hora_ordinaria * self.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO
        recargo_total_jornada += recargo_ord_df
        horas_con_recargo_jornada += horas_ord_df

        # 5. Horas extras diurnas en domingo/festivo
        horas_ext_diur_df = categorized_hours["horas_extras_diurnas_domingo_festivo"]
        # El recargo es sobre el valor base, más el recargo dominical/festivo, más el recargo extra diurno
        recargo_ext_diur_df = horas_ext_diur_df * valor_hora_ordinaria * (self.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO + self.PORCENTAJE_HORA_EXTRA_DIURNA)
        recargo_total_jornada += recargo_ext_diur_df
        horas_con_recargo_jornada += horas_ext_diur_df

        # 6. Horas extras nocturnas en domingo/festivo
        horas_ext_noct_df = categorized_hours["horas_extras_nocturnas_domingo_festivo"]
        # El recargo es sobre el valor base, más el recargo dominical/festivo, más el recargo extra nocturno
        recargo_ext_noct_df = horas_ext_noct_df * valor_hora_ordinaria * (self.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO + self.PORCENTAJE_HORA_EXTRA_NOCTURNA)
        recargo_total_jornada += recargo_ext_noct_df
        horas_con_recargo_jornada += horas_ext_noct_df

        return recargo_total_jornada, horas_con_recargo_jornada, categorized_hours

    def generar_reporte_empleado(self, empleado):
        """Genera un reporte detallado para un empleado específico."""
        reporte_str = f"--- Reporte de Recargos para {empleado.nombre} ---\n"
        reporte_str += f"Salario Mensual: ${empleado.salario_mensual:,.2f}\n"
        reporte_str += f"Valor Hora Ordinaria: ${empleado.obtener_valor_hora_ordinaria():,.2f}\n"
        reporte_str += f"Horas Diarias Estándar: {empleado.standard_daily_hours} horas\n"
        reporte_str += "\nDetalle de Jornadas:\n"

        total_recargos_empleado = 0.0
        total_horas_con_recargo_empleado = 0.0
        
        # Acumuladores para el resumen de horas categorizadas
        acum_horas = {
            "horas_ordinarias": 0.0,
            "horas_ordinarias_nocturnas": 0.0,
            "horas_extras_diurnas": 0.0,
            "horas_extras_nocturnas": 0.0,
            "horas_ordinarias_domingo_festivo": 0.0,
            "horas_extras_diurnas_domingo_festivo": 0.0,
            "horas_extras_nocturnas_domingo_festivo": 0.0
        }

        if not empleado.jornadas_registradas:
            reporte_str += "No se han registrado jornadas para este empleado.\n"
            return reporte_str

        for jornada in empleado.jornadas_registradas:
            fecha = jornada["fecha"]
            hora_entrada = jornada["hora_entrada"]
            hora_salida = jornada["hora_salida"]

            recargo, horas_recargo, categorized_hours = self.calcular_recargos_jornada(empleado, jornada)
            
            reporte_str += f" Jornada del {fecha.strftime('%Y-%m-%d')} ({hora_entrada.strftime('%H:%M')} - {hora_salida.strftime('%H:%M')}):\n"
            reporte_str += f"   Horas Ordinarias (Diurnas): {categorized_hours['horas_ordinarias']:.2f}h\n"
            reporte_str += f"   Horas Ordinarias (Nocturnas): {categorized_hours['horas_ordinarias_nocturnas']:.2f}h\n"
            reporte_str += f"   Horas Extras (Diurnas): {categorized_hours['horas_extras_diurnas']:.2f}h\n"
            reporte_str += f"   Horas Extras (Nocturnas): {categorized_hours['horas_extras_nocturnas']:.2f}h\n"
            reporte_str += f"   Horas Ordinarias D/F: {categorized_hours['horas_ordinarias_domingo_festivo']:.2f}h\n"
            reporte_str += f"   Horas Extras Diurnas D/F: {categorized_hours['horas_extras_diurnas_domingo_festivo']:.2f}h\n"
            reporte_str += f"   Horas Extras Nocturnas D/F: {categorized_hours['horas_extras_nocturnas_domingo_festivo']:.2f}h\n"
            reporte_str += f"   Recargo Calculado para esta jornada: ${recargo:,.2f}\n"
            reporte_str += f"   Horas que generaron recargo en esta jornada: {horas_recargo:.2f}h\n"
            reporte_str += "-----------------------------------------------------\n"

            total_recargos_empleado += recargo
            total_horas_con_recargo_empleado += horas_recargo

            for key, value in categorized_hours.items():
                acum_horas[key] += value

        reporte_str += f"\n--- Resumen de Horas Acumuladas para {empleado.nombre} ---\n"
        reporte_str += f"Total Horas Ordinarias (Diurnas): {acum_horas['horas_ordinarias']:.2f}h\n"
        reporte_str += f"Total Horas Ordinarias (Nocturnas): {acum_horas['horas_ordinarias_nocturnas']:.2f}h\n"
        reporte_str += f"Total Horas Extras (Diurnas): {acum_horas['horas_extras_diurnas']:.2f}h\n"
        reporte_str += f"Total Horas Extras (Nocturnas): {acum_horas['horas_extras_nocturnas']:.2f}h\n"
        reporte_str += f"Total Horas Ordinarias D/F: {acum_horas['horas_ordinarias_domingo_festivo']:.2f}h\n"
        reporte_str += f"Total Horas Extras Diurnas D/F: {acum_horas['horas_extras_diurnas_domingo_festivo']:.2f}h\n"
        reporte_str += f"Total Horas Extras Nocturnas D/F: {acum_horas['horas_extras_nocturnas_domingo_festivo']:.2f}h\n"

        reporte_str += f"\nTotal Recargos Acumulados para {empleado.nombre}: ${total_recargos_empleado:,.2f}\n"
        reporte_str += f"Total Horas con Recargo para {empleado.nombre}: {total_horas_con_recargo_empleado:.2f} horas\n"
        reporte_str += "-----------------------------------------------------\n"
        return reporte_str

    def generar_reporte_consolidado(self, lista_empleados, periodo_inicio=None, periodo_fin=None):
        """
        Genera un reporte consolidado de recargos para todos los empleados
        en un período dado.
        """
        reporte_str = "--- Reporte Consolidado de Recargos ---\n"
        if periodo_inicio and periodo_fin:
            reporte_str += f"Período: {periodo_inicio.strftime('%Y-%m-%d')} a {periodo_fin.strftime('%Y-%m-%d')}\n"
        elif periodo_inicio:
            reporte_str += f"Período: Desde {periodo_inicio.strftime('%Y-%m-%d')}\n"
        elif periodo_fin:
            reporte_str += f"Período: Hasta {periodo_fin.strftime('%Y-%m-%d')}\n"
        reporte_str += "\n"

        total_general_recargos = 0.0
        total_general_horas_con_recargo = 0.0
        
        acum_horas_general = {
            "horas_ordinarias": 0.0,
            "horas_ordinarias_nocturnas": 0.0,
            "horas_extras_diurnas": 0.0,
            "horas_extras_nocturnas": 0.0,
            "horas_ordinarias_domingo_festivo": 0.0,
            "horas_extras_diurnas_domingo_festivo": 0.0,
            "horas_extras_nocturnas_domingo_festivo": 0.0
        }

        if not lista_empleados:
            return "No hay empleados registrados para generar un reporte consolidado."

        for empleado in lista_empleados:
            recargos_empleado_periodo = 0.0
            horas_empleado_periodo = 0.0
            
            acum_horas_empleado_periodo = {
                "horas_ordinarias": 0.0,
                "horas_ordinarias_nocturnas": 0.0,
                "horas_extras_diurnas": 0.0,
                "horas_extras_nocturnas": 0.0,
                "horas_ordinarias_domingo_festivo": 0.0,
                "horas_extras_diurnas_domingo_festivo": 0.0,
                "horas_extras_nocturnas_domingo_festivo": 0.0
            }

            for jornada in empleado.jornadas_registradas:
                fecha_jornada = jornada["fecha"]
                if (periodo_inicio is None or fecha_jornada >= periodo_inicio) and \
                   (periodo_fin is None or fecha_jornada <= periodo_fin):
                    
                    recargo, horas_con_recargo, categorized_hours = self.calcular_recargos_jornada(empleado, jornada)
                    recargos_empleado_periodo += recargo
                    horas_empleado_periodo += horas_con_recargo
                    
                    for key, value in categorized_hours.items():
                        acum_horas_empleado_periodo[key] += value

            if recargos_empleado_periodo > 0 or any(v > 0 for v in acum_horas_empleado_periodo.values()):
                reporte_str += f" Empleado: {empleado.nombre}\n"
                reporte_str += f"   Horas Ordinarias (Diurnas): {acum_horas_empleado_periodo['horas_ordinarias']:.2f}h\n"
                reporte_str += f"   Horas Ordinarias (Nocturnas): {acum_horas_empleado_periodo['horas_ordinarias_nocturnas']:.2f}h\n"
                reporte_str += f"   Horas Extras (Diurnas): {acum_horas_empleado_periodo['horas_extras_diurnas']:.2f}h\n"
                reporte_str += f"   Horas Extras (Nocturnas): {acum_horas_empleado_periodo['horas_extras_nocturnas']:.2f}h\n"
                reporte_str += f"   Horas Ordinarias D/F: {acum_horas_empleado_periodo['horas_ordinarias_domingo_festivo']:.2f}h\n"
                reporte_str += f"   Horas Extras Diurnas D/F: {acum_horas_empleado_periodo['horas_extras_diurnas_domingo_festivo']:.2f}h\n"
                reporte_str += f"   Horas Extras Nocturnas D/F: {acum_horas_empleado_periodo['horas_extras_nocturnas_domingo_festivo']:.2f}h\n"
                reporte_str += f"   Recargos en el período: ${recargos_empleado_periodo:,.2f}\n"
                reporte_str += f"   Horas con recargo en el período: {horas_empleado_periodo:.2f} horas\n\n"
                
                total_general_recargos += recargos_empleado_periodo
                total_general_horas_con_recargo += horas_empleado_periodo
                
                for key, value in acum_horas_empleado_periodo.items():
                    acum_horas_general[key] += value

        if total_general_recargos == 0 and all(v == 0 for v in acum_horas_general.values()):
            reporte_str += "No se encontraron recargos ni horas trabajadas en el período especificado para ningún empleado.\n"
        else:
            reporte_str += f"\n--- Resumen General de Horas Acumuladas para la Empresa ---\n"
            reporte_str += f"Total Horas Ordinarias (Diurnas): {acum_horas_general['horas_ordinarias']:.2f}h\n"
            reporte_str += f"Total Horas Ordinarias (Nocturnas): {acum_horas_general['horas_ordinarias_nocturnas']:.2f}h\n"
            reporte_str += f"Total Horas Extras (Diurnas): {acum_horas_general['horas_extras_diurnas']:.2f}h\n"
            reporte_str += f"Total Horas Extras (Nocturnas): {acum_horas_general['horas_extras_nocturnas']:.2f}h\n"
            reporte_str += f"Total Horas Ordinarias D/F: {acum_horas_general['horas_ordinarias_domingo_festivo']:.2f}h\n"
            reporte_str += f"Total Horas Extras Diurnas D/F: {acum_horas_general['horas_extras_diurnas_domingo_festivo']:.2f}h\n"
            reporte_str += f"Total Horas Extras Nocturnas D/F: {acum_horas_general['horas_extras_nocturnas_domingo_festivo']:.2f}h\n"

            reporte_str += f"\nTotal General de Recargos para la Empresa: ${total_general_recargos:,.2f}\n"
            reporte_str += f"Total General de Horas con Recargo para la Empresa: {total_general_horas_con_recargo:.2f} horas\n"
        reporte_str += "---------------------------------------------\n"
        return reporte_str

    def agregar_dia_festivo(self, fecha):
        """Agrega una fecha a la lista de días festivos."""
        if not isinstance(fecha, datetime.date):
            raise ValueError("La fecha debe ser un objeto datetime.date.")
        if fecha not in self.dias_festivos:
            self.dias_festivos.append(fecha)
            self.dias_festivos.sort() # Mantener la lista ordenada
            return f"Día festivo {fecha.strftime('%Y-%m-%d')} agregado."
        else:
            return f"El día {fecha.strftime('%Y-%m-%d')} ya está en la lista de festivos."

    def eliminar_dia_festivo(self, fecha):
        """Elimina una fecha de la lista de días festivos."""
        if fecha in self.dias_festivos:
            self.dias_festivos.remove(fecha)
            return f"Día festivo {fecha.strftime('%Y-%m-%d')} eliminado."
        else:
            return f"El día {fecha.strftime('%Y-%m-%d')} no se encontró en la lista de festivos."

    def actualizar_porcentajes_recargo(self, nuevo_porcentaje_dominical=None,
                                       nuevo_porcentaje_extra_diurna=None,
                                       nuevo_porcentaje_extra_nocturna=None,
                                       nuevo_porcentaje_ordinaria_nocturna=None): # Nuevo parámetro
        """
        Permite actualizar los porcentajes de recargo.
        """
        mensajes = []
        if nuevo_porcentaje_dominical is not None:
            self.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO = nuevo_porcentaje_dominical / 100
            mensajes.append(f"Porcentaje de recargo dominical/festivo actualizado a {nuevo_porcentaje_dominical}%.")
        if nuevo_porcentaje_extra_diurna is not None:
            self.PORCENTAJE_HORA_EXTRA_DIURNA = nuevo_porcentaje_extra_diurna / 100
            mensajes.append(f"Porcentaje de hora extra diurna actualizado a {nuevo_porcentaje_extra_diurna}%.")
        if nuevo_porcentaje_extra_nocturna is not None:
            self.PORCENTAJE_HORA_EXTRA_NOCTURNA = nuevo_porcentaje_extra_nocturna / 100
            mensajes.append(f"Porcentaje de hora extra nocturna actualizado a {nuevo_porcentaje_extra_nocturna}%.")
        if nuevo_porcentaje_ordinaria_nocturna is not None: # Nuevo porcentaje
            self.PORCENTAJE_HORA_ORDINARIA_NOCTURNA = nuevo_porcentaje_ordinaria_nocturna / 100
            mensajes.append(f"Porcentaje de hora ordinaria nocturna actualizado a {nuevo_porcentaje_ordinaria_nocturna}%.")
        return "\n".join(mensajes) if mensajes else "Ningún porcentaje fue actualizado."