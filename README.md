# FeedbackIQ — AI Customer Feedback Intelligence

Portfolio prototype for an APM interview.

## What it does
Turns unstructured customer feedback into structured, evidence-backed product insights.

## Features
- LLM extraction: sentiment, category, topic, product area, severity, intent, summary, key issue, evidence, confidence
- CSV upload (`feedback` column)
- Recurring-topic analysis
- Transparent priority view
- Evidence behind each theme
- Grounded Q&A over analyzed feedback
- Demo mode without an API key

## Setup
1. Open Command Prompt in this folder.
2. `python -m pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your Gemini key.
4. `python -m streamlit run app.py`

Do not claim production deployment or real company data. This is a portfolio prototype using synthetic/sample feedback.

## Product principle
AI handles language understanding; deterministic code handles measurable business logic.
