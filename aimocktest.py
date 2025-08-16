import streamlit as st
import time
import random
from datetime import datetime, timedelta
import json
import os
import google.generativeai as genai
from config.QuestionBank import QUESTION_BANK
from config.fallback_questions import create_fallback_questions


genai.configure(api_key="AIzaSyDWQlFnZtNVF7ydDxn6x3GS65tbNeAuHm0")

def generate_aptitude_mcqs_gemini(num_questions=5, topic="Mixed Aptitude", difficulty="medium"):
    """Generate AI questions using Gemini API"""
  
    difficulty_desc = {
        'easy': 'basic and simple level suitable for beginners',
        'medium': 'moderate difficulty with standard complexity', 
        'hard': 'challenging and complex requiring advanced thinking'
    }
    
    topic_prompts = {
        'Practice Set-1': 'General aptitude covering quantitative ability,Distance and Relative Speed, Profit and Loss, Pipes and Work, Average Age, Average Speed, Relative Speed and Meeting Points, Work and Time (Task Completion), Work and Time (Multiple Workers and Leaving Times), Train and Platform Length, Pipes Filling Tank with Different Running Times, Percentage and Number Problems, Age Problems and Ratios, Profit Percentage and Selling Price, Work and Time (One Leaves After Some Days), Trains Meeting Problem, Average after Removing Numbers, Geometry - Largest Square in Rectangle, Sets - Students Playing Games, Modular Arithmetic (Remainders), Arithmetic Progression - Sum of Terms, Exponentiation and Powers, Clock Angles, Day Calculation (Calendar Problem), Simple Interest and Amount, Speed of Train Calculation, Pipes Filling and Emptying Tank, Relative Speed - Overtaking Problem, Age Problems with Ratios, Partnership and Profit Sharing, Percentage Equations, Age Problems - Father and Daughter, Mixture Problems - Milk and Water, Boat Speed Upstream/Downstream, Remainders in Division, Permutations and Combinations, Compound Interest vs Simple Interest, Consecutive Even Numbers, Successive Discounts and Profit Percentage, Pipes Filling Tank with Closure of One Pipe, Ratio Problems, Simple Interest Rate Calculation',
        'Practice Set-2': 'logical reasoning,Clock and Time Calculation, Coding and Decoding, Artificial Language and Meaning Deduction, Family Relationship Problems, Number Series Completion, Letter Series Completion, Dice and Probability, Set Theory and Venn Diagrams, Seating Arrangement in a Row, Seating Arrangement in a Circle, Direction and Distance Problems, Alphabetic Coding, Clock Angle Problems,Probability, Circular Seating Arrangement Logic, Mixed Series Completion,Direction and Path Problems,Calendar Day Calculation',
        'Practice Set-3': 'programming-related MCQs ,Python , java ,C ,C++,javascript, SQl, DSA  and language skills,Core Languages: Python ,Fibonacci recursion, list copying, slicing, set operations, for-else loops; ,Java static variables, Boolean operators, array indexing, virtual functions;, C  undefined behavior, array initialization, operator precedence; ,C++ : references, struct vs class, virtual functions and polymorphism; ,JavaScript floating-point precision, const arrays, array methods; ,SQL queries, constraints, joins, keys, functions; ,Data Structures & Algorithms arrays, searching, sorting, stacks, queues, hash tables; ,Programming Concepts  object-oriented programming, memory management, complexity analysis; ,Output-based Questions code comprehension and output prediction',
        'Practice Set-4': 'Mixed aptitude and reasoning test covering advanced mathematics (compound interest, combinatorics, LCM, probability, statistics), practical problem-solving (work-time, age, speed-distance,Percentages,Averages,Train Problems ), logical reasoning (patterns, spatial reasoning, graph theory, analytical puzzles, Seating Arrangements (Linear & Circular),Series Completion (Number, Letter, Mixed)), and verbal ability (grammar, vocabulary, writing skills),language-specific MCQs and code-output puzzles covering Python, Java, C, C++, JavaScript, SQL, DSA, algorithms, memory & pointers, Output based Que, and debugging.',
        'Practice Set-5': 'Mixed aptitude and reasoning test covering advanced mathematics (compound interest, combinatorics, LCM, probability, statistics), practical problem-solving (work-time, age, speed-distance,Percentages,Averages,Train Problems ), logical reasoning (patterns, spatial reasoning, graph theory, analytical puzzles, Seating Arrangements (Linear & Circular),Series Completion (Number, Letter, Mixed)), and verbal ability (grammar, vocabulary, writing skills),language-specific MCQs and code-output puzzles covering Python, Java, C, C++, JavaScript, SQL, DSA, algorithms, memory & pointers, Output based Que, and debugging.',
        'Practice Set-6': 'Mixed aptitude and reasoning test covering advanced mathematics (compound interest, combinatorics, LCM, probability, statistics), practical problem-solving (work-time, age, speed-distance,Percentages,Averages,Train Problems ), logical reasoning (patterns, spatial reasoning, graph theory, analytical puzzles, Seating Arrangements (Linear & Circular),Series Completion (Number, Letter, Mixed)), and verbal ability (grammar, vocabulary, writing skills),language-specific MCQs and code-output puzzles covering Python, Java, C, C++, JavaScript, SQL, DSA, algorithms, memory & pointers, Output based Que, and debugging.'
    }
    
    specific_topic = topic_prompts.get(topic, "General aptitude and reasoning problems")
    
    prompt = f"""
Create exactly {num_questions} multiple-choice questions for Computer Engineering placement preparation.

TOPIC: {specific_topic}
DIFFICULTY: {difficulty_desc[difficulty]}

REQUIREMENTS:
1. Each question must have exactly 4 options
2. Questions should be relevant for campus placements
3. Include clear explanations for correct answers
4. Use proper mathematical notation where needed

OUTPUT FORMAT - Return ONLY valid JSON array:
[
  {{
    "question": "What is 25% of 80?",
    "options": ["15", "20", "25", "30"],
    "correct": 1,
    "explanation": "25% of 80 = (25/100) × 80 = 0.25 × 80 = 20"
  }}
]

Generate exactly {num_questions} questions now. Return only the JSON array, no other text.
"""
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        if not response or not response.text:
            return create_fallback_questions(num_questions, topic, difficulty)
        
        # Clean response text
        text = response.text.strip()
        json_text = extract_json_from_response(text)
        
        if not json_text:
            return create_fallback_questions(num_questions, topic, difficulty)
        
        try:
            mcqs = json.loads(json_text)
        except json.JSONDecodeError:
            return create_fallback_questions(num_questions, topic, difficulty)
        
        formatted_questions = validate_and_format_questions(mcqs, num_questions)
        
        if len(formatted_questions) == 0:
            return create_fallback_questions(num_questions, topic, difficulty)
        
        if len(formatted_questions) < num_questions:
            needed = num_questions - len(formatted_questions)
            fallback = create_fallback_questions(needed, topic, difficulty)
            formatted_questions.extend(fallback)
        
        return formatted_questions[:num_questions]
        
    except Exception:
        return create_fallback_questions(num_questions, topic, difficulty)

