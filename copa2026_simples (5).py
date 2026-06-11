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

# Formata valor: B se >= 1B, M se menor
def fmt_valor(v_milhoes):
    if v_milhoes >= 1000:
        b = v_milhoes / 1000
        return f"€{b:.2f}B" if b % 1 != 0 else f"€{int(b)}B"
    else:
        m = round(v_milhoes)
        return f"€{m}M"

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
    por_grupo['LABEL'] = por_grupo['VALOR_M'].apply(fmt_valor)
    fig = px.bar(por_grupo, x='GRUPO', y='VALOR_B', text='LABEL',
                 color='VALOR_B', color_continuous_scale='Blues',
                 labels={'GRUPO': '', 'VALOR_B': 'Valor (€B)'},
                 category_orders={'GRUPO': por_grupo.sort_values('VALOR_M', ascending=False)['GRUPO'].tolist()})
    fig.update_traces(textposition='outside')
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

    # Cards: jogador mais valioso, menos valioso e valor médio
    _jmais  = dados.loc[dados['VALOR_M'].idxmax()]
    _jmenos_df = dados[dados['VALOR_M'] > 0]
    _jmenos = _jmenos_df.loc[_jmenos_df['VALOR_M'].idxmin()]
    _vmedio = dados[dados['VALOR_M'] > 0]['VALOR_M'].mean()

    vc1, vc2, vc3 = st.columns(3)
    vc1.metric("Jogador mais valioso",  fmt_valor(_jmais['VALOR_M']),  f"{_jmais['PLAYER NAME']}",  delta_color="off")
    vc2.metric("Jogador menos valioso", fmt_valor(_jmenos['VALOR_M']), f"{_jmenos['PLAYER NAME']}", delta_color="off")
    vc3.metric("Valor médio por jogador", fmt_valor(_vmedio))

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
    por_selecao['LABEL'] = por_selecao['VALOR_M'].apply(fmt_valor)
    fig2 = px.bar(por_selecao, x='PAIS', y='VALOR_B', color='GRUPO', text='LABEL',
                  labels={'VALOR_B': 'Valor total (€B)', 'PAIS': ''},
                  category_orders={'PAIS': por_selecao.sort_values('VALOR_M', ascending=False)['PAIS'].tolist()})
    fig2.update_traces(textposition='outside')
    fig2.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                       font_color='white', height=430, margin=dict(t=20))
    fig2.update_yaxes(gridcolor='#30363d')
    st.plotly_chart(fig2, use_container_width=True)

    # Caption dinâmica: descobre quem é o vice-líder real
    _vice = por_selecao.iloc[1] if len(por_selecao) > 1 else None
    _lider = por_selecao.iloc[0] if len(por_selecao) > 0 else None
    if _lider is not None and _vice is not None:
        st.caption(f"💡 {_lider['PAIS']} lidera com {fmt_valor(_lider['VALOR_M'])} — {_lider['VALOR_M']/_vice['VALOR_M']:.1f}x mais que {_vice['PAIS']} ({fmt_valor(_vice['VALOR_M'])}), vice-líder.")


