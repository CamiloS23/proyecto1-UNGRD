import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv("UNGRD_LIMPIO.csv")
df_analisis = df[['proveedor_adjudicado', 'valor_del_contrato', 'modalidad_de_contratacion']].copy()
df_analisis['valor_del_contrato'] = pd.to_numeric(df_analisis['valor_del_contrato'], errors='coerce')
df_analisis = df_analisis.drop(index=23)
df_analisis = df_analisis[df_analisis['valor_del_contrato'] >= 10000]

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Tablero UNGRD - Concentración de contratistas"),

    html.Label("Modalidad de contratación:"),
    dcc.Dropdown(
        id='filtro-modalidad',
        options=[{'label': 'Todas', 'value': 'Todas'}] +
                [{'label': m, 'value': m} for m in df_analisis['modalidad_de_contratacion'].unique()],
        value='Todas'
    ),

    html.Label("Top N contratistas:"),
    dcc.Slider(id='top-n', min=5, max=20, step=1, value=10,
               marks={i: str(i) for i in range(5, 21, 5)}),

    html.Label("Buscar contratista:"),
    dcc.Input(id='buscar-contratista', type='text', placeholder='Escribe un nombre...'),

    html.Div([
        html.Div([
            html.H3(id='kpi-porcentaje'),
            html.P("Concentración del top N")
        ], style={'width': '48%', 'display': 'inline-block', 'textAlign': 'center'}),

        html.Div([
            html.H3(id='kpi-contratistas'),
            html.P("Contratistas totales")
        ], style={'width': '48%', 'display': 'inline-block', 'textAlign': 'center'}),
    ]),

    dcc.Graph(id='grafico-top'),

    html.H3("Modalidad de contratación (dentro del filtro actual)"),
    dash.dash_table.DataTable(id='tabla-modalidad')
])

@app.callback(
    Output('grafico-top', 'figure'),
    Output('kpi-porcentaje', 'children'),
    Output('kpi-contratistas', 'children'),
    Output('tabla-modalidad', 'data'),
    Input('filtro-modalidad', 'value'),
    Input('top-n', 'value'),
    Input('buscar-contratista', 'value')
)
def actualizar_todo(modalidad, top_n, busqueda):
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

if __name__ == '__main__':
    app.run(debug=True)