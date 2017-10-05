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
