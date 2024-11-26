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

# Formatar horas decimais no formato HH:MM:SS
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

    # Filtrar somente os incidentes
    incidentes_df = filtered_df[filtered_df['Tipo'] == 'Incidente']

    # Exibir o total de incidentes
    total_incidentes = incidentes_df.shape[0]
    st.markdown(f"### Total de Incidentes: {total_incidentes}")

    # Detalhar Prioridade
    if not incidentes_df.empty and 'Prioridade' in incidentes_df.columns:
        # Distribuição por Prioridade
        prioridade_distribuicao = incidentes_df['Prioridade'].value_counts().reset_index()
        prioridade_distribuicao.columns = ['Prioridade', 'Quantidade']

        # Gráfico de Pizza
        fig_pizza_incidentes = px.pie(
            prioridade_distribuicao,
            names='Prioridade',
            values='Quantidade',
            title="Distribuição de Prioridades - Incidentes",
            color_discrete_sequence=px.colors.sequential.Teal,
        )
        fig_pizza_incidentes.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pizza_incidentes)

        # Checkbox para métricas adicionais
        if st.checkbox("Exibir métricas detalhadas por Prioridade"):
            # Cálculo de média e tempo máximo
            prioridade_metrica = (
                incidentes_df.groupby('Prioridade')['Horas Decimais']
                .agg(['mean', 'max'])
                .reset_index()
            )
            prioridade_metrica.columns = ['Prioridade', 'Média (Horas)', 'Máximo (Horas)']

            # Formatar para exibir as métricas
            prioridade_metrica['Média (Horas)'] = prioridade_metrica['Média (Horas)'].apply(format_hours_to_hms)
            prioridade_metrica['Máximo (Horas)'] = prioridade_metrica['Máximo (Horas)'].apply(format_hours_to_hms)

            # Exibir tabela
            st.markdown("### Métricas de Tempo por Prioridade")
            st.dataframe(prioridade_metrica, use_container_width=True)
    else:
        st.warning("Não há dados de prioridade para os incidentes.")
else:
    st.info("Selecione um técnico para exibir os dados.")
