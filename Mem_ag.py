import sqlite3, datetime
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

DB = "student_memory.db"

def init_db():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS memories(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT, content TEXT, ts TEXT)""")
    c.commit(); c.close()
init_db()

# Memory tools
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
    rows = c.execute(
        "SELECT content FROM memories WHERE content LIKE ?",
        (f"%{query}%",)).fetchall()
    c.close()
    if not rows:
        return "No matching memories found."
    return "Found:\n" + "\n".join(r[0] for r in rows)

@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression, {"__builtins__": {}}))

tools = [save_student_memory, search_student_memory, calculate]
tools_map = {t.name: t for t in tools}
llm = ChatOllama(model="llama3.2:3b", temperature=0)
llm_tools = llm.bind_tools(tools)

SYSTEM = (
    "You are an intelligent student assistant with memory. "
    "If the user reveals a personal fact (name, degree, hobby, etc.), "
    "call save_student_memory. If they ask about something you might have "
    "stored, call search_student_memory first. Otherwise answer directly."
)

def run():
    # SHORT-TERM memory = the msgs list itself
    msgs = [SystemMessage(content=SYSTEM)]
    print("=== INTELLIGENT STUDENT AI AGENT ===\n")
    while True:
        u = input("You: ").strip()
        if u.lower() in {"quit", "exit"}: break
        msgs.append(HumanMessage(content=u))
        while True:
            r = llm_tools.invoke(msgs)
            msgs.append(r)
            if not r.tool_calls:
                print(f"agent: {r.content}\n"); break
            for tc in r.tool_calls:
                print(f"[TOOL SELECTED] {tc['name']}")
                print(f"[TOOL ARGUMENTS] {tc['args']}")
                out = tools_map[tc["name"]].invoke(tc["args"])
                print(f"[TOOL RESULT] {out}\n")
                msgs.append(ToolMessage(content=str(out), tool_call_id=tc["id"]))

if __name__ == "__main__":
    run()