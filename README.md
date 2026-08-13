# AI Engineering Learning Platform

A production-quality learning platform for AI engineering: structured course
content, an AI tutor chat, auto-graded quizzes, and per-user progress
tracking.

## Stack

- **Backend:** FastAPI (Python) + PostgreSQL
- **Frontend:** React + Vite + TypeScript
- **AI:** provider-agnostic LLM integration (currently backed by Mistral)

## Project layout

- `backend/` — FastAPI application, database models, API routes
- `frontend/` — React single-page application
- `docs/` — supplementary documentation

## Status

Core platform (auth, courses, lessons, AI tutor chat) is implemented, plus
Mermaid diagram rendering in lessons and markdown-formatted chat replies.
An interactive in-browser Python playground and graded coding exercises are
in progress.
