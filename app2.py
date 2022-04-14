from decimal import DivisionByZero
from turtle import width
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dateparser import parse
from wordclouder import make_worcloud
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
from datetime import datetime, timedelta
from PIL import Image
from nltk.corpus import stopwords

# ==============================================================
# Set overall visualization params
# ==============================================================
sns.set_theme(style="white", palette="viridis")
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
LOGO = Image.open(r'assets/pandenus.jpeg')

col1, col2 = st.columns((0.8, 0.2))
col1.title("ReviewGeek".upper())
col2.image(LOGO, width=130)
st.markdown("**ReviewGeek ti permette di analizzare le recensioni TripAdvisor dei tuoi locali.**")
# st.markdown(f"Versione alpha.0.1")
st.markdown("---")
# ==============================================================
# Sidebar
# ==============================================================
with st.sidebar:
    choose = option_menu("NAVIGAZIONE", ["Trend", "Dettaglio", "Wordcloud", "Recensioni"],
                         icons=['graph-up-arrow', 'zoom-in', 'chat-quote',
                                'heart-half'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#F0F2F6"},
        "nav-link-selected": {"background-color": "#FF4B4B"},
    }    
    )


placeholder = st.container()
if choose=="Trend":
    with st.sidebar:        
        # Select display period for trend metrics
        trends_choice = st.radio("Seleziona periodo trend: ", options=["Ultima settimana", "Ultimo mese", "Ultimo anno"])
        if trends_choice == "Ultimo anno":
            delta = 365
        elif trends_choice =="Ultimo mese":
            delta = 30
        else:
            delta = 7
        today = datetime.today()
        trend_start = today - timedelta(days=delta)
        trend_df = df[df.Data.between(trend_start, today)]
        start_trend_df = df[df.Data.between(trend_start - timedelta(days=delta), trend_start)]
    if trend_df.empty:
        st.error("Non ci sono abbastanza dati per questo intervallo. Selezionane un altro.")
        placeholder.empty()
    else:
        with placeholder:
            total_reviews = len(df)
            new_reviews = len(trend_df)
            delta_reviews = len(trend_df) - len(start_trend_df)        
            delta_no_reviews = new_reviews - len(trend_df)
            pos_prev = start_trend_df[start_trend_df["Etichetta"] == "pos"]
            pos_period = trend_df[trend_df["Etichetta"] == "pos"]
            neg_prev = start_trend_df[start_trend_df["Etichetta"] == "neg"]
            neg_period = trend_df[trend_df["Etichetta"] == "neg"]        
    
            col1, col2, col3 = st.columns(3)

            col1.metric("Totale recensioni", total_reviews)
            col2.metric("Nuove recensioni", new_reviews,
                        f"{new_reviews/delta_reviews * 100:.1f} %")

            no_pos_period = len(pos_period)
            no_neg_period = len(neg_period)
            no_pos_prev = len(pos_prev)
            no_neg_prev = len(neg_prev)


            try:
                delta_pos = no_pos_period/(no_pos_period - no_pos_prev)
            except ZeroDivisionError:
                delta_pos = 0
            try:
                delta_neg = no_neg_period/(no_neg_period - no_neg_prev)
            except ZeroDivisionError:
                delta_neg = 0
            col3.metric("Recensioni positive", no_pos_period,
                        f"{delta_pos * 100:.1f} %")
            col3.metric("Recensioni negative", no_neg_period,
                        f"{delta_neg * 100:.1f} %", delta_color="inverse")


