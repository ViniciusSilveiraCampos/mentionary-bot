from langgraph.checkpoint.memory import MemorySaver
from uuid import uuid4
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from tools import tools
from langgraph.graph import StateGraph, END, START
import schemas
from langchain_core.messages import ToolMessage
import json

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=4 * 1024,
    timeout=None,
    max_retries=2,
)


checkpointer = MemorySaver()

config: RunnableConfig = {
    "configurable": {
        "thread_id": str(uuid4()),
    },
    "recursion_limit": 100,
}

prompt = """
You're Mentionary, an AI on the Discord platform, created to help, play games, and answer questions from server members. You tend to send emojis, be charismatic, and talk a lot."""

tools_by_name = {tool.name: tool for tool in tools}


def tool_node(state: schemas.AgentState):
    outputs = []
    for tool_call in state["messages"][-1].tool_calls:
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        outputs.append(
            ToolMessage(
                content=json.dumps(tool_result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}


def should_continue(state: schemas.AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


agent_graph = create_react_agent(
    llm,
    tools=tools,
    checkpointer=checkpointer,
    prompt=prompt,
)

workflow = StateGraph(schemas.AgentState)
workflow.add_node("agent", agent_graph)
workflow.add_node("tool", tool_node)

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tool",
        "end": END,
    },
)

workflow.add_edge(START, "agent")
workflow.add_edge("tool", "agent")
graph = workflow.compile(checkpointer=checkpointer)

ids = set()
