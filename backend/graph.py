from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from llm import llm

# ____________________________________
# Graph State
class CookingState(TypedDict):
    user_input: str
    classification: Optional[str]
    recipe: Optional[str]
    cookware_needed: Optional[List[str]]
    cookware_missing: Optional[List[str]]
    final_answer: Optional[str]
    debug: List[str]

# ____________________________________
# Nodes
def classify_query(state: CookingState) -> CookingState:
    user_input = state['user_input']

    # Add a basic but strict prompt
    prompt = f"""
    You are a classifier.

    Determine whether the following query is related to cooking or recipes.

    Respond with only one word:
    - cooking
    - non-cooking

    Query: {user_input}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    response = response.content.strip().lower()

    # Check if response starts with "cooking" or equals "cooking"
    if response.startswith("cooking") or response == "cooking":
        classification = "cooking"
    elif response.startswith("non-cooking") or response == "non-cooking":
        classification = "non-cooking"
    else:
        # Default to non-cooking if unclear
        classification = "non-cooking"

    # Update state and classification
    state["classification"] = classification
    state["debug"].append(f"LLM classified as: {classification}")
    return state

def generate_recipe(state: CookingState) -> CookingState:
    user_input = state["user_input"]

    prompt = f"""
    You are a cooking assistant.

    The user asked: {user_input}

    Generate a detailed recipe.

    At the end, return a JSON block like this:

    {{
      "cookware_needed": ["item1", "item2"]
    }}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content

    state["recipe"] = content
    state["debug"].append("Generated recipe")
    return state

def finalize(state: CookingState) -> CookingState:
    if state["classification"] == "non-cooking":
        state["final_answer"] = "Sorry, I can only help with cooking-related questions."
    else:
        state["final_answer"] = state.get("recipe", "Here is your recipe.")

    state["debug"].append("Finalized response")
    return state


# ____________________________________
# Build Graph

# Routing
def route_after_classify(state: CookingState):
    if state["classification"] == "cooking":
        return "generate"
    return "finalize"

def build_graph():
    graph = StateGraph(CookingState)

    graph.add_node("classify", classify_query)
    graph.add_node("generate", generate_recipe)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("classify")
    
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "generate": "generate",
            "finalize": "finalize"
        }
    )

    graph.add_edge("generate", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


graph = build_graph()
