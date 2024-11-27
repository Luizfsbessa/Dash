import pandas as pd
import plotly.express as px
import streamlit as st

# Função para formatar horas para o formato HH:MM:SS
def format_hours_to_hms(hours):
    hours = int(hours)
    minutes = int((hours * 60) % 60)
    seconds = int((hours * 3600) % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Função para exibir os totais de tempo de maneira destacada
def exibir_total_tempo(titulo, total, tempos_detalhes):
    return f"""
    <div style='background-color: #A1C6D8; padding: 20px; border-radius: 8px; margin-bottom: 20px;'>
        <h3 style="margin-top: 0; font-size: 20px;">{titulo}</h3>
        <b>Tempo Total:</b> {format_hours_to_hms(total)} <br><br>
        <ul>
            {tempos_detalhes}
        </ul>
    </div>
    """

# Exemplo de DataFrames de incidentes e requisições
incidentes_df = pd.DataFrame({
    'Horas Decimais': [1.5, 2.0, 1.2, 3.5, 4.0],
    'Prioridade': ['Alta', 'Média', 'Baixa', 'Alta', 'Média'],
    'Mês/Ano': ['Jan/2024', 'Fev/2024', 'Mar/2024', 'Abr/2024', 'Mai/2024']
})

requisicoes_df = pd.DataFrame({
    'Horas Decimais': [0.5, 1.0, 2.5, 1.5, 1.0],
    'Prioridade': ['Baixa', 'Média', 'Alta', 'Alta', 'Baixa'],
    'Mês/Ano': ['Jan/2024', 'Fev/2024', 'Mar/2024', 'Abr/2024', 'Mai/2024']
})

# Menu de seleção para escolher os dados (Incidentes ou Requisições)
selecao_dados = st.selectbox("Escolha os dados", ["Incidentes", "Requisições"])

# Selecione a prioridade
selecao_prioridade = st.selectbox("Selecione a Prioridade", ["Todas", "Alta", "Média", "Baixa"])

# Selecione o período (meses)
selecao_periodo = st.selectbox("Selecione o Período", ["Todos", "Jan/2024", "Fev/2024", "Mar/2024", "Abr/2024", "Mai/2024"])

# Função para calcular os totais de tempo, baseado na seleção do usuário
def calcular_totais(df, tipo, prioridade, periodo):
    if tipo == "Incidentes":
        df_filtrado = incidentes_df
    else:
        df_filtrado = requisicoes_df

    # Filtrando por prioridade
    if prioridade != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Prioridade'] == prioridade]

    # Filtrando por período
    if periodo != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Mês/Ano'] == periodo]

    # Cálculo do tempo total
    total_tempo = df_filtrado['Horas Decimais'].sum()
    return total_tempo, df_filtrado

# Calculando os totais de tempo
total_tempo, df_filtrado = calcular_totais(None, selecao_dados, selecao_prioridade, selecao_periodo)

# Detalhando os tempos médios e máximos por prioridade
tempos_medio_maximo = df_filtrado.groupby('Prioridade').agg(
    Média=('Horas Decimais', 'mean'),
    Máximo=('Horas Decimais', 'max')
).reset_index()

# Exibindo os totais de tempo
detalhes_tempo = "".join([  
    f"<li><b>{row['Prioridade']}:</b> Média: {format_hours_to_hms(row['Média'])} | Máximo: {format_hours_to_hms(row['Máximo'])}</li>"
    for _, row in tempos_medio_maximo.iterrows()
])

st.markdown(exibir_total_tempo(f"Tempo Total em {selecao_dados}", total_tempo, detalhes_tempo), unsafe_allow_html=True)

# Definir cores personalizadas para cada prioridade
prioridade_cores = {
    'Baixa': '#90ACB8',
    'Média': '#587D8E',
    'Alta': '#C1D8E3',
    'Muito Alta': '#2D55263'
}

# Gráficos de barras - Número de atendimentos por mês
if not df_filtrado.empty:
    fig = px.bar(
        df_filtrado,
        x='Mês/Ano',
        y='Horas Decimais',
        title=f"Número de Atendimentos por Mês - {selecao_dados}",
        text='Horas Decimais',
        color='Prioridade',
        color_discrete_map=prioridade_cores  # Cores personalizadas
    )
    fig.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Horas",
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="black"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        showticklabels=False
    )
    st.plotly_chart(fig)

# Gráficos de pizza para distribuição por prioridade
df_prioridade = df_filtrado.groupby('Prioridade').agg(
    Total=('Horas Decimais', 'sum')
).reset_index()

# Gráfico de pizza
fig_pizza = px.pie(
    df_prioridade,
    names='Prioridade',
    values='Total',
    title=f"Distribuição de {selecao_dados} por Prioridade",
    color='Prioridade',
    color_discrete_map=prioridade_cores  # Cores personalizadas
)
st.plotly_chart(fig_pizza)
