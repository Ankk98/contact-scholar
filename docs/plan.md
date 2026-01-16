# Research Scholar Contact Pipeline - Detailed Implementation Plan

## Executive Summary

**Project:** `contact-scholar` - Modular, configurable pipeline to discover researchers in any field, enrich with contact information, generate personalized outreach messages, and send emails.

**Target:** Build working pipeline step-by-step with validation at each stage, capable of processing 1000+ researchers with ~$5-10 in LLM costs. Configurable for any research domain.

**Key Decisions:**
- Use ArXiv XML API (no PDFs)
- OpenRouter + DeepSeek for LLM calls
- DuckDuckGo for social profile discovery
- CSV-based intermediate storage with contact memory
- uv for Python dependency management
- Gmail SMTP for email sending (simple one-at-a-time)

---

## 1. Project Scope & Requirements

### Functional Requirements

1. **Keyword Expansion**: Take initial keywords → LLM-augmented comprehensive search terms (configurable by domain)
2. **Paper Discovery**: Query ArXiv API for relevant papers using expanded keywords + categories + date filters
3. **Researcher Extraction**: Parse author information from papers, deduplicate researchers
4. **Profile Enrichment**: Find LinkedIn/Twitter/GitHub profiles via search
5. **Message Personalization**: Generate tailored outreach emails using researcher context (English focus)
6. **Email Sending**: Send emails one at a time with manual control
7. **Contact Memory**: Track contacted scholars with simple status (sent/pending) and manual notes

### Non-Functional Requirements

- **Cost**: <$10> total for 1000 researchers (depending on LLM usage)
- **Speed**: Complete pipeline in <1 hour for 1000 researchers
- **Reliability**: Handle API failures, malformed LLM responses
- **Transparency**: Inspectable intermediate CSVs at each step with contact history
- **Maintainability**: Config-driven, no hardcoded domain-specific values
- **Modularity**: Step-by-step validation, easy to pause/resume/update, manual CSV management

### Success Criteria

- Pipeline processes 1000+ researchers successfully (configurable scale)
- Generated emails are personalized and professional (English language focus)
- CSV outputs maintain memory of contacted scholars and their response status
- System handles common edge cases (missing data, API limits)
- Easy to re-run stages independently with modular design
- Configurable research domains
- Manual tracking of responses and collaboration opportunities

---

## 2. Technical Stack Validation

### ✅ Confirmed Working Components

**OpenRouter API:**
- ✅ Active and functional
- ✅ DeepSeek models available: `deepseek/deepseek-chat`, `deepseek/deepseek-r1`, `deepseek/deepseek-v3.2`, etc.
- ✅ OpenAI-compatible SDK usage confirmed
- ✅ Pricing: ~$0.0014-$0.0028 per 1K tokens (very cost-effective)

**Python Libraries:**
- ✅ `arxiv` package: v2.4.0 available (stable, well-maintained)
- ✅ `duckduckgo-search` package: v8.1.1 available (active development)
- ✅ `openai` SDK: Compatible with OpenRouter
- ✅ Standard libraries: `pandas`, `requests`, `smtplib` all available

**APIs & Services:**
- ✅ ArXiv XML API: Free, 3 req/sec limit, structured data
- ✅ DuckDuckGo Search: Free, no auth required
- ✅ Gmail SMTP: App passwords still supported

### ⚠️ Potential Concerns

**DuckDuckGo Search Reliability:**
- May return inconsistent results
- No official API (uses web scraping)
- Could be blocked or rate-limited
- **Mitigation:** Accept partial enrichment, manual fallback for important targets

**DeepSeek Model Availability:**
- Models confirmed available but may change
- **Mitigation:** Configurable model selection, fallback options

**Gmail Deliverability:**
- App passwords still work but Gmail may flag bulk emails
- **Mitigation:** Start small (10-20 emails/day), professional content, monitor bounce rates

### 🔄 Alternative Options Considered

**Search Alternatives:**
- SerpAPI (~$50/month) - More reliable but expensive
- **Decision:** Stick with DuckDuckGo for cost reasons

**LLM Alternatives:**
- Direct API calls to DeepSeek (if available)
- **Decision:** OpenRouter provides better vendor abstraction

**Email Alternatives:**
- SendGrid/Mailgun APIs
- **Decision:** Gmail SMTP sufficient for small scale

### Gmail SMTP Setup Guide

**Prerequisites:**
- Gmail account (preferably dedicated for outreach)
- 2-factor authentication enabled on Gmail account

