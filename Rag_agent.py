import sqlite3
import datetime
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
#Part D
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import timezone, timedelta

current_date = datetime.datetime.now().strftime("%Y-%m-%d")

# Setup RAG Database
embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

@tool
def search_university_knowledge(query: str) -> str:
    """Retrieve relevant passages from the university handbook (RAG)."""
    docs = vectorstore.similarity_search(query, k=3)
    if not docs:
        return "No relevant documents found."
    return "\n\n".join(
        f"Source: {d.metadata.get('source','?')}, Page: {d.metadata.get('page','?')}\n{d.page_content}"
        for d in docs)

# Setup Memory Database
DB = "student_memory.db"

# Create table if it doesn't exist
c = sqlite3.connect(DB)
c.execute("""CREATE TABLE IF NOT EXISTS memories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT, content TEXT, ts TEXT)""")
c.commit()
c.close()

@tool
def save_student_memory(content: str) -> str:
    """Save a fact the user shared (name, course, preference, etc.)."""
    c = sqlite3.connect(DB)
    c.execute("INSERT INTO memories(user,content,ts) VALUES (?,?,?)",
              ("default", content, datetime.datetime.now().isoformat()))
    c.commit(); c.close()
    return f"[SAVED] {content}"

@tool
def search_student_memory(query: str) -> str:
    """Search previously stored memories by keyword."""
    c = sqlite3.connect(DB)
    rows = c.execute("SELECT content FROM memories WHERE content LIKE ?", (f"%{query}%",)).fetchall()
    c.close()
    if not rows:
        return "No matching memories found."
    return "Found:\n" + "\n".join(r[0] for r in rows)

# Setup Calculator Tool
@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"Error: {e}"

# Setup Google Calendar Tools
creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/calendar"])
service = build("calendar", "v3", credentials=creds)

@tool
def create_calendar_event(summary: str, start_iso: str, end_iso: str, description: str = "") -> str:
    """Create a Google Calendar event. 
    start_iso / end_iso format MUST be: '2025-11-08T15:00:00+05:30'."""
    body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_iso, "timeZone": "Asia/Colombo"},
        "end":   {"dateTime": end_iso,   "timeZone": "Asia/Colombo"},
    }
    ev = service.events().insert(calendarId="primary", body=body).execute()
    return f"Created event: {ev.get('htmlLink')}"

@tool
def get_today_events() -> str:
    """Get the user's PERSONAL Google Calendar events for today. 
    Use this tool whenever the user asks about their own schedule, meetings, appointments, or calendar."""
    now = datetime.datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0).isoformat()
    end   = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat()
    
    res = service.events().list(calendarId="primary", timeMin=start, timeMax=end, 
                                singleEvents=True, orderBy="startTime").execute()
    evs = res.get("items", [])
    
    if not evs: return "No events today."
    return "\n".join(
        f"- {e['summary']} @ {e['start'].get('dateTime', e['start'].get('date'))}"
        for e in evs)


# Initialize Agent & Loop
tools = [search_university_knowledge, save_student_memory, search_student_memory, calculate,create_calendar_event, get_today_events]
tools_map = {t.name: t for t in tools}

llm = ChatOllama(model="llama3.2:3b", temperature=0)
llm_tools = llm.bind_tools(tools)

SYSTEM = (
    f"You are an intelligent university assistant. Today's date is {current_date}. "
    "1. If the user asks about their personal schedule, meetings, or calendar, use get_today_events or create_calendar_event. "
    "2. If get_today_events returns that the calendar is empty, simply tell the user they have no events today. DO NOT ask for a student ID. "
    "3. Use search_university_knowledge for questions about courses, rules, or the handbook. "
    "4. Use save_student_memory if the user tells you their name or details. "
    "5. Use calculate for math."
)

def run():
    msgs = [SystemMessage(content=SYSTEM)]
    print("============================================")
    print("RAG UNIVERSITY ASSISTANT")
    print("============================================")
    print("Type 'quit' to exit.\n")
    
    while True:
        u = input("You: ").strip()
        if u.lower() in {"quit", "exit"}: 
            break
        msgs.append(HumanMessage(content=u))
        
        # Inner loop to handle tool calls
        while True:
            r = llm_tools.invoke(msgs)
            msgs.append(r)
            
            if not r.tool_calls:
                print(f"agent: {r.content}\n")
                break
                
            for tc in r.tool_calls:
                print(f"[TOOL SELECTED] {tc['name']}")
                print(f"[TOOL ARGUMENTS] {tc['args']}")
                out = tools_map[tc["name"]].invoke(tc["args"])
                print(f"[TOOL RESULT] {out}\n")
                msgs.append(ToolMessage(content=str(out), tool_call_id=tc["id"]))

if __name__ == "__main__":
    run()