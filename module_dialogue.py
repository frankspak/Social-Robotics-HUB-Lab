
# -*- coding: utf-8 -*-

ROBOT_PORT = 9559 # Robot
ROBOT_IP = "192.168.1.140" # Pepper default

#ltfc3fdb42c2a6.local
#192.168.1.140
AUTODEC = True
#
from optparse import OptionParser
import re
import naoqi
import time
import sys
import codecs
from naoqi import ALProxy
import json
import socket

from tinyllama.client import TinyLlamaClient

from oaichat.oaiclient import OaiClient

hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
ip_address_host = socket.gethostbyname(hostname)
class DialogueSpeechReceiverModule(naoqi.ALModule):
    """
    Use this object to get call back from the ALMemory of the naoqi world.
    Your callback needs to be a method with two parameter (variable name, value).
    """

    def __init__(self, strModuleName, strNaoIp):
        self.autodec = AUTODEC
        self.misunderstandings = 0
        self.log = codecs.open('dialogue.log', 'a', encoding='utf-8')
        try:
            naoqi.ALModule.__init__(self, strModuleName)
            self.BIND_PYTHON(self.getName(), "callback")
            self.strNaoIp = strNaoIp
            # self.session = qi.Session()
        except BaseException, err:
            print("ERR: ReceiverModule: loading error: %s" % str(err))

        

    def __del__(self):
        print("INF: ReceiverModule.__del__: cleaning everything")
        self.stop()

    def start(self):
        self.memory = naoqi.ALProxy("ALMemory", self.strNaoIp, ROBOT_PORT)
        self.memory.subscribeToEvent("SpeechRecognition", self.getName(), "processRemote")
        print("INF: ReceiverModule: started!")
        try:
            self.posture = ALProxy("ALRobotPosture", self.strNaoIp, ROBOT_PORT)
            self.aup = ALProxy("ALAnimatedSpeech", self.strNaoIp, ROBOT_PORT)
            self.tablet_service = ALProxy("ALTabletService", self.strNaoIp, ROBOT_PORT)
            print(self.tablet_service.showWebview("http://{}:5000/homepage".format(ip_address_host)))
            
        except RuntimeError:
            print("Can't connect to Naoqi at ip \"" + self.strNaoIp + "\" on port " + str(ROBOT_PORT) + ".\n"
                                                                                                        "Please check your script arguments. Run with -h option for help.")
    
    def stop(self):
        print("INF: ReceiverModule: stopping...")
        self.memory.unsubscribe(self.getName())
        print("INF: ReceiverModule: stopped!")

    def version(self):
        return "2.0"

    def encode(self, s):
        s = s.replace(u'å', 'a').replace(u'ä', 'a').replace(u'ö', 'o')
        s = s.replace(u'Skovde', 'Schoe the')
        return codecs.encode(s, 'ascii', 'ignore')

    def processRemote(self, signalName, message):
        self.log.write('INP: ' + message + '\n')
        if message == 'error':
            print('Input not recognized, continue listen')
            return
        if self.autodec:
            # always disable to not detect its own speech
            SpeechRecognition.disableAutoDetection()
            # and stop if it was already recording another time
            SpeechRecognition.pause()
        # received speech recognition result
        print("INPUT RECOGNIZED: \n" + message)
        # computing answer
        if message == 'error':
            self.misunderstandings += 1
            if self.misunderstandings == 1:
                answer = "I didn't understand, can you repeat?"
            elif self.misunderstandings == 2:
                answer = "Sorry I didn't get it, can you say it one more time?"
            elif self.misunderstandings == 3:
                answer = "Today I'm having troubles uderstanding what you are saying, I'm sorry"
            else:
                answer = "Please repeat that."
            print('ERROR, DEFAULT ANSWER:\n' + answer)
        elif message == "scherm aan":
            self.aup.say("Oké, scherm aan!")
            self.tablet_service.showWebview("http://{}:5000".format(ip_address_host))
            if self.autodec:
                print("starting service speech-rec again")
                SpeechRecognition.start()
                print("autodec enabled")
                SpeechRecognition.enableAutoDetection()
            else:
                # asking the Speech Recognition to LISTEN AGAIN
                SpeechRecognition.startRecording()
            return
        else:
            self.misunderstandings = 0
            self.create_json(message, "sent")
            self.tablet_service.showWebview("http://{}:5000".format(ip_address_host))
            answer = self.encode(chatbot.respond(message))
            print('DATA RECEIVED AS ANSWER:\n' + answer)
        # text to speech the answer
        
        
        self.log.write('ANS: ' + answer + '\n')
        self.create_json(answer, "received")
        self.tablet_service.showWebview("http://{}:5000".format(ip_address_host))
        self.aup.say(answer)
        self.react(answer)
        # time.sleep(2)
        if self.autodec:
            print("starting service speech-rec again")
            SpeechRecognition.start()
            print("autodec enabled")
            SpeechRecognition.enableAutoDetection()
        else:
            # asking the Speech Recognition to LISTEN AGAIN
            SpeechRecognition.startRecording()

    def react(self, s):
        if re.match(".*I.*sit down.*", s):  # Sitting down
            self.posture.goToPosture("Sit", 1.0)
        elif re.match(".*I.*stand up.*", s):  # Standing up
            self.posture.goToPosture("Stand", 1.0)
        elif re.match(".*I.*(lie|lyi).*down.*", s):  # Lying down
            self.posture.goToPosture("LyingBack", 1.0)
   
    def create_json(self,message, role):
        with open("conversation.json","r") as f:
            current_messages = json.load(f)
        current_messages.append({
            "message":message,
            "sender": role
        })

        with open("conversation.json","w") as f:
            json.dump(current_messages, f)

    
