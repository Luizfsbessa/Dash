import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import streamlit as st
from dash.dash_table.Format import Format

# Configurar a página no Streamlit
st.set_page_config(page_title="Dashboard de Atendimento", layout="wide")

# Carregar os dados
file_path = "backtest.xlsx"
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    st.error(f"Erro: O arquivo {file_path} não foi encontrado. Certifique-se de que ele está no mesmo diretório.")
    st.stop()

# Certificar-se de que a coluna 'Data de abertura' esteja no formato datetime
df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')

# Converter a coluna 'Tempo em atendimento' para horas decimais
def time_to_hours(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h + m / 60 + s / 3600
    except ValueError:
        return 0  # Caso haja um valor inválido, retorna 0

df['Horas Decimais'] = df['Tempo em atendimento'].apply(time_to_hours)

# Inicializar o app Dash
app = dash.Dash(__name__)

# Layout do Dashboard com filtro de data
app.layout = html.Div([
    html.H1("Dashboard de Atendimento", style={'textAlign': 'center'}),
    
    # Dropdown para selecionar o técnico
    html.Div([
        html.Label("Selecionar Técnico:"),
        dcc.Dropdown(
            id='tecnico-dropdown',
            options=[{'label': tecnico, 'value': tecnico} for tecnico in sorted(df['Atribuído - Técnico'].dropna().unique())],
            value=df['Atribuído - Técnico'].dropna().iloc[0]
        )
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    # Dropdown para selecionar o tipo de atendimento
    html.Div([
        html.Label("Filtrar por Tipo:"),
        dcc.Dropdown(
            id='tipo-dropdown',
            options=[{'label': tipo, 'value': tipo} for tipo in df['Tipo'].dropna().unique()],
            value=None,
            multi=True
        )
    ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '20px'}),
    
    # Filtro de data (intervalo de data)
    html.Div([
        html.Label("Selecionar Intervalo de Data:"),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=df['Data de abertura'].min().date(),
            end_date=df['Data de abertura'].max().date(),
            display_format='DD/MM/YYYY',
            style={'marginTop': '20px'}
        )
    ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '20px'}),
    
    # Exibição do total de tempo em atendimento
    html.Div(id='total-time-display', style={'marginTop': '20px', 'fontSize': '20px'}),
    
    # Gráfico de histograma
    dcc.Graph(id='histogram-graph')
])

# Callbacks para interação
@app.callback(
    [Output('total-time-display', 'children'),
     Output('histogram-graph', 'figure')],
    [Input('tecnico-dropdown', 'value'),
     Input('tipo-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_dashboard(selected_tecnico, selected_tipo, start_date, end_date):
    filtered_df = df[df['Atribuído - Técnico'] == selected_tecnico]
    
    if selected_tipo:
        filtered_df = filtered_df[filtered_df['Tipo'].isin(selected_tipo)]
    
    filtered_df = filtered_df[
        (filtered_df['Data de abertura'] >= start_date) & (filtered_df['Data de abertura'] <= end_date)
    ]
    
    total_time = filtered_df['Horas Decimais'].sum()
    total_time_str = f"Total de Tempo em Atendimento: {total_time:.2f} horas"
    
    histogram_fig = px.histogram(
        filtered_df,
        x='Tipo',
        title="Distribuição de Atendimentos por Tipo",
        labels={'Tipo': 'Tipo de Atendimento'},
        text_auto=True
    )
    
    return total_time_str, histogram_fig

# Incorporar o Dash no Streamlit
st.write(
    f"<iframe srcdoc='{app.index()}' style='border:none;width:100%;height:100vh;'></iframe>",
    unsafe_allow_html=True
)

