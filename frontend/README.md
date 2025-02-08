# Sick Finance News

A modern financial news aggregator built with FastHTML that displays stock-related news articles with filtering capabilities.

## Features

- Clean, modern UI with responsive design
- Stock and source filtering
- Infinite scroll news feed
- Article cards with images and summaries
- PostgreSQL backend integration

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your database:
   - Copy `.env.example` to `.env`
   - Update the database credentials in `.env`
   - Ensure your PostgreSQL database is running and accessible

4. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Database Schema

The application uses the following PostgreSQL schema:

- `source_article`: Original source articles
  - URL
  - Timestamp
  - Publish timestamp
  - Content

- `generated_article`: Processed articles
  - Source (references source_article)
  - Content
  - Image
  - Timestamp
  - Metadata

- `content`: Article content
  - Title
  - Lead
  - Text

- `metadata_idx`: Article metadata
  - Source (references generated_article)
  - Stocks
  - Country
  - Persons
  - Language

## Contributing

Feel free to submit issues and enhancement requests! 