from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json

app = FastAPI()

# Allow CORS for all origins (use cautiously)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML content for the web interface
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dialogue Interface with Pepper</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #ececec;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        #messages {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 20px;
        }
        .message {
            font-size: 1.5em;
            margin: 10px 0;
        }
        .user {
            font-weight: bold;
            color: red;
        }
        .bot {
            font-weight: bold;
            color: black;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Dialogue with Pepper</h2>
        <div id="messages"></div>
        <form id="chat-form">
            <input type="text" id="user-input" name="user_input" placeholder="Say something..." required>
            <button type="submit">Send</button>
        </form>
    </div>
    <script>
        const form = document.getElementById("chat-form");
        const messages = document.getElementById("messages");

        form.onsubmit = async function (event) {
            event.preventDefault();

            const userInputElement = document.getElementById("user-input");
            const userInput = userInputElement.value;

            messages.innerHTML += `<div class="message user">User: ${userInput}</div>`;

            // Clear input field immediately after sending
            userInputElement.value = "";

            // Send the user input to the backend
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `user_input=${encodeURIComponent(userInput)}`,
            });

            const data = await response.json();
            messages.innerHTML += `<div class="message bot">Pepper: ${data.response}</div>`;
            messages.scrollTop = messages.scrollHeight;
        };
    </script>
</body>
</html>
'''

# Route to serve the HTML interface
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=html_content)

# Endpoint to handle chat messages
@app.post("/chat")
async def chat(user_input: str = Form(...)):
    # Send user input to the local Ollama server and retrieve response
    ollama_server_url = "http://localhost:11434/api/chat"
    payload = {
        "model": "pepper_hublab_llama3:8b",  # Replace with the appropriate model name
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }
    try:
        response = requests.post(ollama_server_url, json=payload, stream=True)
        response.raise_for_status()  # Check if the request was successful

        # Accumulate all parts of the response
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    line_data = json.loads(line)
                    if "message" in line_data:
                        full_response += line_data["message"].get("content", "")
                except json.JSONDecodeError:
                    continue

        # If we have an empty response, return an error message
        if not full_response:
            full_response = "An error occurred: Unable to parse response."

    except requests.exceptions.RequestException as e:
        full_response = f"An error occurred: {e}"

    return {"response": full_response}

# Run the app using: uvicorn app:app --reload
