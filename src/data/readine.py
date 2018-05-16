import numpy as np
import pandas as pd
import os
import generate as gen

with open('dataload.py') as source_file:
	exec(source_file.read())

with open('maketable.py') as source_file:
	exec(source_file.read())

#### Generar el grupo de edad de la madre según municipio ####
## probabilidades para los grupos  ##
print("Probabilidades de grupos de edad")
nac_edad["total"] = nac_edad.iloc[:,2:].sum(axis=1)
# long format
grupos= pd.melt(nac_edad, id_vars=nac_edad.columns[0:2],
		 value_vars=nac_edad.columns[2:-1], var_name="grupo", value_name="nacimientos")
grupos["total"] = list(pd.concat([nac_edad["total"]]*len(grupos["grupo"].unique())))
grupos["prob"] = grupos["nacimientos"]/grupos["total"]
#tabla.index = np.arange(len(tabla))

# verifica que todos suman 1
grupos.drop(["total","nacimientos"], axis=1).groupby(["estado","municipio"]).sum()
#grupos = grupos.drop(["nacimientos","total"], axis=1)
grupos.to_pickle("../../data/processed/probedad.pkl")
grupos = grupos.drop(["nacimientos","total"], axis=1)

## probabilidades del sexo del niño ##
print("Probabilidades de sexo del niño")
# long format
sexo = pd.melt(nac_edad_sex, id_vars=nac_edad_sex.columns[0:3], 
		value_vars=nac_edad_sex.columns[3:], var_name="grupo", value_name="nacimientos")
sexo.columns = [i.lower() for i in sexo.columns]
# nacimientos totales agrupados por año y sexo
total_sexos = sexo.groupby([sexo.año, sexo.grupo]).sum()
total_sexos = total_sexos.reset_index()  # convertir en dataframe again
sexo["prob"] = sexo["nacimientos"]/sexo["total"]

# verifica que todos suman 1
sexo.drop(["total","nacimientos","grupo"], axis=1).groupby(["sexo","año"]).sum()
sexo.to_pickle("../../data/processed/probsexo.pkl")
sexo = sexo.drop(["nacimientos","total"], axis=1)
## probabilidades de la situación conyugal ##
print("Probabilidades de situación conyugal")		
sit_cony = pd.melt(nac_edad_cony, id_vars=["situación","total"], value_vars=nac_edad_cony.columns[2:], var_name="grupo", value_name="nacimientos")
sit_cony.grupo.loc[sit_cony.grupo == 15] = "Menos de 15"
sit_cony.nacimientos.loc[sit_cony.nacimientos == "-"] = 0
sit_cony["prob"] = sit_cony.nacimientos/sit_cony.total

#verifica que todos suman 1
sit_cony.drop(["total","nacimientos","grupo"], axis=1).groupby(["situación"]).sum()
sit_cony.to_pickle("../../data/processed/probsitcony.pkl")
sit_cony = sit_cony.drop(["nacimientos","total"], axis=1)

# generando la columna de grupos de edad
gen.choose_var(tabla, grupos, "estado","grupo","municipio")
tabla.to_pickle("../../data/processed/inedata-grupo.pkl")
# generando el sexo del niño 
gen.choose_var(tabla, sexo, "año","sexo","grupo")
tabla.to_pickle("../../data/processed/inedata-sexo.pkl")
# generando la situación conyugal y anexando a la tabla
gen.choose_var(tabla, sit_cony, "grupo", "situación")

# Guardando dataframe completo
print("Guardando datos en disco")
tabla.to_pickle("../../data/processed/inedata.pkl")

# cargar nuevamente
#ld = pd.read_pickle("../../data/processed/inedata.pkl")

#----

# calcular las proporciones para categorias y variables
def make_probs(data, tot_var):
    for i in data:
        var = data[i].columns[0]
        g = data[i].groupby("variable").sum()
        n = data[i][var].unique().size   # numero de categorias en la variable
        aux_df = pd.DataFrame(np.repeat(g[tot_var], n))
        df = aux_df.reset_index(drop=True)
        #cols = data[i].columns
       # data[i] = pd.concat([data[i], df], ignore_index=True, axis=1)

        data[i]["prob"] = data[i][tot_var]/df[tot_var]

# verificar que todas las proporciones den 1      
def verify_probs(data):
    for i in data:
        print(data[i].groupby(["variable"]).sum())

# falta probar que sirvan para los demas dataframes de nac mort matr, div    


        