def extract_json_from_response(text):
    """Extract JSON from response text"""
    if '```json' in text:
        start = text.find('```json') + 7
        end = text.find('```', start)
        if end != -1:
            return text[start:end].strip()
    
    if '```' in text:
        start = text.find('```') + 3
        end = text.find('```', start)
        if end != -1:
            return text[start:end].strip()
    
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    
    return text.strip()

def validate_and_format_questions(mcqs, target_count):
    """Validate and format questions"""
    formatted_questions = []
    
    if not isinstance(mcqs, list):
        return []
    
    for mcq in mcqs:
        try:
            if not isinstance(mcq, dict):
                continue
            
            required_fields = ['question', 'options', 'correct', 'explanation']
            if not all(field in mcq for field in required_fields):
                continue
            
            question = str(mcq['question']).strip()
            if len(question) < 10:
                continue
            
            options = mcq['options']
            if not isinstance(options, list) or len(options) < 4:
                continue
            
            try:
                correct_idx = int(mcq['correct'])
                if not (0 <= correct_idx < len(options)):
                    continue
            except (ValueError, TypeError):
                continue
            
            explanation = str(mcq['explanation']).strip()
            if len(explanation) < 5:
                explanation = f"The correct answer is {options[correct_idx]}."
            
            formatted_question = {
                'question': question,
                'options': [str(opt).strip() for opt in options[:4]],
                'correct': correct_idx,
                'explanation': explanation
            }
            
            formatted_questions.append(formatted_question)
            
        except Exception:
            continue
    
    return formatted_questions