# ----------------------------------------
# Página: Idades
# ----------------------------------------
elif pagina == "🎂 Idades":
    st.title("🎂 Análise de idades")
    st.divider()

    c1, c2, c3 = st.columns(3)
    c1.metric("Mais velho", f"{dados['AGE'].max()} anos", dados[dados['AGE'] == dados['AGE'].max()]['PLAYER NAME'].values[0], delta_color="off")
    c2.metric("Mais novo",  f"{dados['AGE'].min()} anos", dados[dados['AGE'] == dados['AGE'].min()]['PLAYER NAME'].values[0], delta_color="off")
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
        d = media_idade.nlargest(15, 'MEDIA').sort_values('MEDIA', ascending=False)
        fig = px.bar(d, x='PAIS', y='MEDIA', color='GRUPO', text='MEDIA',
                     labels={'MEDIA': 'Média de idade', 'PAIS': ''},
                     category_orders={'PAIS': d['PAIS'].tolist()})
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                          font_color='white', height=400)
        fig.update_yaxes(gridcolor='#30363d', range=[24, 32])
        st.plotly_chart(fig, use_container_width=True)
    with aba2:
        d = media_idade.nsmallest(15, 'MEDIA').sort_values('MEDIA', ascending=True)
        fig = px.bar(d, x='PAIS', y='MEDIA', color='GRUPO', text='MEDIA',
                     labels={'MEDIA': 'Média de idade', 'PAIS': ''},
                     category_orders={'PAIS': d['PAIS'].tolist()})
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
        ligas_todas = dados['Liga'].value_counts().reset_index()
        ligas_todas.columns = ['Liga', 'Jogadores']

        _liga_mais  = ligas_todas.iloc[0]
        _liga_menos = ligas_todas.iloc[-1]
        _liga_media = ligas_todas['Jogadores'].mean()

        lc1, lc2, lc3 = st.columns(3)
        lc1.metric("Liga com mais convocados",  f"{_liga_mais['Jogadores']} jogadores",  f"{_liga_mais['Liga']}",  delta_color="off")
        lc2.metric("Liga com menos convocados", f"{_liga_menos['Jogadores']} jogador(es)", f"{_liga_menos['Liga']}", delta_color="off")
        lc3.metric("Média por liga", f"{_liga_media:.1f} jogadores")

        st.subheader("Ligas com mais convocados")
        ligas = ligas_todas.head(top_n).sort_values('Jogadores', ascending=False)

        fig = px.bar(ligas, x='Jogadores', y='Liga', orientation='h', text='Jogadores',
                     color='Jogadores', color_continuous_scale='Blues',
                     labels={'Liga': ''},
                     category_orders={'Liga': ligas.sort_values('Jogadores')['Liga'].tolist()})
        fig.update_traces(textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22', font_color='white',
                          height=max(400, top_n * 30), yaxis={'categoryorder': 'total ascending'},
                          coloraxis_showscale=False, margin=dict(r=40))
        fig.update_xaxes(gridcolor='#30363d')
        fig.update_yaxes(gridcolor='#30363d')
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"💡 {_liga_mais['Liga']} lidera com {_liga_mais['Jogadores']} convocados.")

    with aba2:
        clube_limpo = dados['CLUB'].str.extract(r'^(.*?)\s*\(')[0].fillna(dados['CLUB'])
        clubes_todos = clube_limpo.value_counts().reset_index()
        clubes_todos.columns = ['Clube', 'Jogadores']

        _clube_mais  = clubes_todos.iloc[0]
        _clube_menos = clubes_todos.iloc[-1]
        _clube_media = clubes_todos['Jogadores'].mean()

        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Clube com mais convocados",  f"{_clube_mais['Jogadores']} jogadores",  f"{_clube_mais['Clube']}",  delta_color="off")
        cc2.metric("Clube com menos convocados", f"{_clube_menos['Jogadores']} jogador(es)", f"{_clube_menos['Clube']}", delta_color="off")
        cc3.metric("Média por clube", f"{_clube_media:.1f} jogadores")

        st.subheader("Clubes com mais convocados")
        clubes = clubes_todos.head(top_n).sort_values('Jogadores', ascending=False)

        fig = px.bar(clubes, x='Jogadores', y='Clube', orientation='h', text='Jogadores',
                     color='Jogadores', color_continuous_scale='Greens',
                     labels={'Clube': ''},
                     category_orders={'Clube': clubes.sort_values('Jogadores')['Clube'].tolist()})
        fig.update_traces(textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22', font_color='white',
                          height=max(400, top_n * 30), yaxis={'categoryorder': 'total ascending'},
                          coloraxis_showscale=False, margin=dict(r=40))
        fig.update_xaxes(gridcolor='#30363d')
        fig.update_yaxes(gridcolor='#30363d')
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"💡 {_clube_mais['Clube']} lidera com {_clube_mais['Jogadores']} convocados.")

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
        por_grupo['LABEL'] = por_grupo['VALOR_M'].apply(fmt_valor)
        fig = px.bar(por_grupo, x='GRUPO', y='VALOR_B', text='LABEL',
                     color='VALOR_B', color_continuous_scale='Blues',
                     labels={'GRUPO': '', 'VALOR_B': 'Valor (€B)'},
                     category_orders={'GRUPO': por_grupo.sort_values('VALOR_M', ascending=False)['GRUPO'].tolist()})
        fig.update_traces(textposition='outside')
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                          font_color='white', coloraxis_showscale=False, height=380)
        fig.update_yaxes(gridcolor='#30363d')
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Idade média por grupo")
        por_grupo_idade = df.groupby('GRUPO')['AGE'].mean().reset_index().sort_values('AGE', ascending=False)
        fig2 = px.bar(por_grupo_idade, x='GRUPO', y='AGE', text='AGE',
                      color='AGE', color_continuous_scale='Oranges',
                      labels={'GRUPO': '', 'AGE': 'Idade média'},
                      category_orders={'GRUPO': por_grupo_idade.sort_values('AGE', ascending=False)['GRUPO'].tolist()})
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
