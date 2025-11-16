# ReliableParts AI Sales Dashboard

An AI-powered sales dashboard for appliance parts featuring semantic search, GPT-powered chatbot, and real-time analytics.

## 🚀 Features

- **Semantic Search**: Find parts using natural language with OpenAI embeddings
- **AI Chatbot**: GPT-3.5 powered assistant for customer queries
- **Real-time Analytics**: Dashboard with inventory and sales metrics
- **149+ Products**: Comprehensive parts database
- **Smart Recommendations**: AI-powered upsell suggestions

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI**: Embeddings (text-embedding-3-small) + GPT-3.5-turbo
- **SQLite**: Lightweight database
- **Scikit-learn**: Similarity calculations

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **shadcn/ui**: UI components
- **Recharts**: Data visualization

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 20+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
uvicorn api.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000/api
npm run dev
```

## 🌐 Deployment

### Frontend → Vercel
1. Push repository to GitHub
2. Import project in [Vercel](https://vercel.com)
3. Set **Root Directory** to `frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL` (your backend URL)
5. Click Deploy

### Backend → Render
1. Create new [Web Service](https://render.com)
2. Connect GitHub repository
3. Set **Root Directory** to `backend`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port 10000`
6. Add environment variable: `OPENAI_API_KEY`
7. Click Deploy

## 🔧 Environment Variables

### Backend (.env)
```env
OPENAI_API_KEY=sk-...
DATABASE_PATH=database/products.db
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
# Production: https://your-backend.onrender.com/api
```

## 📊 Project Structure

```
reliableparts-project/
├── backend/               # FastAPI backend
│   ├── api/              # API routes
│   │   ├── main.py       # FastAPI app
│   │   └── routes/       # Endpoint modules
│   ├── database/         # SQLite database
│   ├── semantic_search.py
│   ├── gpt_query_processor.py
│   ├── gpt_response_generator.py
│   └── intelligent_search.py
│
└── frontend/             # Next.js frontend
    ├── app/              # Pages (App Router)
    ├── components/       # UI components
    ├── lib/              # Utilities & API client
    └── styles/           # Global styles
```

## 🎯 Key Features

### Semantic Search
Uses OpenAI embeddings to understand product queries in natural language. Finds relevant parts even when exact keywords don't match.

**Example:**
- Query: "water filter for Whirlpool fridge"
- Returns: Compatible filters ranked by relevance (similarity scores)

### AI Chatbot
GPT-3.5-turbo powered assistant that:
- Understands customer needs
- Recommends compatible parts
- Provides pricing and availability
- Suggests complementary products (upsells)

### Analytics Dashboard
Real-time insights including:
- Total products and inventory levels
- Category distribution
- Stock status metrics
- Price ranges and averages
- Top-selling categories

## 📖 API Documentation

Backend API docs available at: http://localhost:8000/docs

### Key Endpoints:
- `POST /api/search` - Semantic product search
- `POST /api/chat` - GPT chatbot
- `GET /api/products` - List products (paginated)
- `GET /api/analytics/overview` - Dashboard stats
- `GET /api/categories` - All categories
- `GET /api/brands` - All brands

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/reliableparts-project.git
cd reliableparts-project

# Start backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY to .env
uvicorn api.main:app --reload &

# Start frontend (in new terminal)
cd ../frontend
npm install
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL in .env.local
npm run dev
```

Open http://localhost:3000 in your browser.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

Built for ReliableParts.com sales optimization and customer service enhancement.

## 🙏 Acknowledgments

- **OpenAI** for GPT-3.5-turbo and embeddings API
- **Vercel** for Next.js framework and hosting
- **shadcn/ui** for beautiful UI components
- **Render** for backend hosting

## 📸 Screenshots

### Dashboard
![Dashboard Overview](docs/dashboard.png)

### Semantic Search
![Search Interface](docs/search.png)

### AI Chatbot
![Chat Interface](docs/chat.png)

## 🔗 Links

- **Live Demo**: [Coming Soon]
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## ⚡ Performance

- **Search Response**: < 2 seconds (with GPT parsing)
- **Chat Response**: < 3 seconds
- **Database Queries**: < 100ms
- **Analytics**: < 200ms

## 🛡️ Security

- API keys stored in environment variables
- No sensitive data committed to repository
- CORS configured for production
- Input validation with Pydantic

## 📝 Development Notes

### Backend
- FastAPI for high-performance REST API
- OpenAI API for embeddings and chat
- SQLite for simplicity (can migrate to PostgreSQL)
- Comprehensive error handling and logging

### Frontend
- Next.js App Router for modern React
- TypeScript for type safety
- Tailwind CSS for responsive design
- Real-time updates with React hooks

---

**Built with ❤️ for improving sales efficiency**
