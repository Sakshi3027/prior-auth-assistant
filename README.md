# Prior Authorization Assistant

An AI agent that helps provider offices get insurance approval for treatments
before they happen. A staffer submits a clinical note; the agent reads it,
determines whether prior authorization is required, retrieves the relevant
payer policy, checks the patient against its criteria, and drafts a justified
authorization request with citations and a confidence score.

This is the provider-side mirror of a claims adjudication platform: one gets
approval *before* treatment, the other decides payment *after* it.

## Status

Early — scaffolding the project structure.

## Stack

- LangGraph + FastAPI (agent orchestration and API)
- Groq (LLM)
- Postgres + pgvector (data and policy retrieval in one database)
- FHIR-modeled clinical data
- Next.js (submit, agent-flow, and analytics views)