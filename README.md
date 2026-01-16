# Contact Scholar Pipeline

A modular, configurable pipeline to discover researchers in any field, enrich with contact information, generate personalized outreach messages, and send emails.

## Overview

This pipeline automates the process of:
1. **Keyword Expansion**: Expand initial keywords into comprehensive search terms using LLM
2. **Paper Discovery**: Query ArXiv API for relevant research papers
3. **Researcher Extraction**: Parse author information and infer researcher profiles
4. **Profile Enrichment**: Find LinkedIn/Twitter/GitHub profiles via web search
5. **Message Personalization**: Generate tailored outreach emails using researcher context
6. **Email Sending**: Send emails one at a time with manual control

## Quick Start

### Prerequisites
- Python 3.9+
- OpenRouter API key ([get one here](https://openrouter.ai/))
- uv package manager (`pip install uv`)

### Installation

1. Clone and setup environment:
```bash
git clone <repository-url>
cd contact-scholar
uv sync
```

2. Configure environment and create custom config:
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Create your custom config (this will be gitignored)
cp config/default.yaml config/custom.yaml
# Edit config/custom.yaml for your research domain
```

3. Run the pipeline step-by-step:

```bash
# Activate environment
source .venv/bin/activate

# Run notebooks in order (they'll use your custom config automatically)
jupyter notebook notebooks/01_keyword_expansion.ipynb
jupyter notebook notebooks/02_arxiv_search.ipynb
jupyter notebook notebooks/03_researcher_extraction.ipynb
jupyter notebook notebooks/04_social_enrichment.ipynb
jupyter notebook notebooks/05_message_personalization.ipynb

# Send emails (optional)
python scripts/send_emails.py
```

## Configuration

### Domain Configuration
Copy and customize the configuration for your research domain:

```bash
# Create your custom config (gitignored)
cp config/default.yaml config/custom.yaml
# Edit config/custom.yaml with your settings
```

The pipeline will automatically use `config/custom.yaml` if it exists, otherwise fall back to `config/default.yaml`.

Example customization:

```yaml
domain:
  name: "your-field"
  description: "Brief description of your research area"

keywords:
  - "keyword1"
  - "keyword2"
  - "keyword3"

# ArXiv categories, date ranges, etc.
```

### Processing Limits
Control scale during testing:

```yaml
processing:
  max_researchers: 10  # Start small for testing
```

## Pipeline Stages

### 1. Keyword Expansion (`01_keyword_expansion.ipynb`)
- **Input**: `config/default.yaml`
- **Output**: `data/keywords_expanded.csv`
- **Purpose**: Use LLM to expand initial keywords into comprehensive search terms

### 2. ArXiv Search (`02_arxiv_search.ipynb`)
- **Input**: `data/keywords_expanded.csv`
- **Output**: `data/papers.csv`
- **Purpose**: Query ArXiv API to fetch relevant research papers

### 3. Researcher Extraction (`03_researcher_extraction.ipynb`)
- **Input**: `data/papers.csv`
- **Output**: `data/researchers.csv`
- **Purpose**: Extract researcher information and infer profiles from papers

### 4. Social Enrichment (`04_social_enrichment.ipynb`)
- **Input**: `data/researchers.csv`
- **Output**: `data/researchers_enriched.csv`
- **Purpose**: Find LinkedIn/Twitter/GitHub profiles via DuckDuckGo search

### 5. Message Personalization (`05_message_personalization.ipynb`)
- **Input**: `data/researchers_enriched.csv`
- **Output**: `data/researchers_outreach.csv`
- **Purpose**: Generate personalized outreach messages using LLM

### 6. Email Sending (`scripts/send_emails.py`)
- **Input**: `data/researchers_outreach.csv`
- **Purpose**: Send emails with manual control and status tracking

## Data Flow

```
Config YAML → Keywords → Papers → Researchers → Enriched → Outreach → Emails
     ↓          ↓          ↓         ↓            ↓          ↓         ↓
   config/   keywords_   papers.csv  researchers  enriched    outreach  sent
   default.    expanded.              .csv        .csv        .csv     emails
     yaml        csv
```

## Key Features

- **Modular Design**: Each stage is independent with CSV checkpoints
- **Configurable**: Easy to adapt for different research domains
- **Cost-Effective**: Uses DeepSeek via OpenRouter (~$0.0014-0.0028 per 1K tokens)
- **Transparent**: Human-readable CSVs at each stage
- **Manual Control**: Review and approve before sending emails
- **Resume Capability**: Restart from any checkpoint

## Validation & Testing

Run validation checks:
```bash
python scripts/validate_csv.py
```

## Cost Estimation

For 1000 researchers:
- LLM calls: ~$5-10 total
- ArXiv API: Free
- DuckDuckGo search: Free
- Email sending: Free (Gmail SMTP)

## Project Structure

```
contact-scholar/
├── config/                 # Configuration files
│   ├── default.yaml       # Template configuration (version controlled)
│   ├── custom.yaml        # Your custom config (gitignored)
│   └── prompts/           # LLM prompt templates
├── notebooks/             # Jupyter notebooks (pipeline stages)
├── scripts/               # Utility scripts
├── tests/                 # Basic tests
├── data/                  # Generated CSV files (gitignored)
├── outputs/               # Additional outputs (gitignored)
├── pyproject.toml         # uv configuration
├── .env.example          # Environment variables template
└── README.md
```

## Troubleshooting

### Common Issues

1. **OpenRouter API errors**: Check your API key in `.env`
2. **Missing dependencies**: Run `uv sync` to install packages
3. **ArXiv rate limits**: Built-in delays handle 3 req/sec limits
4. **DuckDuckGo blocking**: May need manual fallback for some searches

### Recovery

Each CSV is a checkpoint - you can restart from any stage by loading the previous CSV.

## Future Enhancements

- Web UI for researcher browsing
- Follow-up email sequences
- Citation count integration
- Geographic filtering
- Response tracking CRM

---

*Built with modern Python tooling (uv) and cost-effective AI (OpenRouter + DeepSeek)*