**Step 1: Generate App Password**
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to "Security" → "2-Step Verification"
3. Scroll down to "App passwords"
4. Select "Mail" and "Other (custom name)"
5. Enter "Research Outreach" as the name
6. Copy the 16-character password generated

**Step 2: Configure Environment Variables**
```bash
# .env file
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=abcd-efgh-ijkl-mnop  # The 16-char app password
```

**Step 3: Test SMTP Connection**
The email script will test connectivity before sending bulk emails.

**Important Notes:**
- Gmail may flag bulk emails as spam initially
- Start with individual emails
- Monitor spam folder and mark legitimate emails as "not spam"
- If Gmail blocks sending, emails can still be sent manually by copying from CSV

**Alternative:** If Gmail setup fails, all generated emails will be saved in CSV for manual sending via your preferred email client.

---

## 2. Technical Architecture

### Core Components

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Config        │    │   Notebooks     │    │   Scripts       │
│   (YAML +       │    │   (Jupyter)     │    │   (Python)      │
│    Prompts)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Flow     │    │   LLM Calls     │    │   API Calls     │
│   (CSV files)   │◄──►│   (OpenRouter)  │◄──►│   (ArXiv, DDG)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow Architecture

```
Config YAML → 01_keyword_expansion.ipynb → data/keywords_expanded.csv
                                                           ↓
                                            02_arxiv_search.ipynb → data/papers.csv
                                                           ↓
                                     03_researcher_extraction.ipynb → data/researchers.csv
                                                           ↓
                                        04_social_enrichment.ipynb → data/researchers_enriched.csv
                                                           ↓
                                    05_message_personalization.ipynb → data/researchers_outreach.csv
                                                           ↓
                                             scripts/send_emails.py → Updated outreach CSV + sent emails
```

### CSV Schemas (Updated for Contact Memory)

#### 1. `keywords_expanded.csv`

| Column    | Type | Description                  |
|-----------|------|------------------------------|
| original  | str  | Original keyword             |
| expanded  | str  | Expanded keyword             |
| category  | str  | (optional) tag/emerging etc. |

#### 2. `papers.csv`

| Column         | Type     | Description                          |
|----------------|----------|--------------------------------------|
| arxiv_id       | str      | ArXiv identifier                     |
| title          | str      | Paper title                          |
| authors_raw    | str      | `Author1 | Author2 | ...`           |
| affiliations   | str      | Combined affiliations (if present)   |
| summary        | str      | Abstract                             |
| published_date | datetime | Publication date                     |
| url            | str      | `https://arxiv.org/abs/{arxiv_id}`   |
| categories     | str      | Comma-separated category codes       |

#### 3. `researchers.csv`

| Column         | Type | Description                                  |
|----------------|------|----------------------------------------------|
| name           | str  | Researcher full name                         |
| affiliation    | str  | University/Lab                               |
| research_focus | str  | Short summary of their topics                |
| seniority      | str  | `senior` / `mid` / `junior` (LLM inferred)   |
| papers         | str  | Semi-colon separated list of ArXiv IDs       |

#### 4. `researchers_enriched.csv`

Same as `researchers.csv` plus:

| Column   | Type | Description            |
|----------|------|------------------------|
| linkedin | str  | LinkedIn profile URL   |
| twitter  | str  | Twitter/X profile URL  |
| github   | str  | GitHub profile URL     |

#### 5. `researchers_outreach.csv`

Same as `researchers_enriched.csv` plus:

| Column              | Type     | Description                           |
|---------------------|----------|---------------------------------------|
| personalized_message| str      | LLM-generated email body              |
| status              | str      | `pending` / `sent`                    |
| sent_date           | datetime | When email was sent (if sent)         |
| notes               | str      | Internal notes (manual fill)          |

### Key Design Decisions

1. **No PDFs**: ArXiv XML provides sufficient metadata without storage/parsing overhead
2. **CSV State**: Human-readable, git-diffable, restartable from any point
3. **LLM-First**: Use AI for extraction/enrichment rather than complex parsing rules
4. **OpenRouter**: Vendor-agnostic, cost-effective, OpenAI-compatible API
5. **Jupyter Development**: Interactive debugging, cell-by-cell execution

---

## 3. Detailed Implementation Plan

### Phase 1: Infrastructure Setup (2-3 hours)