def init_quiz_session_state():
    """Initialize session state for quiz"""
    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = {
            'phase': 'setup',
            'quiz_mode': '',
            'category': '',
            'programming_language': '',
            'ai_topic': '',
            'difficulty': 'medium',
            'num_questions': 5,
            'timer_duration': 15,
            'questions': [],
            'current_question': 0,
            'score': 0,
            'correct_answers': 0,
            'user_answers': [],
            'start_time': None,
            'question_start_time': None,
            'selected_answer': None,
            'show_explanation': False,
            'time_up': False,
            'generating_questions': False,
            'generation_progress': 0,
            'generation_status': ''
        }

def get_category_display_name(category):
    """Get display name for categories"""
    category_names = {
        'General Aptitude': '🧠 General Aptitude',
        'Verbal and Reasoning': '🧩 Verbal and Reasoning',
        'programming': '💻 Programming',
        'Technical MCQs': '📚 Technical MCQs',
        'Data structure and Algorithm': '🧮 Data Structure & Algorithm',
        'Problem Solving': '🕵 Problem Solving',
        'C': '💻 C Programming',
        'C++': '💻 C++ Programming',
        'Java': '💻 Java Programming',
        'Python': '💻 Python Programming',
        'JavaScript': '💻 JavaScript Programming'
    }
    return category_names.get(category, '🌍 General Knowledge')

def shuffle_questions(questions, num_questions):
    """Shuffle and select required number of questions"""
    shuffled = questions.copy()
    random.shuffle(shuffled)
    return shuffled[:num_questions]

def generate_static_questions():
    """Generate questions from question bank"""
    category = st.session_state.quiz_state['category']
    difficulty = st.session_state.quiz_state['difficulty']
    num_questions = st.session_state.quiz_state['num_questions']
    
    # For programming, use the selected programming language as category
    if category == 'programming':
        category = st.session_state.quiz_state['programming_language']
    
    # Get questions for selected difficulty
    category_questions = QUESTION_BANK.get(category, QUESTION_BANK['General Aptitude'])
    questions = category_questions.get(difficulty, []).copy()
    
    # Add questions from other difficulties if needed
    if len(questions) < num_questions:
        for diff in ['easy', 'medium', 'hard']:
            if diff != difficulty and diff in category_questions:
                questions.extend(category_questions[diff])
    
    # If still not enough, use General Aptitude questions
    if len(questions) < num_questions:
        general_questions = QUESTION_BANK['General Aptitude']
        for diff in ['easy', 'medium', 'hard']:
            questions.extend(general_questions.get(diff, []))
    
    return shuffle_questions(questions, num_questions)

def setup_phase():
    """Main setup interface"""
    # st.markdown("# 🎯 AI-Powered Quiz System")
    # st.markdown("Choose your preferred quiz experience:")
    st.markdown("""
    ### 🚀 Welcome to Our Comprehensive Learning Platform!
    
    **Discover knowledge through interactive quizzes designed for modern learners.** 
    
    **Choose your preferred learning experience and challenge yourself across various domains with our advanced assessment system.**
    """)

    # Quiz mode selection
    st.markdown("### Select Category Mode:")
    
    mode_col1, mode_col2 = st.columns(2)
    
    with mode_col1:
        if st.button("**📚 Question Bank Quiz**   \n*Pre-loaded questions from our curated database*", 
                     key="static_mode", use_container_width=True):
            st.session_state.quiz_state['quiz_mode'] = 'static'
            st.rerun()
    
    with mode_col2:
        if st.button("**🤖 AI-Generated Quiz**    \n*Fresh questions powered by Gemini AI*", 
                     key="ai_mode", use_container_width=True, type="primary"):
            st.session_state.quiz_state['quiz_mode'] = 'ai'
            st.rerun()
    
    # Show setup based on mode
    if st.session_state.quiz_state['quiz_mode'] == 'ai':
        ai_quiz_setup()
    elif st.session_state.quiz_state['quiz_mode'] == 'static':
        static_quiz_setup()

