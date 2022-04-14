import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dateparser import parse
from wordclouder import make_worcloud
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html

# ==============================================================
# Set overall visualization params
# ==============================================================
sns.set_theme(style="white", palette="pastel")
sns.set_context("notebook")
st.set_page_config(layout='wide')
# plt.style.use("dark_background")

# ==============================================================
# Retrieve and cache data
# ==============================================================
@st.cache
def get_data(path_to_venue_data):
    df = pd.read_csv(
        path_to_venue_data,
        parse_dates=['Data'],
        date_parser=parse)
    return df

df = get_data("data/all.csv")

# ==============================================================
# Constants
# ==============================================================
VENUES = {
    "Tadino": "tadino",  
    "Gae Aulenti": "gaeaulenti",
    "Concordia": "concordia",
    "La Foppa": "lafoppa",
    "Melzi D'Eril": "melzideril",
    "Mercato": "mercato"
}

# ==============================================================
# Sidebar
# ==============================================================
st.sidebar.header("PARAMETRI")


st.title("REVIEWS ANALYTICS")

with st.sidebar:
    venues = st.multiselect("Filtra per locale:",
                            options=VENUES.keys(), default=VENUES.keys())
    if not venues:
        st.error("Devi scegliere almeno un locale")
    choice = st.radio("Visualizza per:", options=[
                      "Anno", "Mese", "Intervallo di date"])
    year = st.slider(
            "ANNO",
            df.Data.dt.year.min(),
            df.Data.dt.year.max(),
            (df.Data.dt.year.min(), df.Data.dt.year.max())
        )

    
    
venues_selection = [VENUES[venue] for venue in venues]
data_mask = df.Data.dt.year.between(year[0], year[1])
venues_mask = df.Locale.isin(venues_selection)
mask = data_mask & venues_mask

selection = df[mask]

def starsPlot(year):
    fig = plt.figure()
    sns.countplot(
        x="Rating", 
        data=df[mask]
    )
    plt.title(
        f"Distribuzione stelle {year[0]}-{year[1]}".upper())
    sns.despine()
    st.pyplot(fig)

col1, col2  = st.columns((1, 1))
with col1:    
    fig = plt.figure()    
    st.subheader("Ratings")
    st.metric("Mediana", int(df[df.Data.dt.year.between(year[0], year[1])].Rating.median()/10))
    starsPlot(year)
with col2:
    with st.expander("Mostra wordloud"):
        st.subheader("Wordcloud")
        word_cloud = make_worcloud(selection)
        fig = plt.figure()
        plt.imshow(word_cloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()
        st.pyplot(fig)