#### 1.1 Repository Structure
```bash
contact-scholar/
├── pyproject.toml          # uv configuration
├── uv.lock                 # uv lockfile
├── .env.example
├── .gitignore
├── README.md
├── .python-version         # Optional: pyenv version specification
├── docs/
│   └── plan.md
├── config/
│   ├── default.yaml
│   └── prompts/
│       ├── expand_keywords.txt
│       ├── extract_researcher_info.txt
│       └── personalize_message.txt
├── notebooks/
│   ├── 01_keyword_expansion.ipynb
│   ├── 02_arxiv_search.ipynb
│   ├── 03_researcher_extraction.ipynb
│   ├── 04_social_enrichment.ipynb
│   └── 05_message_personalization.ipynb
├── scripts/
│   ├── send_emails.py
│   ├── validate_csv.py
│   └── utils.py
├── tests/         # Optional: basic tests
│   └── test_utils.py
├── data/          # .gitignored
└── outputs/       # .gitignored
```

#### 1.2 Dependency Management with uv
- Modern Python packaging and dependency management
- Faster installation and reproducible environments
- Can work alongside existing Python installations
- Perfect for simple Python package dependencies
- No container overhead needed for this project

#### 1.3 Configuration Design
- `config/default.yaml`: Generic template with all parameters (keywords, API settings, email template guidelines)
- Domain-specific configs: Copy default.yaml and customize
- `config/prompts/*.txt`: LLM prompt templates with variable placeholders
- Environment variables: API keys, email credentials
- Email template: Configurable via text descriptions sent to LLM

**Sample Email Template Config (in default.yaml):**
```yaml
email_template:
  tone: "professional and friendly academic outreach"
  background: "background"
  value_proposition: "value prosition"
  length: "150-200 words"
  call_to_action: "propose 2-3 concrete collaboration opportunities"
```

### Phase 2: Core Pipeline Implementation (4-6 hours)

#### 2.1 Notebook 01: Keyword Expansion
**Input:** `config/default.yaml`
**Output:** `data/keywords_expanded.csv`
**Logic:**
- Load base keywords from config
- Call LLM with expansion prompt
- Parse JSON response (original + expanded + emerging keywords)
- Save to CSV with columns: `original`, `expanded`, `category`

**Risk Mitigation:**
- Handle malformed JSON with retry + repair prompt
- Validate output has expected structure

#### 2.2 Notebook 02: ArXiv Search
**Input:** `data/keywords_expanded.csv`
**Output:** `data/papers.csv`
**Logic:**
- Combine all expanded keywords into ArXiv query
- Add category filters (cs.RO, cs.AI, etc.)
- Add date range filters
- Use `arxiv` library or direct HTTP requests
- Parse XML responses into structured data
- Save CSV with columns: `arxiv_id`, `title`, `authors_raw`, `affiliations`, `summary`, `published_date`, `url`, `categories`

**Risk Mitigation:**
- Rate limiting: 3 requests/sec max
- Pagination handling for large result sets
- Error handling for API failures

#### 2.3 Notebook 03: Researcher Extraction
**Input:** `data/papers.csv`
**Output:** `data/researchers.csv`
**Logic:**
- For each paper, format extraction prompt with paper details
- Call LLM to extract researcher info + infer seniority/focus
- Parse JSON response into researcher records
- Sort by name and leave depduplication logic for future
- Aggregate papers per researcher (semi-colon separated)
- Save CSV with columns: `name`, `affiliation`, `research_focus`, `seniority`, `papers`

**Risk Mitigation:**
- Process in reasonable chunks to manage API calls
- JSON parsing with fallback repair prompts
- Handle missing affiliations gracefully

#### 2.4 Notebook 04: Social Enrichment
**Input:** `data/researchers.csv`
**Output:** `data/researchers_enriched.csv`
**Logic:**
- For each researcher, generate search queries:
  - "{name} {affiliation} LinkedIn"
  - "{name} {affiliation} Twitter"
  - "{name} {affiliation} GitHub"
- Use DuckDuckGo search API
- Extract first plausible URL from results
- Add columns: `linkedin`, `twitter`, `github`

