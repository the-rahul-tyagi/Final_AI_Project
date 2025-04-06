import os
import google.generativeai as genai
from dotenv import load_dotenv
from colorama import init, Fore, Style
import time
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import json

# Initialize colorama for colored output
init()

try:
    # Load environment variables
    load_dotenv()
    
    # Get API key and verify it exists
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print(f"{Fore.RED}Error: GEMINI_API_KEY not found in .env file{Style.RESET_ALL}")
        sys.exit(1)
        
    # Configure Gemini API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Test API connection
    try:
        response = model.generate_content("Test connection")
        print(f"{Fore.GREEN}Successfully connected to Gemini API{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error connecting to Gemini API: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
except Exception as e:
    print(f"{Fore.RED}Initialization Error: {str(e)}{Style.RESET_ALL}")
    sys.exit(1)

# Subject areas and their topics
SUBJECTS = {
    'Mathematics': ['Algebra', 'Calculus', 'Geometry', 'Statistics'],
    'Science': ['Physics', 'Chemistry', 'Biology', 'Earth Science'],
    'Languages': ['English', 'Spanish', 'French', 'German'],
    'History': ['World History', 'American History', 'Ancient History', 'Modern History']
}

# Initialize study history DataFrame
try:
    study_history = pd.DataFrame(columns=['timestamp', 'subject', 'topic', 'difficulty', 'activity_type', 'duration'])
    
    # Try to load existing study history if available
    if os.path.exists('study_history.csv'):
        study_history = pd.read_csv('study_history.csv')
        study_history['timestamp'] = pd.to_datetime(study_history['timestamp'])
        print(f"{Fore.GREEN}Loaded existing study history.{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}Error initializing DataFrame: {str(e)}{Style.RESET_ALL}")
    sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(f"{Fore.CYAN}╔════════════════════════════════════════╗")
    print(f"║           AI Study Buddy v1.0           ║")
    print(f"╚════════════════════════════════════════╝{Style.RESET_ALL}\n")

def print_menu():
    print(f"{Fore.YELLOW}Main Menu:{Style.RESET_ALL}")
    print("1. Generate Study Materials")
    print("2. Create Practice Test")
    print("3. Chat with AI")
    print("4. View Study Statistics")
    print("5. Save Study History")
    print("6. Exit")
    print()

def select_subject():
    print(f"\n{Fore.YELLOW}Available Subjects:{Style.RESET_ALL}")
    for i, subject in enumerate(SUBJECTS.keys(), 1):
        print(f"{i}. {subject}")
    
    while True:
        try:
            choice = int(input("\nSelect subject number: "))
            if 1 <= choice <= len(SUBJECTS):
                return list(SUBJECTS.keys())[choice-1]
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")

def select_topic(subject):
    print(f"\n{Fore.YELLOW}Available Topics for {subject}:{Style.RESET_ALL}")
    topics = SUBJECTS[subject]
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    
    while True:
        try:
            choice = int(input("\nSelect topic number: "))
            if 1 <= choice <= len(topics):
                return topics[choice-1]
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")

def select_difficulty():
    difficulties = ['Beginner', 'Intermediate', 'Advanced']
    print(f"\n{Fore.YELLOW}Select Difficulty:{Style.RESET_ALL}")
    for i, diff in enumerate(difficulties, 1):
        print(f"{i}. {diff}")
    
    while True:
        try:
            choice = int(input("\nSelect difficulty number: "))
            if 1 <= choice <= len(difficulties):
                return difficulties[choice-1]
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")

def generate_study_material(subject, topic, difficulty):
    print(f"\n{Fore.CYAN}Generating study materials...{Style.RESET_ALL}")
    prompt = f"""You are an expert tutor in {subject}. Create comprehensive study material for {topic} at {difficulty} level.

    Include the following sections:
    1. Key Concepts: Explain the fundamental principles and theories
    2. Important Formulas/Theorems: List and explain all relevant formulas or theorems
    3. Step-by-Step Examples: Provide 3 detailed examples with full explanations
    4. Practice Problems: Create 5 practice problems with varying difficulty
    5. Common Mistakes: Highlight common misconceptions and how to avoid them
    6. Study Tips: Provide specific strategies for mastering this topic
    
    Format the response in a clear, structured way with headings and bullet points where appropriate."""
    
    start_time = time.time()
    response = model.generate_content(prompt)
    duration = time.time() - start_time
    
    # Record study session
    study_history.loc[len(study_history)] = {
        'timestamp': datetime.now(),
        'subject': subject,
        'topic': topic,
        'difficulty': difficulty,
        'activity_type': 'Study Materials',
        'duration': duration
    }
    
    return response.text

def generate_practice_test(subject, topic, num_questions=5):
    print(f"\n{Fore.CYAN}Creating practice test...{Style.RESET_ALL}")
    prompt = f"""You are an expert exam creator for {subject}. Create a {num_questions}-question practice test for {topic}.

    For each question:
    1. Write a clear, concise question
    2. Provide 4 multiple choice options (A, B, C, D)
    3. Indicate the correct answer
    4. Provide a detailed explanation of why the answer is correct
    5. Explain why the other options are incorrect
    
    Format each question as follows:
    Question 1: [Question text]
    A) [Option A]
    B) [Option B]
    C) [Option C]
    D) [Option D]
    Correct Answer: [Letter]
    Explanation: [Detailed explanation]"""
    
    start_time = time.time()
    response = model.generate_content(prompt)
    duration = time.time() - start_time
    
    # Record study session
    study_history.loc[len(study_history)] = {
        'timestamp': datetime.now(),
        'subject': subject,
        'topic': topic,
        'difficulty': 'N/A',
        'activity_type': 'Practice Test',
        'duration': duration
    }
    
    return response.text

def chat_with_ai(subject, topic, difficulty):
    print(f"\n{Fore.CYAN}Chat with AI (Type 'exit' to return to main menu){Style.RESET_ALL}")
    print(f"Context: {subject} - {topic} ({difficulty} level)")
    
    start_time = time.time()
    chat_count = 0
    
    while True:
        user_input = input("\nYour question: ")
        if user_input.lower() == 'exit':
            break
            
        prompt = f"""You are an expert tutor in {subject}, specifically knowledgeable about {topic} at {difficulty} level.
        
        User Question: {user_input}
        
        Provide a helpful, educational response that:
        1. Directly addresses the user's question
        2. Uses appropriate examples and analogies
        3. Breaks down complex concepts into simpler parts
        4. Encourages deeper understanding
        5. Suggests related topics for further study
        
        Keep your response focused and concise while being thorough."""
        
        response = model.generate_content(prompt)
        print(f"\n{Fore.GREEN}AI: {response.text}{Style.RESET_ALL}")
        chat_count += 1
    
    duration = time.time() - start_time
    
    # Record study session
    study_history.loc[len(study_history)] = {
        'timestamp': datetime.now(),
        'subject': subject,
        'topic': topic,
        'difficulty': difficulty,
        'activity_type': f'Chat Session ({chat_count} messages)',
        'duration': duration
    }

def view_statistics():
    if len(study_history) == 0:
        print(f"\n{Fore.YELLOW}No study sessions recorded yet.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}Study Statistics:{Style.RESET_ALL}")
    
    # Total study time
    total_time = study_history['duration'].sum()
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)
    print(f"\nTotal Study Time: {hours} hours, {minutes} minutes, {seconds} seconds")
    
    # Subject distribution
    subject_stats = study_history['subject'].value_counts()
    print(f"\nSubject Distribution:")
    for subject, count in subject_stats.items():
        print(f"{subject}: {count} sessions")
    
    # Activity type distribution
    activity_stats = study_history['activity_type'].value_counts()
    print(f"\nActivity Distribution:")
    for activity, count in activity_stats.items():
        print(f"{activity}: {count} sessions")
    
    # Recent activity
    print(f"\nRecent Activity:")
    recent = study_history.sort_values('timestamp', ascending=False).head(5)
    for _, row in recent.iterrows():
        print(f"{row['timestamp']}: {row['activity_type']} - {row['subject']} ({row['topic']})")
    
    input("\nPress Enter to continue...")

def save_study_history():
    try:
        study_history.to_csv('study_history.csv', index=False)
        print(f"\n{Fore.GREEN}Study history saved successfully to 'study_history.csv'{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error saving study history: {str(e)}{Style.RESET_ALL}")
    
    input("\nPress Enter to continue...")

def main():
    while True:
        print_header()
        print_menu()
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            subject = select_subject()
            topic = select_topic(subject)
            difficulty = select_difficulty()
            material = generate_study_material(subject, topic, difficulty)
            print(f"\n{Fore.GREEN}{material}{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            subject = select_subject()
            topic = select_topic(subject)
            test = generate_practice_test(subject, topic)
            print(f"\n{Fore.GREEN}{test}{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            subject = select_subject()
            topic = select_topic(subject)
            difficulty = select_difficulty()
            chat_with_ai(subject, topic, difficulty)
            
        elif choice == '4':
            view_statistics()
            
        elif choice == '5':
            save_study_history()
            
        elif choice == '6':
            # Auto-save before exiting
            if len(study_history) > 0:
                save_study_history()
            print(f"\n{Fore.CYAN}Thank you for using AI Study Buddy!{Style.RESET_ALL}")
            break
            
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            time.sleep(1)

if __name__ == "__main__":
    main() 