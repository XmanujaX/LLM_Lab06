# Lab 6 – Building a Tool-Using AI Agent

**Student:** Hingurala Perera
**Module:** PUSL3205 - Large Language Models and Generative AI

## Overview
In this lab, I built multiple AI agents using LangChain and Ollama. To demonstrate modular programming, the lab tasks are separated into different Python scripts. I utilized `llm.bind_tools()` with a custom execution loop, which proved highly effective for smaller local models like Llama 3.2.

## Contents
* `Cal.py` – Part A: Basic Calculator agent that opens the Windows Calculator app.
* `Multi_tools.py` – Exercise: Agent with OS tools (Notepad, System Info, File Search, etc.).
* `Mem_ag.py` – Part B: Agent with SQLite long-term memory capabilities.
* `Rag_agent.py` – Part C & D: The final intelligent agent combining RAG (ChromaDB), Memory (SQLite), Calculator, and Google Calendar API integration.
* `G_cal.py` – Helper script to generate the `token.json` for Google API OAuth authentication.
* `screenshots/` – Evidence of each working agent.

## Setup Summary
| Feature | Implementation |
|---|---|
| **LLM** | Llama 3.2 3B (via Ollama) |
| **OS Tools** | `pyautogui`, `subprocess`, `psutil` |
| **Memory** | SQLite (`student_memory.db`) |
| **RAG** | ChromaDB (`qwen3-embedding:0.6b`) |
| **API Integration** | Google Calendar API (OAuth 2.0) |

## How to Run
1. Ensure Ollama is running and `llama3.2:3b` is pulled.
2. Install dependencies: `pip install -r requirements.txt`
3. Run any of the scripts, for example: `python Rag_agent.py`