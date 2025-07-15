import datetime
import json
import os

class Empleado:
    """
    Representa a un empleado con su información básica, tipo de contrato y horario estándar.
    El valor de la hora ordinaria se calcula a partir del salario mensual.
    """
    def __init__(self, nombre, salario_mensual, standard_daily_hours=8, tipo_contrato="indefinido"):
        self.nombre = nombre
        self.salario_mensual = salario_mensual
        self.standard_daily_hours = standard_daily_hours # Horas diarias estándar de trabajo
        self.tipo_contrato = tipo_contrato
        self.jornadas_registradas = [] # Lista de diccionarios para registrar jornadas (fecha, hora_entrada, hora_salida)

    def obtener_valor_hora_ordinaria(self):
        """Calcula el valor de la hora ordinaria basándose en el salario mensual (sueldo / 220 horas)."""
        if self.salario_mensual <= 0:
            return 0.0
        return self.salario_mensual / 220 # Sueldo / 220 horas como valor de la hora ordinaria

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

    def to_dict(self):
        """Convierte el objeto Empleado a un diccionario para serialización JSON."""
        jornadas_dicts = []
        for jornada in self.jornadas_registradas:
            jornadas_dicts.append({
                "fecha": jornada["fecha"].isoformat(), # Convert date to string (YYYY-MM-DD)
                "hora_entrada": jornada["hora_entrada"].isoformat(), # Convert time to string (HH:MM:SS.ffffff)
                "hora_salida": jornada["hora_salida"].isoformat() # Convert time to string (HH:MM:SS.ffffff)
            })
        return {
            "nombre": self.nombre,
            "salario_mensual": self.salario_mensual,
            "standard_daily_hours": self.standard_daily_hours,
            "tipo_contrato": self.tipo_contrato,
            "jornadas_registradas": jornadas_dicts
        }

    @staticmethod
    def from_dict(data):
        """Crea un objeto Empleado desde un diccionario (deserialización JSON)."""
        empleado = Empleado(
            data["nombre"],
            data["salario_mensual"],
            data["standard_daily_hours"],
            data["tipo_contrato"]
        )
        empleado.jornadas_registradas = []
        for jornada_dict in data["jornadas_registradas"]:
            empleado.jornadas_registradas.append({
                "fecha": datetime.date.fromisoformat(jornada_dict["fecha"]), # Convert string to date
                "hora_entrada": datetime.time.fromisoformat(jornada_dict["hora_entrada"]), # Convert string to time
                "hora_salida": datetime.time.fromisoformat(jornada_dict["hora_salida"]) # Convert string to time
            })
        return empleado

