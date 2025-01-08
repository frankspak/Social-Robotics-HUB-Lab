from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
from tinyllama.client import TinyLlamaClient
from oaichat.oaiclient import OaiClient
import socket
from optparse import OptionParser

PEPPER_IP = "192.168.1.140"
PORT = 9559

global status_of_checkmark
status_of_checkmark = False
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
    with open("dialoguepage.html", "r+") as f:
        html = f.read()
    text_to_add = ""
    for message in texts:
        message_class = "sent" if message["sender"] == "sent" else "received"
        text_to_add += "<div class=\"message " + message_class + """\">
            <span class="message-text">""" + message['message'] + """</span>
        </div>"""
    html = html.replace("PLACE_TEXT_HERE", text_to_add)
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
    with open("homepage.html", "r+") as f:
        html = f.read()
    html = html.replace("IP_ADDRESS_HERE", ip_address_host)
    return render_template_string(html)

@app.route("/send-input", methods= ["POST"])
def send_input():
    with open("conversation.json", "r+") as f:
        texts = json.load(f)
    data = request.get_json()
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


@app.route("/getcheckmarkstatus")
def status():
    return jsonify({"status":status_of_checkmark})

@app.route("/setcheckmarkstatus", methods= ["POST"])
def set_status():
    data = request.get_json()
    status = data.get("status")
    print(status)
    global status_of_checkmark
    status_of_checkmark = status
    
    return jsonify({"status":status_of_checkmark})


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
