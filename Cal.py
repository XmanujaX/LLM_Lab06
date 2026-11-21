import time
import pyautogui
import pygetwindow as gw
import pyperclip
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

# Initialize LLM
llm = ChatOllama(model="llama3.2:3b", temperature=0)

# Create calculator tool
@tool
def open_calculator(expression: str) -> str:
    """Opens Windows Calculator and evaluates a math expression.
    Input should be a valid arithmetic expression, e.g. '7*4' or '25*4'."""
    # Launch calculator
    pyautogui.hotkey("win", "r")
    time.sleep(0.6)
    pyautogui.write("calc")
    pyautogui.press("enter")
    time.sleep(2)

    # Focus calculator
    try:
        win = gw.getWindowsWithTitle("Calculator")[0]
        win.activate()
    except Exception:
        pass
    time.sleep(0.5)

    # Type the expression (pyautogui uses * / + - symbols directly)
    pyautogui.write(expression)
    pyautogui.press("enter")
    time.sleep(0.8)

    # Copy the result from the calculator display
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.3)
    result = pyperclip.paste().strip()

    return f"Entered {expression} into Windows Calculator. Displayed result: {result}"

tools = [open_calculator]
tools_map = {t.name: t for t in tools}

# Register tool with LLM
llm_with_tools = llm.bind_tools(tools)

# Agent execution loop
SYSTEM = (
    "You are a helpful assistant with access to a calculator tool. "
    "When the user asks for any arithmetic, ALWAYS call the open_calculator tool. "
    "Return a short, direct final answer."
)

def run_agent():
    messages = [SystemMessage(content=SYSTEM)]
    print("Agent ready. Type 'quit' to exit.\n")
    while True:
        user = input("You: ").strip()
        if user.lower() in {"quit", "exit"}:
            break
        messages.append(HumanMessage(content=user))

        # inner loop: keep running tools until model gives final text
        while True:
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            if not response.tool_calls:
                print(f"\nagent: {response.content}\n")
                break

            for tc in response.tool_calls:
                print(f"[TOOL SELECTED] {tc['name']}")
                print(f"[TOOL ARGUMENTS] {tc['args']}")
                result = tools_map[tc["name"]].invoke(tc["args"])
                print(f"[TOOL RESULT] {result}\n")
                messages.append(
                    ToolMessage(content=str(result), tool_call_id=tc["id"])
                )

if __name__ == "__main__":
    run_agent()