# Security Policy

## Supported Versions

Currently, only the latest version of the main branch is supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| Main    | :white_check_mark: |
| < Main  | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please report it privately to the maintainers rather than opening a public issue. We will respond as quickly as possible to triage and resolve the issue.

## Project Security Practices

CityPulse AI is built with security and data privacy in mind. Here is an overview of the security measures currently implemented in the codebase:

### 1. Secrets Management
- **Environment Variables:** Sensitive information such as API keys (`SERPAPI_KEY`, `GEMINI_KEY`) and database credentials (`SUPABASE_URL`, `SUPABASE_KEY`) are loaded via environment variables using `python-dotenv`.
- **Git Ignore:** The `.env` file, virtual environments, and other sensitive files (like `.log`, `secrets.toml`, `keys.json`) are explicitly excluded from version control in `.gitignore` to prevent accidental credential leakage.

### 2. User Interface Security
- **Credential Masking:** When users are prompted to enter API keys (e.g., SerpApi Key) in the Streamlit web dashboard (`app.py`), the input fields use `type="password"` to ensure the entered text is masked and hidden from over-the-shoulder observation.

### 3. Data Privacy and Session Isolation
- **Session State Isolation:** In the Streamlit app (`app.py`), scraped data is stored and accessed using Streamlit's `st.session_state`. This ensures that data is isolated to the specific user's session and not shared across multiple users interacting with the dashboard concurrently.

### 4. Database Security
- **Cloud Storage:** Data is stored in a Supabase PostgreSQL database. Supabase provides row-level security (RLS) and encrypted data transmission, ensuring that the cloud data remains secure.