def static_quiz_setup():
    """Question Bank quiz setup interface"""
    st.markdown("---")
    st.markdown("## 📚 Question Bank Quiz Setup")
    
    # Categories selection
    st.markdown("### Select Category:")
    
    categories = [
        ('General Aptitude', '🧠', 'General Aptitude'),
        ('Verbal and Reasoning', '🧩', 'Verbal and Reasoning'),
        ('programming', '💻', 'Programming'),
        ('Technical MCQs', '📚', 'Technical MCQs'),
        ('Data structure and Algorithm', '🧮', 'Data Structure & Algorithm'),
        ('Problem Solving', '🕵', 'Problem Solving')
    ]
    
    # Create 2x3 grid
    row1_cols = st.columns(3)
    row2_cols = st.columns(3)
    
    for i, (category, icon, display_name) in enumerate(categories[:3]):
        with row1_cols[i]:
            if st.button(f"{icon}\n**{display_name}**", 
                        key=f"static_cat_{category}", use_container_width=True):
                st.session_state.quiz_state['category'] = category
                if category == 'programming':
                    st.session_state.quiz_state['phase'] = 'programming_language'
                    st.rerun()
                else:
                    st.rerun()
    
    for i, (category, icon, display_name) in enumerate(categories[3:]):
        with row2_cols[i]:
            if st.button(f"{icon}\n**{display_name}**", 
                        key=f"static_cat_{category}", use_container_width=True):
                st.session_state.quiz_state['category'] = category
                if category == 'programming':
                    st.session_state.quiz_state['phase'] = 'programming_language'
                    st.rerun()
                else:
                    st.rerun()
    
    # Show settings if category selected (and not programming)
    if st.session_state.quiz_state.get('category') and st.session_state.quiz_state['category'] != 'programming':
        show_static_quiz_settings()

def show_static_quiz_settings():
    """Show settings for static quiz"""
    st.markdown("---")
    st.markdown("### ⚙️ Quiz Settings")
    
    category = st.session_state.quiz_state['category']
    st.success(f"✅ Selected Category: {get_category_display_name(category)}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        difficulty = st.selectbox(
            "🎲 Difficulty Level",
            options=['easy', 'medium', 'hard'],
            index=1,
            key="static_difficulty"
        )
        st.session_state.quiz_state['difficulty'] = difficulty
    
    with col2:
        num_questions = st.selectbox(
            "🎯 Number of Questions",
            options=[15,20,25,30],
            index=1,
            key="static_questions"
        )
        st.session_state.quiz_state['num_questions'] = num_questions
    
    with col3:
        timer_duration = st.selectbox(
            "⏱️ Timer (seconds)",
            options=[15, 20, 30, 45],
            index=0,
            key="static_timer"
        )
        st.session_state.quiz_state['timer_duration'] = timer_duration
    
    st.info(f"🎯 **{difficulty.capitalize()}** difficulty | 📊 **{num_questions}** questions | ⏱️ **{timer_duration}s** per question")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.quiz_state['quiz_mode'] = ''
            st.session_state.quiz_state['category'] = ''
            st.rerun()
    
    with col2:
        if st.button("🚀 Start Question Bank Quiz", use_container_width=True, type="primary"):
            questions = generate_static_questions()
            if questions:
                st.session_state.quiz_state['questions'] = questions
                st.session_state.quiz_state['phase'] = 'quiz'
                st.session_state.quiz_state['start_time'] = datetime.now()
                st.session_state.quiz_state['question_start_time'] = datetime.now()
                st.rerun()
            else:
                st.error("❌ No questions available for this configuration!")

def programming_language_selection():
    """Programming language selection interface"""
    st.markdown("# 💻 Select Programming Language")
    st.markdown("Choose which programming language you'd like to be quizzed on:")
    
    languages = [
        ('C', '🔹', 'C Programming'),
        ('C++', '🔸', 'C++ Programming'),
        ('Java', '☕', 'Java Programming'),
        ('Python', '🐍', 'Python Programming'),
        ('JavaScript', '🟨', 'JavaScript Programming')
    ]
    
    row1_cols = st.columns(3)
    row2_cols = st.columns(2)
    
    for i, (lang, icon, display_name) in enumerate(languages[:3]):
        with row1_cols[i]:
            if st.button(f"{icon}\n{display_name}", key=f"lang_{lang}", use_container_width=True):
                st.session_state.quiz_state['programming_language'] = lang
                st.session_state.quiz_state['phase'] = 'programming_settings'
                st.rerun()
    
    col_start = st.columns([1, 2, 2, 1])
    for i, (lang, icon, display_name) in enumerate(languages[3:]):
        with col_start[i+1]:
            if st.button(f"{icon}\n{display_name}", key=f"lang_{lang}", use_container_width=True):
                st.session_state.quiz_state['programming_language'] = lang
                st.session_state.quiz_state['phase'] = 'programming_settings'
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("⬅ Back to Categories", use_container_width=True):
            st.session_state.quiz_state['phase'] = 'setup'
            st.session_state.quiz_state['category'] = ''
            st.rerun()

