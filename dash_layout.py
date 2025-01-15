import dash
from dash import html, dcc
import folium
from folium.plugins import HeatMap
import os
import base64
import plotly.graph_objects as go


# Funció per a carregar mapes de folium
def load_folium_map(map_filename):
    if os.path.exists(map_filename):
        return html.Iframe(
            id=f'map-{map_filename}',
            srcDoc=open(map_filename, "r").read(),
            width='100%',
            height='800',
            style={'border': '1px solid black', 'margin-bottom': '20px'}
        )
    else:
        return html.Div(f"Map file {map_filename} not found.", style={'color': 'red', 'margin': '20px'})

# Crear app
app = dash.Dash(__name__)

# Preparació imatges
price_sqm = 'price_per_sqm_boxplot.png'
price_sqm64 = base64.b64encode(open(price_sqm, 'rb').read()).decode('ascii')

price_liv = 'price_per_sqm_boxplot.png'
price_liv64 = base64.b64encode(open(price_liv, 'rb').read()).decode('ascii')

mean_income = 'mean_income_and_price_comparison.png'
mean_income64 = base64.b64encode(open(mean_income, 'rb').read()).decode('ascii')

scatter = 'price_vs_livability_score.png'
scatter64 = base64.b64encode(open(scatter, 'rb').read()).decode('ascii')
# App, amb divisors HTML per a cada visualització
app.layout = html.Div([  
    # Index 
    html.Div([  
        html.H2("Dashboard Index", style={  
            'text-align': 'center',  
            'font-size': '36px',
            'color': '#333',  
            'margin-bottom': '20px'
        }),  
        html.Div([  
            html.A('Anar al mapa 1: Mapa calor mètriques custom', href='#map1', style={'font-size': '22px', 'color': '#007BFF', 'display': 'block', 'margin-bottom': '5px'}),  
            html.A('Anar al mapa 2: Preus per rangs', href='#map2', style={'font-size': '22px', 'color': '#007BFF', 'display': 'block', 'margin-bottom': '5px'}),  
            html.A('Anar al mapa 3: Mapes de calor de pobresa i ingressos a NYC', href='#map3', style={'font-size': '22px', 'color': '#007BFF', 'display': 'block', 'margin-bottom': '5px'}),  
            html.A('Anar a preu per habitabilitat', href='#price_sqm', style={'font-size': '22px', 'color': '#007BFF', 'display': 'block', 'margin-bottom': '5px'}),  
            html.A('Anar a Preu per superfície habitable (PNG)', href='#price_liv', style={'font-size': '22px', 'color': '#007BFF', 'display': 'block', 'margin-bottom': '15px'}),  
            html.A('Anar a Preu mitjà per tipus de casa i ingressos mitjans (PNG)', href='#meanhouse', style={'font-size': '22px', 'color': '#007BFF', 'display': 'block', 'margin-bottom': '15px'})  
            ], style={'text-align': 'center'}),  
    ], style={'margin-bottom': '20px'}),  

    # Visualitzacions
    html.Div([  

        html.Div([  
            html.H2("Map 1: Mapa calor mètriques custom", style={  
                'text-align': 'center',  
                'margin-bottom': '10px',  
                'font-size': '30px',
                'color': '#333'  
            }),  
            load_folium_map("NY_House_Metrics_Heatmaps.html")
        ], id='map1', style={  
            'padding': '20px',
            'border-radius': '10px',  
            'margin-bottom': '30px'  
        }),  

        html.Div([  
            html.H2("Map 2: Preus per rangs", style={  
                'text-align': 'center',  
                'margin-bottom': '10px',  
                'font-size': '30px', 
                'color': '#333'  
            }),  
            load_folium_map("NY_House_Map_interactive.html")
        ], id='map2', style={  
            'padding': '20px',
            'border-radius': '10px',  
            'margin-bottom': '30px'
        }),  

        html.Div([  
            html.H2("Preu per habitabilitat", style={  
                'text-align': 'center',  
                'margin-bottom': '10px',  
                'font-size': '30px', 
            }),  
            html.Img(src='data:image/png;base64,{}'.format(scatter64), style={  
                'width': '100%',  
                'max-width': '1000px',
                'display': 'block',  
                'margin': '0 auto',  
                'border': '2px solid black'
            })  
        ], id='price_sqm', style={  
            'padding': '20px',  
            'border-radius': '10px',  
            'margin-bottom': '30px'
        }),  


        html.Div([  
            html.H2("Preu per superfície habitable (PNG)", style={  
                'text-align': 'center',  
                'margin-bottom': '10px',  
                'font-size': '30px',
                'color': '#333'  
            }),  
            html.Img(src='data:image/png;base64,{}'.format(price_liv64), style={  
                'width': '100%',  
                'max-width': '1000px', 
                'display': 'block',  
                'margin': '0 auto',  
                'border': '2px solid black'
            })  
        ], id='price_liv', style={  
            'padding': '20px',
            'border-radius': '10px',  
            'margin-bottom': '30px'
        }),  


        html.Div([  
            html.H2("Mapes de calor de pobresa i ingressos a NYC", style={  
                'text-align': 'center',  
                'margin-bottom': '10px',  
                'font-size': '30px', 
                'color': '#333'  
            }),  
            load_folium_map("NYC_Poverty_Income_Heatmaps.html") 
        ], id='map3', style={  
            'padding': '20px',
            'border-radius': '10px',  
            'margin-bottom': '30px'  
        }),  

        html.Div([  
            html.H2("Anar a Preu mitjà per tipus de casa i ingressos mitjans (PNG)", style={  
                'text-align': 'center',  
                'margin-bottom': '10px',  
                'font-size': '30px', 
                'color': '#333'  
            }),  
            html.Img(src='data:image/png;base64,{}'.format(mean_income64), style={  
                'width': '100%',  
                'max-width': '1000px',
                'display': 'block',  
                'margin': '0 auto',  
                'border': '2px solid black' 
            })  
        ], id='meanhouse', style={  
            'padding': '20px', 
            'border-radius': '10px',  
            'margin-bottom': '30px'  
        }),  

    ], style={  
        'max-width': '1200px', 
        'margin': '0 auto',  
        'padding': '20px',  
        'background-color': '#f0f8ff',
        'border-radius': '10px',  
        'box-shadow': '0px 4px 6px rgba(0, 0, 0, 0.1)'  
    }),  
], style={  
    'background-color': '#ADD8E6',  
    'padding': '40px 0',
})

# Execute
app.run_server(debug=True)