**Risk Mitigation:**
- Accept partial enrichment (many won't have complete profiles)
- Simple URL validation
- Rate limiting between searches

#### 2.5 Notebook 05: Message Personalization
**Input:** `data/researchers_enriched.csv`
**Output:** `data/researchers_outreach.csv`
**Logic:**
- For each researcher, fill personalization prompt template
- Include: name, affiliation, research focus, recent paper, background
- Call LLM to generate email body (150-200 words)
- Add columns: `personalized_message`, `status` (initially "pending"), `sent_date`, `notes`

**Risk Mitigation:**
- Template validation
- Character limits in prompts

### Phase 3: Email Infrastructure (1-2 hours)

#### 3.1 Email Sending Script
**Input:** `data/researchers_outreach.csv`
**Output:** Updated CSV with send status
**Logic:**
- Use Gmail SMTP with app password
- Send one email at a time
- Update status: "sent", sent_date
- Simple error handling

**Risk Mitigation:**
- Manual control over sending
- Easy to pause/resume
- Proper authentication setup

#### 3.2 Validation & Utils
- `validate_csv.py`: Check schemas, nulls, duplicates
- `utils.py`: Shared functions (config loading, LLM client, email setup)

---

## 4. Risk Analysis & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM returns malformed JSON | High | Medium | Retry with repair prompt, fallback parsing, JSON mode if available |
| ArXiv API rate limiting | Medium | Low | Built-in delays (3 req/sec), exponential backoff |
| Missing affiliations in ArXiv | High | Low | Accept "Unknown", use LLM inference from context |
| Wrong social profiles from search | High | Medium | Manual review for top targets, accept partial enrichment, validate URLs |
| Gmail spam filtering | Medium | High | Professional content, manual sending control |
| Researcher deduplication fails | Medium | Low | Fuzzy name matching, manual review, case-insensitive comparison |
| OpenRouter API issues | Low | Medium | Alternative models in config (anthropic/claude-3-haiku as backup) |
| DeepSeek model instability | Medium | Medium | Monitor model performance, have fallback to GPT-3.5-turbo |
| DuckDuckGo blocking/ rate limiting | Medium | Medium | Rate limiting (1 req/sec), fallback to manual enrichment for critical targets |

### Data Quality Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Incomplete researcher data | High | Medium | Graceful handling, partial processing |
| Outdated profiles | Medium | Medium | Accept as "good enough" for initial outreach |
| Non-academic researchers | Low | Low | Category filtering reduces this |
| International name formats | Medium | Low | LLM handles various formats |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| High LLM costs | Low | Low | Budget monitoring |
| Pipeline interruption | Medium | Low | CSV checkpoints allow restart |
| Email deliverability issues | Medium | Medium | Professional templates, gradual scaling |

---

## 5. Step-by-Step Implementation Timeline

### Phase 1: Infrastructure Setup (2-3 hours)
**Goal:** Get basic environment ready for development

1. Create repository structure
2. Set up uv environment and install dependencies
3. Create config files and prompts
4. Test OpenRouter API connectivity

**Deliverable:** Working environment with confirmed API access

### Phase 2: Keyword Expansion & ArXiv Search (2-3 hours)
**Goal:** First end-to-end pipeline segment

1. Implement Notebook 01 (Keyword Expansion)
2. Implement Notebook 02 (ArXiv Search)
3. Test: config → keywords_expanded.csv → papers.csv

**Deliverable:** CSV with 1000+ relevant papers

### Phase 3: Researcher Extraction (2-3 hours)
**Goal:** Extract researcher information from papers

1. Implement Notebook 03 (Researcher Extraction)
2. Debug LLM JSON parsing
3. Test: papers.csv → researchers.csv

**Deliverable:** Deduplicated researcher database

### Phase 4: Profile Enrichment (2-3 hours)
**Goal:** Add social media profiles

1. Implement Notebook 04 (Social Enrichment)
2. Test DuckDuckGo search integration
3. Test: researchers.csv → researchers_enriched.csv

**Deliverable:** Researchers with LinkedIn/Twitter/GitHub links

### Phase 5: Message Personalization (2-3 hours)
**Goal:** Generate personalized outreach messages

1. Implement Notebook 05 (Message Personalization)
2. Test LLM email generation
3. Test: researchers_enriched.csv → researchers_outreach.csv

**Deliverable:** Contact book ready for outreach

### Phase 6: Email Infrastructure (2-3 hours)
**Goal:** Email sending capability

1. Set up Gmail SMTP credentials
2. Implement email sending script (one email at a time)
3. Test individual email sending

**Deliverable:** Ability to send individual emails with status tracking

### Phase 7: Validation & Refinement (Ongoing)
**Goal:** Improve quality and add features as needed

1. Manual verification of researcher data
2. Email template optimization
3. Response tracking and follow-up workflows
4. Advanced features (reporting, automation)

---

## 6. Success Metrics & Validation

### Quantitative Metrics
- **Coverage:** % of papers successfully processed
- **Enrichment:** % of researchers with at least one social profile
- **Email Success:** % of emails delivered (not bounced)
- **Cost:** Total LLM API costs (~$0.003 per call with DeepSeek)
- **Time:** End-to-end pipeline runtime

### Qualitative Metrics
- **Data Quality:** Manual review of 50 random researchers
- **Email Quality:** Professional appearance, personalization accuracy
- **Pipeline Reliability:** % of runs completing without manual intervention
- **Email Success:** % of emails sent successfully

### Validation Checklist
- [ ] All CSVs have correct schemas
- [ ] No duplicate researchers in final output
- [ ] LLM-generated content is coherent
- [ ] Emails send successfully (test individual)
- [ ] Pipeline restarts correctly from any checkpoint
- [ ] Config changes don't require code changes

---

## 7. Assumptions & Prerequisites

### Technical Assumptions
- OpenRouter API key available and functional
- Gmail account with app password configured
- Stable internet connection for API calls
- Sufficient disk space for CSVs (minimal)

### Data Assumptions
- ArXiv has sufficient coverage of target research area
- Researchers have discoverable online presence
- Email addresses can be inferred or will be added manually

### Business Assumptions
- Cold outreach is acceptable in this research community
- Recipients will be receptive to personalized academic outreach
- Small-scale operation (not millions of emails)

---

## 8. Future Enhancements

### Phase 2 Features
- Web UI for researcher browsing/filtering (Streamlit)
- Follow-up email sequences
- Response tracking and CRM integration
- Citation count integration (Semantic Scholar)
- Geographic/regional filtering

### Production Improvements
- Replace Jupyter with proper Python scripts
- Database storage instead of CSVs
- Queue system for email sending
- Monitoring and alerting
- A/B testing for email templates

---

## 9. Updated Questions for Clarification

✅ **Answered:**
1. **Scale:** 1000+ configurable, can send to 1 as well ✓
2. **Credentials:** OpenRouter API key ready, Gmail account available ✓
3. **Focus:** English only for now, keep simple ✓
4. **Accuracy vs Scale:** Both important, modular for verification/updates ✓
5. **Email Strategy:** Focus on initial outreach only ✓
6. **Legal/Compliance:** Ignore regulations for now ✓
7. **Success Definition:** Response rates, collaboration willingness, contracts ✓
8. **Timeline:** Step-by-step validation approach ✓

**All questions answered - ready to proceed with implementation**

---

## 10. Go/No-Go Decision Criteria

**Go Criteria:**
- OpenRouter API key confirmed working
- Gmail credentials configured
- Clear target scale and success metrics defined
- No major legal/compliance concerns

**No-Go Criteria:**
- Unavailable API access
- Strict regulatory constraints
- Unreasonable accuracy requirements
- Timeline pressure incompatible with thorough implementation

---

## 11. Final Recommendation Table

| Component             | Choice                        | Why                                      |
|-----------------------|-------------------------------|------------------------------------------|
| Data source           | ArXiv XML API                 | Structured, free, complete enough        |
| PDFs                  | Not used                      | Overhead, no benefit for metadata        |
| LLM provider          | OpenRouter                    | Multi-vendor, OpenAI-compatible          |
| Default model         | DeepSeek-V3 (`deepseek-chat`) | Cheap, fast, good quality                |
| Data format           | CSV with contact memory       | Simple, human-readable, tracks outreach  |
| Config                | YAML + text prompts           | Flexible, domain-independent             |
| Execution             | Jupyter with uv               | Modern Python environment, fast setup     |
| Search for profiles   | DuckDuckGo text search        | Free, no login, good enough              |
| Email                 | Gmail SMTP (manual fallback)  | Easy setup, reliable, with manual option |
| Scale                 | 1000+ configurable           | Process any number, send emails one at a time |
| Memory                | CSV-based contact tracking    | Remembers sent emails, manual response updates |

---

## 12. Implementation Gotchas & Tips

### Common Issues to Watch For:
1. **LLM JSON Parsing**: DeepSeek sometimes returns malformed JSON - always have fallback parsing
2. **ArXiv Rate Limits**: 3 requests/second - implement delays between batches
3. **DuckDuckGo Blocking**: May block automated requests - have manual fallback
4. **Gmail Authentication**: App passwords expire - document renewal process
5. **CSV Encoding**: Ensure UTF-8 encoding for international researcher names

### Development Tips:
1. **Test Small First**: Always test with 5-10 researchers before scaling
2. **Version Control**: Commit after each successful phase
3. **Backup CSVs**: Keep backups of intermediate results
4. **Monitor Costs**: Track OpenRouter usage in dashboard
5. **Validate Data**: Spot-check LLM outputs for hallucinations

### Quick Recovery:
- Each CSV is a checkpoint - can restart from any phase
- Failed LLM calls can be retried individually
- Manual intervention always possible for edge cases

---

*This plan provides a structured path to build a working research contact pipeline. The modular CSV-based approach ensures transparency and debuggability while keeping costs low and development time reasonable.*