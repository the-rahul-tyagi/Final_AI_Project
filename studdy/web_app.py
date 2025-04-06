from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import google.generativeai as genai
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Subject areas and their topics
SUBJECTS = {
    'Mathematics': ['Algebra', 'Calculus', 'Geometry', 'Statistics'],
    'Science': ['Physics', 'Chemistry', 'Biology', 'Earth Science'],
    'Languages': ['English', 'Spanish', 'French', 'German'],
    'History': ['World History', 'American History', 'Ancient History', 'Modern History']
}

# Initialize or load study history
if os.path.exists('study_history.csv'):
    study_history = pd.read_csv('study_history.csv')
    study_history['timestamp'] = pd.to_datetime(study_history['timestamp'])
else:
    study_history = pd.DataFrame(columns=['timestamp', 'subject', 'topic', 'difficulty', 'activity_type', 'duration'])

@app.route('/')
def index():
    return render_template('index.html', subjects=SUBJECTS)

@app.route('/study_material', methods=['GET', 'POST'])
def study_material():
    if request.method == 'POST':
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        difficulty = request.form.get('difficulty')
        
        prompt = f"""You are an expert tutor in {subject}. Create comprehensive study material for {topic} at {difficulty} level.

        Include the following sections:
        1. Key Concepts: Explain the fundamental principles and theories
        2. Important Formulas/Theorems: List and explain all relevant formulas or theorems
        3. Step-by-Step Examples: Provide 3 detailed examples with full explanations
        4. Practice Problems: Create 5 practice problems with varying difficulty
        5. Common Mistakes: Highlight common misconceptions and how to avoid them
        6. Study Tips: Provide specific strategies for mastering this topic
        
        Format the response in HTML with appropriate headings and styling."""
        
        response = model.generate_content(prompt)
        
        # Record study session
        global study_history
        study_history.loc[len(study_history)] = {
            'timestamp': datetime.now(),
            'subject': subject,
            'topic': topic,
            'difficulty': difficulty,
            'activity_type': 'Study Materials',
            'duration': 0
        }
        study_history.to_csv('study_history.csv', index=False)
        
        return render_template('study_material.html', content=response.text, subject=subject, topic=topic)
    
    return render_template('generate_material.html', subjects=SUBJECTS)

@app.route('/practice_test', methods=['GET', 'POST'])
def practice_test():
    if request.method == 'POST':
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        
        prompt = f"""You are an expert exam creator for {subject}. Create a 5-question practice test for {topic}.

        For each question:
        1. Write a clear, concise question
        2. Provide 4 multiple choice options (A, B, C, D)
        3. Indicate the correct answer
        4. Provide a detailed explanation of why the answer is correct
        
        Format the response in HTML with appropriate styling and a modern quiz layout.
        Make sure to wrap each question in a div with class 'question' and include a form for submission.
        Add a 'data-correct' attribute to the correct answer option."""
        
        response = model.generate_content(prompt)
        
        # Record session
        global study_history
        study_history.loc[len(study_history)] = {
            'timestamp': datetime.now(),
            'subject': subject,
            'topic': topic,
            'difficulty': 'N/A',
            'activity_type': 'Practice Test',
            'duration': 0
        }
        study_history.to_csv('study_history.csv', index=False)
        
        return render_template('practice_test.html', content=response.text, subject=subject, topic=topic)
    
    return render_template('generate_test.html', subjects=SUBJECTS)

@app.route('/submit_test', methods=['POST'])
def submit_test():
    answers = request.get_json()
    score = 0
    total_questions = len(answers)
    results = []
    
    for question_id, selected_answer in answers.items():
        correct_answer = request.form.get(f'correct_{question_id}')
        is_correct = selected_answer == correct_answer
        if is_correct:
            score += 1
        results.append({
            'question_id': question_id,
            'is_correct': is_correct,
            'correct_answer': correct_answer
        })
    
    percentage = (score / total_questions) * 100
    
    return jsonify({
        'score': score,
        'total': total_questions,
        'percentage': percentage,
        'results': results
    })

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = request.get_json()
                question = data.get('question')
                subject = data.get('subject')
                topic = data.get('topic')
                difficulty = data.get('difficulty')
                
                if not all([question, subject, topic, difficulty]):
                    return jsonify({'error': 'Missing required parameters'}), 400
                
                prompt = f"""You are an expert tutor in {subject}, specifically knowledgeable about {topic} at {difficulty} level.
                
                User Question: {question}
                
                Provide a helpful, educational response that:
                1. Directly addresses the user's question
                2. Uses appropriate examples and analogies
                3. Breaks down complex concepts into simpler parts
                4. Encourages deeper understanding
                5. Suggests related topics for further study
                
                Format your response in HTML with appropriate styling. Use:
                - <p> tags for paragraphs
                - <ul> or <ol> for lists
                - <code> for code snippets
                - <strong> for important points
                - <em> for emphasis
                - <blockquote> for quotes or important notes
                
                Make the response engaging and easy to read."""
                
                response = model.generate_content(prompt)
                
                # Record chat session
                global study_history
                study_history.loc[len(study_history)] = {
                    'timestamp': datetime.now(),
                    'subject': subject,
                    'topic': topic,
                    'difficulty': difficulty,
                    'activity_type': 'Chat',
                    'duration': 0
                }
                study_history.to_csv('study_history.csv', index=False)
                
                return jsonify({'response': response.text})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        difficulty = request.form.get('difficulty')
        session['chat_context'] = {'subject': subject, 'topic': topic, 'difficulty': difficulty}
        return render_template('chat.html', subject=subject, topic=topic, difficulty=difficulty)
    
    return render_template('start_chat.html', subjects=SUBJECTS)

@app.route('/statistics')
def statistics():
    if len(study_history) == 0:
        return render_template('statistics.html', has_data=False)
    
    total_time = study_history['duration'].sum()
    subject_stats = study_history['subject'].value_counts().to_dict()
    activity_stats = study_history['activity_type'].value_counts().to_dict()
    recent_activity = study_history.sort_values('timestamp', ascending=False).head(5).to_dict('records')
    
    return render_template('statistics.html', 
                         has_data=True,
                         total_time=total_time,
                         subject_stats=subject_stats,
                         activity_stats=activity_stats,
                         recent_activity=recent_activity)

if __name__ == '__main__':
    app.run(debug=True) 