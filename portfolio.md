# Portfolio – Lab 6: Tool-Using AI Agents

## Part A: Calculator Agent (`Cal.py`)
I created the initial calculator agent. To make it truly interactive, the script uses `pyautogui` to press `Win+R`, open the Calculator app, type the math expression, and copy the result to the clipboard to return to the LLM.

*(Evidence: `screenshots/calculator/`)*

## Exercise: Expanding with Multiple Tools (`Multi_tools.py`)
I implemented the requested tools (Date/Time, Notepad, File Search, File Creation, System Info). I used `pathlib` for file operations and `psutil` for system information. 

**Reflection:** Using `llm.bind_tools()` and a custom `while True` loop made the agent much more reliable with Llama 3.2, as it perfectly parsed the `tool_calls` list.

*(Evidence: `screenshots/Multiple_tools.png`)*

## Part B: Memory Agent (`Mem_ag.py`)
I gave the agent memory using SQLite. I created custom tools `save_student_memory` and `search_student_memory`. 
When the user says "Hi, I'm Thilini", the agent calls the save tool. If the user later asks "What is my name?", it queries the SQLite database to remember.

*(Evidence: `screenshots/Agent_memory.PNG`)*

## Part C & D: RAG and Google Calendar (`Rag_agent.py`)
This is the final, comprehensive agent. It combines:
1. **RAG:** Connects to the ChromaDB from Lab 5 to search the university handbook.
2. **Memory:** SQLite for user facts.
3. **Google Calendar:** I configured OAuth 2.0 in Google Cloud Console, ran `G_cal.py` to generate `token.json`, and integrated tools to read today's schedule and create new events.

**Struggle & Fix:** Integrating Google Calendar required careful date/time formatting (ISO 8601). I added clear instructions to the agent's System Prompt to ensure it passed the correct parameters to `create_calendar_event`.

*(Evidence: `screenshots/Rag_agent.png`, `screenshots/Calender/`)*