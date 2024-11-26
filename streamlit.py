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

# Converter a coluna 'Tempo em atendimento' para horas decimais
def time_to_hours(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h + m / 60 + s / 3600
    except ValueError:
        return 0

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
start_date = st.date_input("Data de Início", value=df['Data de abertura'].min(), format="DD/MM/YYYY")
end_date = st.date_input("Data de Fim", value=df['Data de abertura'].max(), format="DD/MM/YYYY")

# Validar se as datas foram preenchidas corretamente
if start_date and end_date and start_date > end_date:
    st.error("A data de início não pode ser maior que a data de fim.")
else:
    # Filtragem de dados
    filtered_df = df[(df['Data de abertura'] >= pd.to_datetime(start_date)) & (df['Data de abertura'] <= pd.to_datetime(end_date))]

    if tecnico:
        # Filtrar por técnico
        filtered_df = filtered_df[filtered_df['Atribuído - Técnico'] == tecnico]

    # Calcular a média, máximo e mínimo de horas por tipo (Incidente e Requisição)
    incidentes_df = filtered_df[filtered_df['Tipo'] == 'Incidente']
    requisicoes_df = filtered_df[filtered_df['Tipo'] == 'Requisição']

    # Função para calcular as métricas
    def calculate_metrics(df):
        return {
            'Média': df['Horas Decimais'].mean(),
            'Máximo': df['Horas Decimais'].max(),
            'Mínimo': df['Horas Decimais'].min()
        }

    # Obter as métricas para incidentes e requisições
    incidentes_metrics = calculate_metrics(incidentes_df)
    requisicoes_metrics = calculate_metrics(requisicoes_df)

    # Criar DataFrame para plotar
    metrics_df = pd.DataFrame({
        'Métrica': ['Média', 'Máximo', 'Mínimo'],
        'Incidentes': [incidentes_metrics['Média'], incidentes_metrics['Máximo'], incidentes_metrics['Mínimo']],
        'Requisições': [requisicoes_metrics['Média'], requisicoes_metrics['Máximo'], requisicoes_metrics['Mínimo']]
    })

    # Plotar o gráfico de barras agrupadas
    fig = px.bar(
        metrics_df,
        x='Métrica',
        y=['Incidentes', 'Requisições'],
        barmode='group',
        title="Tempo de Atendimento por Tipo - Média, Máximo e Mínimo",
        labels={'value': 'Tempo em Horas', 'Métrica': 'Tipo de Métrica'},
    )

    # Exibir o gráfico
    st.plotly_chart(fig)

    # Se houver incidentes, mostrar a tabela de incidentes por mês
    if not incidentes_df.empty:
        incidentes_por_mes = incidentes_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos')
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
        st.plotly_chart(fig_incidentes)

    # Se houver requisições, mostrar a tabela de requisições por mês
    if not requisicoes_df.empty:
        requisicoes_por_mes = requisicoes_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos')
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
        st.plotly_chart(fig_requisicoes)


