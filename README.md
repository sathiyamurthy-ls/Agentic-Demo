# Agentic-Demo
🧠 Smart Ticket Triage Agent Demo (Flask + LangGraph + Gemini)
This project demonstrates an Agentic AI workflow using Python's Flask and LangGraph frameworks. The agent autonomously classifies incoming support requests (Severity, Department, Action Required) using the Gemini API and routes them to a simulated action (either Standard Logging or Critical RPA Escalation).
The classification is heavily grounded to ensure departments are chosen only from a predefined list, eliminating LLM hallucination in this critical decision point.
Prerequisites
Python 3.8+ installed on your system.
A text editor or IDE (VS Code is recommended).
1. Project Setup
Step 1: Clone or Download Files
Ensure you have the following two files saved in the same directory:
app.py (The Python Backend / LangGraph Agent)
index.html (The HTML/JavaScript Frontend)
Step 2: Create a Virtual Environment (Recommended)
Using a virtual environment prevents dependency conflicts with other Python projects.
# Create the environment
python -m venv venv

# Activate the environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate


Step 3: Install Python Dependencies
Install all necessary libraries using pip:
pip install Flask langgraph pydantic requests


2. Gemini API Key Configuration
To allow the Python agent to use the Gemini model for classification, you must obtain an API key and update the app.py file.
Step 2.1: Get Your API Key
Go to the [Google AI Studio] or [Google AI Developer Website] to generate your key.
Copy the generated key (it will look like a long alphanumeric string starting with AIza...).
Step 2.2: Update app.py
Open the app.py file.
Locate the following line near the top:
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"


Replace "YOUR_GEMINI_API_KEY" with the key you copied in Step 2.1:
# Example (DO NOT USE THIS KEY)
GEMINI_API_KEY = "AIzaSy...[Your Actual Key Here]...gY7w"


3. Running the Application (Using VS Code)
VS Code provides a smooth way to manage and run Python projects.
Step 3.1: Open the Project in VS Code
Open VS Code.
Go to File > Open Folder... and select the folder containing app.py and index.html.
Step 3.2: Select the Python Interpreter
In the bottom right corner of the VS Code window, you might see the Python version displayed (e.g., Python 3.11.x). Click this.
Select the virtual environment you created in Step 1 (./venv/bin/python). This ensures the correct libraries are used.
Step 3.3: Run the Flask Server
Open the integrated terminal in VS Code (Terminal > New Terminal or shortcut Ctrl + \ or Cmd + \).
Ensure your virtual environment is active (you should see (venv) at the beginning of the prompt).
Execute the application file:
python app.py


The server will start and output a line similar to:
 * Running on [http://127.0.0.1:5000](http://127.0.0.1:5000) (Press CTRL+C to quit)


Step 3.4: Access the Frontend
Open your web browser.
Navigate to the address: http://127.0.0.1:5000
You can now use the chat box to test the Triage Agent logic!
Testing the Agent Logic
Use the following inputs to test the agent's ability to classify and route the ticket correctly:

"Our ERP application is broken in the finance department. We are losing transactions, please check immediately."

"I have joined the sales department and need to request a new laptop for working."

"I'm having trouble logging into my system. It's not urgent, but I can't work without it."

"Can someone from HR confirm my vacation days balance for next month?"




