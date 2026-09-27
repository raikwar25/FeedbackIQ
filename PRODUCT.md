# Product Specification

## Primary user
Product Manager / Product Operations / Customer Experience team.

## Problem
Large volumes of unstructured feedback make recurring issues difficult to identify and prioritize.

## MVP
Input: feedback CSV.
Output per item: sentiment, category, topic, product area, severity, intent, summary, key issue, evidence, confidence.

Dashboard: volume, negative share, high-severity share, recurring topics, evidence and transparent priority.

## Success metrics
- Time to identify top issues
- Theme coverage
- Useful-theme confirmation rate
- Insight-to-action rate
- Extraction accuracy
- Hallucination rate
- Latency
- Cost per feedback item

## Risks
Hallucinations, wrong clustering, sarcasm, sampling bias, over-automation, excessive taxonomy complexity.

## Future roadmap
Evaluation set → embeddings/vector search → RAG → trend analysis → source connectors → human review workflows.
