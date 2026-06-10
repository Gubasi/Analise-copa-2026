import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------
# Configuração da página
# ----------------------------------------
st.set_page_config(
    page_title="Copa 2026 — Análise de Elencos",
    page_icon="⚽",
    layout="wide"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    [data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------
# Leitura dos dados
# ----------------------------------------
df = pd.read_excel("FIFA_WC2026_Squads_Groups.xlsx")


# Adiciona o grupo de cada seleção
grupos = {
    'Algeria (ALG)': 'Grupo J',      'Argentina (ARG)': 'Grupo J',
    'Australia (AUS)': 'Grupo D',    'Austria (AUT)': 'Grupo J',
    'Belgium (BEL)': 'Grupo G',      'Bosnia And Herzegovina (BIH)': 'Grupo B',
    'Brazil (BRA)': 'Grupo C',       'Cabo Verde (CPV)': 'Grupo H',
    'Canada (CAN)': 'Grupo B',       'Colombia (COL)': 'Grupo K',
    'Congo DR (COD)': 'Grupo K',     "Côte D'Ivoire (CIV)": 'Grupo E',
    'Croatia (CRO)': 'Grupo L',      'Curaçao (CUW)': 'Grupo E',
    'Czechia (CZE)': 'Grupo A',      'Ecuador (ECU)': 'Grupo E',
    'Egypt (EGY)': 'Grupo G',        'England (ENG)': 'Grupo L',
    'France (FRA)': 'Grupo I',       'Germany (GER)': 'Grupo E',
    'Ghana (GHA)': 'Grupo L',        'Haiti (HAI)': 'Grupo C',
    'IR Iran (IRN)': 'Grupo G',      'Iraq (IRQ)': 'Grupo I',
    'Japan (JPN)': 'Grupo F',        'Jordan (JOR)': 'Grupo J',
    'Korea Republic (KOR)': 'Grupo A', 'Mexico (MEX)': 'Grupo A',
    'Morocco (MAR)': 'Grupo C',      'Netherlands (NED)': 'Grupo F',
    'New Zealand (NZL)': 'Grupo G',  'Norway (NOR)': 'Grupo I',
    'Panama (PAN)': 'Grupo L',       'Paraguay (PAR)': 'Grupo D',
    'Portugal (POR)': 'Grupo K',     'Qatar (QAT)': 'Grupo B',
    'Saudi Arabia (KSA)': 'Grupo H', 'Scotland (SCO)': 'Grupo C',
    'Senegal (SEN)': 'Grupo I',      'South Africa (RSA)': 'Grupo A',
    'Spain (ESP)': 'Grupo H',        'Sweden (SWE)': 'Grupo F',
    'Switzerland (SUI)': 'Grupo B',  'Tunisia (TUN)': 'Grupo F',
    'Türkiye (TUR)': 'Grupo D',      'USA (USA)': 'Grupo D',
    'Uruguay (URU)': 'Grupo H',      'Uzbekistan (UZB)': 'Grupo K',
}
df['GRUPO'] = df['TEAM'].map(grupos)

# Nome do país sem o código (ex: "France (FRA)" → "France")
df['PAIS'] = df['TEAM'].str.extract(r'^(.*?)\s*\(')

# Converte valor de mercado para número em milhões
def converter_valor(v):
    v = str(v).replace(',', '.')
    if 'K' in v:
        return float(v.replace('K', '')) / 1000
    if 'M' in v:
        return float(v.replace('M', ''))
    return 0.0

df['VALOR_M'] = df['MARKET_VALUE'].apply(converter_valor)


# ----------------------------------------
# Sidebar com filtros e navegação
# ----------------------------------------
with st.sidebar:
    st.title("⚽ Copa 2026")
    st.caption("Análise dos elencos convocados")
    st.divider()

    pagina = st.radio("Navegar", [
        "🏠 Início",
        "💰 Valores",
        "🎂 Idades",
        "🏟️ Clubes & Ligas",
        "📋 Por Grupo"
    ])

    st.divider()

    grupo_filtro = st.selectbox("Filtrar por grupo", ["Todos"] + sorted(df['GRUPO'].unique()))
    pos_filtro   = st.selectbox("Filtrar por posição", ["Todas"] + sorted(df['POS'].unique()))

# Aplica os filtros
dados = df.copy()
if grupo_filtro != "Todos":
    dados = dados[dados['GRUPO'] == grupo_filtro]
if pos_filtro != "Todas":
    dados = dados[dados['POS'] == pos_filtro]


# ----------------------------------------
# Página: Início
# ----------------------------------------
if pagina == "🏠 Início":
    st.title("⚽ Copa do Mundo 2026 — Análise de Elencos")
    st.caption("48 seleções · 1.248 jogadores · 12 grupos · Fonte: FIFA")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Seleções",    "48")
    c2.metric("Jogadores",   "1.248")
    c3.metric("Valor total", f"€ {df['VALOR_M'].sum()/1000:.1f}B")
    c4.metric("Idade média", f"{df['AGE'].mean():.1f} anos")

    st.divider()
    st.subheader("Valor total por grupo")

    por_grupo = df.groupby('GRUPO')['VALOR_M'].sum().reset_index().sort_values('VALOR_M', ascending=False)
    por_grupo['VALOR_B'] = por_grupo['VALOR_M'] / 1000
    fig = px.bar(por_grupo, x='GRUPO', y='VALOR_B', text='VALOR_B',
                 color='VALOR_B', color_continuous_scale='Blues',
                 labels={'GRUPO': '', 'VALOR_B': 'Valor (€B)'})
    fig.update_traces(texttemplate='€%{text:.2f}B', textposition='outside')
    fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                      font_color='white', coloraxis_showscale=False, height=380)
    fig.update_yaxes(gridcolor='#30363d')
    st.plotly_chart(fig, use_container_width=True)

    st.caption("💡 Grupo I (França, Senegal, Noruega, Iraque) é o mais valioso com €2,6B — quase 5x mais que o Grupo A.")


# ----------------------------------------
# Página: Valores
# ----------------------------------------
elif pagina == "💰 Valores":
    st.title("💰 Valores de mercado")
    st.divider()

    top_n = st.slider("Quantos jogadores exibir", 5, 30, 15)

    st.subheader(f"Top {top_n} jogadores mais valiosos")
    top_jogadores = dados.nlargest(top_n, 'VALOR_M')[['PLAYER NAME', 'PAIS', 'POS', 'VALOR_M', 'GRUPO']]

    fig = px.bar(top_jogadores, x='VALOR_M', y='PLAYER NAME', orientation='h',
                 color='GRUPO', text='VALOR_M', hover_data=['PAIS', 'POS'],
                 labels={'VALOR_M': 'Valor (€M)', 'PLAYER NAME': ''})
    fig.update_traces(texttemplate='€%{text:.0f}M', textposition='outside')
    fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22', font_color='white',
                      yaxis={'categoryorder': 'total ascending'}, height=max(400, top_n * 28),
                      margin=dict(r=80))
    fig.update_xaxes(gridcolor='#30363d')
    fig.update_yaxes(gridcolor='#30363d')
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Seleções mais valiosas")

    por_selecao = dados.groupby(['PAIS', 'GRUPO'])['VALOR_M'].sum().reset_index().sort_values('VALOR_M', ascending=False).head(20)
    por_selecao['VALOR_B'] = por_selecao['VALOR_M'] / 1000
    fig2 = px.bar(por_selecao, x='PAIS', y='VALOR_B', color='GRUPO', text='VALOR_B',
                  labels={'VALOR_B': 'Valor total (€B)', 'PAIS': ''})
    fig2.update_traces(texttemplate='€%{text:.2f}B', textposition='outside')
    fig2.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                       font_color='white', height=430, margin=dict(t=20))
    fig2.update_yaxes(gridcolor='#30363d')
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("💡 França lidera com €1,5B — mais do que o dobro do Brasil (€941M), vice-líder.")


