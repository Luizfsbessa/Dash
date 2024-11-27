import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
def load_data(file_path="backtest.xlsx"):
    df = pd.read_excel(file_path)
    df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], errors='coerce')
    df['Mês/Ano'] = df['Data de abertura'].dt.to_period('M').astype(str)
    df['Horas Decimais'] = df['Tempo em atendimento'].apply(time_to_hours)
    return df

# Converter tempo de atendimento para horas decimais
def time_to_hours(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h + m / 60 + s / 3600
    except ValueError:
        return 0

# Formatar horas decimais no formato "HH:MM:SS"
def format_hours_to_hms(decimal_hours):
    h = int(decimal_hours)
    m = int((decimal_hours - h) * 60)
    s = int(((decimal_hours - h) * 60 - m) * 60)
    return f"{h:02}:{m:02}:{s:02}"

# Exibir gráficos
def display_bar_chart(data, title, color, x, y):
    fig = px.bar(data, x=x, y=y, text=y, title=title, color_discrete_sequence=[color])
    fig.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
    fig.update_layout(xaxis_title=None, yaxis_title=None, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="black"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False, zeroline=False, showline=False, showticklabels=False)
    st.plotly_chart(fig)

def display_pie_chart(data, title, color_map):
    fig = px.pie(data, names='Prioridade', values='Número de Atendimentos', title=title, color='Prioridade', color_discrete_map=color_map)
    st.plotly_chart(fig)

# Estilizando o app
def style_app():
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
    </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)

# Função principal de exibição
def main():
    # Carregar dados
    df = load_data()

    # Título do app
    st.title("Dashboard de Atendimento")

    # Estilizando o fundo e a cor do texto
    style_app()

    # Filtros de técnico e data
    tecnico = st.selectbox("Selecionar Técnico:", options=[""] + sorted(df['Atribuído - Técnico'].dropna().unique()), help="Escolha o técnico para filtrar os dados")
    start_date = st.date_input("Data de Início", value=df['Data de abertura'].min(), min_value=df['Data de abertura'].min(), max_value=df['Data de abertura'].max(), help="Escolha a data inicial")
    end_date = st.date_input("Data de Fim", value=df['Data de abertura'].max(), min_value=df['Data de abertura'].min(), max_value=df['Data de abertura'].max(), help="Escolha a data final")

    # Validação de datas
    if start_date > end_date:
        st.error("A data de início não pode ser maior que a data de fim.")

    # Filtrar os dados
    filtered_df = df[(df['Data de abertura'] >= pd.to_datetime(start_date)) & (df['Data de abertura'] <= pd.to_datetime(end_date))]
    if tecnico:
        filtered_df = filtered_df[filtered_df['Atribuído - Técnico'] == tecnico]

    # Cálculos de tempos médios e máximos
    incidentes_df = filtered_df[filtered_df['Tipo'] == 'Incidente']
    requisicoes_df = filtered_df[filtered_df['Tipo'] == 'Requisição']

    # Exibir os tempos e gráficos
    if not incidentes_df.empty:
        st.markdown(f"<b>Tempo total em Incidentes:</b> {format_hours_to_hms(incidentes_df['Horas Decimais'].sum())}", unsafe_allow_html=True)
        display_bar_chart(incidentes_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos'), "Número de Atendimentos por Mês - Incidentes", '#1EA4B6', 'Mês/Ano', 'Número de Atendimentos')
        display_pie_chart(incidentes_df.groupby('Prioridade').size().reset_index(name='Número de Atendimentos'), "Distribuição de Incidentes por Prioridade", {'Baixa': '#90ACB8', 'Média': '#587D8E', 'Alta': '#C1D8E3', 'Muito Alta': '#2D55263'})

    if not requisicoes_df.empty:
        st.markdown(f"<b>Tempo total em Requisições:</b> {format_hours_to_hms(requisicoes_df['Horas Decimais'].sum())}", unsafe_allow_html=True)
        display_bar_chart(requisicoes_df.groupby('Mês/Ano').size().reset_index(name='Número de Atendimentos'), "Número de Atendimentos por Mês - Requisições", '#00C6E0', 'Mês/Ano', 'Número de Atendimentos')
        display_pie_chart(requisicoes_df.groupby('Prioridade').size().reset_index(name='Número de Atendimentos'), "Distribuição de Requisições por Prioridade", {'Baixa': '#90ACB8', 'Média': '#587D8E', 'Alta': '#C1D8E3', 'Muito Alta': '#2D55263'})

if __name__ == "__main__":
    main()

