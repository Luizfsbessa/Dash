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
    'Prioridade': ['Alta', 'Média', 'Baixa', 'Alta', 'Média']
})

requisicoes_df = pd.DataFrame({
    'Horas Decimais': [0.5, 1.0, 2.5, 1.5, 1.0],
    'Prioridade': ['Baixa', 'Média', 'Alta', 'Alta', 'Baixa']
})

# Cálculo do total de tempo
total_incidentes = incidentes_df['Horas Decimais'].sum()
total_requisicoes = requisicoes_df['Horas Decimais'].sum()

# Detalhamento de tempos médio e máximo por prioridade
tempos_incidentes = pd.DataFrame({
    'Prioridade': ['Alta', 'Média', 'Baixa'],
    'Média': [1.8, 2.1, 1.0],
    'Máximo': [3.5, 2.5, 1.5]
})

tempos_requisicoes = pd.DataFrame({
    'Prioridade': ['Alta', 'Média', 'Baixa'],
    'Média': [1.2, 1.5, 1.0],
    'Máximo': [2.5, 2.0, 1.5]
})

# Detalhes dos tempos médios e máximos para inserir na caixa
incidentes_detalhes = "".join([  
    f"<li><b>{row['Prioridade']}:</b> Média: {row['Média']} | Máximo: {row['Máximo']}</li>"
    for _, row in tempos_incidentes.iterrows()
])

requisicoes_detalhes = "".join([  
    f"<li><b>{row['Prioridade']}:</b> Média: {row['Média']} | Máximo: {row['Máximo']}</li>"
    for _, row in tempos_requisicoes.iterrows()
])

# Exibindo os totais de tempo
st.markdown(exibir_total_tempo("Tempo total em Incidentes", total_incidentes, incidentes_detalhes), unsafe_allow_html=True)
st.markdown(exibir_total_tempo("Tempo total em Requisições", total_requisicoes, requisicoes_detalhes), unsafe_allow_html=True)

# Gráficos de barras - Número de atendimentos por mês
incidentes_por_mes = pd.DataFrame({
    'Mês/Ano': ['Jan/2024', 'Fev/2024', 'Mar/2024'],
    'Número de Atendimentos': [100, 150, 120]
})

requisicoes_por_mes = pd.DataFrame({
    'Mês/Ano': ['Jan/2024', 'Fev/2024', 'Mar/2024'],
    'Número de Atendimentos': [80, 130, 110]
})

# Gráficos de barras para número de atendimentos
if not incidentes_por_mes.empty:
    fig_incidentes = px.bar(
        incidentes_por_mes,
        x='Mês/Ano',
        y='Número de Atendimentos',
        text='Número de Atendimentos',
        title="Número de Atendimentos por Mês - Incidentes",
        color_discrete_sequence=['#1EA4B6']  # Cor para Incidentes
    )
    fig_incidentes.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
    fig_incidentes.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="black"),
    )
    fig_incidentes.update_xaxes(showgrid=False)
    fig_incidentes.update_yaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        showticklabels=False
    )
    st.plotly_chart(fig_incidentes)

if not requisicoes_por_mes.empty:
    fig_requisicoes = px.bar(
        requisicoes_por_mes,
        x='Mês/Ano',
        y='Número de Atendimentos',
        text='Número de Atendimentos',
        title="Número de Atendimentos por Mês - Requisições",
        color_discrete_sequence=['#00C6E0']  # Cor para Requisições
    )
    fig_requisicoes.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
    fig_requisicoes.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="black"),
    )
    fig_requisicoes.update_xaxes(showgrid=False)
    fig_requisicoes.update_yaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        showticklabels=False
    )
    st.plotly_chart(fig_requisicoes)

# Gráficos de pizza para distribuição por prioridade
incidentes_por_prioridade = pd.DataFrame({
    'Prioridade': ['Alta', 'Média', 'Baixa'],
    'Número de Atendimentos': [50, 80, 70]
})

requisicoes_por_prioridade = pd.DataFrame({
    'Prioridade': ['Alta', 'Média', 'Baixa'],
    'Número de Atendimentos': [30, 60, 40]
})

# Gráficos de pizza
if not incidentes_por_prioridade.empty:
    fig_incidentes_pizza = px.pie(
        incidentes_por_prioridade,
        names='Prioridade',
        values='Número de Atendimentos',
        title="Distribuição de Incidentes por Prioridade",
        color='Prioridade',
        color_discrete_map={'Alta': '#E60000', 'Média': '#FFD700', 'Baixa': '#228B22'}  # Cores customizadas
    )
    st.plotly_chart(fig_incidentes_pizza)

if not requisicoes_por_prioridade.empty:
    fig_requisicoes_pizza = px.pie(
        requisicoes_por_prioridade,
        names='Prioridade',
        values='Número de Atendimentos',
        title="Distribuição de Requisições por Prioridade",
        color='Prioridade',
        color_discrete_map={'Alta': '#E60000', 'Média': '#FFD700', 'Baixa': '#228B22'}  # Cores customizadas
    )
    st.plotly_chart(fig_requisicoes_pizza)

