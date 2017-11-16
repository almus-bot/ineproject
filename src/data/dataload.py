import numpy as np
import pandas as pd
import os
import generate as gen

print("cargando datos")
path = "../../data/interim/"
data_dict = {file[:len(file)-4]: pd.read_excel(path+file, sheetname="Sheet2") for file in os.listdir(path) if file.endswith(".xls")}

nacimientos = {i:data_dict[i] for i in data_dict.keys() if i.startswith("Na")}
mortalidad = {i:data_dict[i] for i in data_dict.keys() if i.startswith("Mort")}
matrimonios = {i:data_dict[i] for i in data_dict.keys() if i.startswith("Mat")}
suicidios = {i:data_dict[i] for i in data_dict.keys() if i.startswith("Sui")}
divorcios = {i:data_dict[i] for i in data_dict.keys() if i.startswith("Div")}

"""
limpieza y organización de los dataframes de nacimientos
"""

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


"""
limpieza y organización de los dataframes de Mortalidad 
DataFrame objetivo:  
	año entidad municipio sexo edad defunciones
"""

# limpiar espacios en entidades y municipios / long format
for i in mortalidad:
	mortalidad[i].entidad = mortalidad[i].entidad.map(lambda x: x.strip())
	mortalidad[i].entidad = mortalidad[i].entidad.map(lambda x: x.replace("Estado","").strip())


	if "municipio" in mortalidad[i].columns.values:
		mortalidad[i].municipio = mortalidad[i].municipio.map(lambda x: x.strip())
		mortalidad[i] = pd.melt(mortalidad[i], id_vars=["entidad", "municipio"], 
			value_vars=list(mortalidad[i].columns.values[2:]), 
			value_name="defunciones")
	else:
		mortalidad[i] = pd.melt(mortalidad[i], id_vars=["entidad"], 
			value_vars=list(mortalidad[i].columns.values[1:]), 
			value_name="defunciones", var_name="year")


# Defunciones registradas de hombres por año de registro, según entidad federal de ocurrencia, 2001 - 2012
mort_hombre = mortalidad['MortHombxAnoEntFedOcu']
# Defunciones registradas de mujeres por año de registro, según entidad federal de ocurrencia, 2001 - 2012
mort_mujer = mortalidad['MortMujxAnoEntFedOcu']
# Defunciones registradas por grupo de edad, según entidad federal de ocurrencia, 2012
#mort_edad =  mortalidad['MortGruEdad']
# Defunciones registradas por año de registro, según entidad federal y municipio de residencia habitual del fallecido, 2007-2012 
mort_year =  mortalidad['MortAnoRegistro']
# Defunciones registradas por grupo de edad, según entidad federal y municipiode residencia habitual del fallecido, 2012
mort_grupoe =  mortalidad['MortGruposEdad']
# Defunciones registradas por año de registro, según entidad federal de ocurrencia, 2001 - 2012
mort_entidad =  mortalidad['MortAnoRegEntFedOcu']

# ajustando nombres de columnas nuevas
mort_year.columns = mort_year.columns.str.replace("variable","year")
mort_grupoe.columns = mort_grupoe.columns.str.replace("variable","edad")

# Opcional: datos por año y sexo concatenados
# agregando identificador del sexo antes de concatenar
#mort_hombre["sexo"] = "H"
#mort_mujer["sexo"] = "M"
#mort_sexo = pd.concat([mort_hombre, mort_mujer])

## Nota: Las defunciones en mort_entidad, es la suma de las defunciones en hombre y mujer

"""
limpieza y organización de los dataframes de Divorcios
DataFrame objetivo:  
	año entidad municipio sexo edad defunciones
"""

# Divorcios
div_dur_hijos = divorcios["DivorSentDuraMatrNumHij"]
div_dur = divorcios["DivorSentDuraMatriEF"]
div_causa = divorcios["DivorCauFundSentEF"]
div_entidad = divorcios["Divorcios"]
