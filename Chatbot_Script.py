from flask import Flask, render_template, request, jsonify
import json
from fuzzywuzzy import fuzz
import re

app = Flask(__name__)

def sanitize_input(input_text):
    """Sanitize user input by removing special characters and check if input is valid."""
    sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', input_text)
    return sanitized.strip()

def get_response(user_message):
    user_message = sanitize_input(user_message)  # Sanitize the input
    
    if not user_message:
        return {"response": "Sorry, I can't understand messages with only special characters. Please try again with some text."}, False
    
    with open('intents_trial.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    if not user_message.strip():
        return None

    max_similarity = -1
    best_match = None

    for intent in data['intents']:
        for pair in intent['pairs']:
            pattern = pair['pattern']
            response = pair['response']
            similarity = fuzz.ratio(pattern.lower(), user_message.lower())
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = pair

    if best_match is not None and max_similarity > 50:  # Adjust threshold as needed
        response = str(best_match['response']).strip()
        
        # Check if the response is for a greeting
        if best_match['pattern'].lower() in ["hi", "hello", "hey", "helo", "good day", "is anyone there"]:
            options = [
                "Tell me about micro-credential courses",
                "Courses Offered",
                "Res4City",
                "Res4Chat",
                "Skills Gained",
                "Job Assistance",
                "Enrollment",
                "Contact Us"
            ]
            return {"response": response, "options": options}, False
        else:
            return {"response": response}, False
    else:
        return {"response": "Sorry, I'm not sure about that, but I'm here to help with anything else! For more details please visit our website: <a href='https://www.res4city.eu/'>Res4City</a>."}, False

@app.route('/')
def home():
    return render_template('Chatbot_HTML_Script.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message.strip():
        return jsonify({'error': 'Please enter a message.'}), 400
    
    response_data, is_error = get_response(user_message)
   
    if is_error or user_message.lower() in ["ok", "thanks", "thank you", "thank u", "bye", "bi"]:
        follow_up = "Is there anything else I can help you with?"
        return jsonify({'response': follow_up, 'follow_up': True, 'options': []})  # Empty options to keep the current ones
   
    return jsonify({'response': response_data.get('response'), 'options': response_data.get('options', []), 'follow_up': False})

@app.route('/follow_up', methods=['POST'])
def follow_up():
    user_message = request.json.get('message')
    if not user_message.strip():
        return jsonify({'error': 'Please enter a message.'}), 400

    if user_message.lower() in ["no"]:
        final_message = "Thank you for chatting with us! Have a great day!"
        return jsonify({'response': final_message, 'options': []})  # No options on exit
    elif user_message.lower() == "yes":
        continue_message = "Great! What else can I help you with?"
        return jsonify({'response': continue_message, 'options': []})  # Continue with no new options
   
    response, _ = get_response(user_message)
    return jsonify({'response': response, 'options': []})

if __name__ == '__main__':
    app.run(debug=True)
