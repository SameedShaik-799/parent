import numpy as np
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import joblib

app = Flask(__name__)
app.secret_key = 'your_random_secret_key_123'
model = joblib.load('student_grade_predictor.joblib')

# --- Dummy Data ---
DUMMY_USER = {
    'email': 'parent@school.com',
    'password': 'password123'
}
DUMMY_STUDENT_DATA = {
    "name": "Alex Doe",
    "class": "10",
    "section": "B",
    "attendance": "92%",
    "marks": {
        "Mathematics": 85,
        "Science": 91,
        "English": 78,
        "History": 88
    }
}

# --- NEW: Chatbot Helper Functions ---
def get_performance_review(data):
    """Analyzes student data and generates a brief review."""
    avg_mark = sum(data['marks'].values()) / len(data['marks'])
    lowest_subject = min(data['marks'], key=data['marks'].get)
    highest_subject = max(data['marks'], key=data['marks'].get)
    
    review = (f"Overall, {data['name']} is performing well with an average score of {avg_mark:.2f}. "
              f"Their strongest subject is currently {highest_subject}. "
              f"The area where they could use the most support is {lowest_subject}. "
              f"Their attendance at {data['attendance']} is excellent, which is a great sign of engagement.")
    return review

def get_suggestions(data):
    """Provides suggestions based on the lowest mark."""
    lowest_subject = min(data['marks'], key=data['marks'].get)
    suggestions = (f"To help improve in {lowest_subject}, you could try a few things: "
                   "1. Review their homework in that subject together. "
                   "2. Use online resources like Khan Academy for difficult topics. "
                   "3. Encourage them to ask questions in class, even if they feel shy. "
                   "A little extra focus here can make a big difference!")
    return suggestions

def get_motivation_tips():
    """Provides general motivational and guidance tips for parents."""
    tips = ("To help motivate your child, try to focus on effort, not just grades. "
            "Create a consistent, quiet space for homework. "
            "Celebrate small successes to build confidence. "
            "Most importantly, maintain open communication about their challenges and successes at school.")
    return tips


# --- Routes ---
@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['email'] == DUMMY_USER['email'] and request.form['password'] == DUMMY_USER['password']:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        return render_template('dashboard.html', student=DUMMY_STUDENT_DATA)
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'logged_in' in session:
        features = [float(x) for x in request.form.values()]
        prediction = model.predict([np.array(features)])
        output = round(prediction[0], 2)
        prediction_text = f'Predicted Final Grade (out of 20): {output}'
        return render_template('dashboard.html', prediction_text=prediction_text, student=DUMMY_STUDENT_DATA)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- UPGRADED CHATBOT ROUTE ---
@app.route('/chatbot', methods=['POST'])
def chatbot():
    if 'logged_in' not in session:
        return jsonify({'response': 'You are not logged in.'})

    user_message = request.json['message'].lower()
    bot_response = ""

    # Check for new, more intelligent keywords
    if 'review' in user_message or 'summary' in user_message or 'performance' in user_message:
        bot_response = get_performance_review(DUMMY_STUDENT_DATA)
    elif 'suggest' in user_message or 'advice' in user_message or 'low marks' in user_message:
        bot_response = get_suggestions(DUMMY_STUDENT_DATA)
    elif 'motivate' in user_message or 'homework' in user_message or 'guide' in user_message:
        bot_response = get_motivation_tips()
    # Keep the old simple questions
    elif 'marks' in user_message or 'grade' in user_message:
        marks_str = ", ".join([f"{subject}: {mark}" for subject, mark in DUMMY_STUDENT_DATA['marks'].items()])
        bot_response = f"Alex's current marks are: {marks_str}."
    elif 'attendance' in user_message:
        bot_response = f"Alex's attendance is {DUMMY_STUDENT_DATA['attendance']}."
    else:
        bot_response = "I can help with a few things. Try asking for a 'review', 'suggestions for low marks', or 'how to motivate'."

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)