def programming_settings_phase():
    """Settings phase for programming quizzes"""
    st.markdown(f"# 💻 {st.session_state.quiz_state['programming_language']} Programming Quiz")
    st.markdown("Configure your quiz settings:")
    
    lang = st.session_state.quiz_state['programming_language']
    language_icons = {'C': '🔹', 'C++': '🔸', 'Java': '☕', 'Python': '🐍', 'JavaScript': '🟨'}
    
    st.success(f"✅ Selected: {language_icons.get(lang, '💻')} {lang} Programming")
    st.markdown("<br>", unsafe_allow_html=True)
    
    settings_cols = st.columns(3)
    
    with settings_cols[0]:
        st.markdown("⏱ Timer Settings")
        timer_duration = st.selectbox(
            "Timer per question",
            options=[10, 15, 20, 30],
            format_func=lambda x: f"{x} seconds",
            index=1,
            key="prog_timer_select"
        )
        st.session_state.quiz_state['timer_duration'] = timer_duration

    with settings_cols[1]:
        st.markdown("🎲 Difficulty Level")
        difficulty = st.selectbox(
            "Choose difficulty",
            options=['easy', 'medium', 'hard'],
            index=1,
            key="prog_difficulty_select"
        )
        st.session_state.quiz_state['difficulty'] = difficulty

    with settings_cols[2]:
        st.markdown("🎯 Quiz Length")
        num_questions = st.selectbox(
            "Number of questions",
            options=[ 15, 20,25,30],
            format_func=lambda x: f"{x} questions",
            index=1,
            key="prog_questions_select"
        )
        st.session_state.quiz_state['num_questions'] = num_questions

    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅ Back to Languages", use_container_width=True):
            st.session_state.quiz_state['phase'] = 'programming_language'
            st.session_state.quiz_state['programming_language'] = ''
            st.rerun()
    
    with col2:
        # Generate questions based on quiz mode
        if st.button("🚀 Start Programming Quiz", use_container_width=True, type="primary"):
            if st.session_state.quiz_state['quiz_mode'] == 'static':
                questions = generate_static_questions()
            else:  # AI mode
                questions = generate_aptitude_mcqs_gemini(
                    num_questions=st.session_state.quiz_state['num_questions'],
                    topic='Programming Logic',
                    difficulty=st.session_state.quiz_state['difficulty']
                )
            
            if questions:
                st.session_state.quiz_state['questions'] = questions
                st.session_state.quiz_state['phase'] = 'quiz'
                st.session_state.quiz_state['start_time'] = datetime.now()
                st.session_state.quiz_state['question_start_time'] = datetime.now()
                st.rerun()
            else:
                st.error("❌ No questions available for this configuration!")

def ai_quiz_setup():
    """AI quiz setup interface"""
    st.markdown("---")
    st.markdown("## 🤖 AI-Generated Quiz Setup")
    st.markdown("### Select Topic:")

    ai_topics = [
        ("Practice Set-1", "🔢", "Numerical Ability"),
        ("Practice Set-2", "🧠", "Verbal and Reasoning"),
        ("Practice Set-3", "🖥️", "Programming Logic"),
        ("Practice Set-4", "📝", "Mock Test-1"),
        ("Practice Set-5", "📝", "Mock Test-2"),
        ("Practice Set-6", "📝", "Mock Test-3")
    ]

    topic_row1 = st.columns(3)
    topic_row2 = st.columns(3)

    # First row
    for i, (set_name, icon, description) in enumerate(ai_topics[:3]):
        with topic_row1[i]:
            if st.button(f"**{set_name}**\n{icon} {description}",
                         key=f"ai_topic_{set_name}", use_container_width=True):
                st.session_state.quiz_state['ai_topic'] = set_name
                st.rerun()

    # Second row
    for i, (set_name, icon, description) in enumerate(ai_topics[3:]):
        with topic_row2[i]:
            if st.button(f"**{set_name}**\n{icon} {description}",
                         key=f"ai_topic_{set_name}", use_container_width=True):
                st.session_state.quiz_state['ai_topic'] = set_name
                st.rerun()

    if st.session_state.quiz_state.get('ai_topic'):
        show_ai_quiz_settings()

