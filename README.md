# CareerShield AI

**ML-powered career prediction platform** that predicts how artificial intelligence will impact 500+ careers. Built with FastAPI, React, scikit-learn, and Claude AI.

## Features

- **AI Risk Scoring** - Automation risk predictions (0-100%) for 197+ careers using ensemble ML models
- **4 ML Models** - Linear Regression, Random Forest, Gradient Boosting, Neural Network with weighted ensemble
- **Career Dashboard** - Interactive data visualization with filters, charts, and industry breakdowns
- **FabriceAI Chatbot** - Claude-powered career advisor that gives personalized, data-backed advice
- **Career DNA** - Skills/interest quiz that matches you to AI-resilient careers
- **Career Comparison** - Compare up to 4 careers side-by-side
- **Salary Projections** - 5-year and 10-year salary forecasts factoring in AI impact

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy, Alembic, Python 3.11+ |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| ML | scikit-learn, pandas, numpy, joblib |
| AI Agent | Anthropic Claude API |
| Charts | Recharts |
| Database | SQLite (dev) / PostgreSQL (prod) |

## Quick Start

### 1. Clone and Setup Backend

```bash
cd careershield-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r backend/requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Seed Database & Train Models

```bash
python scripts/seed_database.py    # Seeds 197 careers with skills & predictions
python scripts/train_models.py     # Trains 4 ML models, generates ensemble predictions
```

### 3. Start Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173** to see the app!

## ML Model Performance

| Model | Risk Score R² | Stability R² |
|-------|--------------|-------------|
| Gradient Boosting | 0.947 | 0.937 |
| Random Forest | 0.943 | 0.949 |
| Neural Network | 0.912 | 0.574 |
| Linear Regression | 0.870 | 0.867 |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/careers` | List careers with filters & pagination |
| `GET /api/careers/{id}` | Career detail with skills & predictions |
| `GET /api/predictions/stats` | Platform statistics |
| `GET /api/predictions/top-risk` | Highest risk careers |
| `GET /api/predictions/top-safe` | Safest careers |
| `GET /api/predictions/industry-breakdown` | Risk by industry |
| `POST /api/compare` | Compare careers side-by-side |
| `POST /api/recommendations/career-dna` | Career DNA matching |
| `POST /api/chat` | FabriceAI streaming chat |

## Data Sources

- **O*NET** - Occupational skills, tasks, abilities, and knowledge requirements
- **Bureau of Labor Statistics** - Salary data, employment counts, growth projections
- **Custom AI Risk Scoring** - Heuristic-based task automation potential analysis

## License

MIT
