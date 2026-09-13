# -*- coding: utf-8 -*-


# Tablero: Valor de contratos por modalidad y tiempo (UNGRD)
# Pregunta de negocio:
# ¿Cómo varía el valor de los contratos de UNGRD según la modalidad de contratación, y ha cambiado esta relación a lo largo del tiempo?


# Ejecute esta aplicación con 
# python app1.py
# y luego visite el sitio 
# http://127.0.0.1:8050/ 
# en su navegador.

import dash
from dash import dcc  # dash core components
from dash import html  # dash html components
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.express as px


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# Cargamos los datos ya limpios de la Tarea 2
df = pd.read_csv('dff_final.csv')
df['log_valor'] = np.log10(df['valor_del_contrato'].clip(lower=1))


app.layout = html.Div(children=[
    html.H1(children='Valor de contratos por modalidad y tiempo (UNGRD)'),
 
    html.Div(children='''
        Selecciona un rango de años para ver cómo cambia el valor de los
        contratos según la modalidad de contratación.
    '''),
 
    dcc.RangeSlider(
        id='year-slider',
        min=df['anio'].min(),
        max=df['anio'].max(),
        step=1,
        value=[df['anio'].min(), df['anio'].max()],
        marks={str(year): str(year) for year in sorted(df['anio'].unique())},
    ),

            html.Br(),

    dcc.Checklist(
        id='modalidad-checklist',
        options=[{'label': m, 'value': m} for m in sorted(df['modalidad_agrupada'].unique())],
        value=sorted(df['modalidad_agrupada'].unique()),
        labelStyle={'display': 'block'},
    ),

    html.Br(),
 
    dcc.Graph(id='boxplot-modalidad'),
    dcc.Graph(id='tendencia-modalidad'),
])
 
 
@app.callback(
    Output('boxplot-modalidad', 'figure'),
    Output('tendencia-modalidad', 'figure'),
    [Input('year-slider', 'value'),
     Input('modalidad-checklist', 'value')]
)

def actualizar_graficas(rango_anios, modalidades_sel):
    anio_min, anio_max = rango_anios
    dff = df[
        (df['anio'] >= anio_min)
        & (df['anio'] <= anio_max)
        & (df['modalidad_agrupada'].isin(modalidades_sel))
    ]
 
    fig_box = px.box(
        dff,
        x='modalidad_agrupada',
        y='log_valor',
        labels={'modalidad_agrupada': 'Modalidad', 'log_valor': 'log10(valor del contrato)'},
        title='Valor del contrato por modalidad',
    )
 
    tendencia = dff.groupby(['anio', 'modalidad_agrupada'])['log_valor'].median().reset_index()
    fig_tend = px.line(
        tendencia,
        x='anio',
        y='log_valor',
        color='modalidad_agrupada',
        labels={'anio': 'Año', 'log_valor': 'Mediana log10(valor)', 'modalidad_agrupada': 'Modalidad'},
        title='Evolución del valor por modalidad a través del tiempo',
    )
 
    return fig_box, fig_tend
 
 
if __name__ == '__main__':
    app.run(debug=True)
