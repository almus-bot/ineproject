import numpy as np
import pandas as pd
import os
import random



# Genera fechas de nacimiento aleatorias


""" Simulación de nacimientos para los años 2008-2012, segun nac_año. Simulado según el año y municipio
de nacimiento.

+ Número de nacimientos: valor aleatorio exponencial según el total de nacimientos para cada municipio en el año
+ Media de nacimientos diarios al año
+ Sexo del recién nacido según municipio y año 
+ Grupo de edad de la madre según municipio y año
+ Situación conyugal de la madre según el municipio y año

-> np.random.exponential(beta, tamaño)

beta = 1/lambda
lambda: tasa de nacimientos diarios = total del municipio / 365 
* Ajustar lambda si el año es bisiesto

Si 175 es el total de nacimientos de un año, la media diaria es lambda = 175/365 = 0.479.
beta = 1/lambda = 365/175 = 2.086

Siguiente nacimiento dentro de x días
x = np.random.exponential(2.086, 1)
"""

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
		fechas_nac[año]	= fechas # devuelve diccionario con las fechas nacimientos de cada año
	
	return fechas_nac

# Genera tabla principal a partir del diccionario de fechas de nacimiento
def gen_data(results):
	df = pd.DataFrame()
	for m in results:	
		l = []
		for año in results[m].values():
			l.extend(año)
	
		df = pd.concat([
			df,
			pd.DataFrame({"Estado":m[0], "Municipio":m[1],"Fechas" :l})],
			ignore_index=True)
	return df

# Generar los grupos de edad y los anexa a la tabla principal
def choose_group(tabla, grupos):
###
	ind = 0
	while ind < len(tabla):
		e =tabla.iloc[ind].Estado
		m =tabla.iloc[ind].Municipio

		t = tabla.loc[(tabla.Estado == e) & tabla.Municipio.isin([m])]
		g = grupos.loc[(grupos.estado == e) & grupos.municipio.isin([m])]		

		choices = random.choices(population=list(g.Grupo), weights=list(g.prob), k=len(t))
		tabla["Grupos de Edad"].loc[ind:(ind+len(t))] = choices

		ind += len(t)

# Genera el sexo de cada nacimiento y actualiza la tabla principal
def choose_sex(tabla, sexo):
	# posibles combinaciones de años y grupos en la tabla
	pares = tabla.loc[:,["Año","Grupos de Edad"]].drop_duplicates()

	for i in range(len(pares)):
		# para cada par año-grupo
		grupo_edad = pares.iloc[i]["Grupos de Edad"]
		y = pares.iloc[i].Año

		# elegir los registros que cumplan
		t = tabla.loc[(tabla.Año == y) & tabla["Grupos de Edad"].isin([grupo_edad])]
		s  = sexo.loc[(sexo.Año == y) & sexo.Grupo.isin([grupo_edad])]
		#sex.index = np.arange(len(sex))

		choices = random.choices(population=list(s.Sexo), weights=list(s.prob), k=len(t))
		
		# colocando los valores generados
		tabla["Sexo"].loc[t.index] = choices