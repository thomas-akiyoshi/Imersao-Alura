import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Estilo CSS Personalizado (Filtros Fixos) ---
st.markdown(
    """
    <style>
    /* Fundo da página rosa pastel bem claro */
    .stApp {
        background-color: #fff0f5;
    }

    /* Fundo cinza com transparência para gráficos e tabelas */
    div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] {
        background-color: rgba(200, 200, 200, 0.3);
        padding: 15px;
        border-radius: 10px;
    }

    /* Fixar o primeiro bloco horizontal (onde estão os filtros) no topo ao rolar */
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:nth-of-type(1) {
        position: sticky;
        top: 0;
        z-index: 1000;
        background-color: #fff0f5;
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros abaixo para refinar sua análise.")

# --- Filtros (Layout Moderno) ---
st.subheader("🔍 Filtros")

col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
with col_filtro1:
    anos_selecionados = st.multiselect("Ano", options=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
with col_filtro2:
    senioridades_selecionadas = st.multiselect("Senioridade", options=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
with col_filtro3:
    contratos_selecionados = st.multiselect("Tipo de Contrato", options=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
with col_filtro4:
    tamanhos_selecionados = st.multiselect("Tamanho da Empresa", options=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas. Se vazio, considera todos.
df_filtrado = df.copy()

if anos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['ano'].isin(anos_selecionados)]
if senioridades_selecionadas:
    df_filtrado = df_filtrado[df_filtrado['senioridade'].isin(senioridades_selecionadas)]
if contratos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['contrato'].isin(contratos_selecionados)]
if tamanhos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['tamanho_empresa'].isin(tamanhos_selecionados)]

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

col_graf5, col_graf6 = st.columns(2)

with col_graf5:
    if not df_filtrado.empty:
        df_data_scientist = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']

        df_salario_pais_ds = df_data_scientist.groupby('empresa')['usd'].mean().sort_values(ascending=False).reset_index()

        fig = px.bar(
            df_salario_pais_ds,
            x='empresa',
            y='usd',
            title='Média Salarial para Cientistas de Dados por País',
            labels={'empresa': 'País da Empresa', 'usd': 'Média Salarial Anual em USD'},
            color='empresa',
            color_discrete_sequence=px.colors.qualitative.Plotly
)

        fig.update_layout(xaxis_title='País da Empresa', yaxis_title='Média Salarial Anual em USD')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de salário por país para Cientistas de Dados.")  

with col_graf6:
    if not df_filtrado.empty:
        # Filtrar apenas para cargos de 'Data Scientist' (já feito no código anterior)
        df_data_scientist = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']

        # Calcular a média salarial por país para Cientistas de Dados (já feito)
        df_salario_pais_ds = df_data_scientist.groupby('empresa')['usd'].mean().sort_values(ascending=False).reset_index()

        # Selecionar o Top 10 países
        top_10_paises = df_salario_pais_ds.head(10)

        # Calcular a média salarial para os países restantes (fora do Top 10)
        media_outros = df_salario_pais_ds.iloc[10:]['usd'].mean()

        # Criar um DataFrame para a categoria 'Outros'
        df_outros = pd.DataFrame([{'empresa': 'Outros', 'usd': media_outros}])

        # Concatenar o Top 10 com a categoria 'Outros'
        df_final_plot = pd.concat([top_10_paises, df_outros])

        # Criar o gráfico de barras horizontal com Plotly
        fig = px.bar(
            df_final_plot,
            y='empresa',  # Eixo Y para os países
            x='usd',      # Eixo X para o salário
            title='Top 10 Países com Maior Salário Médio para Cientistas de Dados',
            labels={'empresa': 'País da Empresa', 'usd': 'Média Salarial Anual em USD'},
            color='empresa',
            color_discrete_sequence=px.colors.qualitative.Plotly,
            orientation='h' # Definir como horizontal
        )

        fig.update_layout(yaxis_title='País da Empresa', xaxis_title='Média Salarial Anual em USD')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de Top 10 países para Cientistas de Dados.")


# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)