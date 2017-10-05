results = {(nac_año.estado[i],nac_año.municipio[i]):gen.generate_birth_dates(nac_año.iloc[i]) for i in range(len(nac_año))}	

#results = {(nac_año.estado[i],nac_año.municipio[i]):gen.generate_birth_dates(nac_año.iloc[i]) for i in range(1,4)}	

# diff = {}
# # diferencias entre los nacimientos totales tabulados y los simulados
# for i in range(len(nac_año)):
# 	mun = nac_año.iloc[i]
# 	diff[(mun[0],mun[1])] = {total:abs(len(results[(mun[0],mun[1])][total]) - mun[total]) for total in results[(mun[0],mun[1])].keys()}

# print(diff)

# dataframe con estado-municipio-fechas
tabla = gen.gen_data(results)
tabla.columns = [i.lower() for i in tabla.columns]
tabla["año"] = [i.year for i in tabla["fechas"]]
tabla.to_pickle("../../data/processed/inedata-in.pkl")