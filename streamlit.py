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

# Título centralizado no app
st.markdown("<h1 style='text-align: center;'>Dashboard de Atendimento</h1>", unsafe_allow_html=True)

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
    key="tecnico_selectbox",  # Chave única
    help="Escolha o técnico para filtrar os dados",
)

# Filtro de intervalo de datas
start_date = st.date_input(
    "Data de Início", 
    value=default_start_date, 
    min_value=min_date, 
    max_value=max_date, 
    format="DD/MM/YYYY",
    key="start_date_input",  # Chave única
    help="Escolha a data inicial para o filtrar os dados",
)

end_date = st.date_input(
    "Data de Fim", 
    value=max_date, 
    min_value=min_date, 
    max_value=max_date, 
    format="DD/MM/YYYY",
    key="end_date_input",  # Chave única
    help="Escolha a data final para o filtrar os dados",
)

# Validar e converter datas
if start_date and end_date:
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    if start_date > end_date:
        st.error("A data de início não pode ser maior que a data de fim.")

# Verificar colunas necessárias
if 'Data de abertura' in df.columns and 'Horas Decimais' in df.columns:
    df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')
    df['Horas Decimais'] = pd.to_numeric(df['Horas Decimais'], errors='coerce')

    # Filtrar dados por técnico e datas
    if tecnico:  # Só filtrar se o técnico foi selecionado
        filtered_df = df[df['Atribuído - Técnico'] == tecnico]
        if start_date:
            filtered_df = filtered_df[filtered_df['Data de abertura'] >= start_date]
        if end_date:
            filtered_df = filtered_df[filtered_df['Data de abertura'] <= end_date]

        # Calcular o total de horas por tipo
        incidentes_df = filtered_df[filtered_df['Tipo'] == 'Incidente']
        requisicoes_df = filtered_df[filtered_df['Tipo'] == 'Requisição']

        # Definir a ordem das prioridades
        prioridade_ordem = ['baixa', 'média', 'alta', 'muito alta']

        # Exibir tempos totais em incidentes com detalhes
        if not incidentes_df.empty:
            tempos_incidentes = incidentes_df.groupby('Prioridade')['Horas Decimais'].agg(['mean', 'max']).reset_index()

            # Reorganizar as prioridades conforme a ordem desejada
            tempos_incidentes['Prioridade'] = pd.Categorical(tempos_incidentes['Prioridade'], categories=prioridade_ordem, ordered=True)
            tempos_incidentes = tempos_incidentes.sort_values('Prioridade')

            tempos_incidentes['Média'] = tempos_incidentes['mean'].apply(format_hours_to_hms)
            tempos_incidentes['Máximo'] = tempos_incidentes['max'].apply(format_hours_to_hms)

            incidentes_detalhes = "".join([  
                f"<p><b>Prioridade {row['Prioridade']}:</b> Média: {row['Média']} | Máximo: {row['Máximo']}</p>"
                for _, row in tempos_incidentes.iterrows()
            ])

            st.markdown(
                f"""
                <div style='background-color: #C1D8E3; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                    <h2 style='text-align: center; color: #1E4C67;'>Tempo total em Incidentes:</h2>
                    <h1 style='text-align: center; color: #103D52; font-size: 1.2em; font-weight: bold;'>{format_hours_to_hms(incidentes_df['Horas Decimais'].sum())}</h1>
                    {incidentes_detalhes}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Exibir tempos totais em requisições com detalhes
        if not requisicoes_df.empty:
            tempos_requisicoes = requisicoes_df.groupby('Prioridade')['Horas Decimais'].agg(['mean', 'max']).reset_index()

            # Reorganizar as prioridades conforme a ordem desejada
            tempos_requisicoes['Prioridade'] = pd.Categorical(tempos_requisicoes['Prioridade'], categories=prioridade_ordem, ordered=True)
            tempos_requisicoes = tempos_requisicoes.sort_values('Prioridade')

            tempos_requisicoes['Média'] = tempos_requisicoes['mean'].apply(format_hours_to_hms)
            tempos_requisicoes['Máximo'] = tempos_requisicoes['max'].apply(format_hours_to_hms)

            requisicoes_detalhes = "".join([  
                f"<p><b>Prioridade {row['Prioridade']}:</b> Média: {row['Média']} | Máximo: {row['Máximo']}</p>"
                for _, row in tempos_requisicoes.iterrows()
            ])

            st.markdown(
                f"""
                <div style='background-color: #C1D8E3; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                    <h2 style='text-align: center; color: #1E4C67;'>Tempo total em Requisições:</h2>
                    <h1 style='text-align: center; color: #103D52; font-size: 1.2em; font-weight: bold;'>{format_hours_to_hms(requisicoes_df['Horas Decimais'].sum())}</h1>
                    {requisicoes_detalhes}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Gráficos de número de atendimentos por mês, separados por Tipo (Requisição e Incidente)
        incidentes_por_mes = incidentes_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos')
        requisicoes_por_mes = requisicoes_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos')

        # Verificar se os DataFrames não estão vazios e exibir os gráficos de barras
        if not incidentes_por_mes.empty:
            fig_incidentes = px.bar(
                incidentes_por_mes,
                x='Mês/Ano',
                y='Número de Atendimentos',
                title="Número de Atendimentos - Incidentes",
                color='Número de Atendimentos',
                labels={'Número de Atendimentos': 'Número de Incidentes', 'Mês/Ano': 'Mês/Ano'}
            )
            st.plotly_chart(fig_incidentes)

        if not requisicoes_por_mes.empty:
            fig_requisicoes = px.bar(
                requisicoes_por_mes,
                x='Mês/Ano',
                y='Número de Atendimentos',
                title="Número de Atendimentos - Requisições",
                color='Número de Atendimentos',
                labels={'Número de Atendimentos': 'Número de Requisições', 'Mês/Ano': 'Mês/Ano'}
            )
            st.plotly_chart(fig_requisicoes)

    else:
        st.error("Colunas necessárias não encontradas no arquivo.")
