from flask import Flask, render_template
from data_collection import scrape_yahoo_finance, save_to_firebase
from analysis import analyze_articles, save_analysis_results

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/analysis')
def analysis():
    # Scrape news articles from Yahoo Finance
    yahoo_news = scrape_yahoo_finance()

    # Save scraped data into the database
    save_to_firebase(yahoo_news)

    # Analyze the articles
    analyzed_articles = analyze_articles(yahoo_news)

    # Save analysis results into the database
    save_analysis_results(analyzed_articles)

    # Pass the analyzed data to the analysis page template
    return render_template('analysis.html', yahoo_news=yahoo_news, analyzed_articles=analyzed_articles)


@app.route("/trading")
def trading():
    return render_template("trading.html")


if __name__ == "__main__":
    app.run(debug=True)