def show_ai_quiz_settings():
    """Show settings for AI quiz"""
    st.markdown("---")
    st.markdown("### ⚙️ AI Quiz Settings")
    
    topic = st.session_state.quiz_state['ai_topic']
    st.success(f"✅ Selected Topic: 🤖 {topic}")
    
    # Two columns instead of three
    col1, col2 = st.columns(2)
    
    with col1:
        num_questions = st.selectbox(
            "🎯 Number of Questions",
            options=[15, 20, 25, 30],
            index=1,
            key="ai_questions"
        )
        st.session_state.quiz_state['num_questions'] = num_questions
    
    with col2:
        timer_duration = st.selectbox(
            "⏱️ Timer (seconds)",
            options=[15, 20, 30, 45],
            index=0,
            key="ai_timer"
        )
        st.session_state.quiz_state['timer_duration'] = timer_duration
    
    st.info(f"📊 **{num_questions}** questions | ⏱️ **{timer_duration}s** per question")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.quiz_state['quiz_mode'] = ''
            st.session_state.quiz_state['ai_topic'] = ''
            st.rerun()
    
    with col2:
        if st.button("🚀 Generate AI Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_state['phase'] = 'generating'
            st.rerun()


def generating_phase():
    """Show loading screen during AI generation"""
    st.markdown("# 🤖 Generating Your AI Quiz")
    
    topic = st.session_state.quiz_state['ai_topic']
    difficulty = st.session_state.quiz_state['difficulty']
    num_questions = st.session_state.quiz_state['num_questions']
    
    st.info(f"📋 **Topic:** {topic} | 🎯 **Difficulty:** {difficulty.capitalize()} | 📊 **Questions:** {num_questions}")
    
    progress_container = st.container()
    status_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0, text="Initializing AI generation...")
    
    with status_container:
        status_info = st.empty()
    
    steps = [
        (20, "🔗 Connecting to Gemini AI..."),
        (40, "🧠 Analyzing topic requirements..."),
        (60, "✨ Generating creative questions..."),
        (80, "✅ Validating question quality..."),
        (100, "🎯 Finalizing your quiz...")
    ]
    
    for progress, message in steps:
        progress_bar.progress(progress / 100, text=message)
        status_info.info(message)
        time.sleep(0.8)
    
    questions = generate_aptitude_mcqs_gemini(
        num_questions=num_questions,
        topic=topic,
        difficulty=difficulty
    )
    
    if questions and len(questions) > 0:
        st.session_state.quiz_state['questions'] = questions
        st.session_state.quiz_state['phase'] = 'quiz'
        st.session_state.quiz_state['start_time'] = datetime.now()
        st.session_state.quiz_state['question_start_time'] = datetime.now()
        
        progress_bar.progress(100, text="✅ Quiz generated successfully!")
        status_info.success("🎉 Your AI quiz is ready! Starting now...")
        time.sleep(1)
        st.rerun()
    else:
        progress_bar.progress(100, text="❌ Generation failed")
        status_info.error("❌ Failed to generate questions. Please try again.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Try Again", use_container_width=True, type="primary"):
                st.rerun()
            
            if st.button("⬅️ Back to Setup", use_container_width=True):
                st.session_state.quiz_state['phase'] = 'setup'
                st.rerun()

