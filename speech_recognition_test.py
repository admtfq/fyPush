import speech_recognition as sr
import pyttsx3
import logging

# Initialize the recognizer and pyttsx3 engine
r = sr.Recognizer()
engine = pyttsx3.init()

# Set up logging
logging.basicConfig(filename="recognition.log", level=logging.DEBUG)

def record_text():
    attempts = 0
    max_attempts = 3  # Retry up to 3 times if recognition fails
    while attempts < max_attempts:
        try:
            with sr.Microphone() as source2:
                # Provide audio feedback to the user
                engine.say("Adjusting for ambient noise, please wait.")
                engine.runAndWait()

                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source2, duration=1)
                logging.debug("Adjusted for ambient noise")
                print("Listening...")

                # Listen to the user input with timeout and phrase time limit
                audio2 = r.listen(source2, timeout=10, phrase_time_limit=5)

                # Recognize speech using Google's recognizer
                MyText = r.recognize_google(audio2).lower()  # Convert text to lowercase
                logging.debug(f"Recognized text: {MyText}")
                return MyText

        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
            logging.warning("Timeout while waiting for speech.")
            return None

        except sr.RequestError as e:
            print(f"Could not request results from the API; {e}")
            logging.error(f"API Request error: {e}")
            return None

        except sr.UnknownValueError:
            print("Sorry, I did not catch that. Please repeat.")
            logging.warning("Failed to recognize speech.")
            attempts += 1  # Increment the attempts count

    return None  # Return None if all attempts fail

def output_text(text):
    # Check if text is not None before writing to file
    if text:
        with open("output.txt", "a") as f:
            f.write(text)
            f.write("\n")
        
        # Provide audio feedback by speaking the recognized text
        engine.say(f"You said: {text}")
        engine.runAndWait()

# Set a custom energy threshold if needed (optional)
# Lower values make the recognizer more sensitive to softer sounds
r.energy_threshold = 4000  # Adjust this value based on your environment

# Main loop
while True:
    text = record_text()  # Capture and recognize the speech
    if text:  # Only proceed if some text was successfully recognized
        if "exit" in text or "stop" in text:  # Check if the user said "exit" or "stop"
            print("Exiting the system...")
            engine.say("Exiting the system. Goodbye!")
            engine.runAndWait()
            break  # Break out of the loop to stop the system
        output_text(text)
        print(f"Wrote and spoke text: {text}")
