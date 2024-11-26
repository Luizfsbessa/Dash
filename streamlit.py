import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
file_path = "backtest.xlsx"
df = pd.read_excel(file_path)

# Certificar-se de que a coluna 'Data de abertura' está no formato datetime
df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')

# Definir o período de corte
cutoff_date = pd.to_datetime("03/07/2024")

# Dividir os dados em antes e depois da data de corte
df_before_cutoff = df[df['Data de abertura'] < cutoff_date]
df_after_cutoff = df[df['Data de abertura'] >= cutoff_date]

# Agrupar os dados de atendimentos por dia
df_before_cutoff_grouped = df_before_cutoff.groupby('Data de abertura').size().reset_index(name='Número de Atendimentos')
df_after_cutoff_grouped = df_after_cutoff.groupby('Data de abertura').size().reset_index(name='Número de Atendimentos')

# Criar uma tabela combinando antes e depois da data de corte
df_combined = pd.concat([df_before_cutoff_grouped, df_after_cutoff_grouped])

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
    value=df['Data de abertura'].min(), 
    min_value=df['Data de abertura'].min(), 
    max_value=df['Data de abertura'].max(), 
    format="DD/MM/YYYY",
    key="start_date"
)

end_date = st.date_input(
    "Data de Fim", 
    value=df['Data de abertura'].max(), 
    min_value=df['Data de abertura'].min(), 
    max_value=df['Data de abertura'].max(), 
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

    # Calcular o total de horas por tipo, com verificação de coluna
    incidentes_df = filtered_df[filtered_df['Tipo'] == 'Incidente']
    requisicoes_df = filtered_df[filtered_df['Tipo'] == 'Requisição']

    if 'Horas Decimais' in incidentes_df.columns:
        total_incidentes = incidentes_df['Horas Decimais'].sum()
    else:
        total_incidentes = 0  # Caso a coluna não exista

    if 'Horas Decimais' in requisicoes_df.columns:
        total_requisicoes = requisicoes_df['Horas Decimais'].sum()
    else:
        total_requisicoes = 0  # Caso a coluna não exista

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

    # Criar gráfico combinado por dia
    fig = px.bar(
        df_combined,
        x='Data de abertura',
        y='Número de Atendimentos',
        title="Número de Atendimentos por Dia",
        color='Data de abertura',  # Para diferenciar os períodos
        labels={'Número de Atendimentos': 'Número de Atendimentos'},
    )
    
    # Customizar a aparência do gráfico
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Número de Atendimentos",
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_tickformat="%d/%m/%Y"  # Formato de data
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig)

else:
    st.info("Selecione um técnico para exibir os dados.")
