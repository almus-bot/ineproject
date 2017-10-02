import pandas as pd
def gen_data(results):
	df = pd.DataFrame()
	for m in results:	
		l = []
		for año in results[m].values():
			l.extend(año)

		#dfaux = pd.DataFrame({"Estado":m[0], "Municipio":m[1],"Fechas" :l})
		df = pd.concat(
			df,
			pd.DataFrame({"Estado":m[0], "Municipio":m[1],"Fechas" :l}),
			ignore_index=True)
	return df