if choose in ["Dettaglio", "Wordcloud", "Recensioni"]:
    with st.sidebar:
    # Select venues
        all_venues_options = list(VENUES.keys())
        all_venues_options.append("Tutti")
        venues_choice = st.multiselect("Seleziona locali:",
                                        all_venues_options, 
                                        VENUES.keys()
        )

        if "Tutti" in venues_choice:
            venues_selection = VENUES.values()
        else:
            venues_selection = [VENUES[venue] for venue in venues_choice]

        # Filter data by selected venues
        venues_mask = df.Locale.isin(venues_selection)
        venues_df = df[venues_mask]

        # Choose viz type by date
        date_choice = st.radio("Visualizza per:", options=[
                            "Anno", "Mese", "Intervallo di date"])
        if not date_choice:
            st.error("Devi scegliere almeno una modalità.")

        if date_choice == "Anno":
            year = st.slider(
                    "ANNO",
                    venues_df.Data.dt.year.min(),
                    venues_df.Data.dt.year.max(),
                    (venues_df.Data.dt.year.min(), venues_df.Data.dt.year.max())
                )
            start_date = start_date = pd.to_datetime(str(year[0]), format="%Y")
            end_date = pd.to_datetime(str(year[1]), format="%Y")

        elif date_choice == "Mese":
            year = st.slider(
                "Anni",
                venues_df.Data.dt.year.min(),
                venues_df.Data.dt.year.max(),
                (venues_df.Data.dt.year.min(), venues_df.Data.dt.year.max())
            )
            month = st.slider(
                "Mesi",
                venues_df.Data.dt.month.min(),
                venues_df.Data.dt.month.max(),
                (venues_df.Data.dt.month.min(), venues_df.Data.dt.month.max())
            )
            start_date = pd.to_datetime(str(month[0]) + str(year[0]), format="%m%Y")
            end_date = pd.to_datetime(str(month[1]) + str(year[1]), format="%m%Y")
            
        elif date_choice == "Intervallo di date":
            cols = st.columns(2)
            with cols[0]:
                start_date = st.date_input(
                    "Inizio", 
                    df.Data.min(),
                    )
            with cols[1]:
                end_date = st.date_input("Fine")
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

    data_mask = df.Data.between(start_date, end_date)
    mask = data_mask & venues_mask
    selection = df[mask]
    with placeholder:
        if choose=="Dettaglio":
            col1, col2 = st.columns((1, 1))
            with col1:
            # Plot overall rating distribution
                fig = plt.figure()
                sns.countplot(
                    x="Rating",
                    data=selection
                )
                plt.title(
                    f"Rating".upper())
                sns.despine()
                st.pyplot(fig)

                # Plot rating distribution over venues
            with col2:
                fig = plt.figure()
                sns.boxplot(
                    x="Locale",
                    y="Rating",
                    data=selection,
                )
                st.write(plt.get_figlabels()[0])
                plt.title(
                    f"Rating per locale".upper())
                sns.despine()
                st.pyplot(fig)
        if choose == "Wordcloud":
            with st.sidebar:
                no_words = st.slider("Numero parole massimo", min_value=10, max_value=100, step=10, value=30)
            col1, col2, col3 = st.columns((1, 1, 1))
            with col1:
                st.subheader("Tutte")
                word_cloud = make_worcloud(selection, no_words)
                fig = plt.figure()
                plt.imshow(word_cloud, interpolation="bilinear")
                plt.axis("off")
                st.pyplot(fig)
            with col2:
                st.subheader("Positive")
                word_cloud = make_worcloud(selection[selection["Etichetta"] == "pos"], no_words)
                fig = plt.figure()
                plt.imshow(word_cloud, interpolation="bilinear")
                plt.axis("off")
                st.pyplot(fig)
            with col3:
                st.subheader("Negative")
                word_cloud = make_worcloud(selection[selection["Etichetta"] == "neg"], no_words)
                fig = plt.figure()
                plt.imshow(word_cloud, interpolation="bilinear")
                plt.axis("off")
                st.pyplot(fig)
        if choose=="Recensioni":
            with st.sidebar:
                search_words = st.text_input("Ricerca", max_chars=30)
                search_words = search_words.lower()
                no_reviews_to_display = st.number_input(
                    "Numero recensioni", max_value=len(selection), 
                    value=5
                    )
            review = selection[selection["Testo"].str.contains(search_words)]            
            placeholder.table(review[["Data", "Titolo", "Testo"]].head(
                no_reviews_to_display).style.hide_index())
# ==============================================================
# Body
# ==============================================================





