import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
file_path = "backtest.xlsx"
df = pd.read_excel(file_path)

# Preparação de dados
df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')
df['Mês/Ano'] = df['Data de abertura'].dt.to_period('M').astype(str)
df['Horas Decimais'] = df['Tempo em atendimento'].apply(lambda x: sum(int(i) * 60**(2-i) for i, x in enumerate(x.split(":"))))

# Definir limites de datas e técnico
min_date, max_date = df['Data de abertura'].min(), df['Data de abertura'].max()
default_start_date = min_date.replace(day=1) if pd.notnull(min_date) else None
tecnico = st.selectbox("Selecionar Técnico", options=[""] + sorted(df['Atribuído - Técnico'].dropna().unique()))
start_date = st.date_input("Data de Início", value=default_start_date, min_value=min_date, max_value=max_date)
end_date = st.date_input("Data de Fim", value=max_date, min_value=min_date, max_value=max_date)

# Filtragem de dados
filtered_df = df[(df['Data de abertura'] >= pd.to_datetime(start_date)) & (df['Data de abertura'] <= pd.to_datetime(end_date))]
if tecnico:
    filtered_df = filtered_df[filtered_df['Atribuído - Técnico'] == tecnico]

# Função para formatar horas
def format_hours(decimal_hours):
    h, m = divmod(int(decimal_hours), 60)
    s = int((decimal_hours - int(decimal_hours)) * 60)
    return f"{h:02}:{m:02}:{s:02}"

# Função para exibir gráficos
def plot_bar(df, title, color):
    fig = px.bar(df, x='Mês/Ano', y='Número de Atendimentos', text='Número de Atendimentos', title=title, color_discrete_sequence=[color])
    fig.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
    fig.update_layout(xaxis_title=None, yaxis_title=None, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig)

# Gráficos por tipo de atendimento
for tipo, color in [("Incidente", "#1EA4B6"), ("Requisição", "#00C6E0")]:
    tipo_df = filtered_df[filtered_df['Tipo'] == tipo]
    if not tipo_df.empty:
        tipo_por_mes = tipo_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos')
        plot_bar(tipo_por_mes, f"Número de Atendimentos por Mês - {tipo}s", color)

# Gráfico de pizza para distribuição por prioridade
prioridade_cores = {'Baixa': '#90ACB8', 'Média': '#587D8E', 'Alta': '#C1D8E3', 'Muito Alta': '#2D55263'}
for tipo in ['Incidente', 'Requisição']:
    tipo_df = filtered_df[filtered_df['Tipo'] == tipo]
    if not tipo_df.empty:
        tipo_por_prioridade = tipo_df.groupby('Prioridade').size().reset_index(name='Número de Atendimentos')
        fig = px.pie(tipo_por_prioridade, names='Prioridade', values='Número de Atendimentos', title=f"Distribuição de {tipo}s por Prioridade", color='Prioridade', color_discrete_map=prioridade_cores)
        fig.update_traces(texttemplate='<b>%{value}</b>', textinfo='value')
        st.plotly_chart(fig)
