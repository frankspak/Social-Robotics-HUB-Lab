# -*- coding: utf-8 -*-

"""Zmq server interface for the OpenAI chatbot"""

import zmq, os
import datetime
from threading import Thread
from oaichat.openaichat import OaiChat
import json

class OaiServer(OaiChat):

    def __init__(self, user, prompt=None):
        super().__init__(user, prompt)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind('tcp://*:'+os.getenv('CHATBOT_SERVER_ADDRESS').split(':')[-1])
        self.thread = None

    def start(self):
        self.thread = Thread(target=self._run)
        self.thread.start()

    def _run(self): 
        print('Starting OpenAI chat server...')
        while self.thread:
            response = {}
            i = self.listen()
            print('Input received:', i)
            if 'handshake' in i: 
                print('New client connected:', i['handshake'])
                response['handshake'] = 'ok'
            if 'reset' in i and i['reset']:
                print('Resetting history.')
                self.reset(i['user'])
                response['reset']='ok'
            if 'history' in i:
                print('Extending history:')
                for row in i['history']: 
                    print('\t'+row.strip())
                    self.history.append(row.strip())
                response['history']='ok'
            if 'input' in i:
                r = self.respond(i['input'])
                response.update(r)
            response['time'] = datetime.datetime.now().isoformat()
            print('Sending response:', response)        
            self.send(response)

    def respond(self, input_text):
        """Custom respond method to enforce the desired output format."""
        print(f"Processing input: {input_text}")

        # Custom prompt to ensure 4-5 sentences ending with a question
        guidance = (
            "Provide a response in a maximum of 4-5 complete sentences."
            "to invite further engagement, such as 'Would you like to know more about this topic?' or 'What would you like to know more?'."
        )

        # Combine guidance with user input
        prompt = f"{guidance}\nUser: {input_text}"

        # Pass the custom prompt to the parent respond method
        self.history.append({'role': 'user', 'content': prompt})

        response = self.client.chat.completions.create(
            model="gpt-4",  # Specify the model
            messages=self.history,
            max_tokens=200,
            temperature=0.4,
        )

        # Extract the generated response content
        content = response.choices[0].message.content
        print(f"Generated response: {content}")

         # Append the assistant's response to history
        self.history.append({'role': 'assistant', 'content': content})

        # Save the conversation to a JSON file
        conversation = {
            "input": input_text,
            "response": content,
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open("conversation.json", "a") as json_file:
            json.dump(conversation, json_file)
            json_file.write("\n")  # Write each conversation on a new line

        # Return the response content
        return {'choices': [{'message': {'content': content}}]}

    def stop(self):
        self.socket.close()
        self.thread = None
        #self.log.close()

    def listen(self):
        #  Wait for next request from client
        return self.socket.recv_json()

    def send(self, s):
        return self.socket.send_json(s)

def main():
    server = OaiServer(user="DefaultUser")
    server.start()
    try: 
        while True:
            i = input('Enter q to quit. > ')
            if i == 'q': break
    finally:
        server.stop()
