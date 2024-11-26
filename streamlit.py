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

    # Dados de incidentes e requisições
    incidentes_df = filtered_df[filtered_df['Tipo'] == 'Incidente']
    requisicoes_df = filtered_df[filtered_df['Tipo'] == 'Requisição']

    # Cálculo de tempos médios, máximos e totais por prioridade
    def calcular_tempo_prioridade(df):
        prioridades = df['Prioridade'].unique()
        resultados = []
        for prioridade in prioridades:
            subset = df[df['Prioridade'] == prioridade]
            media = subset['Horas Decimais'].mean()
            maxima = subset['Horas Decimais'].max()
            resultados.append({
                "Prioridade": prioridade,
                "Média": format_hours_to_hms(media),
                "Máxima": format_hours_to_hms(maxima)
            })
        return pd.DataFrame(resultados)

    tempos_incidentes = calcular_tempo_prioridade(incidentes_df)
    tempos_requisicoes = calcular_tempo_prioridade(requisicoes_df)

    # Markdown para incidentes
    st.markdown("### Detalhes de Incidentes por Prioridade")
    st.markdown(tempos_incidentes.to_markdown(index=False))

    # Markdown para requisições
    st.markdown("### Detalhes de Requisições por Prioridade")
    st.markdown(tempos_requisicoes.to_markdown(index=False))

    # Gráficos de Pizza para "Prioridade" - Segregado por Tipo (Incidente e Requisição)
    col1, col2 = st.columns(2)

    with col1:
        if not incidentes_df.empty and 'Prioridade' in incidentes_df.columns:
            prioridade_incidentes = incidentes_df['Prioridade'].value_counts().reset_index()
            prioridade_incidentes.columns = ['Prioridade', 'Quantidade']

            fig_pizza_incidentes = px.pie(
                prioridade_incidentes,
                names='Prioridade',
                values='Quantidade',
                title="Distribuição de Prioridades - Incidentes",
                color_discrete_sequence=px.colors.sequential.Teal,
            )
            fig_pizza_incidentes.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pizza_incidentes)

    with col2:
        if not requisicoes_df.empty and 'Prioridade' in requisicoes_df.columns:
            prioridade_requisicoes = requisicoes_df['Prioridade'].value_counts().reset_index()
            prioridade_requisicoes.columns = ['Prioridade', 'Quantidade']

            fig_pizza_requisicoes = px.pie(
                prioridade_requisicoes,
                names='Prioridade',
                values='Quantidade',
                title="Distribuição de Prioridades - Requisições",
                color_discrete_sequence=px.colors.sequential.Teal,
            )
            fig_pizza_requisicoes.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pizza_requisicoes)

else:
    st.info("Selecione um técnico para exibir os dados.")