# ----------------------------------------
# Página: Idades
# ----------------------------------------
elif pagina == "🎂 Idades":
    st.title("🎂 Análise de idades")
    st.divider()

    c1, c2, c3 = st.columns(3)
    c1.metric("Mais velho", f"{dados['AGE'].max()} anos", dados[dados['AGE'] == dados['AGE'].max()]['PLAYER NAME'].values[0])
    c2.metric("Mais novo",  f"{dados['AGE'].min()} anos", dados[dados['AGE'] == dados['AGE'].min()]['PLAYER NAME'].values[0])
    c3.metric("Média geral", f"{dados['AGE'].mean():.1f} anos")

    st.divider()
    st.subheader("Distribuição de idades")

    fig = px.histogram(dados, x='AGE', nbins=27, color_discrete_sequence=['#388bfd'],
                       labels={'AGE': 'Idade', 'count': 'Jogadores'})
    fig.add_vline(x=dados['AGE'].mean(), line_dash='dash', line_color='#f0a500',
                  annotation_text=f"Média: {dados['AGE'].mean():.1f}",
                  annotation_font_color='#f0a500')
    fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                      font_color='white', height=360, bargap=0.1)
    fig.update_xaxes(gridcolor='#30363d', dtick=1)
    fig.update_yaxes(gridcolor='#30363d')
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Média de idade por seleção")

    media_idade = dados.groupby(['PAIS', 'GRUPO'])['AGE'].mean().reset_index()
    media_idade.columns = ['PAIS', 'GRUPO', 'MEDIA']

    aba1, aba2 = st.tabs(["👴 Mais velhos", "👶 Mais jovens"])
    with aba1:
        d = media_idade.nlargest(15, 'MEDIA')
        fig = px.bar(d, x='PAIS', y='MEDIA', color='GRUPO', text='MEDIA',
                     labels={'MEDIA': 'Média de idade', 'PAIS': ''})
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                          font_color='white', height=400)
        fig.update_yaxes(gridcolor='#30363d', range=[24, 32])
        st.plotly_chart(fig, use_container_width=True)
    with aba2:
        d = media_idade.nsmallest(15, 'MEDIA')
        fig = px.bar(d, x='PAIS', y='MEDIA', color='GRUPO', text='MEDIA',
                     labels={'MEDIA': 'Média de idade', 'PAIS': ''})
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                          font_color='white', height=400)
        fig.update_yaxes(gridcolor='#30363d', range=[24, 32])
        st.plotly_chart(fig, use_container_width=True)

    st.caption("💡 A faixa de 25–28 anos concentra o maior número de convocados — a geração principal desta Copa.")


