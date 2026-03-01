from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from llm import llm
from tools import web_search
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ____________________________________
# Graph State
class CookingState(TypedDict):
    user_input: str
    classification: Optional[str]
    web_search_result: Optional[str]
    recipe: Optional[str]
    cookware_needed: Optional[List[str]]
    cookware_missing: Optional[List[str]]
    final_answer: Optional[str]
    debug: List[str]

# Constant
ALLOWED_COOKWARE = ["Spatula", "Frying Pan", "Little Pot", "Stovetop", "Whisk", "Knife", "Ladle", "Spoon"]

# ____________________________________
# Nodes
def classify_query(state: CookingState) -> CookingState:
    user_input = state['user_input']
    logger.info(f"Classifying query: {user_input}")

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
    logger.info(f"Classification result: {classification}")
    return state

def search_recipe(state: CookingState) -> CookingState:
    """Use web search to find recipe information if needed."""
    user_input = state["user_input"]
    logger.info(f"Searching web for: {user_input}")

    # Let LLM decide if search is needed
    prompt = f"""
    User asked: {user_input}

    Should we search the web for this recipe? Answer only 'yes' or 'no'.
    Answer 'yes' if it's a specific dish or needs current recipe info.
    Answer 'no' if it's a general cooking question.
    """

    decision = llm.invoke([HumanMessage(content=prompt)])
    decision = decision.content.strip().lower()

    if "yes" in decision:
        search_query = f"recipe for {user_input}"
        search_result = web_search(search_query)
        state["web_search_result"] = search_result
        state["debug"].append("Web search performed")
        logger.info("Web search completed")
    else:
        state["web_search_result"] = None
        state["debug"].append("Web search skipped")
        logger.info("Web search skipped")

    return state

def generate_recipe(state: CookingState) -> CookingState:
    user_input = state["user_input"]
    web_result = state.get("web_search_result")
    logger.info("Generating recipe")

    # Include web search results if available
    context = f"\nWeb search results: {web_result}\n" if web_result else ""

    prompt = f"""
    You are a cooking assistant.

    The user asked: {user_input}
    {context}
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
    logger.info("Recipe generated")
    return state

def check_cookware(state: CookingState) -> CookingState:
    logger.info("Checking cookware availability")
    try:
        recipe_data = json.loads(state["recipe"])
        needed = recipe_data.get("cookware_needed", [])
    except:
        needed = []

    missing = [item for item in needed if item not in ALLOWED_COOKWARE]

    state["cookware_needed"] = needed
    state["cookware_missing"] = missing

    if missing:
        state["debug"].append(f"Missing cookware: {missing}")
        logger.warning(f"Missing cookware: {missing}")
    else:
        state["debug"].append("All cookware available")
        logger.info("All required cookware available")
    return state

def finalize(state: CookingState) -> CookingState:
    logger.info("Finalizing response")
    if state["classification"] == "non-cooking":
        state["final_answer"] = "Sorry, I can only help with cooking-related questions."
    else:
        recipe_text = state.get("recipe", "")
        if state.get("cookware_missing"):
            warning = "\nMISSING cookware: " + ", ".join(state["cookware_missing"])
            state["final_answer"] = recipe_text + warning
        else:
            state["final_answer"] = recipe_text

    state["debug"].append("Finalized response")
    logger.info("Response finalized")
    return state


# ____________________________________
# Build Graph

# Routing
def route_after_classify(state: CookingState):
    if state["classification"] == "cooking":
        return "search"
    return "finalize"

def build_graph():
    graph = StateGraph(CookingState)

    graph.add_node("classify", classify_query)
    graph.add_node("search", search_recipe)
    graph.add_node("generate", generate_recipe)
    graph.add_node("check", check_cookware)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "search": "search",
            "finalize": "finalize"
        }
    )

    graph.add_edge("search", "generate")
    graph.add_edge("generate", "check")
    graph.add_edge("check", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


graph = build_graph()
