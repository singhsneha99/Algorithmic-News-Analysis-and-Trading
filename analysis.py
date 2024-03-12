import re
import firebase_admin
from firebase_admin import credentials, db
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from textblob import TextBlob
import spacy
import requests
from bs4 import BeautifulSoup

# Check if Firebase app is already initialized
if not firebase_admin._apps:
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

# Load English language model for spaCy
nlp = spacy.load("en_core_web_sm")


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

# Perform topic modeling (LDA or NMF)
# Implement LDA or NMF as needed


def sanitize_title(title):
    # Replace illegal characters with underscores
    sanitized_title = re.sub(r'[^\w\s]', '_', title)
    return sanitized_title


def analyze_articles(articles):
    analyzed_articles = []
    for article in articles:
        # Extract relevant information
        title = article['title']
        url = article['url']

        # Skip articles with Yahoo Plus subscription URLs
        if 'ncid=yahooproperties_plusresear%' in url:
            print(
                f"Skipping article '{title}' with Yahoo Plus subscription URL: {url}")
            continue

        # Extract article text from URL
        article_text = extract_article_text(url)

        # Perform analysis
        preprocessed_text = preprocess_text(article_text)
        sentiment_score = perform_sentiment_analysis(article_text)
        company_mentions = perform_ner(article_text)

        # Add analysis results to the article
        article['preprocessed_text'] = preprocessed_text
        article['sentiment_score'] = sentiment_score
        article['company_mentions'] = company_mentions

        # Append analyzed article to the list
        analyzed_articles.append(article)

    return analyzed_articles


def save_analysis_results(articles):
    ref = db.reference('analyzed_articles')
    for article in articles:
        title = article['title']
        sanitized_title = sanitize_title(title)  # Sanitize the title
        ref.child(sanitized_title).set(article)

# Fetch articles from Firebase


def fetch_articles():
    ref = db.reference('yahoo_finance_news')
    articles = ref.get()
    return articles


def extract_article_text(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes

        # Check if the response status code is 404 (Not Found)
        if response.status_code == 404:
            print(f"Article not found at URL: {url}")
            return ''  # Return empty string to indicate article not found

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the elements containing the article text
        article_content = soup.find('div', class_='caas-body')

        # Extract text from the article content
        if article_content:
            article_text = article_content.get_text(separator='\n')
        else:
            article_text = ''  # If article content not found, set text to empty string

        return article_text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article from {url}: {e}")
        return ''


def main():
    articles = fetch_articles()
    analyzed_articles = analyze_articles(articles)
    save_analysis_results(analyzed_articles)


if __name__ == "__main__":
    main()
