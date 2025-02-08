from fasthtml.common import *
from datetime import datetime
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastHTML app with Pico CSS and Flexbox Grid for styling
gridlink = Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css", type="text/css")
app = FastHTML(hdrs=(picolink, gridlink))

# Database connection
def get_db_connection():
    return sqlite3.connect('finance_news.db')

@app.get("/")
def home():
    return (
        Title("Your Finance News by Sick Bros"),
        Main(
            # Filters section
            Div(
                Div(Button("Stock Filter", cls="outline"), cls="col-xs-6"),
                Div(Button("Source Filter", cls="outline"), cls="col-xs-6"),
                cls="row"
            ),
            # Articles container with initial load
            Div(
                # Loading indicator
                Div(
                    Div(cls="spinner"),
                    P("Loading more articles..."),
                    cls="loading-indicator",
                    _="on htmx:beforeRequest show me on htmx:afterRequest hide me"
                ),
                # Articles will be loaded here
                Div(id="articles-container", hx_get="/load-more?page=1", hx_trigger="revealed"),
                cls="container"
            ),
            cls="container"
        )
    )

@app.get("/load-more")
def load_more():
    try:
        page = int(request.query_params.get('page', 1))
        per_page = 10
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        # Set row_factory to get dictionary-like results
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Updated SQL query for SQLite
        cur.execute("""
            SELECT ga.*, c.title, c.lead, c.text, m.stocks, m.country, m.persons, m.language
            FROM generated_article ga
            JOIN content c ON ga.content = c.id
            LEFT JOIN metadata_idx m ON ga.id = m.source
            ORDER BY ga.timestamp DESC
            LIMIT ? OFFSET ?
        """, (per_page + 1, offset))  # Use ? instead of %s for SQLite
        
        articles = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Check if there are more articles
        has_more = len(articles) > per_page
        articles = articles[:per_page]  # Remove the extra article
        
        articles_div = Div(
            *[article_card(article) for article in articles],
            cls="row"
        )
        
        # If there are more articles, add a trigger for the next page
        if has_more:
            next_page = Div(
                id="articles-container",
                hx_get=f"/load-more?page={page + 1}",
                hx_trigger="revealed",
                cls="next-page-trigger"
            )
            return articles_div, next_page
        
        return articles_div
        
    except Exception as e:
        return Div(f"Error loading articles: {str(e)}", cls="error")

def article_card(article):
    return Div(
        Div(
            # Article image
            Div(Img(src=article['image'], alt=article['title'], style="width:100%;"), cls="article-image"),
            # Article content
            H3(article['title']),
            P(article['lead'], cls="article-lead"),
            P(", ".join(article['stocks']) if article['stocks'] else "", cls="article-stocks"),
            cls="card"
        ),
        cls="col-xs-12 col-sm-6 col-md-4 article-card"
    )

# Add some custom CSS
custom_css = Style("""
    .article-card { margin-bottom: 2rem; }
    .card { padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .article-image { margin-bottom: 1rem; }
    .article-lead { font-size: 0.9rem; color: #666; }
    .article-stocks { font-size: 0.8rem; color: #007bff; }
    
    /* Loading indicator styles */
    .loading-indicator {
        text-align: center;
        padding: 2rem;
        display: none;
    }
    .loading-indicator.show {
        display: block;
    }
    .spinner {
        width: 40px;
        height: 40px;
        margin: 0 auto 1rem;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
""")
app.hdrs += (custom_css,)

if __name__ == "__main__":
    serve() 