import os, platform, datetime, subprocess
import pyautogui, pygetwindow as gw, pyperclip
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

llm = ChatOllama(model="llama3.2:3b", temperature=0)

# Calculator
@tool
def open_calculator(expression: str) -> str:
    """Opens Windows Calculator and evaluates a math expression."""
    pyautogui.hotkey("win", "r"); import time; time.sleep(0.6)
    pyautogui.write("calc"); pyautogui.press("enter"); time.sleep(2)
    try: gw.getWindowsWithTitle("Calculator")[0].activate()
    except Exception: pass
    time.sleep(0.4)
    pyautogui.write(expression); pyautogui.press("enter"); time.sleep(0.6)
    pyautogui.hotkey("ctrl", "a"); pyautogui.hotkey("ctrl", "c"); time.sleep(0.2)
    return f"{expression} = {pyperclip.paste().strip()}"

# Date & Time
@tool
def get_datetime() -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().strftime("%A, %d %B %Y, %H:%M:%S")

# Notepad
@tool
def open_notepad_and_write(text: str) -> str:
    """Opens Windows Notepad and writes the given text."""
    subprocess.Popen("notepad.exe"); import time; time.sleep(1.5)
    try: gw.getWindowsWithTitle("Notepad")[0].activate()
    except Exception: pass
    time.sleep(0.4)
    pyautogui.write(text, interval=0.02)
    return f"Wrote {len(text)} chars to Notepad."

# File Search
@tool
def search_files(directory: str, pattern: str) -> str:
    """Search for files by name/extension inside a directory.
    Example: directory='D:\\MSC AI', pattern='*.pdf'"""
    root = Path(directory)
    if not root.exists():
        return f"Directory {directory} not found."
    hits = [str(p) for p in root.rglob(pattern)][:50]
    return f"Found {len(hits)} files:\n" + "\n".join(hits) if hits else "No matches."

# File Creation
@tool
def create_file(path: str, content: str) -> str:
    """Create a text file at path with the given content."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Created {p} ({p.stat().st_size} bytes)."

# System Info
@tool
def get_system_info() -> str:
    """Return OS, processor and memory information."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        mem_line = f"{mem.total/1e9:.1f} GB total, {mem.available/1e9:.1f} GB free"
    except ImportError:
        mem_line = "install psutil for memory info"
    return (f"OS: {platform.system()} {platform.release()} ({platform.version()})\n"
            f"Machine: {platform.machine()}\n"
            f"Processor: {platform.processor()}\n"
            f"Memory: {mem_line}")

tools = [open_calculator, get_datetime, open_notepad_and_write,
         search_files, create_file, get_system_info]
tools_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)

SYSTEM = ("You are a tool-using assistant. Use the right tool for each request. "
          "When the user wants to search files, extract directory and pattern. "
          "When creating a file, extract full path and content.")

def run():
    msgs = [SystemMessage(content=SYSTEM)]
    while True:
        u = input("You: ").strip()
        if u.lower() in {"quit", "exit"}: break
        msgs.append(HumanMessage(content=u))
        while True:
            r = llm_with_tools.invoke(msgs)
            msgs.append(r)
            if not r.tool_calls:
                print(f"agent: {r.content}\n"); break
            for tc in r.tool_calls:
                print(f"[TOOL] {tc['name']} {tc['args']}")
                out = tools_map[tc["name"]].invoke(tc["args"])
                print(f"[RESULT] {out}\n")
                msgs.append(ToolMessage(content=str(out), tool_call_id=tc["id"]))

if __name__ == "__main__":
    run()