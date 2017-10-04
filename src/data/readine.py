import numpy as np
import pandas as pd
import os
import generate as gen

print("cargando datos")
path = "../../data/interim/"
data_dict = {file[:len(file)-4]: pd.read_excel(path+file, sheetname="Sheet2") for file in os.listdir(path) if file.endswith(".xls")}

#### limpieza y organización de los dataframes de nacimientos ####
nacimientos = {i:data_dict[i] for i in data_dict.keys() if i.startswith("Na")}

## nacimientos por año de registro, estado y municipio del 2008 al 2012
print("Nacimientos por año")
nac_año = nacimientos['NacimientosAnoRegistro']

# Dejar solo municipio libertador en Distrito capital # eliminando espacios en blanco de las cadenas
nac_año.municipio = nac_año.municipio.map(lambda x: x.strip())
nac_año.estado = nac_año.estado.map(lambda x: x.replace("Estado","").strip())
nac_año = nac_año[nac_año.municipio.isin(["Libertador"]) | ~nac_año.estado.isin(["Distrito Capital"])]
nac_año.index = np.arange(len(nac_año))

#### Nacimientos por sexo del niño, edad de la madre y año de registro 2006-2012
print("Nacimientos por sexo del niño")
nac_edad_sex = nacimientos['NatGEMadSexNinArReg']
# eliminando la columna de total
#nac_edad_sex = nac_edad_sex.drop("Total", axis=1)

# reemplazando "hombre y mujer" por M y F 2001-2012
nac_edad_sex.Sexo.replace(["Hombres","Mujeres"],["M","F"], inplace=True)

#### Nacimientos totales por estado 2001 - 2012
print("Nacimientos por entidad")
nac_ent = nacimientos['NatEntFedResMad']

#### Nacimientos por grupo de edad de la madre, estado y municipio de residencia sólo 2012
print("Nacimientos por grupo de edad")
nac_edad = nacimientos['NacimientosGruposEdad']
nac_edad.estado = nac_edad.estado.map(lambda x: x.replace("Estado","").strip())
nac_edad.municipio = nac_edad.municipio.map(lambda x: x.strip())
nac_edad = nac_edad.drop("total", axis=1)

#### Nacimientos por edad de la madre, situación conyugal solo 2012
print("Nacimientos por situación conyugal")
nac_edad_cony = nacimientos['NatGEMadSitConMad']
#nac_edad_cony = nac_edad_cony.drop("total", axis=1)
print("Datos cargados")

print("Creando fechas de nacimientos...")
# diccionario con las fechas por año de cada municipio (prueba solo de  1 a 4)
results = {(nac_año.estado[i],nac_año.municipio[i]):gen.generate_birth_dates(nac_año.iloc[i]) for i in range(1,4)}	

# prueba completa
#results = {(nac_año.estado[i],nac_año.municipio[i]):gen.generate_birth_dates(nac_año.iloc[i]) for i in range(len(nac_año))}	

# diff = {}
# # diferencias entre los nacimientos totales tabulados y los simulados
# for i in range(len(nac_año)):
# 	mun = nac_año.iloc[i]
# 	diff[(mun[0],mun[1])] = {total:abs(len(results[(mun[0],mun[1])][total]) - mun[total]) for total in results[(mun[0],mun[1])].keys()}

# print(diff)

# dataframe con estado-municipio-fechas
tabla = gen.gen_data(results)

#### Generar el grupo de edad de la madre según municipio ####

## probabilidades para los grupos  ##
print("Probabilidades de grupos de edad")
nac_edad["total"] = nac_edad.iloc[:,2:].sum(axis=1)
# long format
grupos= pd.melt(nac_edad, id_vars=nac_edad.columns[0:2], value_vars=nac_edad.columns[2:-1], var_name="Grupo", value_name="Nacimientos")
#grupos= pd.melt(nac_edad, id_vars=nac_edad.columns[0:3], value_vars=nac_edad.columns[3:-1], var_name="Grupo", value_name="Nacimientos")

# columna de totales
grupos["total"] = list(pd.concat([nac_edad["total"]]*len(grupos["Grupo"].unique())))
# columna de proporciones
grupos["prob"] = grupos["Nacimientos"]/grupos["total"]
tabla.index = np.arange(len(tabla))

# generando la columna de grupos de edad
gen.choose_var(tabla, grupos, "estado","grupo","municipio")

#### Generar el sexo del niño ####
print("Probabilidades de sexo del niño")
# formato largo para los datos del sexo
sexo = pd.melt(nac_edad_sex, id_vars=nac_edad_sex.columns[0:3], value_vars=nac_edad_sex.columns[3:], var_name="Grupo", value_name="Nacimientos")
# nacimientos totales agrupados por año y sexo
total_sexos = sexo.groupby([sexo.Año, sexo.Grupo]).sum()
total_sexos = total_sexos.reset_index()  # convertir en dataframe again
sexo["prob"] = sexo["Nacimientos"]/sexo["Total"]

# verifica que todos suman 1
sexo.drop(["Total","Nacimientos","Grupo"], axis=1).groupby(["Sexo","Año"]).sum()

# columna de fechas para acceder con comodidad
tabla["año"] = [i.year for i in tabla["fechas"]]
gen.choose_var(tabla, sexo, "año","sexo","grupo")

## verificar que sean proporciones parecidas a los datos reales.

#### Generar la situación conyugal ####		
print("Probabilidades de situación conyugal")		

sit_cony = pd.melt(nac_edad_cony, id_vars=["situación","total"], value_vars=nac_edad_cony.columns[2:], var_name="grupo", value_name="nacimientos")
sit_cony.grupo.loc[sit_cony.grupo == 15] = "Menos de 15"
sit_cony.nacimientos.loc[sit_cony.nacimientos == "-"] = 0
sit_cony["prob"] = sit_cony.nacimientos/sit_cony.total

#verifica que todos suman 1
sit_cony.drop(["total","nacimientos","grupo"], axis=1).groupby(["situación"]).sum()

# generando la situación conyugal y anexando a la tabla
gen.choose_var(tabla, sit_cony, "grupo", "situación")

# Guardando dataframe completo
print("Guardando datos en disco")
tabla.to_pickle("../../data/processed/inedata.pkl")

print(tabla.head(15))
#sexo.to_pickle("../../data/processed/probsexo.pkl")
#grupos.to_pickle("../../data/processed/probedad.pkl")
#sit_cony.to_pickle("../../data/processed/probsitcony.pkl")

# cargar nuevamente
#ld = pd.read_pickle("../../data/processed/inedata.pkl")