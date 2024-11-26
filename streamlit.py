import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
file_path = "backtest.xlsx"
df = pd.read_excel(file_path)

# Certificar-se de que a coluna 'Data de abertura' está no formato datetime
df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')

# Adicionar a coluna 'Mês/Ano' apenas com mês e ano
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

# Criar a coluna 'Horas Decimais' convertendo 'Tempo em atendimento' para horas decimais
df['Horas Decimais'] = df['Tempo em atendimento'].apply(time_to_hours)

# Título do app
st.title("Dashboard de Atendimento")

# Estilizando o fundo e a cor do texto das caixas de seleção e data
custom_style = """
    <style>
        .stSelectbox, .stDateInput, .stMultiselect, .stCheckbox, .stTextInput, .stTextArea {
            background-color: white;
            color: black;
            padding: 15px;
            font-size: 16px;
            border-radius: 5px;
            margin-bottom: 10px;
            border: 1px solid #A1C6D8;
        }
        .stSelectbox select, .stDateInput input {
            background-color: white;
            color: black;
            border: 1px solid #A1C6D8;
        }
        .stSelectbox, .stDateInput {
            font-size: 16px;
        }
    </style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# Filtro de técnico
tecnico = st.selectbox(
    "Selecionar Técnico:",
    options=[""] + sorted(df['Atribuído - Técnico'].dropna().unique()),
    format_func=lambda x: "Selecione um técnico" if x == "" else x,
    key="tecnico",
    help="Escolha o técnico para filtrar os dados",
)

# Filtro de intervalo de datas
start_date = st.date_input(
    "Data de Início", 
    value=default_start_date, 
    min_value=min_date, 
    max_value=max_date, 
    format="DD/MM/YYYY",
    key="start_date"
)

end_date = st.date_input(
    "Data de Fim", 
    value=max_date, 
    min_value=min_date, 
    max_value=max_date, 
    format="DD/MM/YYYY",
    key="end_date"
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

    # Exibir os tempos em atendimento com fundo cinza e texto em preto
    if total_incidentes > 0:
        st.markdown(
            f"<div style='background-color: #C1D8E3; padding: 15px; border-radius: 5px; margin-bottom: 10px;'>Tempo total em Incidentes: <b>{formatted_incidentes}</b></div>",
            unsafe_allow_html=True
        )

    if total_requisicoes > 0:
        st.markdown(
            f"<div style='background-color: #C1D8E3; padding: 15px; border-radius: 5px; margin-bottom: 10px;'>Tempo total em Requisições: <b>{formatted_requisicoes}</b></div>",
            unsafe_allow_html=True
        )

    # Gráficos de número de atendimentos por mês, separados por Tipo (Requisição e Incidente)
    incidentes_por_mes = incidentes_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos')
    requisicoes_por_mes = requisicoes_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos')

    # Verificar se os DataFrames não estão vazios e exibir os gráficos
    if not incidentes_por_mes.empty:
        fig_incidentes = px.bar(
            incidentes_por_mes,
            x='Mês/Ano',
            y='Número de Atendimentos',
            text='Número de Atendimentos',
            title="Número de Atendimentos por Mês - Incidentes",
        )
        fig_incidentes.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
        fig_incidentes.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig_incidentes.update_xaxes(showgrid=False)
        fig_incidentes.update_yaxes(showgrid=False)
        st.plotly_chart(fig_incidentes)

    if not requisicoes_por_mes.empty:
        fig_requisicoes = px.bar(
            requisicoes_por_mes,
            x='Mês/Ano',
            y='Número de Atendimentos',
            text='Número de Atendimentos',
            title="Número de Atendimentos por Mês - Requisições",
        )
        fig_requisicoes.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
        fig_requisicoes.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig_requisicoes.update_xaxes(showgrid=False)
        fig_requisicoes.update_yaxes(showgrid=False)
        st.plotly_chart(fig_requisicoes)
else:
    st.info("Selecione um técnico para exibir os dados.")

