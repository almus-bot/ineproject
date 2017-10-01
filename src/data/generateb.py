import numpy as np
import pandas as pd
import os

def generate_birth_dates(municipio_row):
	fechas_nac = {}
	for año in municipio_row[2:len(municipio_row)].index:
		# fecha inicial: primer día del año
		fechas = [pd.Timestamp(str(año) + "0101")]
		fechas.append(fechas[-1] + pd.to_timedelta(np.random.exponential(365/(municipio_row[año]), 1)[0], unit="D"))

		# genera fechas mientras la siguiente siga estando en el año actual
		while fechas[-1].year == fechas[-2].year:
			fechas.append(fechas[-1] + pd.to_timedelta(np.random.exponential(365/(municipio_row[año]),1)[0], unit="D"))

		fechas.pop()  # la última es del próximo año, no interesa
		fechas_nac[año]	= fechas
	
	return fechas_nac
