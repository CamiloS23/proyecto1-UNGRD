# -*- coding: utf-8 -*-

# Tablero UNGRD - Control de contratación
# Combina las 2 preguntas de negocio del equipo en pestañas:
# 1. Concentración de contratistas (Andrés Camilo Silva)
# 2. Valor de contratos por modalidad y tiempo (María José Serna)

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
server = app.server

# ==========================================================
# Datos - Sección 1: Andrés (concentración de contratistas)
# ==========================================================
df_andres = pd.read_csv("UNGRD_LIMPIO.csv")
df_analisis = df_andres[['proveedor_adjudicado', 'valor_del_contrato', 'modalidad_de_contratacion']].copy()
df_analisis['valor_del_contrato'] = pd.to_numeric(df_analisis['valor_del_contrato'], errors='coerce')
df_analisis = df_analisis.drop(index=23)
df_analisis = df_analisis[df_analisis['valor_del_contrato'] >= 10000]

# ==========================================================
# Datos - Sección 2: María José (valor por modalidad y tiempo)
# ==========================================================
df_maria = pd.read_csv('dff_final.csv')
df_maria['log_valor'] = np.log10(df_maria['valor_del_contrato'].clip(lower=1))

# ==========================================================
# Layout - Sección 1: Andrés
# ==========================================================
layout_andres = html.Div([
    html.H2("Concentración de contratistas", style={'textAlign': 'center', 'color': '#2c3e50'}),

    html.Div([
        html.Label("Modalidad de contratación:"),
        dcc.Dropdown(
            id='filtro-modalidad',
            options=[{'label': 'Todas', 'value': 'Todas'}] +
                    [{'label': m, 'value': m} for m in df_analisis['modalidad_de_contratacion'].unique()],
            value='Todas'
        ),

        html.Label("Top N contratistas:", style={'marginTop': '15px'}),
        dcc.Slider(id='top-n', min=5, max=20, step=1, value=10,
                   marks={i: str(i) for i in range(5, 21, 5)}),

        html.Label("Buscar contratista:", style={'marginTop': '15px'}),
        dcc.Input(id='buscar-contratista', type='text', placeholder='Escribe un nombre...',
                  style={'width': '100%', 'padding': '8px'}),
    ], style={'maxWidth': '600px', 'margin': '0 auto', 'padding': '20px'}),

    html.Div([
        html.Div([
            html.H3(id='kpi-porcentaje', style={'color': '#e74c3c'}),
            html.P("Concentración del top N")
        ], style={'width': '48%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '8px'}),

        html.Div([
            html.H3(id='kpi-contratistas', style={'color': '#3498db'}),
            html.P("Contratistas totales")
        ], style={'width': '48%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '8px'}),
    ], style={'maxWidth': '600px', 'margin': '20px auto'}),

    dcc.Graph(id='grafico-top'),

    html.H3("Modalidad de contratación (dentro del filtro actual)", style={'textAlign': 'center'}),
    dash.dash_table.DataTable(id='tabla-modalidad',
                                style_cell={'textAlign': 'left', 'padding': '10px'},
                                style_header={'backgroundColor': '#2c3e50', 'color': 'white'})
])

# ==========================================================
# Layout - Sección 2: María José
# ==========================================================
layout_maria = html.Div([
    html.H2("Valor de contratos por modalidad y tiempo", style={'textAlign': 'center', 'color': '#2c3e50'}),

    html.Div('''Selecciona un rango de años para ver cómo cambia el valor de los
        contratos según la modalidad de contratación.'''),

    dcc.RangeSlider(
        id='year-slider',
        min=df_maria['anio'].min(),
        max=df_maria['anio'].max(),
        step=1,
        value=[df_maria['anio'].min(), df_maria['anio'].max()],
        marks={str(year): str(year) for year in sorted(df_maria['anio'].unique())},
    ),

    html.Br(),

    dcc.Checklist(
        id='modalidad-checklist',
        options=[{'label': m, 'value': m} for m in sorted(df_maria['modalidad_agrupada'].unique())],
        value=sorted(df_maria['modalidad_agrupada'].unique()),
        labelStyle={'display': 'block'},
    ),

    html.Br(),

    dcc.Graph(id='boxplot-modalidad'),
    dcc.Graph(id='tendencia-modalidad'),
])

# ==========================================================
# Layout general - pestañas
# ==========================================================
app.layout = html.Div([
    html.H1("Tablero UNGRD - Control de contratación", style={'textAlign': 'center'}),

    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Concentración de contratistas', value='tab-1'),
        dcc.Tab(label='Valor vs. modalidad y tiempo', value='tab-2'),
    ]),

    html.Div(id='contenido-tab')
])


@app.callback(Output('contenido-tab', 'children'), Input('tabs', 'value'))
def render_tab(tab):
    if tab == 'tab-1':
        return layout_andres
    elif tab == 'tab-2':
        return layout_maria


# ==========================================================
# Callback - Sección 1: Andrés
# ==========================================================
@app.callback(
    Output('grafico-top', 'figure'),
    Output('kpi-porcentaje', 'children'),
    Output('kpi-contratistas', 'children'),
    Output('tabla-modalidad', 'data'),
    Input('filtro-modalidad', 'value'),
    Input('top-n', 'value'),
    Input('buscar-contratista', 'value')
)
def actualizar_seccion_andres(modalidad, top_n, busqueda):
    datos = df_analisis.copy()

    if modalidad != 'Todas':
        datos = datos[datos['modalidad_de_contratacion'] == modalidad]

    if busqueda:
        datos = datos[datos['proveedor_adjudicado'].str.contains(busqueda, case=False, na=False)]

    top = datos.groupby('proveedor_adjudicado')['valor_del_contrato'].sum().sort_values(ascending=False).head(top_n)
    fig = px.bar(top, x=top.values, y=top.index, orientation='h', title=f"Top {top_n} contratistas")
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})

    valor_total = datos['valor_del_contrato'].sum()
    porcentaje = (top.sum() / valor_total * 100) if valor_total > 0 else 0
    total_contratistas = datos['proveedor_adjudicado'].nunique()

    tabla = datos['modalidad_de_contratacion'].value_counts().reset_index()
    tabla.columns = ['Modalidad', 'Cantidad']

    return fig, f"{porcentaje:.1f}%", f"{total_contratistas}", tabla.to_dict('records')


# ==========================================================
# Callback - Sección 2: María José
# ==========================================================
@app.callback(
    Output('boxplot-modalidad', 'figure'),
    Output('tendencia-modalidad', 'figure'),
    [Input('year-slider', 'value'),
     Input('modalidad-checklist', 'value')]
)
def actualizar_seccion_maria(rango_anios, modalidades_sel):
    anio_min, anio_max = rango_anios
    dff = df_maria[
        (df_maria['anio'] >= anio_min)
        & (df_maria['anio'] <= anio_max)
        & (df_maria['modalidad_agrupada'].isin(modalidades_sel))
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