def quiz_phase():
    """Main quiz interface"""
    quiz_state = st.session_state.quiz_state
    
    if not quiz_state.get('questions') or len(quiz_state['questions']) == 0:
        st.error("❌ No questions available!")
        if st.button("🔄 Go Back to Setup"):
            st.session_state.quiz_state['phase'] = 'setup'
            st.rerun()
        return
    
    current_q_idx = quiz_state['current_question']
    
    if current_q_idx >= len(quiz_state['questions']):
        st.session_state.quiz_state['phase'] = 'results'
        st.rerun()
        return
        
    question_data = quiz_state['questions'][current_q_idx]
    
    # Progress bar
    progress = (current_q_idx + 1) / len(quiz_state['questions'])
    # st.progress(progress, text=f"Question {current_q_idx + 1} of {len(quiz_state['questions'])}")
    
    # # Question meta info
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     difficulty_icons = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}
    #     icon = difficulty_icons.get(quiz_state['difficulty'], '🟡')
    #     st.markdown(f"{icon} **{quiz_state['difficulty'].capitalize()}**")
    # with col2:
    #     st.markdown(f"📊 **Score: {quiz_state['score']}/{len(quiz_state['questions']) * 10}**")
    # with col3:
    #     st.markdown("**+10 points per correct answer**")
    
    # Question display
    st.markdown(f"### Question {current_q_idx + 1}")
    st.markdown(f"**{question_data['question']}**")
    
    st.markdown("---")
    
    # Answer options
    st.markdown("### Choose your answer:")
    
    options = question_data.get('options', [])
    for i, option in enumerate(options):
        if st.button(f"**{chr(65+i)}.** {option}", key=f"q{current_q_idx}_opt{i}", use_container_width=True):
            # Record answer
            correct_idx = question_data.get('correct', 0)
            is_correct = i == correct_idx
            
            answer_record = {
                'question_index': current_q_idx,
                'selected': i,
                'correct': correct_idx,
                'is_correct': is_correct,
                'question': question_data['question'],
                'options': options,
                'explanation': question_data.get('explanation', 'No explanation available.'),
                'time_taken': (datetime.now() - quiz_state['question_start_time']).total_seconds()
            }
            
            st.session_state.quiz_state['user_answers'].append(answer_record)
            
            if is_correct:
                st.session_state.quiz_state['score'] += 10
                st.session_state.quiz_state['correct_answers'] += 1
            
            # Next question or results
            if current_q_idx < len(quiz_state['questions']) - 1:
                st.session_state.quiz_state['current_question'] += 1
                st.session_state.quiz_state['question_start_time'] = datetime.now()
            else:
                st.session_state.quiz_state['phase'] = 'results'
            
            st.rerun()

def get_performance_message(percentage, correct, total):
    """Generate performance message based on score"""
    if percentage >= 90:
        return f"🏆 Outstanding! You're a quiz champion! {correct}/{total} correct answers shows exceptional knowledge."
    elif percentage >= 80:
        return f"🌟 Excellent! Great job! You demonstrated solid understanding with {correct}/{total} correct answers."
    elif percentage >= 70:
        return f"👍 Good Work! Well done! {correct}/{total} correct shows good knowledge. Keep practicing to reach excellence."
    elif percentage >= 50:
        return f"📈 Keep Improving! You got {correct}/{total} correct. With more practice, you'll definitely improve!"
    else:
        return f"💪 Keep Learning! Don't worry! {correct}/{total} is a start. Practice makes perfect - try again to boost your score!"