class CalculadoraRecargos:
    """
    Clase para manejar la lógica de cálculo de recargos,
    distinguiendo entre domingos y días festivos.
    Los porcentajes de recargo son ahora MULTIPLICADORES TOTALES sobre el valor de la hora ordinaria.
    Ejemplo: Un multiplicador de 1.25 para "Hora extra diurna" significa que se paga el 125% del valor de la hora ordinaria.
    """
    def __init__(self):
        # Multiplicadores de recargo según la tabla proporcionada (VALOR TOTAL sobre la hora ordinaria)
        self.MULTIPLIER_HORA_EXTRA_DIURNA = 1.25 # Hora extra diurna 125%
        self.MULTIPLIER_HORA_EXTRA_NOCTURNA = 1.75 # Horas extras Nocturnas 175%
        self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO = 2.00 # Horas extras diurnas dominicales o festivas 200%
        self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO = 2.50 # Horas extras Noctur Dom o Festivas 250%
        
        # Para los recargos, la tabla muestra el porcentaje ADICIONAL. Lo convertimos a multiplicador total.
        self.MULTIPLIER_HORA_ORDINARIA_NOCTURNA = 1.00 + (35 / 100) # Recargo Nocturno 35% -> 135% total
        self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE = 1.00 + (80 / 100) # Recargo dominical o festivo diurno no compensado (<22h) 80% -> 180% total
        self.MULTIPLIER_ORDINARIA_NOCTURNA_DOMINGOFESTIVO = 1.00 + (110 / 100) # Recargo Nocturno Dominical o festivo 110% -> 210% total
        self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA = 1.00 + (180 / 100) # Recargo dominical o festivo diurno no compensado (>=23h) 180% -> 280% total
        self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA = 1.00 + (210 / 100) # Recargo Dominical o Festivo nocturno no compensado 210% -> 310% total

        # Días festivos de Colombia (pueden ser actualizados manualmente o desde una API externa)
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

    def es_domingo(self, fecha):
        """Verifica si una fecha dada es domingo."""
        return fecha.weekday() == 6 # 6 es domingo (Monday=0, Sunday=6)

    def es_festivo(self, fecha):
        """Verifica si una fecha dada es un día festivo."""
        return fecha in self.dias_festivos

    def _categorize_shift_hours(self, empleado, fecha, hora_entrada, hora_salida):
        """
        Categoriza las horas de una jornada en ordinarias, extras, diurnas, nocturnas,
        y si son en domingo o festivo (separadamente), basándose en el horario estándar del empleado.
        """
        dt_entrada = datetime.datetime.combine(fecha, hora_entrada)
        dt_salida = datetime.datetime.combine(fecha, hora_salida)

        # Manejar turnos que cruzan la medianoche
        if dt_salida < dt_entrada:
            dt_salida += datetime.timedelta(days=1)

        standard_daily_minutes = empleado.standard_daily_hours * 60

        # Categorías de horas separadas para Domingo y Festivo
        categorized_minutes = {
            "horas_ordinarias_diurnas": 0,       # Día regular (no D/F), diurnas, ordinarias
            "horas_ordinarias_nocturnas": 0,     # Día regular (no D/F), nocturnas, ordinarias
            "horas_extras_diurnas": 0,           # Día regular (no D/F), diurnas, extras
            "horas_extras_nocturnas": 0,         # Día regular (no D/F), nocturnas, extras
            
            # Categorías para Domingo
            "horas_ordinarias_diurnas_domingo": 0,
            "horas_ordinarias_nocturnas_domingo": 0,
            "horas_extras_diurnas_domingo": 0,
            "horas_extras_nocturnas_domingo": 0,

            # Categorías para Festivo
            "horas_ordinarias_diurnas_festivo": 0,
            "horas_ordinarias_nocturnas_festivo": 0,
            "horas_extras_diurnas_festivo": 0,
            "horas_extras_nocturnas_festivo": 0,
        }

        current_dt = dt_entrada
        minutes_processed = 0

        while current_dt < dt_salida:
            minutes_processed += 1
            
            current_time = current_dt.time()
            # Determinar si este minuto es nocturno (entre 9 PM y 6 AM)
            is_nocturnal = (current_time >= datetime.time(21, 0) or current_time < datetime.time(6, 0))

            is_domingo_actual = current_dt.weekday() == 6 # 6 es domingo
            is_festivo_actual = current_dt.date() in self.dias_festivos

            if is_festivo_actual: # Priorizar festivo si es ambos (domingo y festivo)
                if minutes_processed <= standard_daily_minutes:
                    if is_nocturnal:
                        categorized_minutes["horas_ordinarias_nocturnas_festivo"] += 1
                    else:
                        categorized_minutes["horas_ordinarias_diurnas_festivo"] += 1
                else: # Horas extras en festivo
                    if is_nocturnal:
                        categorized_minutes["horas_extras_nocturnas_festivo"] += 1
                    else:
                        categorized_minutes["horas_extras_diurnas_festivo"] += 1
            elif is_domingo_actual: # Es domingo, pero no festivo
                if minutes_processed <= standard_daily_minutes:
                    if is_nocturnal:
                        categorized_minutes["horas_ordinarias_nocturnas_domingo"] += 1
                    else:
                        categorized_minutes["horas_ordinarias_diurnas_domingo"] += 1
                else: # Horas extras en domingo
                    if is_nocturnal:
                        categorized_minutes["horas_extras_nocturnas_domingo"] += 1
                    else:
                        categorized_minutes["horas_extras_diurnas_domingo"] += 1
            else: # Día regular (no domingo ni festivo)
                if minutes_processed <= standard_daily_minutes:
                    if is_nocturnal:
                        categorized_minutes["horas_ordinarias_nocturnas"] += 1
                    else:
                        categorized_minutes["horas_ordinarias_diurnas"] += 1
                else: # Horas extras en día regular
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
        Calcula el valor total de la jornada (base + recargos adicionales)
        y el valor monetario de los recargos adicionales para cada tipo de hora.
        La fórmula general para el valor bruto es:
        horas_categorizadas * valor_hora_ordinaria * MULTIPLICADOR
        El valor de recargo adicional es:
        horas_categorizadas * valor_hora_ordinaria * (MULTIPLIER - 1)
        """
        fecha = jornada["fecha"]
        hora_entrada = jornada["hora_entrada"]
        hora_salida = jornada["hora_salida"]

        dt_entrada = datetime.datetime.combine(fecha, hora_entrada)
        dt_salida = datetime.datetime.combine(fecha, hora_salida)
        if dt_salida < dt_entrada: # Manejar turnos que cruzan la medianoche para calcular la duración
            dt_salida += datetime.timedelta(days=1)
        
        total_shift_duration = dt_salida - dt_entrada
        total_shift_hours = total_shift_duration.total_seconds() / 3600.0


        categorized_hours = self._categorize_shift_hours(empleado, fecha, hora_entrada, hora_salida)
        valor_hora_ordinaria = empleado.obtener_valor_hora_ordinaria()
        
        total_gross_value_jornada = 0.0 # Suma del valor total (base + recargos)
        total_surcharge_value_jornada = 0.0 # Suma de solo los recargos adicionales
        
        # Diccionario para almacenar solo el VALOR DEL RECARGO ADICIONAL por categoría
        categorized_surcharge_values = { 
            "horas_ordinarias_diurnas": 0.0, # No hay recargo adicional para estas
            "horas_ordinarias_nocturnas": 0.0,
            "horas_extras_diurnas": 0.0,
            "horas_extras_nocturnas": 0.0,
            
            "horas_ordinarias_diurnas_domingo": 0.0,
            "horas_ordinarias_nocturnas_domingo": 0.0,
            "horas_extras_diurnas_domingo": 0.0,
            "horas_extras_nocturnas_domingo": 0.0,

            "horas_ordinarias_diurnas_festivo": 0.0,
            "horas_ordinarias_nocturnas_festivo": 0.0,
            "horas_extras_diurnas_festivo": 0.0,
            "horas_extras_nocturnas_festivo": 0.0,
        }

        # 1. Horas ordinarias diurnas (días regulares) - Multiplicador 1.00 (100%)
        total_gross_value_jornada += categorized_hours["horas_ordinarias_diurnas"] * valor_hora_ordinaria * 1.00

        # 2. Horas ordinarias nocturnas (días regulares)
        if categorized_hours["horas_ordinarias_nocturnas"] > 0:
            gross_amount = categorized_hours["horas_ordinarias_nocturnas"] * valor_hora_ordinaria * self.MULTIPLIER_HORA_ORDINARIA_NOCTURNA
            surcharge_amount = gross_amount - (categorized_hours["horas_ordinarias_nocturnas"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_ordinarias_nocturnas"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount
            
        # 3. Horas extras diurnas (días regulares)
        if categorized_hours["horas_extras_diurnas"] > 0:
            gross_amount = categorized_hours["horas_extras_diurnas"] * valor_hora_ordinaria * self.MULTIPLIER_HORA_EXTRA_DIURNA
            surcharge_amount = gross_amount - (categorized_hours["horas_extras_diurnas"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_extras_diurnas"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # 4. Horas extras nocturnas (días regulares)
        if categorized_hours["horas_extras_nocturnas"] > 0:
            gross_amount = categorized_hours["horas_extras_nocturnas"] * valor_hora_ordinaria * self.MULTIPLIER_HORA_EXTRA_NOCTURNA
            surcharge_amount = gross_amount - (categorized_hours["horas_extras_nocturnas"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_extras_nocturnas"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # --- Cálculos para Horas en Domingo ---
        # 5. Horas ordinarias diurnas en Domingo -> Multiplicador condicional
        if categorized_hours["horas_ordinarias_diurnas_domingo"] > 0:
            if total_shift_hours < 22: # Menos de 22 horas
                multiplier = self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE # 1.80
            elif total_shift_hours >= 23: # 23 horas o más
                multiplier = self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA # 2.80
            else: # Para 22 horas exactas, o si hay un rango entre 22 y 23
                # Puedes definir un comportamiento específico para 22 horas si es necesario,
                # por ahora, usaremos el valor base si no cumple las otras condiciones.
                multiplier = self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE # O un valor por defecto
            
            gross_amount = categorized_hours["horas_ordinarias_diurnas_domingo"] * valor_hora_ordinaria * multiplier
            surcharge_amount = gross_amount - (categorized_hours["horas_ordinarias_diurnas_domingo"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_ordinarias_diurnas_domingo"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # 6. Horas ordinarias nocturnas en Domingo -> Multiplicador condicional
        if categorized_hours["horas_ordinarias_nocturnas_domingo"] > 0:
            if total_shift_hours >= 23:
                multiplier = self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA # 3.10
            else:
                multiplier = self.MULTIPLIER_ORDINARIA_NOCTURNA_DOMINGOFESTIVO # 2.10
            
            gross_amount = categorized_hours["horas_ordinarias_nocturnas_domingo"] * valor_hora_ordinaria * multiplier
            surcharge_amount = gross_amount - (categorized_hours["horas_ordinarias_nocturnas_domingo"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_ordinarias_nocturnas_domingo"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # 7. Horas extras diurnas en Domingo
        if categorized_hours["horas_extras_diurnas_domingo"] > 0:
            gross_amount = categorized_hours["horas_extras_diurnas_domingo"] * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO # 2.00
            surcharge_amount = gross_amount - (categorized_hours["horas_extras_diurnas_domingo"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_extras_diurnas_domingo"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # 8. Horas extras nocturnas en Domingo
        if categorized_hours["horas_extras_nocturnas_domingo"] > 0:
            gross_amount = categorized_hours["horas_extras_nocturnas_domingo"] * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO # 2.50
            surcharge_amount = gross_amount - (categorized_hours["horas_extras_nocturnas_domingo"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_extras_nocturnas_domingo"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # --- Cálculos para Horas en Festivo (same logic as Domingo) ---
        # 9. Horas ordinarias diurnas en Festivo
        if categorized_hours["horas_ordinarias_diurnas_festivo"] > 0:
            if total_shift_hours < 22: # Menos de 22 horas
                multiplier = self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE # 1.80
            elif total_shift_hours >= 23: # 23 horas o más
                multiplier = self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA # 2.80
            else: # Para 22 horas exactas, o si hay un rango entre 22 y 23
                multiplier = self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE # O un valor por defecto
            
            gross_amount = categorized_hours["horas_ordinarias_diurnas_festivo"] * valor_hora_ordinaria * multiplier
            surcharge_amount = gross_amount - (categorized_hours["horas_ordinarias_diurnas_festivo"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_ordinarias_diurnas_festivo"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # 10. Horas ordinarias nocturnas en Festivo
        if categorized_hours["horas_ordinarias_nocturnas_festivo"] > 0:
            if total_shift_hours >= 23:
                multiplier = self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA # 3.10
            else:
                multiplier = self.MULTIPLIER_ORDINARIA_NOCTURNA_DOMINGOFESTIVO # 2.10
            
            gross_amount = categorized_hours["horas_ordinarias_nocturnas_festivo"] * valor_hora_ordinaria * multiplier
            surcharge_amount = gross_amount - (categorized_hours["horas_ordinarias_nocturnas_festivo"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_ordinarias_nocturnas_festivo"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # 11. Horas extras diurnas en Festivo
        if categorized_hours["horas_extras_diurnas_festivo"] > 0:
            gross_amount = categorized_hours["horas_extras_diurnas_festivo"] * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO # 2.00
            surcharge_amount = gross_amount - (categorized_hours["horas_extras_diurnas_festivo"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_extras_diurnas_festivo"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # 12. Horas extras nocturnas en Festivo
        if categorized_hours["horas_extras_nocturnas_festivo"] > 0:
            gross_amount = categorized_hours["horas_extras_nocturnas_festivo"] * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO # 2.50
            surcharge_amount = gross_amount - (categorized_hours["horas_extras_nocturnas_festivo"] * valor_hora_ordinaria)
            categorized_surcharge_values["horas_extras_nocturnas_festivo"] = surcharge_amount
            total_surcharge_value_jornada += surcharge_amount
            total_gross_value_jornada += gross_amount

        # Horas que generaron recargo (suma de horas en categorías con recargo)
        horas_con_recargo_jornada = (
            categorized_hours["horas_ordinarias_nocturnas"] +
            categorized_hours["horas_extras_diurnas"] +
            categorized_hours["horas_extras_nocturnas"] +
            
            categorized_hours["horas_ordinarias_diurnas_domingo"] +
            categorized_hours["horas_ordinarias_nocturnas_domingo"] +
            categorized_hours["horas_extras_diurnas_domingo"] +
            categorized_hours["horas_extras_nocturnas_domingo"] +

            categorized_hours["horas_ordinarias_diurnas_festivo"] +
            categorized_hours["horas_ordinarias_nocturnas_festivo"] +
            categorized_hours["horas_extras_diurnas_festivo"] +
            categorized_hours["horas_extras_nocturnas_festivo"]
        )

        return total_gross_value_jornada, horas_con_recargo_jornada, categorized_hours, categorized_surcharge_values

    def generar_reporte_empleado(self, empleado):
        """Genera un reporte detallado para un empleado específico, incluyendo acumulados por tipo de hora y su valor de recargo."""
        reporte_str = f"--- Reporte de Recargos para {empleado.nombre} ---\n"
        reporte_str += f"Salario Mensual: ${empleado.salario_mensual:,.2f}\n"
        reporte_str += f"Valor Hora Ordinaria (Sueldo/220): ${empleado.obtener_valor_hora_ordinaria():,.2f}\n"
        reporte_str += f"Horas Diarias Estándar: {empleado.standard_daily_hours} horas\n"
        reporte_str += "\nDetalle de Jornadas:\n"

        total_general_valor_empleado = 0.0 # Acumula el valor TOTAL (base + recargos)
        total_general_recargo_adicional_empleado = 0.0 # Acumula solo los recargos adicionales
        total_horas_con_recargo_empleado = 0.0
        
        # Acumuladores para el resumen de horas y valores de recargo categorizados
        acum_horas = {
            "horas_ordinarias_diurnas": 0.0,
            "horas_ordinarias_nocturnas": 0.0,
            "horas_extras_diurnas": 0.0,
            "horas_extras_nocturnas": 0.0,
            
            "horas_ordinarias_diurnas_domingo": 0.0,
            "horas_ordinarias_nocturnas_domingo": 0.0,
            "horas_extras_diurnas_domingo": 0.0,
            "horas_extras_nocturnas_domingo": 0.0,

            "horas_ordinarias_diurnas_festivo": 0.0,
            "horas_ordinarias_nocturnas_festivo": 0.0,
            "horas_extras_diurnas_festivo": 0.0,
            "horas_extras_nocturnas_festivo": 0.0,
        }
        acum_surcharge_values = { # Esto almacenará el VALOR DEL RECARGO ADICIONAL
            "horas_ordinarias_diurnas": 0.0,
            "horas_ordinarias_nocturnas": 0.0,
            "horas_extras_diurnas": 0.0,
            "horas_extras_nocturnas": 0.0,
            
            "horas_ordinarias_diurnas_domingo": 0.0,
            "horas_ordinarias_nocturnas_domingo": 0.0,
            "horas_extras_diurnas_domingo": 0.0,
            "horas_extras_nocturnas_domingo": 0.0,

            "horas_ordinarias_diurnas_festivo": 0.0,
            "horas_ordinarias_nocturnas_festivo": 0.0,
            "horas_extras_diurnas_festivo": 0.0,
            "horas_extras_nocturnas_festivo": 0.0,
        }


        if not empleado.jornadas_registradas:
            reporte_str += "No se han registrado jornadas para este empleado.\n"
            return reporte_str

        for jornada in empleado.jornadas_registradas:
            fecha = jornada["fecha"]
            hora_entrada = jornada["hora_entrada"]
            hora_salida = jornada["hora_salida"]

            total_gross_value_jornada, horas_recargo, categorized_hours, categorized_surcharge_values = self.calcular_recargos_jornada(empleado, jornada)
            
            reporte_str += f" Jornada del {fecha.strftime('%Y-%m-%d')} ({hora_entrada.strftime('%I:%M %p')} - {hora_salida.strftime('%I:%M %p')}):\n"
            
            # Imprimir horas y su valor de recargo
            if categorized_hours["horas_ordinarias_diurnas"] > 0:
                base_value_for_ord_diur = categorized_hours['horas_ordinarias_diurnas'] * empleado.obtener_valor_hora_ordinaria()
                reporte_str += f"   Horas Ordinarias Diurnas: {categorized_hours['horas_ordinarias_diurnas']:.2f}h (Valor Base: ${base_value_for_ord_diur:,.2f})\n"
            if categorized_hours["horas_ordinarias_nocturnas"] > 0:
                reporte_str += f"   Horas Ordinarias Nocturnas: {categorized_hours['horas_ordinarias_nocturnas']:.2f}h (Recargo: ${categorized_surcharge_values['horas_ordinarias_nocturnas']:,.2f})\n"
            if categorized_hours["horas_extras_diurnas"] > 0:
                reporte_str += f"   Horas Extras Diurnas: {categorized_hours['horas_extras_diurnas']:.2f}h (Recargo: ${categorized_surcharge_values['horas_extras_diurnas']:,.2f})\n"
            if categorized_hours["horas_extras_nocturnas"] > 0:
                reporte_str += f"   Horas Extras Nocturnas: {categorized_hours['horas_extras_nocturnas']:.2f}h (Recargo: ${categorized_surcharge_values['horas_extras_nocturnas']:,.2f})\n"
            
            # Reporte para Domingo
            if categorized_hours["horas_ordinarias_diurnas_domingo"] > 0:
                reporte_str += f"   Horas Ordinarias Diurnas Domingo: {categorized_hours['horas_ordinarias_diurnas_domingo']:.2f}h (Recargo: ${categorized_surcharge_values['horas_ordinarias_diurnas_domingo']:,.2f})\n"
            if categorized_hours["horas_ordinarias_nocturnas_domingo"] > 0:
                reporte_str += f"   Horas Ordinarias Nocturnas Domingo: {categorized_hours['horas_ordinarias_nocturnas_domingo']:.2f}h (Recargo: ${categorized_surcharge_values['horas_ordinarias_nocturnas_domingo']:,.2f})\n"
            if categorized_hours["horas_extras_diurnas_domingo"] > 0:
                reporte_str += f"   Horas Extras Diurnas Domingo: {categorized_hours['horas_extras_diurnas_domingo']:.2f}h (Recargo: ${categorized_surcharge_values['horas_extras_diurnas_domingo']:,.2f})\n"
            if categorized_hours["horas_extras_nocturnas_domingo"] > 0:
                reporte_str += f"   Horas Extras Nocturnas Domingo: {categorized_hours['horas_extras_nocturnas_domingo']:.2f}h (Recargo: ${categorized_surcharge_values['horas_extras_nocturnas_domingo']:,.2f})\n"

            # Reporte para Festivo
            if categorized_hours["horas_ordinarias_diurnas_festivo"] > 0:
                reporte_str += f"   Horas Ordinarias Diurnas Festivo: {categorized_hours['horas_ordinarias_diurnas_festivo']:.2f}h (Recargo: ${categorized_surcharge_values['horas_ordinarias_diurnas_festivo']:,.2f})\n"
            if categorized_hours["horas_ordinarias_nocturnas_festivo"] > 0:
                reporte_str += f"   Horas Ordinarias Nocturnas Festivo: {categorized_hours['horas_ordinarias_nocturnas_festivo']:.2f}h (Recargo: ${categorized_surcharge_values['horas_ordinarias_nocturnas_festivo']:,.2f})\n"
            if categorized_hours["horas_extras_diurnas_festivo"] > 0:
                reporte_str += f"   Horas Extras Diurnas Festivo: {categorized_hours['horas_extras_diurnas_festivo']:.2f}h (Recargo: ${categorized_surcharge_values['horas_extras_diurnas_festivo']:,.2f})\n"
            if categorized_hours["horas_extras_nocturnas_festivo"] > 0:
                reporte_str += f"   Horas Extras Nocturnas Festivo: {categorized_hours['horas_extras_nocturnas_festivo']:.2f}h (Recargo: ${categorized_surcharge_values['horas_extras_nocturnas_festivo']:,.2f})\n"
            
            reporte_str += f"   Valor Total de la Jornada: ${total_gross_value_jornada:,.2f}\n"
            reporte_str += f"   Horas que generaron recargo en esta jornada: {horas_recargo:.2f}h\n"
            reporte_str += "-----------------------------------------------------\n"

            total_general_valor_empleado += total_gross_value_jornada 
            total_general_recargo_adicional_empleado += sum(categorized_surcharge_values.values()) # Sumar solo los recargos adicionales
            total_horas_con_recargo_empleado += horas_recargo

            for key, value in categorized_hours.items():
                acum_horas[key] += value
            for key, value in categorized_surcharge_values.items():
                acum_surcharge_values[key] += value

        reporte_str += f"\n--- Resumen de Horas y Recargos Acumulados para {empleado.nombre} ---\n"
        # Mostrar el valor base de las horas ordinarias diurnas acumuladas
        if acum_horas["horas_ordinarias_diurnas"] > 0:
            base_value_for_total_ord_diur = acum_horas['horas_ordinarias_diurnas'] * empleado.obtener_valor_hora_ordinaria()
            reporte_str += f"Total Horas Ordinarias Diurnas: {acum_horas['horas_ordinarias_diurnas']:.2f}h (Valor Base: ${base_value_for_total_ord_diur:,.2f})\n"
        if acum_horas["horas_ordinarias_nocturnas"] > 0:
            reporte_str += f"Total Horas Ordinarias Nocturnas: {acum_horas['horas_ordinarias_nocturnas']:.2f}h (Recargo: ${acum_surcharge_values['horas_ordinarias_nocturnas']:,.2f})\n"
        if acum_horas["horas_extras_diurnas"] > 0:
            reporte_str += f"Total Horas Extras Diurnas: {acum_horas['horas_extras_diurnas']:.2f}h (Recargo: ${acum_surcharge_values['horas_extras_diurnas']:,.2f})\n"
        if acum_horas["horas_extras_nocturnas"] > 0:
            reporte_str += f"Total Horas Extras Nocturnas: {acum_horas['horas_extras_nocturnas']:.2f}h (Recargo: ${acum_surcharge_values['horas_extras_nocturnas']:,.2f})\n"
        
        # Resumen para Domingo
        if acum_horas["horas_ordinarias_diurnas_domingo"] > 0:
            reporte_str += f"Total Horas Ordinarias Diurnas Domingo: {acum_horas['horas_ordinarias_diurnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values['horas_ordinarias_diurnas_domingo']:,.2f})\n"
        if acum_horas["horas_ordinarias_nocturnas_domingo"] > 0:
            reporte_str += f"Total Horas Ordinarias Nocturnas Domingo: {acum_horas['horas_ordinarias_nocturnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values['horas_ordinarias_nocturnas_domingo']:,.2f})\n"
        if acum_horas["horas_extras_diurnas_domingo"] > 0:
            reporte_str += f"Total Horas Extras Diurnas Domingo: {acum_horas['horas_extras_diurnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values['horas_extras_diurnas_domingo']:,.2f})\n"
        if acum_horas["horas_extras_nocturnas_domingo"] > 0:
            reporte_str += f"Total Horas Extras Nocturnas Domingo: {acum_horas['horas_extras_nocturnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values['horas_extras_nocturnas_domingo']:,.2f})\n"

        # Resumen para Festivo
        if acum_horas["horas_ordinarias_diurnas_festivo"] > 0:
            reporte_str += f"Total Horas Ordinarias Diurnas Festivo: {acum_horas['horas_ordinarias_diurnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values['horas_ordinarias_diurnas_festivo']:,.2f})\n"
        if acum_horas["horas_ordinarias_nocturnas_festivo"] > 0:
            reporte_str += f"Total Horas Ordinarias Nocturnas Festivo: {acum_horas['horas_ordinarias_nocturnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values['horas_ordinarias_nocturnas_festivo']:,.2f})\n"
        if acum_horas["horas_extras_diurnas_festivo"] > 0:
            reporte_str += f"Total Horas Extras Diurnas Festivo: {acum_horas['horas_extras_diurnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values['horas_extras_diurnas_festivo']:,.2f})\n"
        if acum_horas["horas_extras_nocturnas_festivo"] > 0:
            reporte_str += f"Total Horas Extras Nocturnas Festivo: {acum_horas['horas_extras_nocturnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values['horas_extras_nocturnas_festivo']:,.2f})\n"


        reporte_str += f"\nTotal Valor Bruto Acumulado para {empleado.nombre}: ${total_general_valor_empleado:,.2f}\n"
        reporte_str += f"Total Recargos Adicionales para {empleado.nombre}: ${total_general_recargo_adicional_empleado:,.2f}\n"
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

        total_general_valor = 0.0 # Acumula el valor TOTAL (base + recargos)
        total_general_recargo_adicional = 0.0 # Acumula solo los recargos adicionales
        total_general_horas_con_recargo = 0.0
        
        acum_horas_general = {
            "horas_ordinarias_diurnas": 0.0,
            "horas_ordinarias_nocturnas": 0.0,
            "horas_extras_diurnas": 0.0,
            "horas_extras_nocturnas": 0.0,
            
            "horas_ordinarias_diurnas_domingo": 0.0,
            "horas_ordinarias_nocturnas_domingo": 0.0,
            "horas_extras_diurnas_domingo": 0.0,
            "horas_extras_nocturnas_domingo": 0.0,

            "horas_ordinarias_diurnas_festivo": 0.0,
            "horas_ordinarias_nocturnas_festivo": 0.0,
            "horas_extras_diurnas_festivo": 0.0,
            "horas_extras_nocturnas_festivo": 0.0,
        }
        acum_surcharge_values_general = { # Esto almacenará el VALOR DEL RECARGO ADICIONAL
            "horas_ordinarias_diurnas": 0.0,
            "horas_ordinarias_nocturnas": 0.0,
            "horas_extras_diurnas": 0.0,
            "horas_extras_nocturnas": 0.0,
            
            "horas_ordinarias_diurnas_domingo": 0.0,
            "horas_ordinarias_nocturnas_domingo": 0.0,
            "horas_extras_diurnas_domingo": 0.0,
            "horas_extras_nocturnas_domingo": 0.0,

            "horas_ordinarias_diurnas_festivo": 0.0,
            "horas_ordinarias_nocturnas_festivo": 0.0,
            "horas_extras_diurnas_festivo": 0.0,
            "horas_extras_nocturnas_festivo": 0.0,
        }

        if not lista_empleados:
            return "No hay empleados registrados para generar un reporte consolidado."

        for empleado in lista_empleados:
            valor_empleado_periodo = 0.0
            recargo_adicional_empleado_periodo = 0.0
            horas_empleado_periodo = 0.0
            
            acum_horas_empleado_periodo = {
                "horas_ordinarias_diurnas": 0.0,
                "horas_ordinarias_nocturnas": 0.0,
                "horas_extras_diurnas": 0.0,
                "horas_extras_nocturnas": 0.0,
                
                "horas_ordinarias_diurnas_domingo": 0.0,
                "horas_ordinarias_nocturnas_domingo": 0.0,
                "horas_extras_diurnas_domingo": 0.0,
                "horas_extras_nocturnas_domingo": 0.0,

                "horas_ordinarias_diurnas_festivo": 0.0,
                "horas_ordinarias_nocturnas_festivo": 0.0,
                "horas_extras_diurnas_festivo": 0.0,
                "horas_extras_nocturnas_festivo": 0.0,
            }
            acum_surcharge_values_empleado_periodo = {
                "horas_ordinarias_diurnas": 0.0,
                "horas_ordinarias_nocturnas": 0.0,
                "horas_extras_diurnas": 0.0,
                "horas_extras_nocturnas": 0.0,
                
                "horas_ordinarias_diurnas_domingo": 0.0,
                "horas_ordinarias_nocturnas_domingo": 0.0,
                "horas_extras_diurnas_domingo": 0.0,
                "horas_extras_nocturnas_domingo": 0.0,

                "horas_ordinarias_diurnas_festivo": 0.0,
                "horas_ordinarias_nocturnas_festivo": 0.0,
                "horas_extras_diurnas_festivo": 0.0,
                "horas_extras_nocturnas_festivo": 0.0,
            }

            for jornada in empleado.jornadas_registradas:
                fecha_jornada = jornada["fecha"]
                if (periodo_inicio is None or fecha_jornada >= periodo_inicio) and \
                   (periodo_fin is None or fecha_jornada <= periodo_fin):
                    
                    total_gross_value_jornada, horas_con_recargo, categorized_hours, categorized_surcharge_values = self.calcular_recargos_jornada(empleado, jornada)
                    valor_empleado_periodo += total_gross_value_jornada
                    recargo_adicional_empleado_periodo += sum(categorized_surcharge_values.values())
                    horas_empleado_periodo += horas_con_recargo
                    
                    for key, value in categorized_hours.items():
                        acum_horas_empleado_periodo[key] += value
                    for key, value in categorized_surcharge_values.items():
                        acum_surcharge_values_empleado_periodo[key] += value

            if valor_empleado_periodo > 0 or any(v > 0 for v in acum_horas_empleado_periodo.values()):
                reporte_str += f" Empleado: {empleado.nombre} (Salario: ${empleado.salario_mensual:,.2f})\n"
                # Mostrar el valor base de las horas ordinarias diurnas acumuladas
                if acum_horas_empleado_periodo["horas_ordinarias_diurnas"] > 0:
                    base_value_for_period_ord_diur = acum_horas_empleado_periodo['horas_ordinarias_diurnas'] * empleado.obtener_valor_hora_ordinaria()
                    reporte_str += f"   Horas Ordinarias Diurnas: {acum_horas_empleado_periodo['horas_ordinarias_diurnas']:.2f}h (Valor Base: ${base_value_for_period_ord_diur:,.2f})\n"
                if acum_horas_empleado_periodo["horas_ordinarias_nocturnas"] > 0:
                    reporte_str += f"   Horas Ordinarias Nocturnas: {acum_horas_empleado_periodo['horas_ordinarias_nocturnas']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_ordinarias_nocturnas']:,.2f})\n"
                if acum_horas_empleado_periodo["horas_extras_diurnas"] > 0:
                    reporte_str += f"   Horas Extras Diurnas: {acum_horas_empleado_periodo['horas_extras_diurnas']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_extras_diurnas']:,.2f})\n"
                if acum_horas_empleado_periodo["horas_extras_nocturnas"] > 0:
                    reporte_str += f"   Horas Extras Nocturnas: {acum_horas_empleado_periodo['horas_extras_nocturnas']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_extras_nocturnas']:,.2f})\n"
                
                # Reporte para Domingo
                if acum_horas_empleado_periodo["horas_ordinarias_diurnas_domingo"] > 0:
                    reporte_str += f"   Horas Ordinarias Diurnas Domingo: {acum_horas_empleado_periodo['horas_ordinarias_diurnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_ordinarias_diurnas_domingo']:,.2f})\n"
                if acum_horas_empleado_periodo["horas_ordinarias_nocturnas_domingo"] > 0:
                    reporte_str += f"   Horas Ordinarias Nocturnas Domingo: {acum_horas_empleado_periodo['horas_ordinarias_nocturnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_ordinarias_nocturnas_domingo']:,.2f})\n"
                if acum_horas_empleado_periodo["horas_extras_diurnas_domingo"] > 0:
                    reporte_str += f"   Horas Extras Diurnas Domingo: {acum_horas_empleado_periodo['horas_extras_diurnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_extras_diurnas_domingo']:,.2f})\n"
                if acum_horas_empleado_periodo["horas_extras_nocturnas_domingo"] > 0:
                    reporte_str += f"   Horas Extras Nocturnas Domingo: {acum_horas_empleado_periodo['horas_extras_nocturnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_extras_nocturnas_domingo']:,.2f})\n"

                # Reporte para Festivo
                if acum_horas_empleado_periodo["horas_ordinarias_diurnas_festivo"] > 0:
                    reporte_str += f"   Horas Ordinarias Diurnas Festivo: {acum_horas_empleado_periodo['horas_ordinarias_diurnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_ordinarias_diurnas_festivo']:,.2f})\n"
                if acum_horas_empleado_periodo["horas_ordinarias_nocturnas_festivo"] > 0:
                    reporte_str += f"   Horas Ordinarias Nocturnas Festivo: {acum_horas_empleado_periodo['horas_ordinarias_nocturnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_ordinarias_nocturnas_festivo']:,.2f})\n"
                if acum_horas_empleado_periodo["horas_extras_diurnas_festivo"] > 0:
                    reporte_str += f"   Horas Extras Diurnas Festivo: {acum_horas_empleado_periodo['horas_extras_diurnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_extras_diurnas_festivo']:,.2f})\n"
                if acum_horas_empleado_periodo["horas_extras_nocturnas_festivo"] > 0:
                    reporte_str += f"   Horas Extras Nocturnas Festivo: {acum_horas_empleado_periodo['horas_extras_nocturnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values_empleado_periodo['horas_extras_nocturnas_festivo']:,.2f})\n"

                reporte_str += f"   Valor Bruto en el período: ${valor_empleado_periodo:,.2f}\n"
                reporte_str += f"   Recargos Adicionales en el período: ${recargo_adicional_empleado_periodo:,.2f}\n"
                reporte_str += f"   Horas con recargo en el período: {horas_empleado_periodo:.2f} horas\n\n"
                
                total_general_valor += valor_empleado_periodo
                total_general_recargo_adicional += recargo_adicional_empleado_periodo
                total_general_horas_con_recargo += horas_empleado_periodo
                
                for key, value in acum_horas_empleado_periodo.items():
                    acum_horas_general[key] += value
                for key, value in acum_surcharge_values_empleado_periodo.items():
                    acum_surcharge_values_general[key] += value

        if total_general_valor == 0 and all(v == 0 for v in acum_horas_general.values()):
            reporte_str += "No se encontraron recargos ni horas trabajadas en el período especificado para ningún empleado.\n"
        else:
            reporte_str += f"\n--- Resumen General de Horas y Recargos Acumulados para la Empresa ---\n"
            # Mostrar el valor base de las horas ordinarias diurnas acumuladas
            if acum_horas_general["horas_ordinarias_diurnas"] > 0:
                base_value_for_total_ord_diur_general = acum_horas_general['horas_ordinarias_diurnas'] * empleado.obtener_valor_hora_ordinaria()
                reporte_str += f"Total Horas Ordinarias Diurnas: {acum_horas_general['horas_ordinarias_diurnas']:.2f}h (Valor Base: ${base_value_for_total_ord_diur_general:,.2f})\n"
            if acum_horas_general["horas_ordinarias_nocturnas"] > 0:
                reporte_str += f"Total Horas Ordinarias Nocturnas: {acum_horas_general['horas_ordinarias_nocturnas']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_ordinarias_nocturnas']:,.2f})\n"
            if acum_horas_general["horas_extras_diurnas"] > 0:
                reporte_str += f"Total Horas Extras Diurnas: {acum_horas_general['horas_extras_diurnas']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_extras_diurnas']:,.2f})\n"
            if acum_horas_general["horas_extras_nocturnas"] > 0:
                reporte_str += f"Total Horas Extras Nocturnas: {acum_horas_general['horas_extras_nocturnas']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_extras_nocturnas']:,.2f})\n"

            # Resumen para Domingo (General)
            if acum_horas_general["horas_ordinarias_diurnas_domingo"] > 0:
                reporte_str += f"Total Horas Ordinarias Diurnas Domingo: {acum_horas_general['horas_ordinarias_diurnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_ordinarias_diurnas_domingo']:,.2f})\n"
            if acum_horas_general["horas_ordinarias_nocturnas_domingo"] > 0:
                reporte_str += f"Total Horas Ordinarias Nocturnas Domingo: {acum_horas_general['horas_ordinarias_nocturnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_ordinarias_nocturnas_domingo']:,.2f})\n"
            if acum_horas_general["horas_extras_diurnas_domingo"] > 0:
                reporte_str += f"Total Horas Extras Diurnas Domingo: {acum_horas_general['horas_extras_diurnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_extras_diurnas_domingo']:,.2f})\n"
            if acum_horas_general["horas_extras_nocturnas_domingo"] > 0:
                reporte_str += f"Total Horas Extras Nocturnas Domingo: {acum_horas_general['horas_extras_nocturnas_domingo']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_extras_nocturnas_domingo']:,.2f})\n"

            # Resumen para Festivo (General)
            if acum_horas_general["horas_ordinarias_diurnas_festivo"] > 0:
                reporte_str += f"Total Horas Ordinarias Diurnas Festivo: {acum_horas_general['horas_ordinarias_diurnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_ordinarias_diurnas_festivo']:,.2f})\n"
            if acum_horas_general["horas_ordinarias_nocturnas_festivo"] > 0:
                reporte_str += f"Total Horas Ordinarias Nocturnas Festivo: {acum_horas_general['horas_ordinarias_nocturnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_ordinarias_nocturnas_festivo']:,.2f})\n"
            if acum_horas_general["horas_extras_diurnas_festivo"] > 0:
                reporte_str += f"Total Horas Extras Diurnas Festivo: {acum_horas_general['horas_extras_diurnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_extras_diurnas_festivo']:,.2f})\n"
            if acum_horas_general["horas_extras_nocturnas_festivo"] > 0:
                reporte_str += f"Total Horas Extras Nocturnas Festivo: {acum_horas_general['horas_extras_nocturnas_festivo']:.2f}h (Recargo: ${acum_surcharge_values_general['horas_extras_nocturnas_festivo']:,.2f})\n"

            reporte_str += f"\nTotal General de Valor Bruto para la Empresa: ${total_general_valor:,.2f}\n"
            reporte_str += f"Total General de Recargos Adicionales para la Empresa: ${total_general_recargo_adicional:,.2f}\n"
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

    def actualizar_porcentajes_recargo(self, 
                                       nuevo_extra_diurna=None,
                                       nuevo_extra_nocturna=None,
                                       nuevo_ordinaria_nocturna_recargo=None, # Ahora es el recargo adicional
                                       nuevo_recargo_domingofestivo_diurno_base_recargo=None, # Ahora es el recargo adicional
                                       nuevo_extra_diurna_domingofestivo=None,
                                       nuevo_extra_nocturna_domingofestivo=None,
                                       nuevo_ordinaria_nocturna_domingofestivo_recargo=None, # Ahora es el recargo adicional
                                       nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo=None, # Ahora es el recargo adicional
                                       nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo=None): # Ahora es el recargo adicional
        """
        Permite actualizar los multiplicadores de recargo.
        Los valores de entrada para "extra" deben ser porcentajes totales (ej. 125, 200).
        Los valores de entrada para "recargo" deben ser porcentajes adicionales (ej. 35, 75).
        """
        mensajes = []
        if nuevo_extra_diurna is not None:
            self.MULTIPLIER_HORA_EXTRA_DIURNA = nuevo_extra_diurna / 100
            mensajes.append(f"Multiplicador de hora extra diurna actualizado a {nuevo_extra_diurna}%.")
        if nuevo_extra_nocturna is not None:
            self.MULTIPLIER_HORA_EXTRA_NOCTURNA = nuevo_extra_nocturna / 100
            mensajes.append(f"Multiplicador de hora extra nocturna actualizado a {nuevo_extra_nocturna}%.")
        
        # Para los recargos, sumamos 100% al porcentaje adicional para obtener el multiplicador total
        if nuevo_ordinaria_nocturna_recargo is not None:
            self.MULTIPLIER_HORA_ORDINARIA_NOCTURNA = 1.00 + (nuevo_ordinaria_nocturna_recargo / 100)
            mensajes.append(f"Multiplicador de recargo nocturno actualizado a {nuevo_ordinaria_nocturna_recargo}% (total: {self.MULTIPLIER_HORA_ORDINARIA_NOCTURNA*100:.0f}%).")
        
        if nuevo_recargo_domingofestivo_diurno_base_recargo is not None:
            self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE = 1.00 + (nuevo_recargo_domingofestivo_diurno_base_recargo / 100)
            mensajes.append(f"Multiplicador de recargo dominical/festivo diurno base actualizado a {nuevo_recargo_domingofestivo_diurno_base_recargo}% (total: {self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE*100:.0f}%).")
        
        if nuevo_extra_diurna_domingofestivo is not None:
            self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO = nuevo_extra_diurna_domingofestivo / 100
            mensajes.append(f"Multiplicador de extra diurna dominical/festivo actualizado a {nuevo_extra_diurna_domingofestivo}%.")
        if nuevo_extra_nocturna_domingofestivo is not None:
            self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO = nuevo_extra_nocturna_domingofestivo / 100
            mensajes.append(f"Multiplicador de extra nocturna dominical/festivo actualizado a {nuevo_extra_nocturna_domingofestivo}%.")

        if nuevo_ordinaria_nocturna_domingofestivo_recargo is not None: 
            self.MULTIPLIER_ORDINARIA_NOCTURNA_DOMINGOFESTIVO = 1.00 + (nuevo_ordinaria_nocturna_domingofestivo_recargo / 100)
            mensajes.append(f"Multiplicador de recargo ordinario nocturno dominical/festivo actualizado a {nuevo_ordinaria_nocturna_domingofestivo_recargo}% (total: {self.MULTIPLIER_ORDINARIA_NOCTURNA_DOMINGOFESTIVO*100:.0f}%).")
        
        if nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo is not None:
            self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA = 1.00 + (nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo / 100)
            mensajes.append(f"Multiplicador de recargo dominical/festivo diurno (jornada larga) actualizado a {nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo}% (total: {self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA*100:.0f}%).")
        if nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo is not None:
            self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA = 1.00 + (nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo / 100)
            mensajes.append(f"Multiplicador de recargo dominical/festivo nocturno (jornada larga) actualizado a {nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo}% (total: {self.MULTIPLIER_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA*100:.0f}%).")

        return "\n".join(mensajes) if mensajes else "Ningún porcentaje fue actualizado."

# --- Funciones para Guardar y Cargar Datos ---

DATA_FILE = "recargos_data.json"

def save_app_data(empleados, calculadora_instance):
    """Guarda el estado actual de la aplicación en un archivo JSON."""
    data_to_save = {
        "empleados": {name: emp.to_dict() for name, emp in empleados.items()},
        "dias_festivos": [d.isoformat() for d in calculadora_instance.dias_festivos],
        "configuracion_recargos": {
            "MULTIPLIER_HORA_EXTRA_DIURNA": calculadora_instance.MULTIPLIER_HORA_EXTRA_DIURNA,
            "MULTIPLIER_HORA_EXTRA_NOCTURNA": calculadora_instance.MULTIPLIER_HORA_EXTRA_NOCTURNA,
            "MULTIPLIER_HORA_ORDINARIA_NOCTURNA": calculadora_instance.MULTIPLIER_HORA_ORDINARIA_NOCTURNA,
            "MULTIPLIER_ORDINARIA_NOCTURNA_DOMINGOFESTIVO": calculadora_instance.MULTIPLIER_ORDINARIA_NOCTURNA_DOMINGOFESTIVO, 
            "MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE": calculadora_instance.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE,
            "MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO": calculadora_instance.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO,
            "MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO": calculadora_instance.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO,
            "MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA": calculadora_instance.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA,
            "MULTIPLIER_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA": calculadora_instance.MULTIPLIER_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA,
        }
    }
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Datos guardados exitosamente en {DATA_FILE}")
    except IOError as e:
        print(f"Error al guardar datos en {DATA_FILE}: {e}")

def load_app_data():
    """Carga el estado de la aplicación desde un archivo JSON."""
    empleados = {}
    calculadora = CalculadoraRecargos() # Crea una instancia por defecto primero

    if not os.path.exists(DATA_FILE):
        print(f"Archivo de datos '{DATA_FILE}' no encontrado. Iniciando con datos vacíos.")
        return empleados, calculadora

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        # Cargar empleados
        for name, emp_dict in loaded_data.get("empleados", {}).items():
            empleados[name] = Empleado.from_dict(emp_dict)
        
        # Cargar días festivos
        loaded_festivos_str = loaded_data.get("dias_festivos", [])
        calculadora.dias_festivos = [datetime.date.fromisoformat(d_str) for d_str in loaded_festivos_str]
        calculadora.dias_festivos.sort() # Asegurar que estén ordenados

        # Cargar configuraciones de recargos
        loaded_config = loaded_data.get("configuracion_recargos", {})
        
        calculadora.MULTIPLIER_HORA_EXTRA_DIURNA = loaded_config.get("MULTIPLIER_HORA_EXTRA_DIURNA", 1.25)
        calculadora.MULTIPLIER_HORA_EXTRA_NOCTURNA = loaded_config.get("MULTIPLIER_HORA_EXTRA_NOCTURNA", 1.75)
        calculadora.MULTIPLIER_HORA_ORDINARIA_NOCTURNA = loaded_config.get("MULTIPLIER_HORA_ORDINARIA_NOCTURNA", 1.35)
        calculadora.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE = loaded_config.get("MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_BASE", 1.80) # Actualizado
        
        calculadora.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO = loaded_config.get("MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO", 2.00)
        calculadora.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO = loaded_config.get("MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO", 2.50)

        calculadora.MULTIPLIER_ORDINARIA_NOCTURNA_DOMINGOFESTIVO = loaded_config.get("MULTIPLIER_ORDINARIA_NOCTURNA_DOMINGOFESTIVO", 2.10)
        calculadora.MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA = loaded_config.get("MULTIPLIER_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA", 2.80) # Actualizado
        calculadora.MULTIPLIER_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA = loaded_config.get("MULTIPLIER_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA", 3.10)


        print(f"Datos cargados exitosamente desde {DATA_FILE}")
        return empleados, calculadora

    except (json.JSONDecodeError, IOError) as e:
        print(f"Error al cargar datos desde {DATA_FILE}: {e}. Iniciando con datos vacíos.")
        return {}, CalculadoraRecargos() # En caso de error, iniciar con datos por defecto