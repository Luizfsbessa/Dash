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

# Converter a coluna 'Tempo em atendimento' para horas decimais
def time_to_hours(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h + m / 60 + s / 3600
    except ValueError:
        return 0

# Formatar horas decimais no formato hh:mm:ss
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
    options=[""] + sorted(df['Atribuído - Técnico'].dropna().unique()),  # Adicionar opção em branco
    format_func=lambda x: "Selecione um técnico" if x == "" else x  # Placeholder para a opção em branco
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
elif tecnico:
    # Filtragem de dados
    filtered_df = df[df['Atribuído - Técnico'] == tecnico]
    if start_date:
        filtered_df = filtered_df[filtered_df['Data de abertura'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['Data de abertura'] <= pd.to_datetime(end_date)]

    # Segregar por tipo
    incidentes_df = filtered_df[filtered_df['Tipo'] == 'Incidente']
    requisicoes_df = filtered_df[filtered_df['Tipo'] == 'Requisição']

    # Calcular o total de atendimentos e horas
    total_incidentes = incidentes_df['Horas Decimais'].sum()
    total_requisicoes = requisicoes_df['Horas Decimais'].sum()

    formatted_incidentes = format_hours_to_hms(total_incidentes)
    formatted_requisicoes = format_hours_to_hms(total_requisicoes)

    # Exibir os tempos totais
    st.markdown(
        f"""
        <div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center;'>
            <strong>Tempo total em Incidentes:</strong> {formatted_incidentes}
        </div>
        <div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center; margin-top: 10px;'>
            <strong>Tempo total em Requisições:</strong> {formatted_requisicoes}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Gráfico de número de atendimentos por mês (Requisições)
    requisicoes_por_mes = requisicoes_df.groupby('Período').size().reset_index(name='Atendimentos')
    if not requisicoes_por_mes.empty:
        fig_requisicoes = px.bar(
            requisicoes_por_mes,
            x='Período',
            y='Atendimentos',
            title="Atendimentos por Mês - Requisições",
            labels={'Período': '', 'Atendimentos': ''},
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
            labels={'Período': '', 'Atendimentos': ''},
            template="simple_white"
        )
        fig_incidentes.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
        fig_incidentes.update_xaxes(showgrid=False)
        fig_incidentes.update_yaxes(showgrid=False)
        st.plotly_chart(fig_incidentes)

    # Gráfico de pizza (Esforços por fornecedor)
    fornecedor_counts = filtered_df['Atribuído - Atribuído a um fornecedor'].value_counts().reset_index()
    fornecedor_counts.columns = ['Fornecedor', 'Atendimentos']
    if not fornecedor_counts.empty:
        fig_pizza = px.pie(
            fornecedor_counts,
            names='Fornecedor',
            values='Atendimentos',
            title="Distribuição de Esforços por Fornecedor"
        )
        st.plotly_chart(fig_pizza)
else:
    st.info("Selecione um técnico para exibir os dados.")
