import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
file_path = "backtest.xlsx"
df = pd.read_excel(file_path)

# Certificar-se de que a coluna 'Data de abertura' está no formato datetime
df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')

# Adicionar a coluna 'Mês/Ano'
df['Mês/Ano'] = df['Data de abertura'].dt.to_period('M').astype(str)

# Determinar a data inicial padrão com base na base de dados
min_date = df['Data de abertura'].min()
if pd.notnull(min_date):
    default_start_date = min_date.replace(day=1)
else:
    default_start_date = None

max_date = df['Data de abertura'].max()

# Converter a coluna 'Tempo em atendimento' para horas decimais
def time_to_hours(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h + m / 60 + s / 3600
    except ValueError:
        return 0

# Formatar horas decimais no formato 6680:02:58
def format_hours_to_hms(decimal_hours):
    h = int(decimal_hours)
    m = int((decimal_hours - h) * 60)
    s = int(((decimal_hours - h) * 60 - m) * 60)
    return f"{h:02}:{m:02}:{s:02}"

df['Horas Decimais'] = df['Tempo em atendimento'].apply(time_to_hours)

# Título do app
st.title("Dashboard de Atendimento")

# Filtro de técnico
tecnico = st.selectbox(
    "Selecionar Técnico:",
    options=[""] + sorted(df['Atribuído - Técnico'].dropna().unique()),
    format_func=lambda x: "Selecione um técnico" if x == "" else x
)

# Filtro de intervalo de datas
st.write("Selecionar Intervalo de Datas:")
start_date = st.date_input(
    "Data de Início", 
    value=default_start_date, 
    min_value=min_date, 
    max_value=max_date, 
    format="DD/MM/YYYY"
)
end_date = st.date_input(
    "Data de Fim", 
    value=max_date, 
    min_value=min_date, 
    max_value=max_date, 
    format="DD/MM/YYYY"
)

# Validar se as datas foram preenchidas corretamente
if start_date and end_date and start_date > end_date:
    st.error("A data de início não pode ser maior que a data de fim.")
elif tecnico:  # Só filtrar se o técnico foi selecionado
    # Filtragem de dados
    filtered_df = df[df['Atribuído - Técnico'] == tecnico]
    if start_date:
        filtered_df = filtered_df[filtered_df['Data de abertura'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['Data de abertura'] <= pd.to_datetime(end_date)]

    # Calcular o total de horas por tipo
    incidentes_df = filtered_df[filtered_df['Tipo'] == 'Incidente']
    requisicoes_df = filtered_df[filtered_df['Tipo'] == 'Requisição']

    total_incidentes = incidentes_df['Horas Decimais'].sum()
    total_requisicoes = requisicoes_df['Horas Decimais'].sum()

    formatted_incidentes = format_hours_to_hms(total_incidentes)
    formatted_requisicoes = format_hours_to_hms(total_requisicoes)

    # Exibir os tempos em atendimento com caixa cinza e texto preto
    st.markdown(
        f"<div style='background-color: #f5f5f5; padding: 10px; color: black; font-size: 16px; border-radius: 5px;'>Tempo total em Incidentes: <b>{formatted_incidentes}</b></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div style='background-color: #f5f5f5; padding: 10px; color: black; font-size: 16px; border-radius: 5px;'>Tempo total em Requisições: <b>{formatted_requisicoes}</b></div>",
        unsafe_allow_html=True
    )

    # Gráfico de número de atendimentos por mês com rótulos
    atendimentos_por_mes = filtered_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos')

    fig = px.bar(
        atendimentos_por_mes,
        x='Mês/Ano',
        y='Número de Atendimentos',
        text='Número de Atendimentos',
        title="Número de Atendimentos por Mês",
    )
    fig.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    st.plotly_chart(fig)
else:
    st.info("Selecione um técnico para exibir os dados.")
