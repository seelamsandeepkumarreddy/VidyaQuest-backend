from flask import Blueprint, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

chatbot_bp = Blueprint('chatbot', __name__)

# Configure Gemini AI
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_api_key_here":
    genai.configure(api_key=api_key)
    
    SYSTEM_INSTRUCTION = """
    You are the RuralQuest Learning Assistant, a friendly and helpful AI tutor for students in Grades 8, 9, and 10 in rural areas.
    Your goal is to:
    1. Answer questions clearly and simply about school subjects (Math, Science, English, etc.).
    2. Use examples that rural students can relate to (farming, village life, nature).
    3. Encourage students to keep learning and stay curious.
    4. Keep responses relatively concise and easy to read on a mobile screen.
    5. If a student asks something completely unrelated to education, gently bring them back to their studies.
    """

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )
else:
    model = None
    print("WARNING: Chatbot initialized without a valid API key.")

@chatbot_bp.route('/ask', methods=['POST'])
def ask():
    if not model:
        return jsonify({"answer": "System Error: Chatbot is not configured with a valid API key. Please check the backend .env file."}), 500

    try:
        data = request.json
        if not data:
            return jsonify({"answer": "Error: No data received."}), 400
            
        question = data.get('question', '')
        if not question:
            return jsonify({"answer": "Please type a question!"}), 400

        print(f"Chatbot received: {question}")
        
        # Generate response using Gemini
        response = model.generate_content(question)
        
        try:
            answer = response.text
        except Exception:
            if response.candidates:
                answer = f"I'm sorry, I can't answer that. (Blocked: {response.candidates[0].finish_reason})"
            else:
                answer = "I'm sorry, I couldn't generate an answer. Try a different question."
            
        return jsonify({"answer": answer})
        
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return jsonify({"answer": f"Backend Error: {str(e)}"}), 500
