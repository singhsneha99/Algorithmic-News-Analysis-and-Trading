import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import firebase_admin
from firebase_admin import credentials, db
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from textblob import TextBlob
import spacy

# Initialize Firebase Admin SDK
cred = credentials.Certificate(
    "algo-news-trading-firebase-adminsdk-6qtnt-c4d3efdff7.json")
firebase_admin.initialize_app(
    cred, {'databaseURL': 'https://algo-news-trading-default-rtdb.firebaseio.com/'})

# Load English language model for spaCy
nlp = spacy.load("en_core_web_sm")

# Download NLTK resources
nltk.download("punkt")
nltk.download("stopwords")


def preprocess_text(text):
    # Tokenization
    tokens = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.lower() not in stop_words]

    # Stemming
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(word) for word in tokens]

    return tokens


def perform_sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score


def perform_ner(text):
    entities = []
    doc = nlp(text)
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))
    return entities


def scrape_yahoo_finance():
    # URL for Yahoo Finance news
    url = 'https://finance.yahoo.com/'

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all news articles on the page
        articles = soup.find_all('h3', class_='Mb(5px)')

        # Create a list to store the scraped data
        news_list = []

        # Limit the number of articles to 50
        count = 0

        # Iterate over each article
        for article in articles:
            # Check if we have reached the limit of 50 articles
            if count == 50:
                break

            # Extract article title and URL
            title = article.text
            relative_url = article.a['href']
            # Ensure correct URL format
            article_url = urljoin(url, relative_url)

            # Perform additional processing
            # For demonstration, let's just preprocess the text
            # You can extend this with more NLP tasks

            # You can fetch article text from the URL and preprocess it
            # Here, we're just using the title for demonstration
            preprocessed_text = preprocess_text(title)

            # Append the scraped data to the list
            news_list.append({'title': title, 'url': article_url,
                             'preprocessed_text': preprocessed_text})

            # Increment the count
            count += 1

        return news_list
    else:
        # Return an empty list if the request fails
        return []


def save_to_firebase(data):
    # Get a reference to the Firebase database
    ref = db.reference('yahoo_finance_news')

    # Push the data to the database
    ref.set(data)


# Example usage
if __name__ == "__main__":
    scraped_data = scrape_yahoo_finance()
    save_to_firebase(scraped_data)
    print("Data saved to Firebase successfully.")