# ----------------------------------------
# Página: Clubes & Ligas
# ----------------------------------------
elif pagina == "🏟️ Clubes & Ligas":
    st.title("🏟️ Clubes & Ligas")
    st.divider()

    top_n = st.slider("Quantos exibir no ranking", 5, 25, 15)

    aba1, aba2 = st.tabs(["🌍 Ligas", "🏟️ Clubes"])

    with aba1:
        st.subheader("Ligas com mais convocados")
        ligas = dados['Liga'].value_counts().head(top_n).reset_index()
        ligas.columns = ['Liga', 'Jogadores']

        fig = px.bar(ligas, x='Jogadores', y='Liga', orientation='h', text='Jogadores',
                     color='Jogadores', color_continuous_scale='Blues',
                     labels={'Liga': ''})
        fig.update_traces(textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22', font_color='white',
                          height=max(400, top_n * 30), yaxis={'categoryorder': 'total ascending'},
                          coloraxis_showscale=False, margin=dict(r=40))
        fig.update_xaxes(gridcolor='#30363d')
        fig.update_yaxes(gridcolor='#30363d')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("💡 Premier League tem 154 convocados — mais que o dobro da Bundesliga (98), segunda colocada.")

    with aba2:
        st.subheader("Clubes com mais convocados")
        clube_limpo = dados['CLUB'].str.extract(r'^(.*?)\s*\(')[0].fillna(dados['CLUB'])
        clubes = clube_limpo.value_counts().head(top_n).reset_index()
        clubes.columns = ['Clube', 'Jogadores']

        fig = px.bar(clubes, x='Jogadores', y='Clube', orientation='h', text='Jogadores',
                     color='Jogadores', color_continuous_scale='Greens',
                     labels={'Clube': ''})
        fig.update_traces(textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22', font_color='white',
                          height=max(400, top_n * 30), yaxis={'categoryorder': 'total ascending'},
                          coloraxis_showscale=False, margin=dict(r=40))
        fig.update_xaxes(gridcolor='#30363d')
        fig.update_yaxes(gridcolor='#30363d')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("💡 Manchester City lidera com 19 convocados — seguido de perto por Bayern München (18) e Arsenal (16).")

    st.divider()
    st.subheader("Jogadores por divisão")
    col1, col2 = st.columns(2)
    with col1:
        div = dados['Divisão'].value_counts().reset_index()
        div.columns = ['Divisão', 'Jogadores']
        fig = px.pie(div, names='Divisão', values='Jogadores', hole=0.4,
                     color_discrete_sequence=['#388bfd', '#58a6ff', '#79c0ff', '#a5d6ff'])
        fig.update_layout(paper_bgcolor='#0e1117', font_color='white', height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        for _, row in div.iterrows():
            pct = row['Jogadores'] / len(dados) * 100
            st.markdown(f"**{row['Divisão']}** — {row['Jogadores']} jogadores ({pct:.1f}%)")


# ----------------------------------------
# Página: Por Grupo
# ----------------------------------------
elif pagina == "📋 Por Grupo":
    st.title("📋 Análise por grupo")
    st.divider()

    modo = st.radio("", ["Comparar todos os grupos", "Ver um grupo específico"], horizontal=True)

    if modo == "Comparar todos os grupos":

        st.subheader("Valor total por grupo")
        por_grupo = df.groupby('GRUPO')['VALOR_M'].sum().reset_index().sort_values('VALOR_M', ascending=False)
        por_grupo['VALOR_B'] = por_grupo['VALOR_M'] / 1000
        fig = px.bar(por_grupo, x='GRUPO', y='VALOR_B', text='VALOR_B',
                     color='VALOR_B', color_continuous_scale='Blues',
                     labels={'GRUPO': '', 'VALOR_B': 'Valor (€B)'})
        fig.update_traces(texttemplate='€%{text:.2f}B', textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                          font_color='white', coloraxis_showscale=False, height=380)
        fig.update_yaxes(gridcolor='#30363d')
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Idade média por grupo")
        por_grupo_idade = df.groupby('GRUPO')['AGE'].mean().reset_index().sort_values('AGE', ascending=False)
        fig2 = px.bar(por_grupo_idade, x='GRUPO', y='AGE', text='AGE',
                      color='AGE', color_continuous_scale='Oranges',
                      labels={'GRUPO': '', 'AGE': 'Idade média'})
        fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig2.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                           font_color='white', coloraxis_showscale=False, height=380)
        fig2.update_yaxes(gridcolor='#30363d', range=[25, 30])
        st.plotly_chart(fig2, use_container_width=True)

    else:
        grupo_escolhido = st.selectbox("Escolha o grupo", sorted(df['GRUPO'].unique()))
        df_g = df[df['GRUPO'] == grupo_escolhido]

        st.divider()

        # Cards das 4 seleções
        selecoes = df_g.groupby('PAIS').agg(
            valor=('VALOR_M', 'sum'),
            idade=('AGE', 'mean'),
            jogadores=('PLAYER NAME', 'count')
        ).reset_index().sort_values('valor', ascending=False)

        cols = st.columns(4)
        for i, (_, row) in enumerate(selecoes.iterrows()):
            with cols[i]:
                valor_fmt = f"€ {row['valor']/1000:.2f}B" if row['valor'] >= 1000 else f"€ {row['valor']:.0f}M"
                st.metric(row['PAIS'], valor_fmt, f"Média: {row['idade']:.1f} anos")

        st.divider()
        st.subheader(f"Top jogadores — {grupo_escolhido}")

        top_g = df_g.nlargest(15, 'VALOR_M')[['PLAYER NAME', 'PAIS', 'POS', 'AGE', 'VALOR_M']]
        fig = px.bar(top_g, x='VALOR_M', y='PLAYER NAME', orientation='h',
                     color='PAIS', text='VALOR_M',
                     labels={'VALOR_M': 'Valor (€M)', 'PLAYER NAME': ''})
        fig.update_traces(texttemplate='€%{text:.0f}M', textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22', font_color='white',
                          height=460, yaxis={'categoryorder': 'total ascending'}, margin=dict(r=80))
        fig.update_xaxes(gridcolor='#30363d')
        fig.update_yaxes(gridcolor='#30363d')
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        if st.checkbox(f"Ver todos os jogadores do {grupo_escolhido}"):
            tabela = (df_g[['PLAYER NAME', 'PAIS', 'POS', 'AGE', 'CLUB', 'VALOR_M']]
                      .sort_values('VALOR_M', ascending=False).reset_index(drop=True))
            tabela.index += 1
            tabela.columns = ['Jogador', 'Seleção', 'Pos', 'Idade', 'Clube', 'Valor (€M)']
            st.dataframe(tabela, use_container_width=True)


# ----------------------------------------
# Rodapé
# ----------------------------------------
st.divider()
st.caption("⚽ Copa do Mundo 2026 · Dados: FIFA · Feito com Python, Pandas e Streamlit")
