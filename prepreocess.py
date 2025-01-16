import pandas as pd
import folium
import matplotlib.pyplot as plt
import numpy as np
from folium.plugins import HeatMap
import seaborn as sns
import matplotlib.ticker as ticker

# Llegim dades principals
file_name = 'NY-House-Dataset.csv'
data = pd.read_csv(file_name)

# Localitats uniques
print(data['LOCALITY'].unique())

# Buscades a Google
borough_coordinates = {
    'Bronx': {'Latitude': 40.84676, 'Longitude': -73.873207},
    'Brooklyn': {'Latitude':40.65083, 'Longitude': -73.94972},
    'Manhattan': {'Latitude': 40.728333333333, 'Longitude': -73.994166666667},
    'Queens': {'Latitude': 40.704166666667, 'Longitude': -73.917777777778},
    'Staten Island': {'Latitude': 40.576280555556, 'Longitude': -74.144838888889}
}

# Coordenades auxiliars
coordinates_df = pd.DataFrame.from_dict(borough_coordinates, orient='index').reset_index()
coordinates_df.columns = ['Borough', 'Latitude', 'Longitude']

# Carreguem el dataset auxiliar
aux_dataset = pd.read_csv("Neighborhood_Financial_Health_Digital_Mapping_and_Data_Tool_20250114.csv")

# Agreguem mètriques
aggregated_df = aux_dataset.groupby('Borough').agg({
    'NYC_Poverty_Rate': 'mean',  
    'Median_Income': 'mean'
}).reset_index()

# Afegim coordenades per amostrar més fàcilment
aggregated_df = aggregated_df.merge(coordinates_df, on='Borough', how='left')

# Preprocessat de les dades
critical_columns = ["PRICE", "PROPERTYSQFT", "LATITUDE", "LONGITUDE", "BEDS", "BATH"]
data = data.dropna(subset=critical_columns)
data = data[(data["PRICE"] > 0) & (data["PROPERTYSQFT"] > 0)]
data = data[data["PRICE"] != data["PRICE"].max()]

price_min = data["PRICE"].min()
price_max = data["PRICE"].max()

max_sqft = data["PROPERTYSQFT"].max()
max_beds = data["BEDS"].max()
max_bath = data["BATH"].max()

# Mètrica custom, quan habitable és una casa, en funcó de sqft, llits i banys
data["LIVABILITY_SCORE"] = (
    (data["PROPERTYSQFT"] / max_sqft * 5) + 
    (data["BEDS"] / max_beds * 3) + 
    (data["BATH"] / max_bath * 2) 
)

data["LIVABILITY_SCORE_NORMALIZED"] = (
    (data["LIVABILITY_SCORE"] - data["LIVABILITY_SCORE"].min()) /
    (data["LIVABILITY_SCORE"].max() - data["LIVABILITY_SCORE"].min())
)

# Mètrica que determina valor d'una casa (preu/livability_score)
data["WORTH_IT_METRIC"] = data["PRICE"] / data["LIVABILITY_SCORE_NORMALIZED"]

# Normalitzem
min_worth = data["WORTH_IT_METRIC"].min()
max_worth = data["WORTH_IT_METRIC"].max()
data["NORMALIZED_WORTH_IT_METRIC"] = (data["WORTH_IT_METRIC"] - min_worth) / (max_worth - min_worth)

# Preu per metre quadrat
data["PRICE_PER_SQM"] = data["PRICE"] / data["PROPERTYSQFT"]
data["PRICE_PER_SQM"] = data["PRICE_PER_SQM"].fillna(0)

# Normalitzem
data["NORMALIZED_PRICE_PER_SQM"] = (data["PRICE_PER_SQM"] - data["PRICE_PER_SQM"].min()) / (data["PRICE_PER_SQM"].max() - data["PRICE_PER_SQM"].min())

# Possibles NA
data = data.dropna()

mean_price_per_type = data.groupby('TYPE')['PRICE'].mean()

# Mètriques auxiliars
incomex20 = aggregated_df['Median_Income'] * 20
incomex5 = (aggregated_df['Median_Income']) * 5

# Plot que ensenya preu mitjà comaprat amb ingresos reals
plt.figure(figsize=(14, 8))
sns.barplot(x=mean_price_per_type.index, y=mean_price_per_type.values, color='blue', label='Preu mitjà per tipus de vivenda')
plt.bar("Diners en 20 anys", incomex20, alpha=0.6, label='Income * 20', color='green')
plt.bar("Diners realistes en 20 anys", incomex5, alpha=0.6, label='Income * 10', color='red')
plt.title('Comparació de preu mitjà per tipus de vivenda, amb diners guanys realistes i en 20 anys')
plt.xlabel('Tipus de vivenda')
plt.ylabel('Valor')
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('mean_income_and_price_comparison.png', dpi=1200)

# Plot que ensenya preu mitjà per metre quadrat per barri
plt.figure(figsize=(16, 15))
data.boxplot(column="PRICE_PER_SQM", by="SUBLOCALITY", vert=False)
plt.title("Preu per metre quadrat segons barri")
plt.suptitle("")
plt.xlabel("Preu per metre quadrat")
plt.ylabel("Barri")
plt.tight_layout()
plt.savefig("price_per_sqm_boxplot.png", dpi=1200)
plt.close()

