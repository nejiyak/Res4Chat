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
        
        # Special handling for "Courses Offered" and related options
        elif user_message.lower() == "courses offered":
            courses = [
                "Sustainable Energy Technologies and Strategies in Urban Environment",
                "Decarbonization Strategies and Social Innovation for Cities and Communities",
                "Advanced Design of Sustainable Cities",
                "Business Strategies for a Sustainable Urban Transition",
                "Sustainability by Design: Developing a Resilient Built Environment",
                "Innovation in the Urban Energy Sector: Strategies & Management"
            ]
            return {"response": "Here are the courses offered:", "options": courses}, False
        
        elif any(course.lower() in user_message.lower() for course in ["Sustainable Energy Technologies and Strategies in Urban Environment", "Decarbonization Strategies and Social Innovation for Cities and Communities", "Advanced Design of Sustainable Cities","Business Strategies for a Sustainable Urban Transition", "Sustainability by Design: Developing a Resilient Built Environment", "Innovation in the Urban Energy Sector: Strategies & Management"]):
            course_details = {
                "Sustainable Energy Technologies and Strategies in Urban Environment": "This programme covers renewable energy systems, energy efficiency, and sustainable urban planning. It equips you with the skills needed to design, implement, and manage sustainable energy solutions.",
                "Decarbonization Strategies and Social Innovation for Cities and Communities": "The programme focuses on strategies to reduce carbon emissions and promote social innovation. You will learn about policy development, community engagement, and sustainable urban planning.",
                "Advanced Design of Sustainable Cities": "This programme teaches you how to create urban spaces that are environmentally sustainable and socially inclusive. You'll learn about urban design principles, sustainable architecture, and green infrastructure.",
                "Business Strategies for a Sustainable Urban Transition": "This programme focuses on integrating sustainability into business practices. You will learn about sustainable business models, corporate social responsibility, and green marketing.",
                "Sustainability by Design: Developing a Resilient Built Environment": "The programme focuses on creating buildings and infrastructure that can withstand environmental challenges. You will learn about resilient design principles, sustainable construction practices, and disaster risk reduction.",
                "Innovation in the Urban Energy Sector: Strategies & Management": "The programme teaches you how to develop and manage innovative energy solutions for urban areas. You'll learn about energy management systems, renewable energy integration, and smart grid technologies.",
            }
            course_name = next(course for course in course_details if course.lower() in user_message.lower())
            return {"response": course_details[course_name]}, False
        
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
