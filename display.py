from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json

# Create an instance of FastAPI
app = FastAPI()

def create_conversation(texts):
    html = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=1280, user-scalable=no" />
            <title>WhatsApp Conversation</title>
            <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #ece5dd;
            margin: 0;
            padding: 0;
        }

        .chat-window {
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
            background-color: #fff;
            display: flex;
            flex-direction: column;
        }

        .chat-body {
            flex: 1;
            padding: 15px;
            background-color: #e5ddd5;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            
        }

        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 10px;
            position: relative;
            display: block;
            clear: both; /* Ensures no overlapping */
            max-width: 75%;
            word-wrap: break-word; /* Prevents long words from overflowing */
        }

        .message.received {
            background-color: #fff;
            border: 1px solid #ddd;
            border-bottom-left-radius: 0;
            align-self: flex-start;
        }

        .message.sent {
            background-color: #DCF8C6;
            border-bottom-right-radius: 0;
            align-self: flex-end;
        }

        .message-text {
            font-size: 3vw;
        }
        </style>
        </head>
        <body>
            <div class="chat-window">

                <div class="chat-body">
    '''
    
    for message in texts:
        message_class = "sent" if message["sender"] == "sent" else "received"
        html += f'''
        <div class="message {message_class}">
            <span class="message-text">{message['message']}</span>
        </div>
        '''
    html += '''
                </div>
            </div>
        </body>
    </html>
    '''

    return html

# Define the route for the home page
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("conversation.json", "r+") as f:
        texts = json.load(f)
    html_content = create_conversation(texts)
    return HTMLResponse(content=html_content)



# Run the app (when using uvicorn)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
