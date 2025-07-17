import datetime
import json
import os

class Empleado:
    def __init__(self, nombre, salario_mensual, standard_daily_hours, tipo_contrato="indefinido"):
        self.nombre = nombre
        self.salario_mensual = salario_mensual
        self.standard_daily_hours = standard_daily_hours # Horas diarias estándar
        self.tipo_contrato = tipo_contrato # Nuevo atributo para el tipo de contrato
        self.jornadas_registradas = [] # Almacena diccionarios de jornadas

    def obtener_valor_hora_ordinaria(self):
        # Asume un mes de 30 días y 8 horas diarias para 240 horas/mes
        # Se usa self.standard_daily_hours para mayor precisión si el estándar cambia
        if self.standard_daily_hours <= 0:
            return 0.0
        return self.salario_mensual / (30 * self.standard_daily_hours)

    def registrar_jornada(self, fecha, hora_entrada, hora_salida):
        jornada = {
            "fecha": fecha,
            "hora_entrada": hora_entrada,
            "hora_salida": hora_salida
        }
        self.jornadas_registradas.append(jornada)
        return f"Jornada registrada para {self.nombre} el {fecha.strftime('%Y-%m-%d')} de {hora_entrada.strftime('%I:%M %p')} a {hora_salida.strftime('%I:%M %p')}."


