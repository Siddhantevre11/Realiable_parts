# ReliableParts Backend

FastAPI backend with OpenAI integration for semantic search and intelligent chatbot.

## Features

- **Semantic Search**: OpenAI embeddings for natural language product search
- **GPT Chatbot**: Conversational AI for customer assistance
- **RESTful API**: Clean, well-documented endpoints
- **SQLite Database**: 149+ products with full details
- **Analytics**: Real-time business intelligence

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Verify Database

Make sure `database/products.db` exists with product data and embeddings.

## Run

### Development
```bash
uvicorn api.main:app --reload --port 8000
```

### Production
```bash
uvicorn api.main:app --host 0.0.0.0 --port 10000 --workers 4
```

## API Documentation

Visit http://localhost:8000/docs for interactive Swagger documentation.

## Endpoints

### Search
- `POST /api/search` - Semantic product search
  - Body: `{"query": "water filter", "top_k": 5}`
  - Returns: Products ranked by relevance

### Chat
- `POST /api/chat` - GPT-powered chatbot
  - Body: `{"message": "I need a water filter", "include_products": true}`
  - Returns: Conversational response with product recommendations

### Products
- `GET /api/products` - List products (paginated)
- `GET /api/products/{sku}` - Get product by SKU
- `GET /api/products/category/{category}` - Filter by category
- `GET /api/products/brand/{brand}` - Filter by brand

### Analytics
- `GET /api/analytics/overview` - Dashboard statistics
- `GET /api/analytics/top-products` - Top products by various metrics
- `GET /api/categories` - All categories
- `GET /api/brands` - All brands

## Project Structure

```
backend/
├── api/
│   ├── main.py              # FastAPI app
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── routes/
│       ├── search.py        # Search endpoints
│       ├── chat.py          # Chat endpoints
│       ├── products.py      # Product CRUD
│       └── analytics.py     # Analytics endpoints
│
├── database/
│   └── products.db          # SQLite database
│
├── semantic_search.py       # Semantic search logic
├── gpt_query_processor.py   # Query understanding
├── gpt_response_generator.py # Response generation
├── intelligent_search.py    # Main search system
├── db_queries.py            # Database helpers
├── config.py                # Configuration
│
├── .env                     # Environment variables (not in git)
├── .env.example             # Example environment file
├── .gitignore
├── requirements.txt
└── README.md
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `DATABASE_PATH` | Path to SQLite database | `database/products.db` |
| `OPENAI_MODEL` | GPT model to use | `gpt-3.5-turbo` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |

## Deployment

### Render

1. Create new Web Service on [Render](https://render.com)
2. Connect GitHub repository
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port 10000`
4. Add environment variable: `OPENAI_API_KEY`
5. Deploy

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t reliableparts-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... reliableparts-backend
```

## Testing

```bash
# Run all tests
python test_api.py

# Test specific endpoint
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "water filter", "top_k": 3}'
```

## Performance

- **Search**: < 2 seconds (includes GPT parsing)
- **Chat**: < 3 seconds (includes GPT generation)
- **Products**: < 100ms
- **Analytics**: < 200ms

## Troubleshooting

### "OpenAI API not configured"
- Make sure `OPENAI_API_KEY` is set in `.env`
- Verify key starts with `sk-`

### "Database not found"
- Check `DATABASE_PATH` points to correct location
- Ensure `database/products.db` exists

### "No embeddings found"
- Embeddings must be generated before searching
- Contact administrator for database setup

## API Response Examples

### Search Response
```json
{
  "success": true,
  "query": "water filter",
  "results": [
    {
      "sku": "XWFE",
      "product_name": "GE XWFE Water Filter",
      "brand": "GE",
      "sale_price": 57.62,
      "similarity": 0.89
    }
  ],
  "total_results": 12,
  "response_time_ms": 234
}
```

### Chat Response
```json
{
  "success": true,
  "message": "I found 3 compatible water filters for you...",
  "products": [...],
  "response_time_ms": 567
}
```

## Support

- **Documentation**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **API Status**: http://localhost:8000/api/health

## License

MIT