# Quan habitable és un pis comparat amb el seu preu
plt.figure(figsize=(20, 10))
plt.scatter(data["LIVABILITY_SCORE_NORMALIZED"], data["PRICE"], alpha=0.6, c=data["NORMALIZED_WORTH_IT_METRIC"], cmap="viridis")
plt.colorbar(label="Mereix la pena?")
plt.title("Preu vs. Habitabilitat")
plt.xlabel("Puntuació d'Habitabilitat")
plt.ylabel("Preu")
plt.grid(True)
plt.savefig("price_vs_livability_score.png", dpi=1200)
plt.close()

# Preu mitjà per barri
avg_price_by_neighborhood = data.groupby("SUBLOCALITY")["PRICE"].mean().sort_values(ascending=False)
plt.figure(figsize=(12, 6))
avg_price_by_neighborhood.plot(kind="bar", color="skyblue")
plt.title("Preu Mitjà per Barri")
plt.ylabel("Preu Mitjà")
plt.xlabel("Barri")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("average_price_by_neighborhood.png", dpi=1200)
plt.close()


# Dividim preus en intervals (logaritmics per les diferències)
data["LOG_PRICE"] = np.log1p(data["PRICE"])
# Categories
bins = pd.cut(data["LOG_PRICE"], bins=5, labels=["Very Low", "Low", "Medium", "High", "Very High"])

# Intervals
data["PRICE_RANGE"] = bins

color_mapping = {
    "Very Low": "green",
    "Low": "blue",
    "Medium": "orange",
    "High": "purple",
    "Very High": "red"
}

# Mapa amb totes les cases classificades per preu
overall_center = [data["LATITUDE"].mean(), data["LONGITUDE"].mean()]
base_map = folium.Map(location=overall_center, zoom_start=10)

for price_range, color in color_mapping.items():
    filtered_data = data[data["PRICE_RANGE"] == price_range]

    if not filtered_data.empty:
        price_layer = folium.FeatureGroup(name=price_range, show=True)
        
        # Marcadors
        for _, row in filtered_data.iterrows():
            folium.Marker(
                location=[row["LATITUDE"], row["LONGITUDE"]],
                popup=f"Price: {row['PRICE']}, Range: {row['PRICE_RANGE']}",
                icon=folium.Icon(color=color)
            ).add_to(price_layer)
        
        # Afegim capa
        price_layer.add_to(base_map)

# Controlem toogles
folium.LayerControl().add_to(base_map)

# Html
base_map.save("NY_House_Map_Interactive.html")



# Mapa de calor per a veure concentració preus
overall_center = [data["LATITUDE"].mean(), data["LONGITUDE"].mean()]
base_map = folium.Map(location=overall_center, zoom_start=10)

for price_range, color in color_mapping.items():
    filtered_data = data[data["PRICE_RANGE"] == price_range]

    if not filtered_data.empty:
        heatmap_data = filtered_data[["LATITUDE", "LONGITUDE", "LOG_PRICE"]].values.tolist()
        heatmap_layer = folium.FeatureGroup(name=f"Heatmap: {price_range}", show=True)
        
        HeatMap(
            heatmap_data,
            radius=20,
            blur=15, 
            max_zoom=10,
        ).add_to(heatmap_layer)
        
        # Capes
        heatmap_layer.add_to(base_map)

# Toogle capes
folium.LayerControl().add_to(base_map)
base_map.save("NY_House_Price_Heatmap_Interactive.html")


# Mapa habitabilitat i mereix la pena
overall_center = [data["LATITUDE"].mean(), data["LONGITUDE"].mean()]
base_map = folium.Map(location=overall_center, zoom_start=10)

livability_heatmap_data = data[["LATITUDE", "LONGITUDE", "LIVABILITY_SCORE_NORMALIZED"]].values.tolist()
worth_it_heatmap_data = data[["LATITUDE", "LONGITUDE", "NORMALIZED_WORTH_IT_METRIC"]].values.tolist()


livability_layer = folium.FeatureGroup(name="Heatmap: Livability Score", show=True)
HeatMap(
    livability_heatmap_data,
    radius=15, 
    blur=10,
    max_zoom=10
).add_to(livability_layer)
livability_layer.add_to(base_map)

worth_it_layer = folium.FeatureGroup(name="Heatmap: Worth It Metric", show=False)
HeatMap(
    worth_it_heatmap_data,
    radius=15, 
    blur=10,
    max_zoom=10
).add_to(worth_it_layer)
worth_it_layer.add_to(base_map)

# Toogle
folium.LayerControl().add_to(base_map)
base_map.save("NY_House_Metrics_Heatmaps.html")




# Mapa pobressa i income
overall_center = [aggregated_df["Latitude"].mean(), aggregated_df["Longitude"].mean()]
base_map = folium.Map(location=overall_center, zoom_start=10)

poverty_rate_heatmap_data = aggregated_df[["Latitude", "Longitude", "NYC_Poverty_Rate"]].values.tolist()

median_income_heatmap_data = aggregated_df[["Latitude", "Longitude", "Median_Income"]].values.tolist()

poverty_rate_layer = folium.FeatureGroup(name="Heatmap: Poverty Rate", show=True)
HeatMap(
    poverty_rate_heatmap_data,
    radius=15,
    blur=10,
    max_zoom=10
).add_to(poverty_rate_layer)
poverty_rate_layer.add_to(base_map)

median_income_layer = folium.FeatureGroup(name="Heatmap: Median Income", show=False)
HeatMap(
    median_income_heatmap_data,
    radius=15, 
    blur=10,
    max_zoom=10
).add_to(median_income_layer)
median_income_layer.add_to(base_map)

folium.LayerControl().add_to(base_map)
base_map.save("NYC_Poverty_Income_Heatmaps.html")