class CalculadoraRecargos:
    def __init__(self):
        # Multiplicadores para el VALOR TOTAL de la hora (1.00 + porcentaje adicional)
        # Por ejemplo, 1.25 para hora extra diurna significa 100% valor base + 25% adicional
        self.MULTIPLIER_HORA_EXTRA_DIURNA = 1.25 # 25% adicional
        self.MULTIPLIER_HORA_EXTRA_NOCTURNA = 1.75 # 75% adicional
        self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO = 2.00 # 100% adicional (75% dom/fest + 25% extra diurna)
        self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO = 2.50 # 150% adicional (75% dom/fest + 75% extra nocturna)

        # Porcentajes ADICIONALES para recargos (solo el porcentaje extra)
        self.ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA = 0.35 # 35%
        self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE = 1.80 # 180%
        self.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO = 1.10 # 110% (75% dom/fest + 35% nocturno)
        self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA = 0.80 # 80% (Para jornadas > 8h en D/F diurno)
        self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA = 2.15 # 215% (Para jornadas > 8h en D/F nocturno)

        self.dias_festivos = self._cargar_festivos_iniciales()

    def _cargar_festivos_iniciales(self):
        # Días festivos de Colombia para 2025 (ejemplo)
        # Fuente: https://www.calendario-colombia.com/dias-festivos-2025.html
        festivos = [
            datetime.date(2025, 1, 1),  # Año Nuevo
            datetime.date(2025, 1, 6),  # Día de Reyes Magos
            datetime.date(2025, 3, 24), # Día de San José
            datetime.date(2025, 4, 17), # Jueves Santo
            datetime.date(2025, 4, 18), # Viernes Santo
            datetime.date(2025, 5, 1),  # Día del Trabajo
            datetime.date(2025, 5, 26), # Día de la Ascensión
            datetime.date(2025, 6, 16), # Corpus Christi
            datetime.date(2025, 6, 23), # Sagrado Corazón
            datetime.date(2025, 7, 20), # Grito de Independencia
            datetime.date(2025, 8, 7),  # Batalla de Boyacá
            datetime.date(2025, 8, 18), # Asunción de la Virgen
            datetime.date(2025, 10, 13),# Día de la Raza
            datetime.date(2025, 11, 3), # Día de Todos los Santos
            datetime.date(2025, 11, 17),# Independencia de Cartagena
            datetime.date(2025, 12, 8), # Día de la Inmaculada Concepción
            datetime.date(2025, 12, 25) # Navidad
        ]
        return sorted(list(set(festivos))) # Eliminar duplicados y ordenar

    def es_festivo_o_domingo(self, fecha):
        return fecha.weekday() == 6 or fecha in self.dias_festivos # 6 es domingo

    def agregar_dia_festivo(self, fecha):
        if fecha not in self.dias_festivos:
            self.dias_festivos.append(fecha)
            self.dias_festivos.sort()
            return f"Día festivo {fecha.strftime('%Y-%m-%d')} agregado."
        return f"El día {fecha.strftime('%Y-%m-%d')} ya es un día festivo registrado."

    def eliminar_dia_festivo(self, fecha):
        if fecha in self.dias_festivos:
            self.dias_festivos.remove(fecha)
            return f"Día festivo {fecha.strftime('%Y-%m-%d')} eliminado."
        return f"El día {fecha.strftime('%Y-%m-%d')} no se encontró en la lista de festivos."

    def _get_percentage_for_hour_type(self, hour_type):
        """
        Retorna el porcentaje ADICIONAL para un tipo de hora dado.
        (Este método se mantiene para cálculos internos y para mostrar el porcentaje en los reportes)
        """
        if hour_type == "horas_ordinarias_nocturnas":
            return round(self.ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA * 100)
        elif hour_type == "horas_extras_diurnas":
            return round((self.MULTIPLIER_HORA_EXTRA_DIURNA - 1.0) * 100)
        elif hour_type == "horas_extras_nocturnas":
            return round((self.MULTIPLIER_HORA_EXTRA_NOCTURNA - 1.0) * 100)
        elif hour_type in ["horas_ordinarias_diurnas_domingo", "horas_ordinarias_diurnas_festivo"]:
            return round(self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE * 100)
        elif hour_type in ["horas_ordinarias_nocturnas_domingo", "horas_ordinarias_nocturnas_festivo"]:
            return round(self.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO * 100)
        elif hour_type in ["horas_extras_diurnas_domingo", "horas_extras_diurnas_festivo"]:
            return round((self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO - 1.0) * 100)
        elif hour_type in ["horas_extras_nocturnas_domingo", "horas_extras_nocturnas_festivo"]:
            return round((self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO - 1.0) * 100)
        # Casos específicos de jornada larga en D/F (si se manejan por separado en reportes)
        elif hour_type == "recargo_domingofestivo_diurno_larga_jornada":
            return round(self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA * 100)
        elif hour_type == "recargo_domingofestivo_nocturno_larga_jornada":
            return round(self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA * 100)
        return 0 # Para horas ordinarias diurnas que no tienen recargo adicional

    def calcular_recargos_jornada(self, empleado, jornada):
        fecha = jornada["fecha"]
        hora_entrada = jornada["hora_entrada"]
        hora_salida = jornada["hora_salida"]

        valor_hora_ordinaria = empleado.obtener_valor_hora_ordinaria()
        
        # Calcular duración total de la jornada en horas
        # Manejar jornadas que cruzan la medianoche
        if hora_salida <= hora_entrada: # Si la hora de salida es menor o igual a la de entrada, es al día siguiente
            delta_tiempo = (datetime.datetime.combine(fecha + datetime.timedelta(days=1), hora_salida) - 
                            datetime.datetime.combine(fecha, hora_entrada))
        else:
            delta_tiempo = datetime.datetime.combine(fecha, hora_salida) - datetime.datetime.combine(fecha, hora_entrada)
        
        total_horas_jornada = delta_tiempo.total_seconds() / 3600.0

        # Inicializar contadores de horas por tipo
        horas_categorizadas = {
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

        # Iterar hora por hora para categorizar
        current_time = datetime.datetime.combine(fecha, hora_entrada)
        end_time = datetime.datetime.combine(fecha, hora_salida)
        if hora_salida <= hora_entrada:
            end_time = datetime.datetime.combine(fecha + datetime.timedelta(days=1), hora_salida)

        horas_trabajadas_hoy = 0.0
        
        while current_time < end_time:
            next_hour = current_time + datetime.timedelta(hours=1)
            # Asegurarse de no exceder el end_time si la última fracción de hora es menor a 1
            if next_hour > end_time:
                next_hour = end_time
            
            duration = (next_hour - current_time).total_seconds() / 3600.0
            
            is_domingo_o_festivo = self.es_festivo_o_domingo(current_time.date())
            
            # Determinar si es horario nocturno (9 PM a 6 AM)
            is_nocturno = (current_time.time() >= datetime.time(21, 0) or 
                            current_time.time() < datetime.time(6, 0))

            horas_trabajadas_hoy += duration

            if is_domingo_o_festivo:
                # Determinar si es domingo o festivo específico
                if current_time.date().weekday() == 6: # Es domingo
                    if is_nocturno:
                        if horas_trabajadas_hoy <= empleado.standard_daily_hours:
                            horas_categorizadas["horas_ordinarias_nocturnas_domingo"] += duration
                        else:
                            horas_categorizadas["horas_extras_nocturnas_domingo"] += duration
                    else: # Diurno en domingo
                        if horas_trabajadas_hoy <= empleado.standard_daily_hours:
                            horas_categorizadas["horas_ordinarias_diurnas_domingo"] += duration
                        else:
                            horas_categorizadas["horas_extras_diurnas_domingo"] += duration
                elif current_time.date() in self.dias_festivos: # Es festivo
                    if is_nocturno:
                        if horas_trabajadas_hoy <= empleado.standard_daily_hours:
                            horas_categorizadas["horas_ordinarias_nocturnas_festivo"] += duration
                        else:
                            horas_categorizadas["horas_extras_nocturnas_festivo"] += duration
                    else: # Diurno en festivo
                        if horas_trabajadas_hoy <= empleado.standard_daily_hours:
                            horas_categorizadas["horas_ordinarias_diurnas_festivo"] += duration
                        else:
                            horas_categorizadas["horas_extras_diurnas_festivo"] += duration
            else: # Día hábil
                if is_nocturno:
                    if horas_trabajadas_hoy <= empleado.standard_daily_hours:
                        horas_categorizadas["horas_ordinarias_nocturnas"] += duration
                    else:
                        horas_categorizadas["horas_extras_nocturnas"] += duration
                else: # Diurno en día hábil
                    if horas_trabajadas_hoy <= empleado.standard_daily_hours:
                        horas_categorizadas["horas_ordinarias_diurnas"] += duration
                    else:
                        horas_categorizadas["horas_extras_diurnas"] += duration
            
            current_time = next_hour

        # Calcular recargos basados en las horas categorizadas (se mantiene para cálculos internos)
        recargo_total_jornada = 0.0
        horas_con_recargo_jornada = 0.0
        
        # Horas Ordinarias Diurnas (no tienen recargo adicional, solo valor base)
        recargo_total_jornada += horas_categorizadas["horas_ordinarias_diurnas"] * valor_hora_ordinaria

        # Horas Ordinarias Nocturnas
        if horas_categorizadas["horas_ordinarias_nocturnas"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_ordinarias_nocturnas"] * valor_hora_ordinaria * (1 + self.ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA))
            horas_con_recargo_jornada += horas_categorizadas["horas_ordinarias_nocturnas"]

        # Horas Extras Diurnas
        if horas_categorizadas["horas_extras_diurnas"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_extras_diurnas"] * valor_hora_ordinaria * self.MULTIPLIER_HORA_EXTRA_DIURNA)
            horas_con_recargo_jornada += horas_categorizadas["horas_extras_diurnas"]

        # Horas Extras Nocturnas
        if horas_categorizadas["horas_extras_nocturnas"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_extras_nocturnas"] * valor_hora_ordinaria * self.MULTIPLIER_HORA_EXTRA_NOCTURNA)
            horas_con_recargo_jornada += horas_categorizadas["horas_extras_nocturnas"]

        # Horas Ordinarias Diurnas Domingo/Festivo
        if horas_categorizadas["horas_ordinarias_diurnas_domingo"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_ordinarias_diurnas_domingo"] * valor_hora_ordinaria * (1 + self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE))
            horas_con_recargo_jornada += horas_categorizadas["horas_ordinarias_diurnas_domingo"]

        if horas_categorizadas["horas_ordinarias_diurnas_festivo"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_ordinarias_diurnas_festivo"] * valor_hora_ordinaria * (1 + self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE))
            horas_con_recargo_jornada += horas_categorizadas["horas_ordinarias_diurnas_festivo"]

        # Horas Ordinarias Nocturnas Domingo/Festivo
        if horas_categorizadas["horas_ordinarias_nocturnas_domingo"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_ordinarias_nocturnas_domingo"] * valor_hora_ordinaria * (1 + self.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO))
            horas_con_recargo_jornada += horas_categorizadas["horas_ordinarias_nocturnas_domingo"]

        if horas_categorizadas["horas_ordinarias_nocturnas_festivo"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_ordinarias_nocturnas_festivo"] * valor_hora_ordinaria * (1 + self.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO))
            horas_con_recargo_jornada += horas_categorizadas["horas_ordinarias_nocturnas_festivo"]

        # Horas Extras Diurnas Domingo/Festivo
        if horas_categorizadas["horas_extras_diurnas_domingo"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_extras_diurnas_domingo"] * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO)
            horas_con_recargo_jornada += horas_categorizadas["horas_extras_diurnas_domingo"]

        if horas_categorizadas["horas_extras_diurnas_festivo"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_extras_diurnas_festivo"] * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO)
            horas_con_recargo_jornada += horas_categorizadas["horas_extras_diurnas_festivo"]

        # Horas Extras Nocturnas Domingo/Festivo
        if horas_categorizadas["horas_extras_nocturnas_domingo"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_extras_nocturnas_domingo"] * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO)
            horas_con_recargo_jornada += horas_categorizadas["horas_extras_nocturnas_domingo"]

        if horas_categorizadas["horas_extras_nocturnas_festivo"] > 0:
            recargo_total_jornada += (horas_categorizadas["horas_extras_nocturnas_festivo"] * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO)
            horas_con_recargo_jornada += horas_categorizadas["horas_extras_nocturnas_festivo"]

        return recargo_total_jornada, horas_categorizadas, total_horas_jornada

    def get_accumulated_hours_and_surcharges(self, empleado):
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
        acum_surcharge_values = { # Almacena solo el valor del recargo adicional
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
        total_gross_value = 0.0 # Valor bruto total (valor base + recargos)

        valor_hora_ordinaria = empleado.obtener_valor_hora_ordinaria()

        for jornada in empleado.jornadas_registradas:
            fecha = jornada["fecha"]
            hora_entrada = jornada["hora_entrada"]
            hora_salida = jornada["hora_salida"]

            # Calcular duración total de la jornada en horas
            if hora_salida <= hora_entrada:
                delta_tiempo = (datetime.datetime.combine(fecha + datetime.timedelta(days=1), hora_salida) - 
                                datetime.datetime.combine(fecha, hora_entrada))
            else:
                delta_tiempo = datetime.datetime.combine(fecha, hora_salida) - datetime.datetime.combine(fecha, hora_entrada)
            
            total_horas_jornada = delta_tiempo.total_seconds() / 3600.0

            # Categorizar horas para esta jornada
            current_time = datetime.datetime.combine(fecha, hora_entrada)
            end_time = datetime.datetime.combine(fecha, hora_salida)
            if hora_salida <= hora_entrada:
                end_time = datetime.datetime.combine(fecha + datetime.timedelta(days=1), hora_salida)

            horas_trabajadas_en_dia = 0.0 # Para controlar las horas estándar diarias

            temp_jornada_horas = {key: 0.0 for key in acum_horas.keys()} # Horas para esta jornada
            
            while current_time < end_time:
                next_hour = current_time + datetime.timedelta(hours=1)
                if next_hour > end_time:
                    next_hour = end_time
                
                duration = (next_hour - current_time).total_seconds() / 3600.0
                
                is_domingo_o_festivo = self.es_festivo_o_domingo(current_time.date())
                
                is_nocturno = (current_time.time() >= datetime.time(21, 0) or 
                                current_time.time() < datetime.time(6, 0))

                horas_trabajadas_en_dia += duration

                if is_domingo_o_festivo:
                    if current_time.date().weekday() == 6: # Es domingo
                        if is_nocturno:
                            if horas_trabajadas_en_dia <= empleado.standard_daily_hours:
                                temp_jornada_horas["horas_ordinarias_nocturnas_domingo"] += duration
                            else:
                                temp_jornada_horas["horas_extras_nocturnas_domingo"] += duration
                        else: # Diurno en domingo
                            if horas_trabajadas_en_dia <= empleado.standard_daily_hours:
                                temp_jornada_horas["horas_ordinarias_diurnas_domingo"] += duration
                            else:
                                temp_jornada_horas["horas_extras_diurnas_domingo"] += duration
                    elif current_time.date() in self.dias_festivos: # Es festivo
                        if is_nocturno:
                            if horas_trabajadas_en_dia <= empleado.standard_daily_hours:
                                temp_jornada_horas["horas_ordinarias_nocturnas_festivo"] += duration
                            else:
                                temp_jornada_horas["horas_extras_nocturnas_festivo"] += duration
                        else: # Diurno en festivo
                            if horas_trabajadas_en_dia <= empleado.standard_daily_hours:
                                temp_jornada_horas["horas_ordinarias_diurnas_festivo"] += duration
                            else:
                                temp_jornada_horas["horas_extras_diurnas_festivo"] += duration
                else: # Día hábil
                    if is_nocturno:
                        if horas_trabajadas_en_dia <= empleado.standard_daily_hours:
                            temp_jornada_horas["horas_ordinarias_nocturnas"] += duration
                        else:
                            temp_jornada_horas["horas_extras_nocturnas"] += duration
                    else: # Diurno en día hábil
                        if horas_trabajadas_en_dia <= empleado.standard_daily_hours:
                            temp_jornada_horas["horas_ordinarias_diurnas"] += duration
                        else:
                            temp_jornada_horas["horas_extras_diurnas"] += duration
                
                current_time = next_hour

            # Acumular horas y calcular recargos para esta jornada
            for key, hours in temp_jornada_horas.items():
                if hours > 0:
                    acum_horas[key] += hours
                    
                    # Calcular el valor del recargo adicional para cada tipo de hora
                    if key == "horas_ordinarias_diurnas":
                        # Estas horas no tienen recargo adicional, solo contribuyen al valor base total
                        total_gross_value += hours * valor_hora_ordinaria
                    elif key == "horas_ordinarias_nocturnas":
                        surcharge_value = hours * valor_hora_ordinaria * self.ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA
                        acum_surcharge_values[key] += surcharge_value
                        total_gross_value += (hours * valor_hora_ordinaria) + surcharge_value
                    elif key == "horas_extras_diurnas":
                        surcharge_value = hours * valor_hora_ordinaria * (self.MULTIPLIER_HORA_EXTRA_DIURNA - 1.0)
                        acum_surcharge_values[key] += surcharge_value
                        total_gross_value += hours * valor_hora_ordinaria * self.MULTIPLIER_HORA_EXTRA_DIURNA
                    elif key == "horas_extras_nocturnas":
                        surcharge_value = hours * valor_hora_ordinaria * (self.MULTIPLIER_HORA_EXTRA_NOCTURNA - 1.0)
                        acum_surcharge_values[key] += surcharge_value
                        total_gross_value += hours * valor_hora_ordinaria * self.MULTIPLIER_HORA_EXTRA_NOCTURNA
                    elif key in ["horas_ordinarias_diurnas_domingo", "horas_ordinarias_diurnas_festivo"]:
                        surcharge_value = hours * valor_hora_ordinaria * self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE
                        acum_surcharge_values[key] += surcharge_value
                        total_gross_value += (hours * valor_hora_ordinaria) + surcharge_value
                    elif key in ["horas_ordinarias_nocturnas_domingo", "horas_ordinarias_nocturnas_festivo"]:
                        surcharge_value = hours * valor_hora_ordinaria * self.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO
                        acum_surcharge_values[key] += surcharge_value
                        total_gross_value += (hours * valor_hora_ordinaria) + surcharge_value
                    elif key in ["horas_extras_diurnas_domingo", "horas_extras_diurnas_festivo"]:
                        surcharge_value = hours * valor_hora_ordinaria * (self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO - 1.0)
                        acum_surcharge_values[key] += surcharge_value
                        total_gross_value += hours * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO
                    elif key in ["horas_extras_nocturnas_domingo", "horas_extras_nocturnas_festivo"]:
                        surcharge_value = hours * valor_hora_ordinaria * (self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO - 1.0)
                        acum_surcharge_values[key] += surcharge_value
                        total_gross_value += hours * valor_hora_ordinaria * self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO
        
        return acum_horas, acum_surcharge_values, total_gross_value

    def generar_reporte_empleado(self, empleado):
        reporte_str = f"--- Reporte de Horas para {empleado.nombre} ---\n"
        reporte_str += f"Horas Diarias Estándar: {empleado.standard_daily_hours} horas\n\n"
        reporte_str += "Detalle de Jornadas:\n"

        total_horas_con_recargo_acumulado = 0.0
        total_horas_ordinarias_diurnas_acumulado = 0.0

        if not empleado.jornadas_registradas:
            reporte_str += "  No hay jornadas registradas para este empleado.\n"
        else:
            for i, jornada in enumerate(empleado.jornadas_registradas):
                # No necesitamos el valor total de recargo ni los valores de recargo por categoría aquí
                _, horas_categorizadas, total_horas_jornada = self.calcular_recargos_jornada(empleado, jornada)
                
                reporte_str += f"\nJornada {i+1} - Fecha: {jornada['fecha'].strftime('%Y-%m-%d')} ({jornada['hora_entrada'].strftime('%I:%M %p')} - {jornada['hora_salida'].strftime('%I:%M %p')})\n"
                reporte_str += f"  Total Horas Trabajadas: {total_horas_jornada:.2f}h\n"
                reporte_str += "  Horas Categorizadas:\n"

                jornada_horas_con_recargo = 0.0

                # Sección para horas regulares
                regular_keys = [
                    "horas_ordinarias_diurnas",
                    "horas_ordinarias_nocturnas",
                    "horas_extras_diurnas",
                    "horas_extras_nocturnas",
                ]
                for tipo_hora in regular_keys:
                    horas = horas_categorizadas.get(tipo_hora, 0.0)
                    if horas > 0:
                        reporte_str += f"    - {tipo_hora.replace('_', ' ').title()}: {horas:.2f}h\n"
                        if tipo_hora == "horas_ordinarias_diurnas":
                            total_horas_ordinarias_diurnas_acumulado += horas
                        else:
                            jornada_horas_con_recargo += horas

                # Sección para horas de Domingo
                domingo_keys = [
                    "horas_ordinarias_diurnas_domingo",
                    "horas_ordinarias_nocturnas_domingo",
                    "horas_extras_diurnas_domingo",
                    "horas_extras_nocturnas_domingo",
                ]
                for tipo_hora in domingo_keys:
                    horas = horas_categorizadas.get(tipo_hora, 0.0)
                    if horas > 0:
                        reporte_str += f"    - {tipo_hora.replace('_', ' ').title()}: {horas:.2f}h\n"
                        jornada_horas_con_recargo += horas

                # Sección para horas de Festivo
                festivo_keys = [
                    "horas_ordinarias_diurnas_festivo",
                    "horas_ordinarias_nocturnas_festivo",
                    "horas_extras_diurnas_festivo",
                    "horas_extras_nocturnas_festivo",
                ]
                for tipo_hora in festivo_keys:
                    horas = horas_categorizadas.get(tipo_hora, 0.0)
                    if horas > 0:
                        reporte_str += f"    - {tipo_hora.replace('_', ' ').title()}: {horas:.2f}h\n"
                        jornada_horas_con_recargo += horas


                reporte_str += f"  Horas con Recargo en Jornada: {jornada_horas_con_recargo:.2f}h\n"
                total_horas_con_recargo_acumulado += jornada_horas_con_recargo
                total_horas_ordinarias_diurnas_acumulado += horas_categorizadas["horas_ordinarias_diurnas"] # Asegurarse de sumar estas también para el total general

        total_todas_las_horas = total_horas_con_recargo_acumulado + total_horas_ordinarias_diurnas_acumulado

        reporte_str += "\n--- Resumen General ---\n"
        reporte_str += f"Total Horas Acumuladas con Recargo: {total_horas_con_recargo_acumulado:.2f}h\n"
        reporte_str += f"Total de Todas las Horas Acumuladas (Recargo + Ordinarias Diurnas): {total_todas_las_horas:.2f}h\n"
        reporte_str += "-----------------------------------------------------\n"
        return reporte_str

    def generar_reporte_consolidado(self, lista_empleados, periodo_inicio=None, periodo_fin=None):
        reporte_str = "--- Reporte Consolidado de Horas ---\n"
        if periodo_inicio and periodo_fin:
            reporte_str += f"Período: {periodo_inicio.strftime('%Y-%m-%d')} a {periodo_fin.strftime('%Y-%m-%d')}\n"
        elif periodo_inicio:
            reporte_str += f"Período: Desde {periodo_inicio.strftime('%Y-%m-%d')}\n"
        elif periodo_fin:
            reporte_str += f"Período: Hasta {periodo_fin.strftime('%Y-%m-%d')}\n"
        else:
            reporte_str += "Período: Todas las jornadas registradas\n"
        reporte_str += "----------------------------------------\n\n"

        total_general_horas_con_recargo = 0.0
        total_general_todas_las_horas = 0.0

        if not lista_empleados:
            reporte_str += "No hay empleados registrados.\n"
            return reporte_str

        for empleado in lista_empleados:
            jornadas_filtradas = []
            if periodo_inicio and periodo_fin:
                for jornada in empleado.jornadas_registradas:
                    if periodo_inicio <= jornada["fecha"] <= periodo_fin:
                        jornadas_filtradas.append(jornada)
            elif periodo_inicio: # Solo fecha de inicio
                for jornada in empleado.jornadas_registradas:
                    if jornada["fecha"] >= periodo_inicio:
                        jornadas_filtradas.append(jornada)
            elif periodo_fin: # Solo fecha de fin
                for jornada in empleado.jornadas_registradas:
                    if jornada["fecha"] <= periodo_fin:
                        jornadas_filtradas.append(jornada)
            else: # Sin filtro de período
                jornadas_filtradas = empleado.jornadas_registradas

            if not jornadas_filtradas:
                reporte_str += f"Empleado: {empleado.nombre} - No hay jornadas en el período seleccionado.\n\n"
                continue

            # Crear un empleado temporal con solo las jornadas filtradas para el cálculo
            temp_empleado = Empleado(empleado.nombre, empleado.salario_mensual, empleado.standard_daily_hours, empleado.tipo_contrato)
            temp_empleado.jornadas_registradas = jornadas_filtradas

            acum_horas, _, _ = self.get_accumulated_hours_and_surcharges(temp_empleado) # No necesitamos los valores de recargo ni el total bruto aquí

            reporte_str += f"--- Empleado: {empleado.nombre} ---\n"
            reporte_str += f"  Horas Diarias Estándar: {empleado.standard_daily_hours} horas\n"
            reporte_str += "  Acumulados por Categoría:\n"

            empleado_horas_con_recargo = 0.0
            empleado_horas_ordinarias_diurnas = 0.0

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

            # Sección para horas regulares
            regular_keys = [
                "horas_ordinarias_diurnas",
                "horas_ordinarias_nocturnas",
                "horas_extras_diurnas",
                "horas_extras_nocturnas",
            ]
            for key in regular_keys:
                hours = acum_horas.get(key, 0.0)
                if hours > 0:
                    reporte_str += f"    - {display_names[key]}: {hours:.2f}h\n"
                    if key == "horas_ordinarias_diurnas":
                        empleado_horas_ordinarias_diurnas += hours
                    else:
                        empleado_horas_con_recargo += hours
            
            # Sección para horas de Domingo
            domingo_keys = [
                "horas_ordinarias_diurnas_domingo",
                "horas_ordinarias_nocturnas_domingo",
                "horas_extras_diurnas_domingo",
                "horas_extras_nocturnas_domingo",
            ]
            for key in domingo_keys:
                hours = acum_horas.get(key, 0.0)
                if hours > 0:
                    reporte_str += f"    - {display_names[key]}: {hours:.2f}h\n"
                    empleado_horas_con_recargo += hours

            # Sección para horas de Festivo
            festivo_keys = [
                "horas_ordinarias_diurnas_festivo",
                "horas_ordinarias_nocturnas_festivo",
                "horas_extras_diurnas_festivo",
                "horas_extras_nocturnas_festivo",
            ]
            for key in festivo_keys:
                hours = acum_horas.get(key, 0.0)
                if hours > 0:
                    reporte_str += f"    - {display_names[key]}: {hours:.2f}h\n"
                    empleado_horas_con_recargo += hours


            total_empleado_horas = empleado_horas_con_recargo + empleado_horas_ordinarias_diurnas

            reporte_str += f"  Total Horas Acumuladas con Recargo para {empleado.nombre}: {empleado_horas_con_recargo:.2f}h\n"
            reporte_str += f"  Total de Todas las Horas Acumuladas para {empleado.nombre}: {total_empleado_horas:.2f}h\n\n"
            
            total_general_horas_con_recargo += empleado_horas_con_recargo
            total_general_todas_las_horas += total_empleado_horas

        reporte_str += "--- Resumen General Consolidado ---\n"
        reporte_str += f"Total General de Horas Acumuladas con Recargo: {total_general_horas_con_recargo:.2f}h\n"
        reporte_str += f"Total General de Todas las Horas Acumuladas (Recargo + Ordinarias): {total_general_todas_las_horas:.2f}h\n"
        reporte_str += "-----------------------------------------------------\n"

        return reporte_str

    def actualizar_porcentajes_recargo(self, nuevo_extra_diurna=None, nuevo_extra_nocturna=None,
                                        nuevo_extra_diurna_domingofestivo=None, nuevo_extra_nocturna_domingofestivo=None,
                                        nuevo_ordinaria_nocturna_recargo=None, nuevo_recargo_domingofestivo_diurno_base_recargo=None,
                                        nuevo_ordinaria_nocturna_domingofestivo_recargo=None,
                                        nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo=None,
                                        nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo=None):
        
        if nuevo_extra_diurna is not None:
            self.MULTIPLIER_HORA_EXTRA_DIURNA = nuevo_extra_diurna / 100.0
        if nuevo_extra_nocturna is not None:
            self.MULTIPLIER_HORA_EXTRA_NOCTURNA = nuevo_extra_nocturna / 100.0
        if nuevo_extra_diurna_domingofestivo is not None:
            self.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO = nuevo_extra_diurna_domingofestivo / 100.0
        if nuevo_extra_nocturna_domingofestivo is not None:
            self.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO = nuevo_extra_nocturna_domingofestivo / 100.0
        
        if nuevo_ordinaria_nocturna_recargo is not None:
            self.ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA = nuevo_ordinaria_nocturna_recargo / 100.0
        if nuevo_recargo_domingofestivo_diurno_base_recargo is not None:
            self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE = nuevo_recargo_domingofestivo_diurno_base_recargo / 100.0
        if nuevo_ordinaria_nocturna_domingofestivo_recargo is not None:
            self.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO = nuevo_ordinaria_nocturna_domingofestivo_recargo / 100.0
        if nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo is not None:
            self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA = nuevo_recargo_domingofestivo_diurno_larga_jornada_recargo / 100.0
        if nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo is not None:
            self.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA = nuevo_recargo_domingofestivo_nocturno_larga_jornada_recargo / 100.0

        return "Porcentajes de recargo actualizados con éxito."


def save_app_data(empleados, calculadora, filename="app_data.json"):
    data = {
        "empleados": {},
        "calculadora_config": {
            "MULTIPLIER_HORA_EXTRA_DIURNA": calculadora.MULTIPLIER_HORA_EXTRA_DIURNA,
            "MULTIPLIER_HORA_EXTRA_NOCTURNA": calculadora.MULTIPLIER_HORA_EXTRA_NOCTURNA,
            "MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO": calculadora.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO,
            "MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO": calculadora.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO,
            "ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA": calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA,
            "ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE": calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE,
            "ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO": calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO,
            "ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA": calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA,
            "ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA": calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA,
            "dias_festivos": [d.isoformat() for d in calculadora.dias_festivos]
        }
    }
    for nombre, empleado in empleados.items():
        data["empleados"][nombre] = {
            "nombre": empleado.nombre,
            "salario_mensual": empleado.salario_mensual,
            "standard_daily_hours": empleado.standard_daily_hours,
            "tipo_contrato": empleado.tipo_contrato, # Guardar el tipo_contrato
            "jornadas_registradas": [
                {
                    "fecha": j["fecha"].isoformat(),
                    "hora_entrada": j["hora_entrada"].isoformat(),
                    "hora_salida": j["hora_salida"].isoformat()
                } for j in empleado.jornadas_registradas
            ]
        }
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Datos de la aplicación guardados en {filename}")
    except IOError as e:
        print(f"Error al guardar los datos: {e}")

def load_app_data(filename="app_data.json"):
    empleados = {}
    calculadora = CalculadoraRecargos() # Inicializar con valores por defecto
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Cargar configuración de la calculadora
            config = data.get("calculadora_config", {})
            if "MULTIPLIER_HORA_EXTRA_DIURNA" in config:
                calculadora.MULTIPLIER_HORA_EXTRA_DIURNA = config["MULTIPLIER_HORA_EXTRA_DIURNA"]
            if "MULTIPLIER_HORA_EXTRA_NOCTURNA" in config:
                calculadora.MULTIPLIER_HORA_EXTRA_NOCTURNA = config["MULTIPLIER_HORA_EXTRA_NOCTURNA"]
            if "MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO" in config:
                calculadora.MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO = config["MULTIPLIER_EXTRA_DIURNA_DOMINGOFESTIVO"]
            if "MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO" in config:
                calculadora.MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO = config["MULTIPLIER_EXTRA_NOCTURNA_DOMINGOFESTIVO"]
            
            if "ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA" in config:
                calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA = config["ADDITIONAL_PERCENTAGE_DECIMAL_HORA_ORDINARIA_NOCTURNA"]
            if "ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE" in config:
                calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE = config["ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_BASE"]
            if "ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO" in config:
                calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO = config["ADDITIONAL_PERCENTAGE_DECIMAL_ORDINARIA_NOCTURNA_DOMINGOFESTIVO"]
            if "ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA" in config:
                calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA = config["ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_DIURNO_LARGA_JORNADA"]
            if "ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA" in config:
                calculadora.ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA = config["ADDITIONAL_PERCENTAGE_DECIMAL_RECARGO_DOMINGOFESTIVO_NOCTURNO_LARGA_JORNADA"]

            if "dias_festivos" in config:
                calculadora.dias_festivos = sorted([datetime.date.fromisoformat(d) for d in config["dias_festivos"]])

            # Cargar empleados de forma más segura
            for nombre_empleado_key, emp_data in data.get("empleados", {}).items():
                try:
                    # Usar .get() con valores por defecto o comprobaciones
                    nombre = emp_data.get("nombre")
                    salario_mensual = emp_data.get("salario_mensual")
                    standard_daily_hours = emp_data.get("standard_daily_hours", 8)
                    tipo_contrato = emp_data.get("tipo_contrato", "indefinido") # Añadir valor por defecto aquí

                    if not all([nombre, salario_mensual is not None]):
                        print(f"Advertencia: Datos incompletos para un empleado (nombre o salario mensual). Saltando entrada: {emp_data}")
                        continue # Saltar esta entrada si faltan datos esenciales

                    empleado = Empleado(nombre, salario_mensual, standard_daily_hours, tipo_contrato)
                    
                    jornadas_raw = emp_data.get("jornadas_registradas", [])
                    empleado.jornadas_registradas = []
                    for j in jornadas_raw:
                        try:
                            jornada_parsed = {
                                "fecha": datetime.date.fromisoformat(j["fecha"]),
                                "hora_entrada": datetime.time.fromisoformat(j["hora_entrada"]),
                                "hora_salida": datetime.time.fromisoformat(j["hora_salida"])
                            }
                            empleado.jornadas_registradas.append(jornada_parsed)
                        except (KeyError, ValueError) as je:
                            print(f"Advertencia: Jornada mal formada para empleado {nombre}. Saltando jornada: {j}. Error: {je}")
                            continue

                    empleados[nombre] = empleado
                except (KeyError, ValueError) as e:
                    print(f"Error al procesar datos de empleado '{nombre_empleado_key}': {e}. Saltando este empleado.")
                    continue

            print(f"Datos de la aplicación cargados desde {filename}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error al cargar los datos del archivo {filename}: {e}. Se iniciará con datos vacíos.")
    else:
        print(f"Archivo {filename} no encontrado. Se iniciará con datos vacíos.")
    
    return empleados, calculadora