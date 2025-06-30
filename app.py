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
         'MEDIAS_LC', 'MEDIAS_CH', 'MEDIAS_CN', 'MEDIAS_MT', 'MEDIAS_REDACAO', 'MEDIAS_MEDIA_GERAL']].dropna()

# === Dicionário de disciplinas ===
disciplinas = {
    'Redação': 'MEDIAS_REDACAO',
    'Matemática': 'MEDIAS_MT', 
    'Linguagens e Códigos': 'MEDIAS_LC',
    'Ciências da Natureza': 'MEDIAS_CN',
    'Ciências Humanas': 'MEDIAS_CH',
    'Média Geral': 'MEDIAS_MEDIA_GERAL'
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
    if nota <= 500:
        # Gradiente de vermelho escuro até vermelho claro
        cmap = LinearSegmentedColormap.from_list('red_gradient', ['darkred', 'lightcoral'], N=256)
        norm = colors.Normalize(vmin=vmin, vmax=500)
    else:
        # Gradiente de verde claro até verde escuro
        cmap = LinearSegmentedColormap.from_list('green_gradient', ['lightgreen', 'darkgreen'], N=256)
        norm = colors.Normalize(vmin=500, vmax=vmax)

    return colors.to_hex(cmap(norm(nota)))

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

def formatar_valor(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# === Adicionar marcadores ===
for _, row in df_filtrado.iterrows():
    nota = row[coluna]
    cor = nota_para_cor(nota)
    popup = f"""
    <b>{row['ESCOLA']}</b><br>
    ----------------------------------------------------
    <br>
    Média da escola em cada área de conhecimento:<br>
    - Redação: {formatar_valor(row['MEDIAS_REDACAO'])}<br>
    - Matemática: {formatar_valor(row['MEDIAS_MT'])}<br>
    - Linguagens e Códigos: {formatar_valor(row['MEDIAS_LC'])}<br>
    - Ciências da Natureza: {formatar_valor(row['MEDIAS_CN'])}<br>
    - Ciências Humanas: {formatar_valor(row['MEDIAS_CH'])}<br>
    ---------------------------------------------------- 
    <b>Média Geral: {formatar_valor(row['MEDIAS_MEDIA_GERAL'])} </b> <br>
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