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
	print("Generando nacimientos")
	fechas_nac = {}
	print("para el municipio ", municipio_row["municipio"])
		
	for año in municipio_row[2:len(municipio_row)].index:
		print("para el año ",  año)
		# fecha inicial: primer día del año
		fechas = [pd.Timestamp(str(año) + "0101")]
		fechas.append(fechas[-1] + pd.to_timedelta(np.random.exponential(365/(municipio_row[año]), 1)[0], unit="D"))

		# genera fechas mientras la siguiente siga estando en el año actual
		while fechas[-1].year == fechas[-2].year:
			fechas.append(fechas[-1] + pd.to_timedelta(np.random.exponential(365/(municipio_row[año]),1)[0], unit="D"))

		fechas.pop()  # la última es del próximo año, no interesa
		fechas_nac[año]	= fechas # devuelve diccionario con las fechas nacimientos de cada año
		print("número de nacimientos generados: " ,len(fechas))
	print("Done")
	return fechas_nac

# Genera tabla principal a partir del diccionario de fechas de nacimiento
def gen_data(results):
	print("Generando tabla")
	df = pd.DataFrame()
	for m in results:	
		l = []
		for año in results[m].values():
			l.extend(año)
	
		df = pd.concat([
			df,
			pd.DataFrame({"Estado":m[0], "Municipio":m[1],"Fechas" :l})],
			ignore_index=True)
	print("Done")
	return df

# tabla = tabla principal
# grupos = dataframe con la variable de interés agrupada y sus probabilidades
# col1 = columna para subsección
# col2 = columna para subsección
# var = nombre de la variable a generar
# *todos los nombres de columna en minúsculas
def choose_var(tabla, grupos, col1, var, col2=-1):

	col1, var = col1.lower(), var.lower()
	tabla[var] = "-"
	print("Generando ", var)
	emergency_g = grupos[var].unique()
	emergency_p = [1/len(emergency_g)]*len(emergency_g)
	
	if col2==-1:
		pares = tabla.loc[:,[col1]].drop_duplicates()
		print("pares creados, sin duplicados")
		pares.index = np.arange(len(pares))
		print("inicia bucle para cada par")
		for i in range(len(pares)):
			c1 = pares.iloc[i][col1]
			t = tabla.loc[tabla[col1] == c1]
			g = grupos.loc[grupos[col1] == c1]	
			if not g.empty:
				print("genera choices")	
				print("asigna a la tabla")
				print(g.prob, "sum:", g.prob.sum())
				choices = random.choices(population=list(g[var]), weights=list(g.prob), k=len(t))
				#tabla["Grupos de Edad"].loc[ind:(ind+len(t))] = choices
				tabla[var].loc[t.index] = choices

			else:
				print("problema en ", c1)
				print("grupos ", g)
				choices = random.choices(population=list(emergency_g), weights=list(emergency_p), k=len(t))
				#continue
				print("asigna a la tabla")
				tabla[var].loc[t.index] = choices
		print("Done")
	else:
		col2 = col2.lower()
		pares = tabla.loc[:,[col1,col2]].drop_duplicates()
		print("pares creados, sin duplicados")
		pares.index = np.arange(len(pares))
		print("inicia bucle para cada par")
		for i in range(len(pares)):

			c1 =pares.iloc[i][col1]
			c2 =pares.iloc[i][col2]
			t = tabla.loc[(tabla[col1] == c1) & tabla[col2].isin([c2])]
			g = grupos.loc[(grupos[col1] == c1) & grupos[col2].isin([c2])]	
			if not g.empty:
				print("genera choices")
				print(g.prob, "\n sum: ", g.prob.sum())
				choices = random.choices(population=list(g[var]), weights=list(g.prob), k=len(t))
				#tabla["Grupos de Edad"].loc[ind:(ind+len(t))] = choices
				print("asigna a la tabla")
				tabla[var].loc[t.index] = choices
			else:
				print("problema en ", c1 , c2)
				print("grupos ", g)
				choices = random.choices(population=list(emergency_g), weights=list(emergency_p), k=len(t))
				#continue
				print("asigna a la tabla")
				tabla[var].loc[t.index] = choices
		print("Done")
		