def main():
    """ Main entry point

    """
    """ Main entry point """
    global chatbot
    parser = OptionParser()
    parser.add_option("--pip",
                  help="Parent broker port. The IP address or your robot",
                  dest="pip")
    parser.add_option("--pport",
                  help="Parent broker port. The port NAOqi is listening to",
                  dest="pport",
                  type="int")
    parser.add_option("--server",
                  help="Server to use (tinyllama or openai).",
                  dest="server")
    parser.add_option("--userid",
                  help="participant id to use for llm.",
                  dest="userid")
    parser.set_defaults(
        pip=ROBOT_IP,
        pport=ROBOT_PORT,
        server="openai",
        userid='2001'
    )

    (opts, args_) = parser.parse_args()
    pip = opts.pip
    pport = opts.pport
    server = opts.server
    participantId = opts.userid  # Ensure participant ID is asked before initializing chatbot
    global chatbot
    # Initialize the appropriate chatbot based on the server command line argument
    if server.lower() == "tinyllama":
        chatbot = TinyLlamaClient(user=participantId)
    elif server.lower() == "openai":
        chatbot = OaiClient(user=participantId)
    else:
        print("Unknown server specified. Please use 'tinyllama' or 'openai'.")
        sys.exit(1)

    chatbot.reset()



# We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = naoqi.ALBroker("myBroker",
                              "0.0.0.0",  # listen to anyone
                              0,  # find a free port and use it
                              pip,  # parent broker IP
                              pport)  # parent broker port

    try:
        p = ALProxy("DialogueSpeechReceiver")
        p.exit()  # kill previous instance
    except:
        pass

    # AutonomousLife = ALProxy('ALAutonomousLife')
    # AutonomousLife.setState('solitary')

    # Reinstantiate module

    # Warning: ReceiverModule must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global DialogueSpeechReceiver
    DialogueSpeechReceiver = DialogueSpeechReceiverModule("DialogueSpeechReceiver", pip)
    DialogueSpeechReceiver.start()

    global SpeechRecognition
    SpeechRecognition = ALProxy("SpeechRecognition")
    SpeechRecognition.start()
    # SpeechRecognition.calibrate()

    if (AUTODEC == False):
        print("False, auto-detection not available")
        # one-shot recording for at least 5 seconds
        SpeechRecognition = ALProxy("SpeechRecognition")
        SpeechRecognition.start()
        SpeechRecognition.setHoldTime(5)
        SpeechRecognition.setIdleReleaseTime(1.7)
        SpeechRecognition.setMaxRecordingDuration(10)
        SpeechRecognition.startRecording()

    else:
        print("True, auto-detection selected")
        # auto-detection
        SpeechRecognition = ALProxy("SpeechRecognition")
        SpeechRecognition.start()
        SpeechRecognition.setHoldTime(2.5)
        SpeechRecognition.setIdleReleaseTime(1.0)
        SpeechRecognition.setMaxRecordingDuration(10)
        SpeechRecognition.setLookaheadDuration(0.5)
        # SpeechRecognition.setLanguage("de-de")
        # SpeechRecognition.calibrate()
        SpeechRecognition.setAutoDetectionThreshold(10)
        SpeechRecognition.enableAutoDetection()
        # SpeechRecognition.startRecording()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print
        print("Interrupted by user, shutting down")
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
