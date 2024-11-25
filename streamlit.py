import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
file_path = "backtest.xlsx"
df = pd.read_excel(file_path)

df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')

def time_to_hours(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h + m / 60 + s / 3600
    except ValueError:
        return 0

df['Horas Decimais'] = df['Tempo em atendimento'].apply(time_to_hours)

# Filtros no Streamlit
st.title("Dashboard de Atendimento")
tecnico = st.selectbox("Selecionar Técnico:", sorted(df['Atribuído - Técnico'].dropna().unique()))
tipos = st.multiselect("Filtrar por Tipo:", df['Tipo'].dropna().unique())
start_date, end_date = st.date_input(
    "Selecionar Intervalo de Data:",
    [df['Data de abertura'].min().date(), df['Data de abertura'].max().date()]
)

# Filtragem de dados
filtered_df = df[df['Atribuído - Técnico'] == tecnico]
if tipos:
    filtered_df = filtered_df[filtered_df['Tipo'].isin(tipos)]
filtered_df = filtered_df[(filtered_df['Data de abertura'] >= pd.to_datetime(start_date)) & 
                          (filtered_df['Data de abertura'] <= pd.to_datetime(end_date))]

# Exibir métricas e gráfico
st.write(f"Total de Tempo em Atendimento: {filtered_df['Horas Decimais'].sum():.2f} horas")
fig = px.histogram(filtered_df, x='Tipo', text_auto=True, title="Distribuição de Atendimentos por Tipo")
st.plotly_chart(fig)
