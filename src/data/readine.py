import numpy as np
import pandas as pd
import os

path = "../../data/interim/"
data_dict = {file[:len(file)-4]: pd.read_excel(path+file, sheetname="Sheet2") for file in os.listdir(path) if file.endswith(".xls")}

#### limpieza y organización de los dataframes de nacimientos ####
nacimientos = {i:data_dict[i] for i in data_dict.keys() if i.startswith("Na")}

#### nacimientos por año de registro, estado y municipio del 2008 al 2012
nac_año = nacimientos['NacimientosAnoRegistro']

# Dejar solo municipio libertador en Distrito capital
# eliminando espacios en blanco de las cadenas
nac_año.municipio = nac_año.municipio.map(lambda x: x.strip())
nac_año.estado = nac_año.estado.map(lambda x: x.strip())

nac_año = nac_año[nac_año.municipio.isin(["Libertador"]) | ~nac_año.estado.isin(["Distrito Capital"])]
nac_año.index = np.arange(len(nac_año))

# Sólo el nombre del estado (sin la palabra ESTADO y sin espacios)
nac_año.estado = nac_año.estado.map(lambda x: x.replace("Estado","").strip())

#### Nacimientos por sexo del niño, edad de la madre y año de registro 2006-2012
nac_edad_sex = nacimientos['NatGEMadSexNinArReg']

# eliminando la columna de total
nac_edad_sex = nac_edad_sex.drop("Total", axis=1)

# reemplazando "hombre y mujer" por M y F 2001-2012
nac_edad_sex.Sexo.replace(["Hombres","Mujeres"],["M","F"], inplace=True)

#### Nacimientos totales por estado 2001 - 2012
nac_ent = nacimientos['NatEntFedResMad']

#### Nacimientos por grupo de edad de la madre, estado y municipio de residencia sólo 2012
nac_edad = nacimientos['NacimientosGruposEdad']
nac_edad.estado = nac_edad.estado.map(lambda x: x.replace("Estado","").strip())
nac_edad.municipio = nac_edad.municipio.map(lambda x: x.strip())
nac_edad = nac_edad.drop("total", axis=1)

#### Nacimientos por edad de la madre, situación conyugal solo 2012
nac_edad_cony = nacimientos['NatGEMadSitConMad']
nac_edad_cony = nac_edad_cony.drop("total", axis=1)

### nacim fecha estado mcipio sexo grupo_edad sit_conyugal ###
nac_año.columns
nac_ent.columns
nac_edad_sex.columns
nac_edad.columns

print("-> data loaded")

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

# Generar fechas aleatorias para los nacimientos de cada municipio
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
	
	return fechas_nac  # devuelve diccionario con las fechas nacimientos de cada año

# diccionario con las fechas por año de cada municipio
results = {(nac_año.estado[i],nac_año.municipio[i]):generate_birth_dates(nac_año.iloc[i]) for i in range(1,4)}	
diff = {}

# diferencias entre los nacimientos totales tabulados y los simulados
for i in range(len(nac_año)):
	mun = nac_año.iloc[i]
	diff[(mun[0],mun[1])] = {total:abs(len(results[(mun[0],mun[1])][total]) - mun[total]) for total in results[(mun[0],mun[1])].keys()}

print(diff)

# dataframe con estado-municipio-fechas
def gen_data(results):
	df = pd.DataFrame()
	for m in results:	
		l = []
		for año in results[m].values():
			l.extend(año)

		#dfaux = pd.DataFrame({"Estado":m[0], "Municipio":m[1],"Fechas" :l})
		df = pd.concat([
			df,
			pd.DataFrame({"Estado":m[0], "Municipio":m[1],"Fechas" :l})],
			ignore_index=True)
	return df

tabla = gen_data(results)

#### generar el grupo de edad de la madre según municipio ####

## probabilidades para los grupos  ##

nac_edad["total"] = nac_edad.iloc[:,2:].sum(axis=1)

# long format
grupos= pd.melt(nac_edad, id_vars=nac_edad.columns[0:2], value_vars=nac_edad.columns[2:-1], var_name="Grupo", value_name="Nacimientos")

# columna de totales
t = pd.concat([nac_edad["total"]]*len(grupos["Grupo"].unique()))
grupos["total"] = list(t)

# columna de proporciones
grupos["prob"] = grupos["Nacimientos"]/grupos["total"]

# asignar grupo
import random
tabla["Grupos de Edad"] = "-"  # columna de grupos vacía
tabla.index = np.arange(len(tabla))

def choose_group(tabla, grupos):
###
	ind = 0
	while ind < len(tabla):
		e =tabla.iloc[ind].Estado
		m =tabla.iloc[ind].Municipio

		t = tabla[tabla.Estado==e]
		t = t[t.Municipio==m]
		
		g = grupos[grupos.estado==e]
		g = g[g.municipio==m]

		choices = random.choices(population=list(g.Grupo), weights=list(g.prob), k=len(t))
		tabla["Grupos de Edad"][ind:(ind+len(t))] = choices

		ind += len(t)

# generando la columna de grupos de edad
choose_group(tabla, grupos)


#### Generar el sexo del niño ####
#### Generar la situación conyugal ####
