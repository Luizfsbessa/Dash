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
tecnico = st.selectbox("Selecionar Técnico:", sorted(df['Atribuído - Técnico'].dropna().unique()))

# Filtro de tipo de atendimento
tipos = st.multiselect("Filtrar por Tipo:", df['Tipo'].dropna().unique())

# Filtro de intervalo de datas
st.write("Selecionar Intervalo de Datas:")
start_date = st.date_input("Data de Início", value=df['Data de abertura'].min().date())
end_date = st.date_input("Data de Fim", value=df['Data de abertura'].max().date())

# Validar se a data de início é menor ou igual à data de fim
if start_date > end_date:
    st.error("A data de início não pode ser maior que a data de fim.")
else:
    # Filtragem de dados
    filtered_df = df[df['Atribuído - Técnico'] == tecnico]
    if tipos:
        filtered_df = filtered_df[filtered_df['Tipo'].isin(tipos)]
    filtered_df = filtered_df[
        (filtered_df['Data de abertura'] >= pd.to_datetime(start_date)) &
        (filtered_df['Data de abertura'] <= pd.to_datetime(end_date))
    ]

    # Exibir métricas
    total_time = filtered_df['Horas Decimais'].sum()
    st.write(f"Total de Tempo em Atendimento: {total_time:.2f} horas")

    # Gráfico de histograma
    fig = px.histogram(
        filtered_df,
        x='Tipo',
        text_auto=True,
        title="Distribuição de Atendimentos por Tipo",
        labels={'Tipo': 'Tipo de Atendimento'}
    )
    st.plotly_chart(fig)

