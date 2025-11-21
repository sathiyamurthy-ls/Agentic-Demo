import os
import json
import requests
from typing import TypedDict, Annotated, List
from flask import Flask, request, jsonify, render_template
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

# --- CONFIGURATION ---
# IMPORTANT: Replace this with your actual Gemini API Key
# You mentioned you would key this in yourself.
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" # Replace with your Gemini API Key
GEMINI_MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"

# --- 1. AGENT STATE (MEMORY) ---
class TriageState(TypedDict):
    """Represents the state of the Triage agent."""
    ticket_content: str
    classification: dict
    action_taken: str
    severity: str # For easy access in routing/output

# --- 2. Pydantic Schema for Structured Output ---
# This schema dictates the required output format for the LLM.
class TriageClassification(BaseModel):
    """Structured classification output for the Triage Agent."""
    Severity: str = Field(description="The urgency: 'High', 'Medium', or 'Low'.")
    Department: str = Field(description="The responsible team: 'Sales', 'Tech Support', 'Billing', or 'HR'.")
    Action_Required: str = Field(description="The primary action: 'Follow-up', 'Documentation_Update', 'Pass_to_RPA'.")

# --- 3. CORE FUNCTIONS (NODES) ---

# Helper function to call the Gemini API for structured output
def gemini_call_structured(contents, schema):
    """Generic function to call the Gemini API with structured JSON output enforcement."""
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        return {"Error": "Gemini API Key not set in app.py. Please replace 'YOUR_GEMINI_API_KEY'."}

    system_prompt = (
        "You are an expert Triage Agent. Analyze the user's support ticket (provided as contents) "
        "and output a single JSON object strictly matching the provided schema. "
        "IMPORTANT RULE: The 'Department' MUST be chosen from the user's input text, based on the context of the provided. For example, if the user input is 'The ERP application in the finance department is not working', the Department MUST be 'Finance'. Look for the keywords in the user text and do not hallucinate or guess the Department. "
        "Rule: If the Severity is 'High', the Action_Required MUST be 'Pass_to_RPA'."
    )
    
    payload = {
        "contents": [{"parts": [{"text": contents}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema.model_json_schema(),
        }
    }
        
    try:
        response = requests.post(
            GEMINI_MODEL_URL, 
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        response.raise_for_status()
        
        result_json = response.json()
        
        # Extract the JSON string from the response
        json_text = result_json['candidates'][0]['content']['parts'][0]['text']
        
        # Parse and return the classification dictionary
        classification = json.loads(json_text)
        return classification
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        print(f"API Call or Parsing Error: {e}")
        return {"Error": f"API Call or Parsing failed: {e}"}

# Node 1: Classify Ticket
def classify_ticket(state: TriageState):
    """LangGraph Node: Calls Gemini to classify the ticket content into structured data."""
    
    classification_result = gemini_call_structured(
        state["ticket_content"], 
        TriageClassification
    )
    
    if "Error" in classification_result:
        state["action_taken"] = classification_result["Error"]
        state["severity"] = "Error"
        return state

    # Update state with classification details
    state["classification"] = classification_result
    state["severity"] = classification_result.get("Severity", "Unknown").upper()
    
    return state

# Node 2a: Log Ticket (Low/Medium Action)
def log_ticket(state: TriageState):
    """LangGraph Node: Mocks standard logging action (e.g., Google Sheet, Salesforce)."""
    details = state["classification"]
    state["action_taken"] = (
        f"Ticket logged to Google Sheets for {details['Department']} team. "
        f"Severity: {details['Severity']}. Action: {details['Action_Required']}"
    )
    return state

# Node 2b: Notify RPA (High Action)
def notify_rpa(state: TriageState):
    """LangGraph Node: Mocks high-priority escalation (e.g., RPA Queue, PagerDuty)."""
    details = state["classification"]
    state["action_taken"] = (
        f"🔥 CRITICAL TICKET ESCALATED! Triggering RPA bot for Department: {details['Department']}. "
        f"Severity: {details['Severity']}. Action: {details['Action_Required']}"
    )
    return state

# --- 4. GRAPH DEFINITION ---

# Define a function that determines the next step (Router)
def route_step(state: TriageState):
    """Router: Decides whether to log (Low/Medium) or escalate (High) based on severity."""
    # Check for 'HIGH' severity (case-insensitive, as per logic)
    if state["severity"] == "HIGH":
        return "notify_rpa"
    # Treat Medium, Low, Unknown, or Error as standard logging/default path
    return "log_ticket"

# Build the graph
builder = StateGraph(TriageState)
builder.add_node("classify", classify_ticket)
builder.add_node("log_ticket", log_ticket)
builder.add_node("notify_rpa", notify_rpa)

builder.set_entry_point("classify")

# Add conditional routing after classification
builder.add_conditional_edges(
    "classify",
    route_step,
    {"log_ticket": "log_ticket", "notify_rpa": "notify_rpa"}
)

# End the graph after the action is taken
builder.add_edge("log_ticket", END)
builder.add_edge("notify_rpa", END)

# Compile the graph
agent_graph = builder.compile()

# --- 5. FLASK APP SETUP ---
app = Flask(__name__)

@app.route('/')
def home():
    """Serves the frontend HTML file."""
    return render_template('index.html') 

@app.route('/invoke', methods=['POST'])
def invoke_agent():
    """API endpoint to run the LangGraph agent."""
    try:
        data = request.get_json()
        ticket_content = data.get('query', 'Default test ticket: My monitor is flickering.')
        
        # Initial state
        initial_state = {"ticket_content": ticket_content, "classification": {}, "action_taken": "", "severity": ""}
        
        # Run the agent graph
        final_state = agent_graph.invoke(initial_state)
        
        # Prepare response for UI
        response_data = {
            "final_result": final_state['action_taken'],
            "severity": final_state['severity'],
            "classification_details": final_state.get('classification', {})
        }

        return jsonify(response_data)
        
    except Exception as e:
        print(f"Flask Error: {e}")
        return jsonify({"final_result": f"Internal Server Error: {e}", "severity": "Error", "message": "Check server logs for details."}), 500

if __name__ == '__main__':
    # Run server on localhost:5000
    app.run(debug=True, host='127.0.0.1', port=5000)