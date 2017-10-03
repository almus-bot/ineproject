import numpy as np
import pandas as pd
import os
import generate as gen

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

# diccionario con las fechas por año de cada municipio (prueba solo de  1 a 4)
results = {(nac_año.estado[i],nac_año.municipio[i]):gen.generate_birth_dates(nac_año.iloc[i]) for i in range(1,4)}	

diff = {}
# diferencias entre los nacimientos totales tabulados y los simulados
for i in range(len(nac_año)):
	mun = nac_año.iloc[i]
	diff[(mun[0],mun[1])] = {total:abs(len(results[(mun[0],mun[1])][total]) - mun[total]) for total in results[(mun[0],mun[1])].keys()}

print(diff)

# dataframe con estado-municipio-fechas
tabla = gen.gen_data(results)

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
tabla["Grupos de Edad"] = "-"  # columna de grupos vacía
tabla.index = np.arange(len(tabla))

# generando la columna de grupos de edad
gen.choose_group(tabla,grupos)

#### Generar el sexo del niño ####

# formato largo para los datos del sexo
sexo = pd.melt(nac_edad_sex, id_vars=nac_edad_sex.columns[0:2], value_vars=nac_edad_sex.columns[2:-1], var_name="Grupo", value_name="Nacimientos")

#sexgroup = sexo.groupby([sexo.Año, sexo.Grupo])
# nacimientos totales agrupados por año y sexo
total_sexos = sexo.groupby([sexo.Año, sexo.Grupo]).sum()
total_sexos = total_sexos.reset_index()  # convertir en dataframe again
sexo["total"] = "-"   # columna vacía para los totales

# asignando los totales en la tabla principal de sexos
for i in range(len(total_sexos)):
	sexo.total.loc[
			(sexo.Año == total_sexos.Año[i]) 
			& sexo["Grupo"].isin([total_sexos.Grupo[i]])] = total_sexos.Nacimientos[i]

# calculando y anexando las probabilidades
sexo["prob"] = sexo["Nacimientos"]/sexo["total"]
tabla["Sexo"] = "-"
 # columna de fechas para acceder con comodidad
tabla["Año"] = [i.year for i in tabla["Fechas"]]
 
gen.choose_sex(tabla,sexo)

## verificar que sean proporciones parecidas a los datos reales.

#### Generar la situación conyugal ####				
