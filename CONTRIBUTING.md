# Contributing to HireTrends

Thank you for your interest in contributing to the HireTrends project. We welcome contributions that maintain our high standards of ethical data engineering, reproducibility, and code quality.

## Ethical Standards & Guidelines

1. **Strict Source Compliance:**
   - Any new web source must undergo a documented audit in `reports/source_audit.md`.
   - Never implement scraping logic for sources marked `PROHIBITED` or `REQUIRES_PERMISSION` without verified written authorization.
   - Respect `robots.txt` directives and implement polite crawl delays.

2. **Zero Personal Identifiable Information (PII):**
   - Do not extract, store, or process candidate CVs, applicant contact information, phone numbers, or private recruiter profiles.
   - Only publicly accessible, job-posting-level technical data may be processed.

3. **Code Quality & Testing:**
   - All contributions must pass automated tests (`pytest -v`).
   - Unit tests must be hermetic and offline—never make live HTTP network calls inside test suites.
   - Type hints and docstrings are required for all public functions and classes.

## Development Setup

```powershell
# Clone the repository
git clone https://github.com/Awaisbacha55/hiretrends-pakistan-job-market.git
cd hiretrends-pakistan-job-market

# Create and activate virtual environment
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt

# Run test suite
pytest -v
```

## Pull Request Guidelines

1. Create a descriptive feature branch (`git checkout -b feature/your-feature-name`).
2. Ensure no sensitive files, credentials, or raw scraped caches are committed.
3. Open a Pull Request referencing the relevant task or milestone.
