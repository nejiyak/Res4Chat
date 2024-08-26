from flask import Flask, render_template, request, jsonify
import json
from fuzzywuzzy import fuzz
import re

app = Flask(__name__)

# Dictionary to keep track of user state
user_states = {}

def sanitize_input(input_text):
    """Sanitize user input by removing special characters and check if input is valid."""
    sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', input_text)
    return sanitized.strip()

def get_response(user_message, user_id):
    user_message = sanitize_input(user_message)  # Sanitize the input

    if not user_message:
        return {"response": "Sorry, I can't understand messages with only special characters. Please try again with some text."}, False

    # Initialize user state if not already present
    if user_id not in user_states:
        user_states[user_id] = {"selected_course": None, "current_query": None}

    # Define course details
    course_details = {
        "Sustainable Energy Technologies and Strategies in Urban Environment": {
            "Course Content": "The 'Sustainable Energy Technologies and Strategies in Urban Environment' programme covers renewable energy systems, energy efficiency, and sustainable urban planning. It equips you with the skills needed to design, implement, and manage sustainable energy solutions.",
            "Job Opportunities": "Completing this programme can open up career opportunities as a Renewable Energy Engineer, Energy Consultant, or Sustainable Energy Manager.",
            "Skills Acquired": "Learners will gain skills in understanding and implementing various renewable energy sources, such as solar and wind, and learn about energy storage solutions and grid integration for sustainable energy systems.",
            "Course Duration": "The duration of the RES4CITY courses varies depending on the specific microcredential or program you choose. Generally, these courses are designed to be flexible and can range from 15 hrs per week for 5 weeks.", 
            "How to Enroll": "To enroll this course, kindly visit the RES4CITY- <a href='https://res4city.boostmyskills.eu/programs/'>Boost My Skills</a> website and begin your enrollment process."
        },
            "Decarbonization Strategies and Social Innovation for Cities and Communities": {
            "Course Content": "This course focuses on strategies to reduce carbon emissions across various sectors, such as transportation, industry, and urban development. Key topics include carbon capture and storage (CCS), transitioning to low-carbon energy sources, policy development for emission reductions, and innovative technologies for decarbonization. The course also emphasizes the role of public awareness, corporate responsibility, and government regulations in achieving net-zero carbon goals. Students will engage in projects that model emission reduction scenarios and evaluate their effectiveness.",
            "Job Opportunities": "Career opportunities include roles such as Sustainability Coordinator, Environmental Policy Advisor, and Urban Planner.",
            "Skills Acquired": "This course equips students with the ability to develop and implement strategies to reduce carbon emissions, including knowledge of carbon capture technologies and understanding policy frameworks for low-carbon transitions.",
            "Course Duration": "The duration of the RES4CITY courses varies depending on the specific microcredential or program you choose. Generally, these courses are designed to be flexible and can range from 15 hrs per week for 5 weeks.", 
            "How to Enroll": "To enroll this course, kindly visit the RES4CITY- <a href='https://res4city.boostmyskills.eu/programs/'>Boost My Skills</a> website and begin your enrollment process."
        },
        "Advanced Design of Sustainable Cities": {
            "Course Content": "This course explores the principles of sustainable urban planning and design, focusing on creating cities that are environmentally friendly, economically viable, and socially inclusive. Topics include green building practices, sustainable transportation systems, waste management, and urban green spaces. Students will study successful examples of sustainable cities worldwide, learning how to apply these principles to new and existing urban areas. The course includes workshops on using design software and GIS tools to create sustainable city models.",
            "Job Opportunities": "Career opportunities include roles such as Urban Designer, City Planner, and Sustainability Consultant.",
            "Skills Acquired": "Participants will acquire skills in sustainable urban planning, green building design, and managing energy-efficient infrastructure, as well as using tools like GIS for city planning.",
            "Course Duration": "The duration of the RES4CITY courses varies depending on the specific microcredential or program you choose. Generally, these courses are designed to be flexible and can range from 15 hrs per week for 5 weeks.", 
            "How to Enroll": "To enroll this course, kindly visit the RES4CITY- <a href='https://res4city.boostmyskills.eu/programs/'>Boost My Skills</a> website and begin your enrollment process."
        },
        "Business Strategies for a Sustainable Urban Transition": {
            "Course Content": "This course is designed for business professionals and policymakers, covering strategies to integrate sustainability into business practices and urban development. It includes topics such as sustainable business models, corporate social responsibility (CSR), green finance, and stakeholder engagement. The course also covers regulatory frameworks, market-based mechanisms (like carbon trading), and innovation in sustainability. Participants will analyze case studies of businesses and cities that have successfully implemented sustainable practices.",
            "Job Opportunities": "Career opportunities include roles such as Sustainable Business Consultant, Corporate Sustainability Manager, and Green Business Advisor.",
            "Skills Acquired": "This course focuses on optimizing energy use through energy audits, smart grid technologies, and integrating renewable energy sources into existing systems for greater efficiency.",
            "Course Duration": "The duration of the RES4CITY courses varies depending on the specific microcredential or program you choose. Generally, these courses are designed to be flexible and can range from 15 hrs per week for 5 weeks.", 
            "How to Enroll": "To enroll this course, kindly visit the RES4CITY- <a href='https://res4city.boostmyskills.eu/programs/'>Boost My Skills</a> website and begin your enrollment process."
        },
        "Sustainability by Design- Developing a Resilient Built Environment": {
            "Course Content": "Focused on optimizing energy use and integrating renewable energy systems into existing infrastructure, this course covers the latest technologies in energy efficiency and management. It includes modules on energy auditing, smart grid technologies, demand-side management, and energy storage solutions. Students will learn how to design and implement systems that minimize energy loss, improve energy efficiency, and reduce overall energy consumption.",
            "Job Opportunities": "Career opportunities include roles such as Resilient Design Architect, Sustainable Building Consultant, and Disaster Risk Reduction Specialist.",
            "Skills Acquired": "Skills in resilient design, sustainable construction, and disaster risk reduction.",
            "Course Duration": "The duration of the RES4CITY courses varies depending on the specific microcredential or program you choose. Generally, these courses are designed to be flexible and can range from 15 hrs per week for 5 weeks.", 
            "How to Enroll": "To enroll this course, kindly visit the RES4CITY- <a href='https://res4city.boostmyskills.eu/programs/'>Boost My Skills</a> website and begin your enrollment process."
        },
        "Innovation in the Urban Energy Sector- Strategies And Management": {
            "Course Content": "This course focuses on innovative strategies and management techniques that can be applied to the urban energy sector to enhance sustainability and efficiency. Key topics include the integration of renewable energy sources into urban environments, smart grid technologies, and the development of energy-efficient buildings. The course covers emerging technologies such as energy storage solutions, electric vehicle (EV) infrastructure, and urban microgrids. ",
            "Job Opportunities": "Career opportunities include roles such as Energy Innovation Manager, Urban Energy Planner, and Renewable Energy Project Leader.",
            "Skills Acquired": "Learners will gain skills in integrating renewable energy into urban settings, developing smart grid and microgrid solutions, and managing urban energy projects while promoting stakeholder engagement and policy development.",
            "Course Duration": "The duration of the RES4CITY courses varies depending on the specific microcredential or program you choose. Generally, these courses are designed to be flexible and can range from 15 hrs per week for 5 weeks.", 
            "How to Enroll": "To enroll this course, kindly visit the RES4CITY- <a href='https://res4city.boostmyskills.eu/programs/'>Boost My Skills</a> website and begin your enrollment process."
        }
    }

    # Handle special options for sub-options
    sub_options = ["Course Content", "Job Opportunities", "Skills Acquired", "Course Duration", "How to Enroll"]
    
    # Check if the user's message matches any of the sub-options
    if user_message.lower() in [opt.lower() for opt in sub_options]:
        if user_states[user_id]["selected_course"]:
            course_name = user_states[user_id]["selected_course"]
            course_option = next(opt for opt in sub_options if opt.lower() == user_message.lower())
            
            if course_name in course_details and course_option in course_details[course_name]:
                response = course_details[course_name][course_option]
                return {"response": response}, False
            else:
                response = "Sorry, I don't have details for that option."
                return {"response": response}, False

    # Load intents data
    with open('intents_trial.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

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
        if best_match['pattern'].lower() in ["hi", "hello", "hey", "helo", "good day", "is anyone there", "Hello madam", "hello Sir", "hi madam", "hi Sir", "Sir", "madam", "hei", "sorry"]:
            options = [
                "Tell me about micro-credential courses",
                "Res4City ?",
                "Res4Chat ?",
                "Courses Offered",
                "Skills Gained",
                "Job Assistance",
                "Enrollment",
                "Contact Us"
            ]
            return {"response": response, "options": options}, False
        
        # Special handling for "Courses Offered" and related options
        elif user_message.lower() == "courses offered":
            courses = list(course_details.keys())
            return {"response": "Here are the courses offered:", "options": courses}, False
        
        # Handle course-specific options
        elif any(course.lower() in user_message.lower() for course in course_details.keys()):
            # Match the course name exactly using case-insensitive matching
            course_name = next(course for course in course_details.keys() if course.lower() == user_message.lower())
            user_states[user_id]["selected_course"] = course_name
            options = sub_options

            return {"response": f"You've selected the course: {course_name}. What would you like to know about it?", "options": options}, False
        
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
    user_id = request.json.get('user_id')  # Ensure you pass user_id from the frontend
    if not user_message.strip():
        return jsonify({'error': 'Please enter a message.'}), 400
    
    response_data, is_error = get_response(user_message, user_id)
   
    if is_error or user_message.lower() in ["ok", "thanks", "thank you", "thank u", "bye", "bi"]:
        follow_up = "Is there anything else I can help you with?"
        return jsonify({'response': follow_up, 'follow_up': True, 'options': []})  # Empty options to keep the current ones
   
    return jsonify({'response': response_data.get('response'), 'options': response_data.get('options', []), 'follow_up': False})

@app.route('/follow_up', methods=['POST'])
def follow_up():
    user_message = request.json.get('message')
    user_id = request.json.get('user_id')  # Ensure you pass user_id from the frontend
    if not user_message.strip():
        return jsonify({'error': 'Please enter a message.'}), 400

    if user_message.lower() in ["no"]:
        final_message = "Thank you for chatting with us! Have a great day!"
        return jsonify({'response': final_message, 'options': []})  # No options on exit
    elif user_message.lower() == "yes":
        continue_message = "Great! What else can I help you with?"
        return jsonify({'response': continue_message, 'options': []})  # Continue with no new options
   
    response, _ = get_response(user_message, user_id)
    return jsonify({'response': response, 'options': []})

if __name__ == '__main__':
    app.run(debug=True)
