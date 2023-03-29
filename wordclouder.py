# Start with loading all necessary libraries
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
nltk.download('punkt')


def make_worcloud(data: pd.DataFrame, max_words=100) -> plt.figure:

    reviews_text = (' ').join(data.iloc[:, 3].to_list())
    stop_words = set(stopwords.words('italian'))
    stop_words |= {"tadino", "gae aulenti", "concordia", "pandenus", "euro", "locale", "ristorante", "molto", "due", "tre", "stato", "stata", "stati", "sempre", "senza", "po"}
    word_tokens = word_tokenize(reviews_text)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
    filtered_sentence = (' ').join(filtered_sentence)
    wordcloud = WordCloud(
        max_words=max_words,
        min_font_size=10,
        background_color="white").generate(filtered_sentence)
    return wordcloud
