import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
file_path = "backtest.xlsx"
df = pd.read_excel(file_path)

# Certificar-se de que a coluna 'Data de abertura' está no formato datetime
df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')

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

# Filtro de técnico
tecnico = st.selectbox(
    "Selecionar Técnico:",
    options=[""] + sorted(df['Atribuído - Técnico'].dropna().unique()),  # Adicionar opção em branco
    format_func=lambda x: "Selecione um técnico" if x == "" else x  # Placeholder para a opção em branco
)

# Filtro de tipo de atendimento
tipos = st.multiselect(
    "Filtrar por Tipo:",
    options=df['Tipo'].dropna().unique(),
    default=[],  # Deixar vazio por padrão
)

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
    value=default_start_date,  # Data padrão
    min_value=min_date,  # Limite inferior
    max_value=max_date   # Limite superior
)
end_date = st.date_input(
    "Data de Fim", 
    value=max_date,  # Última data disponível
    min_value=min_date,  # Limite inferior
    max_value=max_date   # Limite superior
)

# Validar se as datas foram preenchidas corretamente
if start_date and end_date and start_date > end_date:
    st.error("A data de início não pode ser maior que a data de fim.")
elif tecnico:  # Só filtrar se o técnico foi selecionado
    # Filtragem de dados
    filtered_df = df[df['Atribuído - Técnico'] == tecnico]
    if tipos:
        filtered_df = filtered_df[filtered_df['Tipo'].isin(tipos)]
    if start_date:
        filtered_df = filtered_df[filtered_df['Data de abertura'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['Data de abertura'] <= pd.to_datetime(end_date)]

    # Calcular o total de horas
    total_time = filtered_df['Horas Decimais'].sum()

    # Exibir o total de tempo em atendimento em uma caixa cinza
    st.markdown(
        f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center;'>"
        f"<strong>Total de Tempo em Atendimento:</strong> {total_time:.2f} horas</div>",
        unsafe_allow_html=True
    )

    # Gráfico de histograma
    fig = px.histogram(
        filtered_df,
        x='Tipo',
        text_auto=True,
        title="Distribuição de Atendimentos por Tipo",
        labels={'Tipo': 'Tipo de Atendimento'}
    )
    st.plotly_chart(fig)
else:
    st.info("Selecione um técnico para exibir os dados.")
