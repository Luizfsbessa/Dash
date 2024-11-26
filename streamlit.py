import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
file_path = "backtest.xlsx"
df = pd.read_excel(file_path)

# Certificar-se de que a coluna 'Data de abertura' está no formato datetime
df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')

# Adicionar uma coluna para o período (ano-mês)
df['Período'] = df['Data de abertura'].dt.to_period('M')

# Adicionar toggle para o modo noturno
modo_noturno = st.checkbox("Ativar Modo Noturno", value=False)

# Definir estilos com base no modo
if modo_noturno:
    fundo = "#000000"  # Preto
    texto = "#FFFF00"  # Amarelo
else:
    fundo = "#FFFFFF"  # Branco
    texto = "#000000"  # Preto

# Estilo customizado
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-color: {fundo};
        color: {texto};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Título do app
st.title("Dashboard de Atendimento")

# Determinar a data inicial e final padrão com base na base de dados
min_date = df['Data de abertura'].min()
if pd.notnull(min_date):
    default_start_date = min_date.replace(day=1)  # Primeiro dia do mês mais antigo
else:
    default_start_date = None

max_date = df['Data de abertura'].max()

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
else:
    # Filtrar dados pelo intervalo de datas
    filtered_df = df.copy()
    if start_date:
        filtered_df = filtered_df[filtered_df['Data de abertura'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['Data de abertura'] <= pd.to_datetime(end_date)]

    # Segregar por tipo
    incidentes_df = filtered_df[filtered_df['Tipo'] == 'Incidente']
    requisicoes_df = filtered_df[filtered_df['Tipo'] == 'Requisição']

    # Gráfico de número de atendimentos por mês (Requisições)
    requisicoes_por_mes = requisicoes_df.groupby('Período').size().reset_index(name='Atendimentos')
    if not requisicoes_por_mes.empty:
        fig_requisicoes = px.bar(
            requisicoes_por_mes,
            x='Período',
            y='Atendimentos',
            title="Atendimentos por Mês - Requisições",
            labels={'Período': '', 'Atendimentos': 'Quantidade'},
            template="simple_white"
        )
        fig_requisicoes.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
        fig_requisicoes.update_xaxes(showgrid=False)
        fig_requisicoes.update_yaxes(showgrid=False)
        st.plotly_chart(fig_requisicoes)

    # Gráfico de número de atendimentos por mês (Incidentes)
    incidentes_por_mes = incidentes_df.groupby('Período').size().reset_index(name='Atendimentos')
    if not incidentes_por_mes.empty:
        fig_incidentes = px.bar(
            incidentes_por_mes,
            x='Período',
            y='Atendimentos',
            title="Atendimentos por Mês - Incidentes",
            labels={'Período': '', 'Atendimentos': 'Quantidade'},
            template="simple_white"
        )
        fig_incidentes.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
        fig_incidentes.update_xaxes(showgrid=False)
        fig_incidentes.update_yaxes(showgrid=False)
        st.plotly_chart(fig_incidentes)

    # Exibir mensagem se não houver dados
    if requisicoes_por_mes.empty and incidentes_por_mes.empty:
        st.warning("Não há dados disponíveis para o período selecionado.")
