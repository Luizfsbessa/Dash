import pandas as pd
from datetime import datetime, timedelta

# Caminho do arquivo Excel 
file_path = r"C:\Users\luiz.bessa\Downloads\teste_automatização.xlsx"

# Função para calcular as horas úteis dentro do expediente (8h - 18h)
def working_hours(start, end):
    start_time = start.replace(hour=8, minute=0, second=0, microsecond=0)
    end_time = start.replace(hour=18, minute=0, second=0, microsecond=0)

# Ajuste para os casos em que a hora está fora do horário comercial
    if start > end_time:
        return 0
    if start < start_time:
        start = start_time
    if end < start_time:
        return 0
    if end > end_time:
        end = end_time

    return (end - start).total_seconds() / 3600  # Retorna horas

# Função para calcular o tempo total de atendimento em horário útil, ignorando finais de semana
def calculate_working_time(row):
    abertura = pd.to_datetime(row['Data de abertura'], format='%d/%m/%Y %H:%M')
    if pd.isna(row['Data da solução']):
        solucoes = datetime.now()  # Se não houver solução, usa a data atual
    else:
        solucoes = pd.to_datetime(row['Data da solução'], format='%d/%m/%Y %H:%M')

    total_hours = 0

# Itera sobre os dias entre abertura e solução
    while abertura.date() < solucoes.date():
        if abertura.weekday() < 5:  # Ignora finais de semana
            next_day = abertura + timedelta(days=1)
            total_hours += working_hours(abertura, next_day)
        abertura = abertura + timedelta(days=1)
        abertura = abertura.replace(hour=8, minute=0)  # Reinicia às 08:00 no próximo dia útil

# Adiciona horas do último dia (ou mesmo dia)
    if abertura.weekday() < 5:
        total_hours += working_hours(abertura, solucoes)

# Converte para formato h:m:s
    hours = int(total_hours)
    minutes = int((total_hours - hours) * 60)
    seconds = int(((total_hours - hours) * 60 - minutes) * 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Lê o arquivo Excel para um DataFrame
df = pd.read_excel(file_path)

# Calcula o tempo de atendimento para cada linha
df['Tempo em atendimento'] = df.apply(calculate_working_time, axis=1)

# Função para estilizar o cabeçalho com fundo preto e texto branco
def highlight_header(data):
    return ['background-color: black; color: black; font-weight: bold;' for _ in data]

# Função para aplicar cores alternadas nas linhas (efeito zebra)
def zebra_stripes(index):
    if index % 2 == 0:
        return ['background-color: #f0f0f0;'] * len(df.columns)  # Linhas pares - cinza claro
    else:
        return ['background-color: white;'] * len(df.columns)  # Linhas ímpares - branco

# Estilizando a tabela
styled_table = (
    df.style
    .apply(highlight_header, axis=0)  # Estilo no cabeçalho
    .apply(lambda row: zebra_stripes(row.name), axis=1)  # Listras zebreadas
    .set_properties(**{
        'border': '1px solid black',  # Grade preta nas células
        'padding': '8px',  # Espaçamento interno
        'text-align': 'center'  # Centralização do texto
    })
)

# Exibindo a tabela direto no Jupyter Notebook
try:
    from IPython.display import display  # Apenas para ambientes interativos
    display(styled_table)
except ImportError:
    print(df)  # Exibe em formato texto no terminal

# (Opcional) Salvar resultado em um novo arquivo Excel
df.to_excel(r"C:\Users\luiz.bessa\Downloads\resultado_automatizacao.xlsx", index=False)

print("Cálculo realizado e armazenado com sucesso")

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Carregar os dados
file_path = r"C:\Users\luiz.bessa\Downloads\backtest.xlsx"
df = pd.read_excel(file_path)

# Certificar-se de que a coluna 'Data de abertura' esteja no formato datetime
df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')

# Converter a coluna 'Tempo em atendimento' para horas decimais
def time_to_hours(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h + m / 60 + s / 3600

df['Horas Decimais'] = df['Tempo em atendimento'].apply(time_to_hours)

# Inicializar o app
app = dash.Dash(__name__)

# Layout do Dashboard com filtro de data
app.layout = html.Div([
    html.H1("Dashboard de Atendimento", style={'textAlign': 'center'}),
    
    # Dropdown para selecionar o técnico
   html.Div([
    html.Label("Selecionar Técnico:"),
    dcc.Dropdown(
        id='tecnico-dropdown',
        options=[{'label': tecnico, 'value': tecnico} for tecnico in sorted(df['Atribuído - Técnico'].unique())],  # Ordenando os técnicos
        value=df['Atribuído - Técnico'].iloc[0]  # Seleção padrão
    )
], style={'width': '30%', 'display': 'inline-block'}),
    # Dropdown para selecionar o tipo de atendimento
    html.Div([
        html.Label("Filtrar por Tipo:"),
        dcc.Dropdown(
            id='tipo-dropdown',
            options=[{'label': tipo, 'value': tipo} for tipo in df['Tipo'].unique()],
            value=None,  # Seleção padrão (nenhum filtro aplicado)
            multi=True  # Permitir múltiplas seleções
        )
    ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '20px'}),
    
    # Filtro de data (intervalo de data)
    html.Div([
        html.Label("Selecionar Intervalo de Data:"),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=df['Data de abertura'].min().date(),
            end_date=df['Data de abertura'].max().date(),
            display_format='DD/MM/YYYY',  # Formato da data
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
    # Filtrar os dados com base nos filtros
    filtered_df = df[df['Atribuído - Técnico'] == selected_tecnico]
    
    if selected_tipo:
        filtered_df = filtered_df[filtered_df['Tipo'].isin(selected_tipo)]
    
    # Filtrar os dados com base no intervalo de datas
    filtered_df = filtered_df[(filtered_df['Data de abertura'] >= start_date) & (filtered_df['Data de abertura'] <= end_date)]
    
    # Calcular o total de horas
    total_time = filtered_df['Horas Decimais'].sum()
    total_time_str = f"Total de Tempo em Atendimento: {total_time:.2f} horas"
    
    # Criar o gráfico de histograma
    histogram_fig = px.histogram(
        filtered_df, 
        x='Tipo', 
        title="Distribuição de Atendimentos por Tipo",
        labels={'Tipo': 'Tipo de Atendimento'},
        text_auto=True
    )
    
    return total_time_str, histogram_fig

# Rodar o app
if __name__ == '__main__':
    app.run_server(debug=True)