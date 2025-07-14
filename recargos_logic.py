# recargos_logic.py

import datetime

class Empleado:
    # ... (todo el código de la clase Empleado) ...
    def __init__(self, nombre, salario_mensual, tipo_contrato="indefinido"):
        self.nombre = nombre
        self.salario_mensual = salario_mensual
        self.tipo_contrato = tipo_contrato
        self.historial_jornadas = []

    def calcular_valor_hora_ordinaria(self):
        horas_mes = 30 * 8
        return self.salario_mensual / horas_mes

    def registrar_jornada(self, fecha, horas_ordinarias_domingo_festivo=0,
                           horas_extras_diurnas_domingo_festivo=0,
                           horas_extras_nocturnas_domingo_festivo=0):
        self.historial_jornadas.append({
            "fecha": fecha,
            "horas_ordinarias_domingo_festivo": horas_ordinarias_domingo_festivo,
            "horas_extras_diurnas_domingo_festivo": horas_extras_diurnas_domingo_festivo,
            "horas_extras_nocturnas_domingo_festivo": horas_extras_nocturnas_domingo_festivo
        })
        return f"Jornada registrada para {self.nombre} el {fecha.strftime('%Y-%m-%d')}."


class CalculadoraRecargos:
    # ... (todo el código de la clase CalculadoraRecargos) ...
    def __init__(self):
        self.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO = 0.75
        self.PORCENTAJE_HORA_EXTRA_DIURNA = 0.25
        self.PORCENTAJE_HORA_EXTRA_NOCTURNA = 0.75
        self.PORCENTAJE_HORA_NOCTURNA_ORDINARIA = 0.35

        # Días festivos de Colombia (pueden ser actualizados manualmente o desde una API externa)
        # Formato: (año, mes, día)
        self.dias_festivos = [
            datetime.date(2025, 1, 1), # Año Nuevo
            datetime.date(2025, 1, 6),# Día de Reyes Magos
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

    def es_domingo_o_festivo(self, fecha):
        return fecha.weekday() == 6 or fecha in self.dias_festivos

    def calcular_recargo_jornada(self, empleado, jornada):
        # ... (código existente) ...
        fecha = jornada["fecha"]
        if not self.es_domingo_o_festivo(fecha):
            return 0.0, 0.0, "No aplica recargo dominical/festivo."

        valor_hora_base = empleado.calcular_valor_hora_ordinaria()
        recargo_total = 0.0
        horas_recargo = 0.0
        detalle_calculo = []

        # Horas ordinarias en domingo/festivo (recargo del 75%)
        horas_ord = jornada["horas_ordinarias_domingo_festivo"]
        if horas_ord > 0:
            recargo_ordinario = horas_ord * valor_hora_base * (1 + self.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO)
            recargo_total += recargo_ordinario
            horas_recargo += horas_ord
            detalle_calculo.append(f"{horas_ord} hrs. ordinarias: ${recargo_ordinario:,.2f}")

        # Horas extras diurnas en domingo/festivo (recargo del 75% + 25% = 100%)
        horas_extra_diurna = jornada["horas_extras_diurnas_domingo_festivo"]
        if horas_extra_diurna > 0:
            recargo_extra_diurna = horas_extra_diurna * valor_hora_base * (1 + self.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO + self.PORCENTAJE_HORA_EXTRA_DIURNA)
            recargo_total += recargo_extra_diurna
            horas_recargo += horas_extra_diurna
            detalle_calculo.append(f"{horas_extra_diurna} hrs. extra diurnas: ${recargo_extra_diurna:,.2f}")

        # Horas extras nocturnas en domingo/festivo (recargo del 75% + 75% = 150%)
        horas_extra_nocturna = jornada["horas_extras_nocturnas_domingo_festivo"]
        if horas_extra_nocturna > 0:
            recargo_extra_nocturna = horas_extra_nocturna * valor_hora_base * (1 + self.PORCENTAJE_RECARGO_DOMINICAL_FESTIVO + self.PORCENTAJE_HORA_EXTRA_NOCTURNA)
            recargo_total += recargo_extra_nocturna
            horas_recargo += horas_extra_nocturna
            detalle_calculo.append(f"{horas_extra_nocturna} hrs. extra nocturnas: ${recargo_extra_nocturna:,.2f}")

        return recargo_total, horas_recargo, "; ".join(detalle_calculo)


    def generar_reporte_empleado(self, empleado):
        # ... (código existente, asegúrate de que retorna un string) ...
        reporte_str = f"--- Reporte de Recargos para {empleado.nombre} ---\n"
        reporte_str += f"Salario Mensual: ${empleado.salario_mensual:,.2f}\n"
        reporte_str += f"Valor Hora Ordinaria: ${empleado.calcular_valor_hora_ordinaria():,.2f}\n"

        total_recargos_empleado = 0.0
        total_horas_recargo_empleado = 0.0

        if not empleado.historial_jornadas:
            reporte_str += "No se han registrado jornadas para este empleado.\n"
            return reporte_str

        for jornada in empleado.historial_jornadas:
            fecha = jornada["fecha"]
            recargo, horas_recargo, detalle = self.calcular_recargo_jornada(empleado, jornada)
            if recargo > 0:
                reporte_str += f" Fecha: {fecha.strftime('%Y-%m-%d')}\n"
                reporte_str += f"   Horas Ordinarias D/F: {jornada['horas_ordinarias_domingo_festivo']}\n"
                reporte_str += f"   Horas Extras Diurnas D/F: {jornada['horas_extras_diurnas_domingo_festivo']}\n"
                reporte_str += f"   Horas Extras Nocturnas D/F: {jornada['horas_extras_nocturnas_domingo_festivo']}\n"
                reporte_str += f"   Recargo Calculado: ${recargo:,.2f}\n"
                reporte_str += f"   Detalle: {detalle}\n"
                total_recargos_empleado += recargo
                total_horas_recargo_empleado += horas_recargo
            elif self.es_domingo_o_festivo(fecha) and \
                 (jornada['horas_ordinarias_domingo_festivo'] == 0 and
                  jornada['horas_extras_diurnas_domingo_festivo'] == 0 and
                  jornada['horas_extras_nocturnas_domingo_festivo'] == 0):
                reporte_str += f" Fecha: {fecha.strftime('%Y-%m-%d')} - Sin horas dominicales/festivas registradas.\n"


        reporte_str += f"\nTotal Recargos Acumulados para {empleado.nombre}: ${total_recargos_empleado:,.2f}\n"
        reporte_str += f"Total Horas con Recargo para {empleado.nombre}: {total_horas_recargo_empleado:.2f} horas\n"
        reporte_str += "-----------------------------------------------------\n"
        return reporte_str


    def generar_reporte_consolidado(self, lista_empleados, periodo_inicio=None, periodo_fin=None):
        # ... (código existente, asegúrate de que retorna un string) ...
        reporte_str = "--- Reporte Consolidado de Recargos ---\n"
        if periodo_inicio and periodo_fin:
            reporte_str += f"Período: {periodo_inicio.strftime('%Y-%m-%d')} a {periodo_fin.strftime('%Y-%m-%d')}\n"
        else:
            reporte_str += "Período: Todo el historial\n"

        total_recargos_empresa = 0.0
        total_horas_recargo_empresa = 0.0

        for empleado in lista_empleados:
            recargos_empleado_periodo = 0.0
            horas_recargo_empleado_periodo = 0.0

            for jornada in empleado.historial_jornadas:
                fecha = jornada["fecha"]
                if (periodo_inicio is None or fecha >= periodo_inicio) and \
                   (periodo_fin is None or fecha <= periodo_fin):
                    recargo, horas_recargo, _ = self.calcular_recargo_jornada(empleado, jornada)
                    recargos_empleado_periodo += recargo
                    horas_recargo_empleado_periodo += horas_recargo

            if recargos_empleado_periodo > 0:
                reporte_str += f" Empleado: {empleado.nombre}\n"
                reporte_str += f"   Recargos en el período: ${recargos_empleado_periodo:,.2f}\n"
                reporte_str += f"   Horas con recargo en el período: {horas_recargo_empleado_periodo:.2f} horas\n"
                total_recargos_empresa += recargos_empleado_periodo
                total_horas_recargo_empresa += horas_recargo_empleado_periodo

        if total_recargos_empresa == 0:
            reporte_str += "No se encontraron recargos en el período especificado.\n"
        else:
            reporte_str += f"\nTotal General de Recargos para la Empresa: ${total_recargos_empresa:,.2f}\n"
            reporte_str += f"Total General de Horas con Recargo para la Empresa: {total_horas_recargo_empresa:.2f} horas\n"
        reporte_str += "---------------------------------------------\n"
        return reporte_str


    def agregar_dia_festivo(self, fecha):
        # ... (código existente) ...
        if fecha not in self.dias_festivos:
            self.dias_festivos.append(fecha)
            self.dias_festivos.sort() # Mantener la lista ordenada
            return f"Día festivo {fecha.strftime('%Y-%m-%d')} agregado."
        else:
            return f"El día {fecha.strftime('%Y-%m-%d')} ya está en la lista de festivos."

    def eliminar_dia_festivo(self, fecha):
        # ... (código existente) ...
        if fecha in self.dias_festivos:
            self.dias_festivos.remove(fecha)
            return f"Día festivo {fecha.strftime('%Y-%m-%d')} eliminado."
        else:
            return f"El día {fecha.strftime('%Y-%m-%d')} no se encontró en la lista de festivos."

    def actualizar_porcentajes_recargo(self, nuevo_porcentaje_dominical=None,
                                       nuevo_porcentaje_extra_diurna=None,
                                       nuevo_porcentaje_extra_nocturna=None):
        # ... (código existente) ...
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
        return "\n".join(mensajes) if mensajes else "Ningún porcentaje fue actualizado."