import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
file_path = "backtest.xlsx"
df = pd.read_excel(file_path)

# Certificar-se de que a coluna 'Data de abertura' está no formato datetime
df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')

# Criar uma nova coluna para o mês/ano para os gráficos
df['Mês/Ano'] = df['Data de abertura'].dt.to_period('M').astype(str)

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

# Função para modo noturno
def apply_dark_mode():
    st.markdown(
        """
        <style>
        div[data-testid="stSidebar"] {
            background-color: #262730;
        }
        div[data-baseweb="select"] {
            background-color: #1e1e1e;
        }
        div[data-baseweb="select"] * {
            color: #f0f0f0 !important;
        }
        div[data-testid="stMarkdownContainer"] {
            color: #f0f0f0;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #f0f0f0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Ativar modo noturno
apply_dark_mode()

# Título do app
st.title("Dashboard de Atendimento")

# Filtro de técnico
tecnico = st.selectbox(
    "Selecionar Técnico:",
    options=[""] + sorted(df['Atribuído - Técnico'].dropna().unique()),
    format_func=lambda x: "Selecione um técnico" if x == "" else x
)

# Determinar a data inicial e final padrão com base na base de dados
min_date = df['Data de abertura'].min()
if pd.notnull(min_date):
    default_start_date = min_date.replace(day=1)
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

    # Exibir os tempos em atendimento
    st.markdown(
        f"""
        <div style='background-color: #333333; padding: 10px; border-radius: 5px; text-align: center;'>
            <strong>Tempo total em Incidentes:</strong> {formatted_incidentes}
        </div>
        <div style='background-color: #333333; padding: 10px; border-radius: 5px; text-align: center; margin-top: 10px;'>
            <strong>Tempo total em Requisições:</strong> {formatted_requisicoes}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Gráfico de Incidentes por mês
    fig_incidentes = px.bar(
        incidentes_df.groupby('Mês/Ano').size().reset_index(name='Número de Incidentes'),
        x='Mês/Ano',
        y='Número de Incidentes',
        title="Incidentes por Mês",
        labels={'Mês/Ano': '', 'Número de Incidentes': ''},
    )
    fig_incidentes.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, plot_bgcolor="#1e1e1e", paper_bgcolor="#1e1e1e")
    fig_incidentes.update_xaxes(showgrid=False, zeroline=False)
    fig_incidentes.update_yaxes(showgrid=False, zeroline=False)

    # Gráfico de Requisições por mês
    fig_requisicoes = px.bar(
        requisicoes_df.groupby('Mês/Ano').size().reset_index(name='Número de Requisições'),
        x='Mês/Ano',
        y='Número de Requisições',
        title="Requisições por Mês",
        labels={'Mês/Ano': '', 'Número de Requisições': ''},
    )
    fig_requisicoes.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, plot_bgcolor="#1e1e1e", paper_bgcolor="#1e1e1e")
    fig_requisicoes.update_xaxes(showgrid=False, zeroline=False)
    fig_requisicoes.update_yaxes(showgrid=False, zeroline=False)

    # Exibir gráficos
    st.plotly_chart(fig_incidentes)
    st.plotly_chart(fig_requisicoes)
else:
    st.info("Selecione um técnico para exibir os dados.")