def results_phase():
    """Display quiz results"""
    quiz_state = st.session_state.quiz_state
    
    st.markdown("# 🎯 Quiz Results")
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Score", f"{quiz_state['score']}/{len(quiz_state['questions']) * 10}")
    with col2:
        st.metric("✅ Correct", quiz_state['correct_answers'])
    with col3:
        st.metric("❌ Incorrect", len(quiz_state['questions']) - quiz_state['correct_answers'])
    with col4:
        accuracy = (quiz_state['correct_answers'] / len(quiz_state['questions'])) * 100
        st.metric("🎯 Accuracy", f"{accuracy:.1f}%")
    
    # Performance feedback
    message = get_performance_message(accuracy, quiz_state['correct_answers'], len(quiz_state['questions']))
    if accuracy >= 80:
        st.success(message)
    elif accuracy >= 60:
        st.info(message)
    else:
        st.warning(message)
    
    # Quiz mode indicator
    mode_indicator = "🤖 AI-Generated" if quiz_state.get('quiz_mode') == 'ai' else "📚 Question Bank"
    topic_display = quiz_state.get('ai_topic', quiz_state.get('programming_language', quiz_state.get('category', 'Mixed')))
    st.info(f"**Quiz Mode:** {mode_indicator} | **Topic:** {topic_display}")
    
    st.markdown("---")
    
    # Detailed analysis
    st.markdown("## 📝 Detailed Analysis")
    
    for i, answer_data in enumerate(quiz_state['user_answers']):
        with st.expander(f"Question {i+1}: {'✅ Correct' if answer_data['is_correct'] else '❌ Incorrect'}"):
            st.markdown(f"**Q:** {answer_data['question']}")
            
            # Show options with indicators
            for opt_idx, option in enumerate(answer_data['options']):
                if opt_idx == answer_data['correct']:
                    st.success(f"✅ **{chr(65+opt_idx)}.** {option} *(Correct Answer)*")
                elif opt_idx == answer_data['selected']:
                    if answer_data['is_correct']:
                        st.success(f"✅ **{chr(65+opt_idx)}.** {option} *(Your Answer)*")
                    else:
                        st.error(f"❌ **{chr(65+opt_idx)}.** {option} *(Your Answer)*")
                else:
                    st.info(f"**{chr(65+opt_idx)}.** {option}")
            
            # Explanation
            st.info(f"💡 **Explanation:** {answer_data['explanation']}")
            
            # Time taken
            if 'time_taken' in answer_data:
                st.caption(f"⏱️ Time taken: {answer_data['time_taken']:.1f} seconds")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🏠 Back to Home", use_container_width=True):
            # Completely reset session state to go back to main menu
            st.session_state.quiz_state = {
                'phase': 'setup',
                'quiz_mode': '',
                'category': '',
                'programming_language': '',
                'ai_topic': '',
                'difficulty': 'medium',
                'num_questions': 5,
                'timer_duration': 15,
                'questions': [],
                'current_question': 0,
                'score': 0,
                'correct_answers': 0,
                'user_answers': [],
                'start_time': None,
                'question_start_time': None,
                'selected_answer': None,
                'show_explanation': False,
                'time_up': False,
                'generating_questions': False,
                'generation_progress': 0,
                'generation_status': ''
            }
            st.rerun()
    
    with col2:
        if st.button("🔄 Retry Same Quiz", use_container_width=True, type="primary"):
            # Reset for same configuration
            current_mode = quiz_state.get('quiz_mode')
            
            # Keep current settings but reset quiz data
            st.session_state.quiz_state.update({
                'current_question': 0,
                'score': 0,
                'correct_answers': 0,
                'user_answers': [],
                'start_time': datetime.now(),
                'question_start_time': datetime.now(),
                'selected_answer': None,
                'show_explanation': False,
                'time_up': False
            })
            
            if current_mode == 'ai':
                # For AI quiz, go to generating phase
                st.session_state.quiz_state['phase'] = 'generating'
                st.session_state.quiz_state['questions'] = []
            else:
                # For static quiz, regenerate questions and start immediately
                st.session_state.quiz_state['questions'] = generate_static_questions()
                st.session_state.quiz_state['phase'] = 'quiz'
            
            st.rerun()
    
    with col3:
        if st.button("📊 New Quiz", use_container_width=True):
            # Reset everything and go back to setup for new quiz selection
            st.session_state.quiz_state = {
                'phase': 'setup',
                'quiz_mode': '',
                'category': '',
                'programming_language': '',
                'ai_topic': '',
                'difficulty': 'medium',
                'num_questions': 5,
                'timer_duration': 15,
                'questions': [],
                'current_question': 0,
                'score': 0,
                'correct_answers': 0,
                'user_answers': [],
                'start_time': None,
                'question_start_time': None,
                'selected_answer': None,
                'show_explanation': False,
                'time_up': False,
                'generating_questions': False,
                'generation_progress': 0,
                'generation_status': ''
            }
            st.rerun()

def run_quiz():
    """Main function to run the quiz"""
    init_quiz_session_state()
    
    phase = st.session_state.quiz_state['phase']
    
    if phase == 'setup':
        setup_phase()
    elif phase == 'programming_language':
        programming_language_selection()
    elif phase == 'programming_settings':
        programming_settings_phase()
    elif phase == 'generating':
        generating_phase()
    elif phase == 'quiz':
        quiz_phase()
    elif phase == 'results':
        results_phase()
    else:
        st.error(f"Unknown phase: {phase}")
        init_quiz_session_state()
        st.rerun()

if __name__ == "__main__":
    st.set_page_config(
        page_title="AI-Powered Quiz System",
        page_icon="🤖",
        layout="wide"
    )
    run_quiz()