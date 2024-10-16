from naoqi import ALProxy
import sys
import time

# Replace with your Pepper robot's IP address
ROBOT_IP = "pepper.local"  # Replace with Pepper's IP address
ROBOT_PORT = 9559  # Default NAOqi port

def display_text_on_tablet():
    try:
        # Create a proxy to ALTabletService
        tablet_service = ALProxy("ALTabletService", ROBOT_IP, ROBOT_PORT)
    except Exception as e:
        print("Could not create proxy to ALTabletService:")
        print(e)
        sys.exit(1)

    try:
        # Hide any previous webview content
        #tablet_service.hideWebview()
        tablet_service.hideWebview()
        # Build the URL to the HTML file
        computer_ip = "145.89.100.131"  # Replace with your computer's IP address
        timestamp = int(time.time())
        url = "http://{}:8000/temp.html?{}".format(computer_ip, timestamp)

        # Load the URL on the tablet
        tablet_service.loadUrl(url)

        # Display the webview
        tablet_service.showWebview()

        print("Text displayed on Pepper's tablet.")
    except Exception as e:
        print("An error occurred while displaying text on the tablet:")
        print(e)

if __name__ == "__main__":
    display_text_on_tablet()
