# <img src="docs/logo.png" alt="Skillo" width="300" />

**AI-powered CV and job posting matching using multi-agent analysis**

Skillo is an intelligent application that uses artificial intelligence to match CVs with job postings through a sophisticated multi-agent system. The application analyzes location compatibility, skills match, experience levels, work preferences, and semantic similarity to provide comprehensive matching scores.

![Python](https://img.shields.io/badge/python-v3.11%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.48.0%2B-red.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)
![Poetry](https://img.shields.io/badge/poetry-dependency%20management-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

### Core Functionality
- **📄 Document Upload**: Upload PDF CVs and job postings through intuitive interface
- **🤖 Multi-Agent Analysis**: 6 specialized AI agents analyze different aspects of matching
- **📊 Comprehensive Scoring**: Weighted scoring system with detailed explanations
- **🔍 Bidirectional Matching**: Find jobs for CVs or candidates for jobs
- **📈 Match Insights**: Detailed breakdown of strengths and weaknesses

### AI Agent System
The application uses 6 specialized agents coordinated by a supervisor:

1. **🌍 Location Agent** - Geographic matching and remote work analysis
2. **💪 Skills Agent** - Technical and soft skills comparison  
3. **📈 Experience Agent** - Years and industry experience relevance
4. **❤️ Preferences Agent** - Work style and culture fit
5. **🧠 Semantic Agent** - Deep semantic similarity using embeddings
6. **👔 Supervisor Agent** - Coordinates agents and produces final scores

**🤖 Profile Classification**: Uses a custom-trained machine learning model to automatically determine candidate profiles (e.g., "Software Developer", "Data Scientist", "Marketing Manager") from CV content, enabling more accurate job-to-candidate matching.

### Management Features
- **📚 Document Management**: View, organize, and manage uploaded documents
- **📊 Database Statistics**: Track document counts and database health
- **🗑️ Database Reset**: Clean database with confirmation workflow
- **📥 Export Data**: Export documents in CSV or JSON format
- **💾 Vector Storage**: Persistent ChromaDB storage for embeddings

## 🛠 Technology Stack

- **Frontend**: Streamlit (Web UI)
- **AI/ML**: OpenAI GPT & Embeddings, LangChain
- **Vector Database**: ChromaDB
- **Document Processing**: pypdf
- **Data Processing**: pandas, numpy
- **Deployment**: Docker, docker-compose, Poetry

## 📋 Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker & Docker Compose (for containerized deployment)
- OpenAI API key

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd skillo

# 2. Setup environment
cp .env.example .env
# Edit .env file and add your OPENAI_API_KEY

# 3. Start the application
docker-compose up --build

# 4. Access the application
# Open http://localhost:8501 in your browser
```

### Option 2: Local Development

```bash
# 1. Clone the repository
git clone <repository-url>
cd skillo

# 2. Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# 3. Install dependencies
poetry install

# 4. Setup environment
cp .env.example .env
# Edit .env file and add your OPENAI_API_KEY

# 5. Run the application
poetry run streamlit run app.py

# 6. Access the application
# Open http://localhost:8501 in your browser
```

## 🎮 Usage Guide

### 1. Upload Documents
- Navigate to **"Upload Documents"** page
- Upload PDF files for CVs and job postings
- Wait for processing and vector embedding generation

### 2. Browse Documents
- **"CV List"** page: Browse all uploaded CVs with candidate profiles, skills preview, and PDF viewer
- **"Job List"** page: Browse all uploaded job postings with company information and position details
- Preview documents directly in the browser
- View extracted candidate/company information

### 3. Perform Matching Analysis
- Go to **"Match Analysis"** page
- Choose analysis type:
  - **Find jobs for a CV**: Select a CV to find matching job postings
  - **Find candidates for a job**: Select a job to find matching CVs
- View detailed match results with scores and explanations

### 4. Manage Documents
- Visit **"Document Management"** page
- View all uploaded documents
- Export data in CSV or JSON format
- Reset database when needed

### 5. Monitor Database
- Check **"Database Statistics"** page
- View document counts and distribution
- Monitor database health

## 📊 Match Analysis Details

### Scoring System
Each match receives a final score (0-100%) based on weighted contributions from all agents:

- **Location** (15%): Geographic compatibility and remote work options
- **Skills** (30%): Technical and soft skills alignment
- **Experience** (25%): Years of experience and seniority level match
- **Preferences** (10%): Work style and cultural fit
- **Semantic** (20%): Deep semantic similarity via embeddings

### Match Results Include:
- **Overall Score**: Weighted final score with performance category
- **Agent Breakdown**: Individual scores from each specialized agent
- **Detailed Insights**: Explanations for each matching dimension
- **Strengths/Weaknesses**: Identification of best and worst matching areas

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

### Customization

You can adjust the agent weights to prioritize different aspects of matching based on your requirements.

## 🐳 Docker Deployment

```bash
# Start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Development

### Development Tools
```bash
# Install with dev dependencies
poetry install

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Development mode with auto-reload
make dev
```

### Project Structure
```
skillo/
├── resume-classification.ipynb # Jupyter notebook for training profile classification model
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # Container build instructions
├── pyproject.toml              # Poetry dependency management
├── docs/                       # Documentation assets
│   ├── logo.png
│   └── screenshot.png
├── data/                       # Document storage
│   ├── cvs/                    # CV PDF files
│   └── jobs/                   # Job posting PDF files
├── chroma_db/                  # ChromaDB vector database storage
└── skillo/                     # Main application package
    ├── main.py                 # Streamlit application entry point
    ├── agents/                 # LangChain-based AI agents (6 specialized + supervisor)
    ├── core/                   # Business logic
    │   ├── matcher.py          # Main matching engine
    │   ├── processing.py       # Document processing and PDF extraction
    │   └── vectorstore.py      # ChromaDB vector database operations
    ├── schemas/                # Pydantic data models and response schemas
    ├── ui/                     # Streamlit user interface
    │   ├── components/         # Reusable UI components
    │   └── pages/              # Page-specific logic
    ├── exceptions/             # Custom exception hierarchy
    ├── utils/                  # Utilities and helpers
    ├── tools/                  # External tools and classifiers
    ├── models/                 # Pre-trained ML models (KNN classifier, etc.)
    ├── prompts/                # AI prompt templates in YAML format
    ├── config/                 # Configuration management
    └── enums/                  # Enumeration definitions
```

## 📸 Screenshots

![Skillo Application Interface](docs/screenshot.png)

*The Skillo application interface showing the CV matching results with detailed scoring breakdown from all AI agents including location, skills, experience, preferences, and semantic analysis.*

