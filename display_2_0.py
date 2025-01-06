from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
from tinyllama.client import TinyLlamaClient
from oaichat.oaiclient import OaiClient
import socket
from optparse import OptionParser

PEPPER_IP = "192.168.1.140"
PORT = 9559

hostname = socket.gethostname()
ip_address_host = socket.gethostbyname(hostname)
print(ip_address_host)

parser = OptionParser()
parser.add_option("--server",
                  help="Server to use (tinyllama or openai).",
                  dest="server")
parser.add_option("--userid",
                  help="participant id to use for llm.",
                  dest="userid")
parser.set_defaults(
    server='openai',
    userid='2001')

# Create an instance of FastAPI
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)

def create_conversation(texts):
    
    html = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=1280, user-scalable=no" />
            <title>WhatsApp Conversation</title>
            <style>

                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }

                body {
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                    background-color: #01a7c9;
                }

                #title {
                    align-self: center;
                }

                button {
                    background-color: #333333;
                    padding: 0.5vh 0.5vw;
                    margin: 0.5vh 0.5vw;
                    border: none;
                    border-radius: 10%;
                    color: white;
                    font-weight: bold;
                    cursor: pointer;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
                    height: 7vh;
                    width: 8vw;
                }

                button:active {
                    transform: scale(0.95);
                }

                .info-banner {
                    height: 8vh;
                    background-color: #BBBBBB;
                    display: flex;
                    flex-direction: row;
                    width: 100vw;
                }

                .checkbox-label {
                    display: flex;
                    margin: 0.5vh 0.5vw;
                    align-self: center;
                }

                .toggle-container {
                    align-self: center;
                }

                .toggle-switch input {
                    display: none;
                }

                .toggle-switch {
                    position: relative;
                    display: inline-block;
                    width: 50px;
                    height: 25px;
                    
                }

                .toggle-switch .slider {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: #999;
                    transition: 0.4s;
                    border-radius: 25px;
                }

                .toggle-switch .slider:before {
                    position: absolute;
                    content: "";
                    height: 18px;
                    width: 18px;
                    left: 4px;
                    bottom: 3.5px;
                    background-color: white;
                    transition: 0.4s;
                    border-radius: 50%;
                }

                .toggle-switch input:checked + .slider {
                    background-color: #01a7c9;
                }

                .toggle-switch input:checked + .slider:before {
                    transform: translateX(24px);
                }

                .push {
                    margin-left: auto;
                    display: flex;
                    flex-direction: row;
                }

                .chat-window {
                    background-color: #01a7c9;
                    display: flex;
                    flex-direction: column;
                }

                .chat-body {
                    flex: 1;
                    background-color: #01a7c9;
                    display: flex;
                    overflow-y: scroll;
                    flex-direction: column;
                    min-height: 84vh;
                    max-height: 84vh;
                }

                .message {
                    padding: 0.5vh 0.5vw;
                    margin: 0.5vh 0.5vw;
                    border-radius: 1vw;
                    position: relative;
                    display: block;
                    clear: both;
                    max-width: 75%;
                    word-wrap: break-word;
                }

                .message.sent {
                    background-color: #ff3f2c;
                    color: #fff;
                    border-bottom-right-radius: 0;
                    align-self: flex-end;
                }

                .message.received {
                    background-color: #fff;
                    border-bottom-left-radius: 0;
                    align-self: flex-start;
                }

                .message-text {
                    font-size: 3vw;
                }

                .chat-input-container {
                    display: flex;
                    width: 100%;
                    background-color: #c0c0c0;
                    border-top: 1px solid #e0e0e0;
                    height: 8vh;
                }

                .chat-input {
                    border: none;
                    padding: 0.75vh 0.75vw;
                    margin: 0.5vh 0.5vw;
                    border-radius: 20px;
                    background-color: #fff;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    font-size: 16px;
                    resize: none;
                    outline: none;
                    height: 7vh;
                    width: 90vw;
                }

            </style>
        </head>
        <body>

            <div class="chat-window">
                <div class="info-banner">
                    <div id="title">
                        <h1>Pepper robot: De robot assistent van de hublab!</h1>
                    </div>
                    <div class="checkboxes push">
                        <span class="checkbox-label">Lopende tekst</span>
                        <div class="toggle-container">
                            <label class="toggle-switch">
                                <input type="checkbox" id="ongoing-text">
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>
                    <div>
                        <a id="return-button" href="http://IP_ADDRESS_HERE:5000/homepage">
                            <button>Terug</button>
                        </a>
                    </div>
                </div>
                <div class="chat-body">
    """
    for message in texts:
        message_class = "sent" if message["sender"] == "sent" else "received"
        html += "<div class=\"message " + message_class + """\">
            <span class="message-text">""" + message['message'] + """</span>
        </div>"""
    html += """
                </div>
                <div class="chat-input-container" id="bottom">
                    <textarea class="chat-input" placeholder="Typ een vraag" id="inputText"></textarea>
                    <button id="send-button">Verzenden</button>
                </div>
            </div>
        </body>
        <script>
                var textbox = document.querySelector('textarea');
                var infobanner = document.querySelector('.info-banner');
                var lastDiv = document.querySelector('#bottom');
                var chatBody = document.querySelector('.chat-body');
                var sendButton = document.querySelector('#send-button');
                var checkbox = document.querySelector('#ongoing-text')

                chatBody.scrollTop = chatBody.scrollHeight;

                function disableScrolling() {
                    lastDiv.style.height = '66vh';
                    chatBody.style['min-height'] = '26vh';
                    chatBody.style['max-height'] = '26vh';
                    chatBody.scrollTop = chatBody.scrollHeight;
                }

                function enableScrolling() {
                    lastDiv.style.height = '8vh';
                    chatBody.style['min-height'] = '84vh';
                    chatBody.style['max-height'] = '84vh';
                    chatBody.scrollTop = chatBody.scrollHeight;
                }

                sendButton.addEventListener('click', function(event) {
                    sendText();
                    enableScrolling();
                });

                chatBody.addEventListener('click', function(event) {
                    if(chatBody.style['min-height'] === '26vh') {
                        console.log(chatBody.style['min-height']);
                        enableScrolling();
                    }
                });

                infobanner.addEventListener('click', function(event) {
                    if(chatBody.style['min-height'] === '26vh') {
                        enableScrolling();
                    }
                });

                textbox.addEventListener('focus', disableScrolling);

                function sendText() {
                    var textbox = document.getElementById("inputText");
                    var text = textbox.value;
                    if(text === "") {
                        return;
                    }
                    textbox.value = '';
                    var newMessageHTML = `
                        <div class="message sent">
                        <span class="message-text">` + text + `</span>
                    </div>`;

                    chatBody.insertAdjacentHTML('beforeend', newMessageHTML);
                    chatBody.scrollTop = chatBody.scrollHeight;

                    var url = "http://IP_ADDRESS_HERE:5000/send-input";
                    fetch(url, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({ "text_input": text })
                    })
                    .then(function(response) {
                        return response.json();  // Parse the JSON body of the response
                    })
                    .then(function(data) {
                        var answer = data.answer
                        if (checkbox.checked) {
                            var newResponseHTML = `
                                <div class="message received">
                                <span class="message-text"></span>
                            </div>`;

                            chatBody.insertAdjacentHTML('beforeend', newResponseHTML);
                            addTextWithRandomDelay(answer)
                        } else {
                            var newResponseHTML = `
                                <div class="message received">
                                <span class="message-text">${answer}</span>
                            </div>`;
                            chatBody.insertAdjacentHTML('beforeend', newResponseHTML);
                            chatBody.scrollTop = chatBody.scrollHeight;
                        }
                    });
                }

                function addTextWithRandomDelay(text) {
                    var spanElements = document.querySelectorAll('span');
                    var spanElement = spanElements[spanElements.length - 1];

                    var words = text.split("");
                    var index = 0;

                    function addWord() {
                        if (index < words.length) {
                            spanElement.textContent += words[index];
                            chatBody.scrollTop = chatBody.scrollHeight;
                            index += 1;

                            // Schedule the next word to be added after a random delay
                            var delay = Math.floor(Math.random() * 5) + 16;
                            setTimeout(addWord, delay);
                        }
                    }

                    addWord(); // Start adding words

                }
            </script>
    </html>
    """
    return html

# Define the route for the home page
@app.route("/")
def home():
    with open("conversation.json", "r+") as f:
        texts = json.load(f)
    html = create_conversation(texts)
    html = html.replace("IP_ADDRESS_HERE", ip_address_host)
    return render_template_string(html)

@app.route("/homepage")
def homepage():
    with open("conversation.json", 'w') as json_file:
        json.dump([], json_file)
    with open("homepage.html", "r+") as f:
        html = f.read()
    html = html.replace("IP_ADDRESS_HERE", ip_address_host)
    return render_template_string(html)

@app.route("/send-input", methods= ["POST"])
def send_input():
    with open("conversation.json", "r+") as f:
        texts = json.load(f)
    data = request.get_json()
    print(data)
    text_input = data.get("text_input")
    print(text_input)

    texts.append({
        "message": text_input,
        "sender": "sent"
    })
    with open("conversation.json", "w+") as f:
        json.dump(texts, f)

    answer = chatbot.respond(text_input)
    texts.append({
        "message":  answer,
        "sender": "received"
    })

    with open("conversation.json", "w+") as f:
        json.dump(texts, f)

    return jsonify({"answer":answer})



if __name__ == "__main__":
    (opts, args_) = parser.parse_args()
    participantId = opts.userid
    if opts.server == 'tinyllama':
        chatbot = TinyLlamaClient(user=participantId)
    elif opts.server == 'openai':
        chatbot = OaiClient(user=participantId)
    else:
        print("incorrect server provided")
        exit()

    app.run(host='0.0.0.0', port=5000, debug=False)
