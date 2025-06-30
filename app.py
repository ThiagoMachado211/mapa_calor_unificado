import streamlit as st
import pandas as pd
import folium
from folium import CircleMarker, Popup
from streamlit_folium import st_folium
from matplotlib import cm, colors
from matplotlib.colors import LinearSegmentedColormap

# === Carregar os dados ===
df = pd.read_excel("Escolas_Estaduais_Total.xlsx")
df = df[['UF', 'REGIONAL', 'ESCOLA', 'LATITUDE', 'LONGITUDE', 
         'MEDIAS_LC', 'MEDIAS_CH', 'MEDIAS_CN', 'MEDIAS_MT', 'MEDIAS_REDACAO']].dropna()

# === Dicionário de disciplinas ===
disciplinas = {
    'Redação': 'MEDIAS_REDACAO',
    'Matemática': 'MEDIAS_MT', 
    'Linguagens e Códigos': 'MEDIAS_LC',
    'Ciências da Natureza': 'MEDIAS_CN',
    'Ciências Humanas': 'MEDIAS_CH'
}

# === Interface Streamlit ===
st.set_page_config(layout="wide")
st.title("📍 Mapa Interativo das Escolas Estaduais")
st.markdown("Use os filtros abaixo para visualizar os dados de desempenho por escola:")

# === Filtro por estado (UF) ===
ufs = sorted(df['UF'].unique())
uf = st.selectbox("Selecione o Estado (UF):", ["Todos"] + ufs)

# === Filtro dinâmico de regionais baseado no estado ===
if uf == "Todos":
    regionais_disponiveis = sorted(df['REGIONAL'].unique())
else:
    regionais_disponiveis = sorted(df[df['UF'] == uf]['REGIONAL'].unique())

regional = st.selectbox("Selecione a Regional:", ["Todas"] + regionais_disponiveis)

# === Filtro de disciplina ===
disciplina = st.selectbox("Selecione a Disciplina:", list(disciplinas.keys()))
coluna = disciplinas[disciplina]

# === Aplicar filtros ao dataframe ===
df_filtrado = df.copy()

if uf != "Todos":
    df_filtrado = df_filtrado[df_filtrado['UF'] == uf]

if regional != "Todas":
    df_filtrado = df_filtrado[df_filtrado['REGIONAL'] == regional]

# === Função de cor da nota ===
def nota_para_cor(nota, vmin=0, vmax=1000):
    cdict = {
        'red':   [(0.0, 1.0, 1.0),  # vermelho (0)
                  (0.5, 1.0, 1.0),  # branco (meio)
                  (1.0, 0.0, 0.0)], # verde (1)
        'green': [(0.0, 0.0, 0.0),
                  (0.5, 1.0, 1.0),
                  (1.0, 1.0, 1.0)],
        'blue':  [(0.0, 0.0, 0.0),
                  (0.5, 1.0, 1.0),
                  (1.0, 0.0, 0.0)],
    }
         
    custom_cmap = LinearSegmentedColormap('RedWhiteGreen', cdict)
         
    # Normalização
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    return colors.to_hex(custom_cmap(norm(nota)))

# def nota_para_cor(nota, vmin=0, vmax=1000):
#    norm = colors.Normalize(vmin=vmin, vmax=vmax)
#    cmap = cm.get_cmap('Reds')
#    return colors.to_hex(cmap(norm(nota)))

# === Criar mapa ===
mapa = folium.Map(
    location=[df_filtrado['LATITUDE'].mean(), df_filtrado['LONGITUDE'].mean()],
    zoom_start=8,
    tiles="CartoDB positron"
)

# === Adicionar marcadores ===
for _, row in df_filtrado.iterrows():
    nota = row[coluna]
    cor = nota_para_cor(nota)
    popup = f"""
    <b>{row['ESCOLA']}</b><br>
    Redação: {row['MEDIAS_REDACAO']}<br>
    Matemática: {row['MEDIAS_MT']}<br>
    Linguagens e Códigos: {row['MEDIAS_LC']}<br>
    Ciências da Natureza: {row['MEDIAS_CN']}<br>
    Ciências Humanas: {row['MEDIAS_CH']}<br>
    """
    CircleMarker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        radius=5,
        color=cor,
        fill=True,
        fill_color=cor,
        fill_opacity=0.8,
        popup=Popup(popup, max_width=300)
    ).add_to(mapa)

# === Mostrar mapa no Streamlit ===
st_folium(mapa, width=1000, height=600, returned_objects=[])
