"""
CareerIQ - Main Application
"""
import streamlit as st
import time
from PIL import Image
from datetime import datetime
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx import Document
import io
import base64
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
from config.courses import COURSES_BY_CATEGORY, RESUME_VIDEOS, INTERVIEW_VIDEOS, get_courses_for_role, get_category_for_role
from config.job_roles import JOB_ROLES
from config.database import (
    get_database_connection, save_resume_data, save_analysis_data,
    init_database, verify_admin, log_admin_action, save_ai_analysis_data,
    get_ai_analysis_stats, reset_ai_analysis_stats, get_detailed_ai_analysis_stats
)
from ui_components import (
    apply_modern_styles, hero_section, feature_card, about_section,
    page_header, render_analytics_section, render_activity_section,
    render_suggestions_section
)
from jobs.job_search import render_job_search
from feedback.feedback import FeedbackManager
from dashboard.dashboard import DashboardManager
from utils.ai_resume_analyzer import AIResumeAnalyzer
from utils.resume_builder import ResumeBuilder
from utils.resume_analyzer import ResumeAnalyzer
import traceback
import plotly.express as px
import pandas as pd
import json
import datetime
from dotenv import load_dotenv
import os
from smartQuiz.aimocktest import run_quiz 

load_dotenv()  # Load from .env file
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    raise Exception("Google API key not found. Please set it in your .env file.")


# Set page config at the very beginning
st.set_page_config(
    page_title="CareerIQ",
    layout="wide"
)

class ResumeApp:
    def __init__(self):
        """Initialize the application"""
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                'personal_info': {
                    'full_name': '',
                    'email': '',
                    'phone': '',
                    'location': '',
                    'linkedin': '',
                    'portfolio': ''
                },
                'summary': '',
                'experiences': [],
                'education': [],
                'projects': [],
                'skills_categories': {
                    'technical': [],
                    'soft': [],
                    'languages': [],
                    'tools': []
                }
            }

        # Initialize navigation state 
        if 'page' not in st.session_state:
            st.session_state.page = 'home'

        # Initialize admin state
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False

        self.pages = {
            "🏠 HOME": self.render_home,
            "📊 DASHBOARD": self.render_dashboard,
            "📝 RESUME BUILDER": self.render_builder,
            "🔍 RESUME ANALYZER": self.render_analyzer,
            "🎯 JOB SEARCH": self.render_job_search,
            "🧩 Smart Quiz ": self.render_quiz, 
            "💬 FEEDBACK": self.render_feedback_page
        }

        # Initialize dashboard manager
        self.dashboard_manager = DashboardManager()
        self.analyzer = ResumeAnalyzer()
        self.ai_analyzer = AIResumeAnalyzer()
        self.builder = ResumeBuilder()
        self.job_roles = JOB_ROLES

        # Initialize session state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'default_user'
        if 'selected_role' not in st.session_state:
            st.session_state.selected_role = None

        # Initialize database
        init_database()

        # Load external CSS
        with open('style/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

        # Load Google Fonts
        st.markdown("""
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        """, unsafe_allow_html=True)

        if 'resume_data' not in st.session_state:
            st.session_state.resume_data = []
        if 'ai_analysis_stats' not in st.session_state:
            st.session_state.ai_analysis_stats = {
                'score_distribution': {},
                'total_analyses': 0,
                'average_score': 0
            }

    def load_lottie_url(self, url: str):
        """Load Lottie animation from URL"""
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    

    def apply_global_styles(self):
        st.markdown("""
        <style>
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #1a1a1a;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: #4CAF50;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #45a049;
        }

        /* Global Styles */
        .main-header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent 0%, rgba(255,255,255,0.1) 100%);
            z-index: 1;
        }

        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 600;
            margin: 0;
            position: relative;
            z-index: 2;
        }

        /* Template Card Styles */
        .template-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
            padding: 1rem;
        }

        .template-card {
            background: rgba(45, 45, 45, 0.9);
            border-radius: 20px;
            padding: 2rem;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .template-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            border-color: #4CAF50;
        }

        .template-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent 0%, rgba(76,175,80,0.1) 100%);
            z-index: 1;
        }

        .template-icon {
            font-size: 3rem;
            color: #4CAF50;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
        }

        .template-title {
            font-size: 1.8rem;
            font-weight: 600;
            color: white;
            margin-bottom: 1rem;
            position: relative;
            z-index: 2;
        }

        .template-description {
            color: #aaa;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
            line-height: 1.6;
        }

        /* Feature List Styles */
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 1.5rem 0;
            position: relative;
            z-index: 2;
        }

        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            color: #ddd;
            font-size: 0.95rem;
        }

        .feature-icon {
            color: #4CAF50;
            margin-right: 0.8rem;
            font-size: 1.1rem;
        }

        /* Button Styles */
        .action-button {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            width: 100%;
            text-align: center;
            position: relative;
            overflow: hidden;
            z-index: 2;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(76,175,80,0.3);
        }

        .action-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
            transition: all 0.6s ease;
        }

        .action-button:hover::before {
            left: 100%;
        }

        /* Form Section Styles */
        .form-section {
            background: rgba(45, 45, 45, 0.9);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .form-section-title {
            font-size: 1.8rem;
            font-weight: 600;
            color: white;
            margin-bottom: 1.5rem;
            padding-bottom: 0.8rem;
            border-bottom: 2px solid #4CAF50;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-label {
            color: #ddd;
            font-weight: 500;
            margin-bottom: 0.8rem;
            display: block;
        }

        .form-input {
            width: 100%;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(30, 30, 30, 0.9);
            color: white;
            transition: all 0.3s ease;
        }

        .form-input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 2px rgba(76,175,80,0.2);
            outline: none;
        }

        /* Skill Tags */
        .skill-tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .skill-tag {
            background: rgba(76,175,80,0.1);
            color: #4CAF50;
            padding: 0.6rem 1.2rem;
            border-radius: 50px;
            border: 1px solid #4CAF50;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .skill-tag:hover {
            background: #4CAF50;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76,175,80,0.2);
        }

        /* Progress Circle */
        .progress-container {
            position: relative;
            width: 150px;
            height: 150px;
            margin: 2rem auto;
        }

        .progress-circle {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }

        .progress-circle circle {
            fill: none;
            stroke-width: 8;
            stroke-linecap: round;
            stroke: #4CAF50;
            transform-origin: 50% 50%;
            transition: all 0.3s ease;
        }

        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.5rem;
            font-weight: 600;
            color: white;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .feature-card {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .animate-slide-in {
            animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .template-container {
                grid-template-columns: 1fr;
            }

            .main-header {
                padding: 1.5rem;
            }

            .main-header h1 {
                font-size: 2rem;
            }

            .template-card {
                padding: 1.5rem;
            }

            .action-button {
                padding: 0.8rem 1.6rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
    def render_quiz(self):
        """Render the AI Quiz page"""
        try:
            # Add a header for consistency with your app
            apply_modern_styles()
    
        # Page Header
            page_header(
            "AI-Powered Quiz",
            "Choose your preferred learning experience and challenge yourself across various domains with our advanced assessment system."
        )
            st.markdown("""
    <style>
    /* Center align and style tab container */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 20px;
        gap: 10px;
    }

    /* Base style for each tab */
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: 600;
        color: #333;
        transition: all 0.2s ease-in-out;
    }

    /* Hover effect */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0f5ec;
        border-color: #00bfa5;
        color: #111;
        transform: translateY(-2px);
        cursor: pointer;
    }

    /* Selected/active tab style */
    .stTabs [aria-selected="true"] {
        background-color: #00bfa5 !important;
        color: white !important;
        border: 1px solid #00bfa5;
        font-weight: 700;
        box-shadow: 0px 4px 12px rgba(0, 191, 165, 0.2);
    }
    </style>
""", unsafe_allow_html=True)
            st.markdown("---")
            
            # Call the quiz function
            run_quiz()
            
        except Exception as e:
            st.error(f"❌ Error loading quiz: {str(e)}")
            st.info("Please ensure the quiz module is properly configured.")
            
            # Optional: Add a refresh button
            if st.button("🔄 Refresh Quiz"):
                st.rerun()

    def add_footer(self):
        """Add a footer to all pages"""
        st.markdown("<hr style='margin-top: 50px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
        st.markdown("""
            <div style='text-align: center; font-family: Arial, sans-serif;'>
                <p style='margin: 5px 0;'>
                    Powered by <strong>Streamlit</strong> & <strong>Google Gemini AI</strong>
                </p>
                <p style='margin: 5px 0; font-size: 15px;'>
                    Developed With By 
                    <strong>Aksh Patel</strong> | <strong>Ayush Patel</strong> | <strong>Prinsi Patel</strong> | <strong>Prerna Patel</strong>
                </p>
                <p style='font-size: 12px; color: #888888; margin-top: 10px;'>
                    "Every star counts! If you find this project helpful, please consider starring the repo to help it reach more people."
                </p>
            </div>
        """, unsafe_allow_html=True)

    def render_dashboard(self):
        """Render the dashboard page"""
        self.dashboard_manager.render_dashboard()


    def render_empty_state(self, icon, message):
        """Render an empty state with icon and message"""
        return f"""
            <div style='text-align: center; padding: 2rem; color: #666;'>
                <i class='{icon}' style='font-size: 2rem; margin-bottom: 1rem; color: #00bfa5;'></i>
                <p style='margin: 0;'>{message}</p>
            </div>
        """

    def analyze_resume(self, resume_text):
        """Analyze resume and store results"""
        analytics = self.analyzer.analyze_resume(resume_text)
        st.session_state.analytics_data = analytics
        return analytics


    def render_builder(self):
        apply_modern_styles()
    
        # Page Header
        page_header(
            "Resume Builder",
            "Create your professional resume"
        )
        st.markdown("""
    <style>
    /* Center align and style tab container */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 20px;
        gap: 10px;
    }

    /* Base style for each tab */
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: 600;
        color: #333;
        transition: all 0.2s ease-in-out;
    }

    /* Hover effect */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0f5ec;
        border-color: #00bfa5;
        color: #111;
        transform: translateY(-2px);
        cursor: pointer;
    }

    /* Selected/active tab style */
    .stTabs [aria-selected="true"] {
        background-color: #00bfa5 !important;
        color: white !important;
        border: 1px solid #00bfa5;
        font-weight: 700;
        box-shadow: 0px 4px 12px rgba(0, 191, 165, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

        

        # Template selection
        template_options = ["Modern", "Professional", "Minimal", "Creative"]
        selected_template = st.selectbox(
    "Select Resume Template", template_options)
        st.success(f"🎨 Currently using: {selected_template} Template")

        # Personal Information
        st.subheader("Personal Information")

        col1, col2 = st.columns(2)
        with col1:
            # Get existing values from session state
            existing_name = st.session_state.form_data['personal_info']['full_name']
            existing_email = st.session_state.form_data['personal_info']['email']
            existing_phone = st.session_state.form_data['personal_info']['phone']

            # Input fields with existing values
            full_name = st.text_input("Full Name", value=existing_name)
            email = st.text_input(
    "Email",
    value=existing_email,
     key="email_input")
            phone = st.text_input("Phone", value=existing_phone)

            # Immediately update session state after email input
            if 'email_input' in st.session_state:
                st.session_state.form_data['personal_info']['email'] = st.session_state.email_input

        with col2:
            # Get existing values from session state
            existing_location = st.session_state.form_data['personal_info']['location']
            existing_linkedin = st.session_state.form_data['personal_info']['linkedin']
            existing_portfolio = st.session_state.form_data['personal_info']['portfolio']

            # Input fields with existing values
            location = st.text_input("Location", value=existing_location)
            linkedin = st.text_input("LinkedIn URL", value=existing_linkedin)
            portfolio = st.text_input(
    "Portfolio Website", value=existing_portfolio)

        # Update personal info in session state
        st.session_state.form_data['personal_info'] = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'location': location,
            'linkedin': linkedin,
            'portfolio': portfolio
        }

        # Professional Summary
        st.subheader("Professional Summary")
        summary = st.text_area("Professional Summary", value=st.session_state.form_data.get('summary', ''), height=150,
                             help="Write a brief summary highlighting your key skills and experience")

        # Experience Section
        st.subheader("Work Experience")
        if 'experiences' not in st.session_state.form_data:
            st.session_state.form_data['experiences'] = []

        if st.button("Add Experience"):
            st.session_state.form_data['experiences'].append({
                'company': '',
                'position': '',
                'start_date': '',
                'end_date': '',
                'description': '',
                'responsibilities': [],
                'achievements': []
            })

        for idx, exp in enumerate(st.session_state.form_data['experiences']):
            with st.expander(f"Experience {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    exp['company'] = st.text_input(
    "Company Name",
    key=f"company_{idx}",
    value=exp.get(
        'company',
         ''))
                    exp['position'] = st.text_input(
    "Position", key=f"position_{idx}", value=exp.get(
        'position', ''))
                with col2:
                    exp['start_date'] = st.text_input(
    "Start Date", key=f"start_date_{idx}", value=exp.get(
        'start_date', ''))
                    exp['end_date'] = st.text_input(
    "End Date", key=f"end_date_{idx}", value=exp.get(
        'end_date', ''))

                exp['description'] = st.text_area("Role Overview", key=f"desc_{idx}",
                                                value=exp.get(
                                                    'description', ''),
                                                help="Brief overview of your role and impact")

                # Responsibilities
                st.markdown("##### Key Responsibilities")
                resp_text = st.text_area("Enter responsibilities (one per line)",
                                       key=f"resp_{idx}",
                                       value='\n'.join(
                                           exp.get('responsibilities', [])),
                                       height=100,
                                       help="List your main responsibilities, one per line")
                exp['responsibilities'] = [r.strip()
                                                   for r in resp_text.split('\n') if r.strip()]

                # Achievements
                st.markdown("##### Key Achievements")
                achv_text = st.text_area("Enter achievements (one per line)",
                                       key=f"achv_{idx}",
                                       value='\n'.join(
                                           exp.get('achievements', [])),
                                       height=100,
                                       help="List your notable achievements, one per line")
                exp['achievements'] = [a.strip()
                                               for a in achv_text.split('\n') if a.strip()]

                if st.button("Remove Experience", key=f"remove_exp_{idx}"):
                    st.session_state.form_data['experiences'].pop(idx)
                    st.rerun()

        # Projects Section
        st.subheader("Projects")
        if 'projects' not in st.session_state.form_data:
            st.session_state.form_data['projects'] = []

        if st.button("Add Project"):
            st.session_state.form_data['projects'].append({
                'name': '',
                'technologies': '',
                'description': '',
                'responsibilities': [],
                'achievements': [],
                'link': ''
            })

        for idx, proj in enumerate(st.session_state.form_data['projects']):
            with st.expander(f"Project {idx + 1}", expanded=True):
                proj['name'] = st.text_input(
    "Project Name",
    key=f"proj_name_{idx}",
    value=proj.get(
        'name',
         ''))
                proj['technologies'] = st.text_input("Technologies Used", key=f"proj_tech_{idx}",
                                                   value=proj.get(
                                                       'technologies', ''),
                                                   help="List the main technologies, frameworks, and tools used")

                proj['description'] = st.text_area("Project Overview", key=f"proj_desc_{idx}",
                                                 value=proj.get(
                                                     'description', ''),
                                                 help="Brief overview of the project and its goals")

                # # Project Responsibilities
                # st.markdown("##### Key Responsibilities")
                # proj_resp_text = st.text_area("Enter responsibilities (one per line)",
                #                             key=f"proj_resp_{idx}",
                #                             value='\n'.join(
                #                                 proj.get('responsibilities', [])),
                #                             height=100,
                #                             help="List your main responsibilities in the project")
                # proj['responsibilities'] = [r.strip()
                #                                     for r in proj_resp_text.split('\n') if r.strip()]

                # # Project Achievements
                # st.markdown("##### Key Achievements")
                # proj_achv_text = st.text_area("Enter achievements (one per line)",
                #                             key=f"proj_achv_{idx}",
                #                             value='\n'.join(
                #                                 proj.get('achievements', [])),
                #                             height=100,
                #                             help="List the project's key achievements and your contributions")
                # proj['achievements'] = [a.strip()
                #                                 for a in proj_achv_text.split('\n') if a.strip()]

                # proj['link'] = st.text_input("Project Link (optional)", key=f"proj_link_{idx}",
                #                            value=proj.get('link', ''),
                #                            help="Link to the project repository, demo, or documentation")

                # if st.button("Remove Project", key=f"remove_proj_{idx}"):
                #     st.session_state.form_data['projects'].pop(idx)
                #     st.rerun()

        # Education Section
        st.subheader("Education")
        if 'education' not in st.session_state.form_data:
            st.session_state.form_data['education'] = []

        if st.button("Add Education"):
            st.session_state.form_data['education'].append({
                'school': '',
                'degree': '',
                'field': '',
                'graduation_date': '',
                'gpa': '',
                'achievements': []
            })

        for idx, edu in enumerate(st.session_state.form_data['education']):
            with st.expander(f"Education {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    edu['school'] = st.text_input(
    "School/University",
    key=f"school_{idx}",
    value=edu.get(
        'school',
         ''))
                    edu['degree'] = st.text_input(
    "Degree", key=f"degree_{idx}", value=edu.get(
        'degree', ''))
                with col2:
                    edu['field'] = st.text_input(
    "Field of Study",
    key=f"field_{idx}",
    value=edu.get(
        'field',
         ''))
                    edu['graduation_date'] = st.text_input("Graduation Date", key=f"grad_date_{idx}",
                                                         value=edu.get('graduation_date', ''))

                edu['gpa'] = st.text_input(
    "GPA (optional)",
    key=f"gpa_{idx}",
    value=edu.get(
        'gpa',
         ''))

                # Educational Achievements
                st.markdown("##### Achievements & Activities")
                edu_achv_text = st.text_area("Enter achievements (one per line)",
                                           key=f"edu_achv_{idx}",
                                           value='\n'.join(
                                               edu.get('achievements', [])),
                                           height=100,
                                           help="List academic achievements, relevant coursework, or activities")
                edu['achievements'] = [a.strip()
                                               for a in edu_achv_text.split('\n') if a.strip()]

                if st.button("Remove Education", key=f"remove_edu_{idx}"):
                    st.session_state.form_data['education'].pop(idx)
                    st.rerun()

        # Skills Section
        st.subheader("Skills")
        if 'skills_categories' not in st.session_state.form_data:
            st.session_state.form_data['skills_categories'] = {
                'technical': [],
                'soft': [],
                'languages': [],
                'tools': []
            }

        col1, col2 = st.columns(2)
        with col1:
            tech_skills = st.text_area("Technical Skills (one per line)",
                                     value='\n'.join(
    st.session_state.form_data['skills_categories']['technical']),
                                     height=150,
                                     help="Programming languages, frameworks, databases, etc.")
            st.session_state.form_data['skills_categories']['technical'] = [
                s.strip() for s in tech_skills.split('\n') if s.strip()]

            soft_skills = st.text_area("Soft Skills (one per line)",
                                     value='\n'.join(
    st.session_state.form_data['skills_categories']['soft']),
                                     height=150,
                                     help="Leadership, communication, problem-solving, etc.")
            st.session_state.form_data['skills_categories']['soft'] = [
                s.strip() for s in soft_skills.split('\n') if s.strip()]

        with col2:
            languages = st.text_area("Languages (one per line)",
                                   value='\n'.join(
    st.session_state.form_data['skills_categories']['languages']),
                                   height=150,
                                   help="Programming or human languages with proficiency level")
            st.session_state.form_data['skills_categories']['languages'] = [
                l.strip() for l in languages.split('\n') if l.strip()]

            tools = st.text_area("Tools & Technologies (one per line)",
                               value='\n'.join(
    st.session_state.form_data['skills_categories']['tools']),
                               height=150,
                               help="Development tools, software, platforms, etc.")
            st.session_state.form_data['skills_categories']['tools'] = [
                t.strip() for t in tools.split('\n') if t.strip()]

        # Update form data in session state
        st.session_state.form_data.update({
            'summary': summary
        })
        
        # Custom Sections
        st.subheader("Custom Sections")
        
        if 'custom_sections' not in st.session_state.form_data:
            st.session_state.form_data['custom_sections'] = []
        
        if st.button("Add More Sections "):
            st.session_state.form_data['custom_sections'].append({
                'section_name': '',
                'items': []
            })
        
        for section_idx, custom_section in enumerate(st.session_state.form_data['custom_sections']):
            with st.expander(f"Custom Section {section_idx + 1}", expanded=True):
                # Section name
                custom_section['section_name'] = st.text_input(
                    "Section Name", 
                    key=f"custom_section_name_{section_idx}",
                    value=custom_section.get('section_name', ''),
                    help="e.g., Certifications, Awards, Volunteer Work, Publications"
                )
                
                # Initialize items if not exists
                if 'items' not in custom_section:
                    custom_section['items'] = []
                
                # Add item button
                if st.button(f"Add Item to {custom_section.get('section_name', 'Section')}", key=f"add_item_{section_idx}"):
                    custom_section['items'].append({
                        'title': '',
                        'details': '',
                        'date': '',
                        'description': ''
                    })
                
                # Display items
                for item_idx, item in enumerate(custom_section['items']):
                    st.markdown(f"**Item {item_idx + 1}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        item['title'] = st.text_input(
                            "Title/Name", 
                            key=f"custom_item_title_{section_idx}_{item_idx}",
                            value=item.get('title', ''),
                            help="e.g., Certificate name, Award title, Organization name"
                        )
                    with col2:
                        item['date'] = st.text_input(
                            "Date (optional)", 
                            key=f"custom_item_date_{section_idx}_{item_idx}",
                            value=item.get('date', ''),
                            help="When you received/completed this"
                        )
                    
                    item['details'] = st.text_input(
                        "Details/Organization", 
                        key=f"custom_item_details_{section_idx}_{item_idx}",
                        value=item.get('details', ''),
                        help="Issuing organization, location, or additional details"
                    )
                    
                    item['description'] = st.text_area(
                        "Description (optional)", 
                        key=f"custom_item_desc_{section_idx}_{item_idx}",
                        value=item.get('description', ''),
                        height=80,
                        help="Brief description of the achievement, work, or certification"
                    )
                    
                    if st.button(f"Remove Item", key=f"remove_custom_item_{section_idx}_{item_idx}"):
                        custom_section['items'].pop(item_idx)
                        st.rerun()
                    
                    st.divider()
                
                if st.button(f"Remove Section", key=f"remove_custom_section_{section_idx}"):
                    st.session_state.form_data['custom_sections'].pop(section_idx)
                    st.rerun()
                
                st.markdown("---")
                

        # Generate Resume button
        if st.columns([1,2,1])[1].button("📄 Generate Resume", type="primary", use_container_width=True):
            print("Validating form data...")
            print(f"Session state form data: {st.session_state.form_data}")
            print(
    f"Email input value: {
        st.session_state.get(
            'email_input',
             '')}")

            # Get the current values from form
            current_name = st.session_state.form_data['personal_info']['full_name'].strip(
            )
            current_email = st.session_state.email_input if 'email_input' in st.session_state else ''

            print(f"Current name: {current_name}")
            print(f"Current email: {current_email}")

            # Validate required fields
            if not current_name:
                st.error("⚠️ Please enter your full name.")
                return

            if not current_email:
                st.error("⚠️ Please enter your email address.")
                return

            # Update email in form data one final time
            st.session_state.form_data['personal_info']['email'] = current_email

            try:
                print("Preparing resume data...")
                # Prepare resume data with current form values
                resume_data = {
                    "personal_info": st.session_state.form_data['personal_info'],
                    "summary": st.session_state.form_data.get('summary', '').strip(),
                    "experience": st.session_state.form_data.get('experiences', []),
                    "education": st.session_state.form_data.get('education', []),
                    "projects": st.session_state.form_data.get('projects', []),
                    "skills": st.session_state.form_data.get('skills_categories', {
                        'technical': [],
                        'soft': [],
                        'languages': [],
                        'tools': []
                    }),
                    "template": selected_template
                }

                print(f"Resume data prepared: {resume_data}")

                try:
                    # Generate resume
                    resume_buffer = self.builder.generate_resume(resume_data)
                    if resume_buffer:
                        try:
                            # Save resume data to database
                            save_resume_data(resume_data)

                            # Offer the resume for download
                            st.success("✅ Resume generated successfully!")

                      
                            st.download_button(
                                label="Download Resume 📥",
                                data=resume_buffer,
                                file_name=f"{
    current_name.replace(
        ' ', '_')}_resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            )
                        except Exception as db_error:
                            print(
    f"Warning: Failed to save to database: {
        str(db_error)}")
                            # Still allow download even if database save fails
                            st.warning(
                                "⚠️ Resume generated but couldn't be saved to database")
                            

                            st.download_button(
                                label="Download Resume 📥",
                                data=resume_buffer,
                                file_name=f"{
    current_name.replace(
        ' ', '_')}_resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            )
                    else:
                        st.error(
                            "❌ Failed to generate resume. Please try again.")
                        print("Resume buffer was None")
                except Exception as gen_error:
                    print(f"Error during resume generation: {str(gen_error)}")
                    print(f"Full traceback: {traceback.format_exc()}")
                    st.error(f"❌ Error generating resume: {str(gen_error)}")

            except Exception as e:
                print(f"Error preparing resume data: {str(e)}")
                print(f"Full traceback: {traceback.format_exc()}")
                st.error(f"❌ Error preparing resume data: {str(e)}")

    
    def render_analyzer(self):
        """Render the resume analyzer page"""
        apply_modern_styles()
    
        # Page Header
        page_header(
            "Resume Analyzer",
            "Get instant AI-powered feedback to optimize your resume"
        )
        st.markdown("""
    <style>
    /* Center align and style tab container */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 20px;
        gap: 10px;
    }

    /* Base style for each tab */
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: 600;
        color: #333;
        transition: all 0.2s ease-in-out;
    }

    /* Hover effect */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0f5ec;
        border-color: #00bfa5;
        color: #111;
        transform: translateY(-2px);
        cursor: pointer;
    }

    /* Selected/active tab style */
    .stTabs [aria-selected="true"] {
        background-color: #00bfa5 !important;
        color: white !important;
        border: 1px solid #00bfa5;
        font-weight: 700;
        box-shadow: 0px 4px 12px rgba(0, 191, 165, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

        # Create tabs for Normal Analyzer and AI Analyzer
        analyzer_tabs = st.tabs(["Standard Analyzer", "AI Analyzer"])

        with analyzer_tabs[0]:
            # Job Role Selection
            categories = list(self.job_roles.keys())
            selected_category = st.selectbox(
    "Job Category", categories, key="standard_category")

            roles = list(self.job_roles[selected_category].keys())
            selected_role = st.selectbox(
    "Specific Role", roles, key="standard_role")

            role_info = self.job_roles[selected_category][selected_role]

            # Display role information
            st.markdown(f"""
            <div style='background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h3>{selected_role}</h3>
                <p>{role_info['description']}</p>
                <h4>Required Skills:</h4>
                <p>{', '.join(role_info['required_skills'])}</p>
            </div>
            """, unsafe_allow_html=True)

            # File Upload
            uploaded_file = st.file_uploader(
    "Upload your resume", type=[
        'pdf', 'docx'], key="standard_file")

            if not uploaded_file:
                # Display empty state with a prominent upload button
                st.markdown(
                    self.render_empty_state(
                    "fas fa-cloud-upload-alt",
                    "Upload your resume to get started with standard analysis"
                    ),
                    unsafe_allow_html=True
                )
                # Add a prominent upload button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown("""
                    <style>
                    .upload-button {
                        background: linear-gradient(90deg, #4b6cb7, #182848);
                        color: white;
                        border: none;
                        border-radius: 10px;
                        padding: 15px 25px;
                        font-size: 18px;
                        font-weight: bold;
                        cursor: pointer;
                        width: 100%;
                        text-align: center;
                        margin: 20px 0;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                        transition: all 0.3s ease;
                    }
                    .upload-button:hover {
                        transform: translateY(-3px);
                        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
                    }

                    """, unsafe_allow_html=True)

            if uploaded_file:
                # Add a prominent analyze button
                analyze_standard = st.button("🔍 Analyze My Resume",
                                    type="primary",
                                    use_container_width=True,
                                    key="analyze_standard_button")

                if analyze_standard:
                    with st.spinner("Analyzing your document..."):
                        # Get file content
                        text = ""
                        try:
                            if uploaded_file.type == "application/pdf":
                                try:
                                    text = self.analyzer.extract_text_from_pdf(uploaded_file)
                                except Exception as pdf_error:
                                    st.error(f"PDF extraction failed: {str(pdf_error)}")
                                    st.info("Trying alternative PDF extraction method...")
                                    # Try AI analyzer as backup
                                    try:
                                        text = self.ai_analyzer.extract_text_from_pdf(uploaded_file)
                                    except Exception as backup_error:
                                        st.error(f"All PDF extraction methods failed: {str(backup_error)}")
                                        return
                            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                try:
                                    text = self.analyzer.extract_text_from_docx(uploaded_file)
                                except Exception as docx_error:
                                    st.error(f"DOCX extraction failed: {str(docx_error)}")
                                    # Try AI analyzer as backup
                                    try:
                                        text = self.ai_analyzer.extract_text_from_docx(uploaded_file)
                                    except Exception as backup_error:
                                        st.error(f"All DOCX extraction methods failed: {str(backup_error)}")
                                        return
                            else:
                                text = uploaded_file.getvalue().decode()
                                
                            if not text or text.strip() == "":
                                st.error("Could not extract any text from the uploaded file. Please try a different file.")
                                return
                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")
                            return

                        # Analyze the document
                        analysis = self.analyzer.analyze_resume({'raw_text': text}, role_info)
                        
                        # Check if analysis returned an error
                        if 'error' in analysis:
                            st.error(analysis['error'])
                            return


                        # Save resume data to database
                        resume_data = {
                            'personal_info': {
                                'name': analysis.get('name', ''),
                                'email': analysis.get('email', ''),
                                'phone': analysis.get('phone', ''),
                                'linkedin': analysis.get('linkedin', ''),
                                'github': analysis.get('github', ''),
                                'portfolio': analysis.get('portfolio', '')
                            },
                            'summary': analysis.get('summary', ''),
                            'target_role': selected_role,
                            'target_category': selected_category,
                            'education': analysis.get('education', []),
                            'experience': analysis.get('experience', []),
                            'projects': analysis.get('projects', []),
                            'skills': analysis.get('skills', []),
                            'template': ''
                        }

                        # Save to database
                        try:
                            resume_id = save_resume_data(resume_data)

                            # Save analysis data
                            analysis_data = {
                                'resume_id': resume_id,
                                'ats_score': analysis['ats_score'],
                                'keyword_match_score': analysis['keyword_match']['score'],
                                'format_score': analysis['format_score'],
                                'section_score': analysis['section_score'],
                                'missing_skills': ','.join(analysis['keyword_match']['missing_skills']),
                                'recommendations': ','.join(analysis['suggestions'])
                            }
                            save_analysis_data(resume_id, analysis_data)
                            st.success("Resume data saved successfully!")
                        except Exception as e:
                            st.error(f"Error saving to database: {str(e)}")
                            print(f"Database error: {e}")

                        # Show results based on document type
                        if analysis.get('document_type') != 'resume':
                            st.error(
    f"⚠️ This appears to be a {
        analysis['document_type']} document, not a resume!")
                            st.warning(
                                "Please upload a proper resume for ATS analysis.")
                            return
                     
                    st.markdown("---")
                    st.markdown("## 📊 Analysis Results")
                    
                    # === TOP METRICS ROW ===
                    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                    
                    with metrics_col1:
                        # ATS Score with color coding
                        ats_score = analysis['ats_score']
                        score_color = '#4CAF50' if ats_score >= 80 else '#FFA500' if ats_score >= 60 else '#FF4444'
                        status = 'Excellent' if ats_score >= 80 else 'Good' if ats_score >= 60 else 'Needs Improvement'
                        
                        st.markdown(f"""
                        <div class="metric-card" style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e1e1e, #2a2a2a); border-radius: 15px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                            <h3 style="color: #fff; margin-bottom: 15px;">🎯 ATS Score</h3>
                            <div style="font-size: 2.5em; font-weight: bold; color: {score_color};">{ats_score}</div>
                            <div style="color: {score_color}; font-weight: bold; margin-top: 5px;">{status}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
                    with metrics_col2:
                        keyword_score = int(analysis.get('keyword_match', {}).get('score', 0))
                        st.markdown(f"""
                        <div class="metric-card" style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e1e1e, #2a2a2a); border-radius: 15px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                            <h3 style="color: #fff; margin-bottom: 15px;">🔍 Keywords</h3>
                            <div style="font-size: 2.5em; font-weight: bold; color: #64B5F6;">{keyword_score}%</div>
                            <div style="color: #64B5F6; font-weight: bold; margin-top: 5px;">Match Rate</div>
                        </div>
                        """, unsafe_allow_html=True)
            
                    with metrics_col3:
                        format_score = int(analysis.get('format_score', 0))
                        st.markdown(f"""
                        <div class="metric-card" style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e1e1e, #2a2a2a); border-radius: 15px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                            <h3 style="color: #fff; margin-bottom: 15px;">📄 Format</h3>
                            <div style="font-size: 2.5em; font-weight: bold; color: #81C784;">{format_score}%</div>
                            <div style="color: #81C784; font-weight: bold; margin-top: 5px;">Structure</div>
                        </div>
                        """, unsafe_allow_html=True)
            
                    with metrics_col4:
                        section_score = int(analysis.get('section_score', 0))
                        st.markdown(f"""
                        <div class="metric-card" style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e1e1e, #2a2a2a); border-radius: 15px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                            <h3 style="color: #fff; margin-bottom: 15px;">📋 Sections</h3>
                            <div style="font-size: 2.5em; font-weight: bold; color: #FFB74D;">{section_score}%</div>
                            <div style="color: #FFB74D; font-weight: bold; margin-top: 5px;">Complete</div>
                        </div>
                        """, unsafe_allow_html=True)
            
                    st.markdown("<br>", unsafe_allow_html=True)
            
            
                    # Main Feature Card Container
                    
                    st.markdown("## 📋 Resume Improvement Suggestions")
                    # Enhanced helper function to render each suggestion section
                    def render_section(title, suggestions, bullet_icon="✓", nested_items=None):
                        """
                        Render a suggestion section with optional nested items
                        """
                        if suggestions or nested_items:
                            st.markdown(f"""
                            <div style='
                                background-color: #1e1e1e;
                                padding: 5px;
                                border-radius: 12px;
                                margin-bottom: 5px;
                                border-left: 4px solid #4CAF50;
                            '>
                                <h3 style='color: #4CAF50; margin-bottom: 15px;'>{title}</h3>
                            """, unsafe_allow_html=True)
                            
                            # Main suggestions
                            if suggestions:
                                st.markdown("<ul style='list-style-type: none; padding-left: 0;'>", unsafe_allow_html=True)
                                for item in suggestions:
                                    st.markdown(f"""
                                        <li style='margin-bottom: 10px; color: #e0e0e0;'>
                                            <span style='color: #4CAF50; margin-right: 8px;'>{bullet_icon}</span>{item}
                                        </li>
                                    """, unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)
                            
                            # Nested items (for missing skills)
                            if nested_items:
                                
                                for skill in nested_items:
                                    st.markdown(f"""
                                        <li style='margin-bottom: 6px; margin-left: 15px; color: #ccc;'>
                                            <span style='color: #66BB6A; margin-right: 8px;'>•</span>{skill}
                                        </li>
                                    """, unsafe_allow_html=True)
                                st.markdown("</ul></div>", unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Render Each Section
                    render_section("📞 Contact Information", analysis.get('contact_suggestions', []))
                    render_section("📝 Professional Summary", analysis.get('summary_suggestions', []))
                    
                    # Skills section with nested missing skills
                    skills_suggestions = analysis.get('skills_suggestions', [])
                    missing_skills = analysis.get('keyword_match', {}).get('missing_skills', [])
                    render_section("🎯 Skills", skills_suggestions, nested_items=missing_skills)
                    
                    render_section("💼 Work Experience", analysis.get('experience_suggestions', []))
                    render_section("🎓 Education", analysis.get('education_suggestions', []))
                    render_section("📄 Formatting", analysis.get('format_suggestions', []))
                    
                    # Close main container
                    st.markdown("</div>", unsafe_allow_html=True)
                        # Course Recommendations
                    st.markdown("## 📚 Recommended Courses ")
                    

                        # Get courses based on role and category
                    courses = get_courses_for_role(selected_role)
                    if not courses:
                            category = get_category_for_role(selected_role)
                            courses = COURSES_BY_CATEGORY.get(
                                category, {}).get(selected_role, [])

                        # Display courses in a grid
                    cols = st.columns(2)
                    for i, course in enumerate(
                        courses[:6]):  # Show top 6 courses
                            with cols[i % 2]:
                                st.markdown(f"""
                                <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                                    <h4>{course[0]}</h4>
                                    <a href='{course[1]}' target='_blank'>View Course</a>
                                </div>
                                """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                        # Learning Resources
                    st.markdown("## 📺 Helpful Videos")
                            

                    tab1, tab2 = st.tabs(["Resume Tips", "Interview Tips"])

                    with tab1:
                            # Resume Videos
                            for category, videos in RESUME_VIDEOS.items():
                                st.subheader(category)
                                cols = st.columns(2)
                                for i, video in enumerate(videos):
                                    with cols[i % 2]:
                                        st.video(video[1])

                    with tab2:
                            # Interview Videos
                            for category, videos in INTERVIEW_VIDEOS.items():
                                st.subheader(category)
                                cols = st.columns(2)
                                for i, video in enumerate(videos):
                                    with cols[i % 2]:
                                        st.video(video[1])

                    st.markdown("</div>", unsafe_allow_html=True)

        with analyzer_tabs[1]:
            st.markdown("""
            <div style='background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h3>AI-Powered Resume Analysis</h3>
                <p>Get detailed insights from advanced AI models that analyze your resume and provide personalized recommendations.</p>
                <p><strong>Upload your resume to get AI-powered analysis and recommendations.</strong></p>
            </div>
            """, unsafe_allow_html=True)
             

            # AI Model Selection
            ai_model = st.selectbox(
                "Select AI Model",
                ["Google Gemini"],
                help="Choose the AI model to analyze your resume"
            )
             
            # Add job description input option
            use_custom_job_desc = st.checkbox("Use custom job description", value=False, 
                                             help="Enable this to provide a specific job description for more targeted analysis")
            
            custom_job_description = ""
            if use_custom_job_desc:
                custom_job_description = st.text_area(
                    "Paste the job description here",
                    height=200,
                    placeholder="Paste the full job description from the company here for more targeted analysis...",
                    help="Providing the actual job description will help the AI analyze your resume specifically for this position"
                )
                
                st.markdown("""
                <div style='background-color: #2e7d32; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                    <p><i class="fas fa-lightbulb"></i> <strong>Pro Tip:</strong> Including the actual job description significantly improves the accuracy of the analysis and provides more relevant recommendations tailored to the specific position.</p>
                </div>
                """, unsafe_allow_html=True)
            
                        # Add AI Analyzer Stats in an expander
            with st.expander("📊 AI Analyzer Statistics", expanded=False):
                try:
                    # Add a reset button for admin users
                    if st.session_state.get('is_admin', False):
                        if st.button(
    "🔄 Reset AI Analysis Statistics",
    type="secondary",
     key="reset_ai_stats_button_2"):
                            from config.database import reset_ai_analysis_stats
                            result = reset_ai_analysis_stats()
                            if result["success"]:
                                st.success(result["message"])
                            else:
                                st.error(result["message"])
                            # Refresh the page to show updated stats
                            st.experimental_rerun()

                    # Get detailed AI analysis statistics
                    from config.database import get_detailed_ai_analysis_stats
                    ai_stats = get_detailed_ai_analysis_stats()

                    if ai_stats["total_analyses"] > 0:
                        # Create a more visually appealing layout
                        st.markdown("""
                        <style>
                        .stats-card {
                            background: linear-gradient(135deg, #1e3c72, #2a5298);
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 15px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            text-align: center;
                        }
                        .stats-value {
                            font-size: 28px;
                            font-weight: bold;
                            color: white;
                            margin: 10px 0;
                        }
                        .stats-label {
                            font-size: 14px;
                            color: rgba(255, 255, 255, 0.8);
                            text-transform: uppercase;
                            letter-spacing: 1px;
                        }
                        .score-card {
                            background: linear-gradient(135deg, #11998e, #38ef7d);
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 15px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            text-align: center;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"""
                            <div class="stats-card">
                                <div class="stats-label">Total AI Analyses</div>
                                <div class="stats-value">{ai_stats["total_analyses"]}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            # Determine color based on score
                            score_color = "#38ef7d" if ai_stats["average_score"] >= 80 else "#FFEB3B" if ai_stats[
                                "average_score"] >= 60 else "#FF5252"
                            st.markdown(f"""
                            <div class="stats-card" style="background: linear-gradient(135deg, #2c3e50, {score_color});">
                                <div class="stats-label">Average Resume Score</div>
                                <div class="stats-value">{ai_stats["average_score"]}/100</div>
                            </div>
                            """, unsafe_allow_html=True)

                        with col3:
                            # Create a gauge chart for average score
                            import plotly.graph_objects as go
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=ai_stats["average_score"],
                                domain={'x': [0, 1], 'y': [0, 1]},
                                title={
    'text': "Score", 'font': {
        'size': 14, 'color': 'white'}},
                                gauge={
                                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                                    'bar': {'color': "#38ef7d" if ai_stats["average_score"] >= 80 else "#FFEB3B" if ai_stats["average_score"] >= 60 else "#FF5252"},
                                    'bgcolor': "rgba(0,0,0,0)",
                                    'borderwidth': 2,
                                    'bordercolor': "white",
                                    'steps': [
                                        {'range': [
                                            0, 40], 'color': 'rgba(255, 82, 82, 0.3)'},
                                        {'range': [
                                            40, 70], 'color': 'rgba(255, 235, 59, 0.3)'},
                                        {'range': [
                                            70, 100], 'color': 'rgba(56, 239, 125, 0.3)'}
                                    ],
                                }
                            ))

                            fig.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font={'color': "white"},
                                height=150,
                                margin=dict(l=10, r=10, t=30, b=10)
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # Display model usage with enhanced visualization
                        if ai_stats["model_usage"]:
                            st.markdown("### 🤖 Model Usage")
                            model_data = pd.DataFrame(ai_stats["model_usage"])

                            # Create a more colorful pie chart
                            import plotly.express as px
                            fig = px.pie(
                                model_data,
                                values="count",
                                names="model",
                                color_discrete_sequence=px.colors.qualitative.Bold,
                                hole=0.4
                            )

                            fig.update_traces(
                                textposition='inside',
                                textinfo='percent+label',
                                marker=dict(
    line=dict(
        color='#000000',
         width=1.5))
                            )

                            fig.update_layout(
                                margin=dict(l=20, r=20, t=30, b=20),
                                height=300,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color="#ffffff", size=14),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.1,
                                    xanchor="center",
                                    x=0.5
                                ),
                                title={
                                    'text': 'AI Model Distribution',
                                    'y': 0.95,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 18, 'color': 'white'}
                                }
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # Display top job roles with enhanced visualization
                        if ai_stats["top_job_roles"]:
                            st.markdown("### 🎯 Top Job Roles")
                            roles_data = pd.DataFrame(
                                ai_stats["top_job_roles"])

                            # Create a more colorful bar chart
                            fig = px.bar(
                                roles_data,
                                x="role",
                                y="count",
                                color="count",
                                color_continuous_scale=px.colors.sequential.Viridis,
                                labels={
    "role": "Job Role", "count": "Number of Analyses"}
                            )

                            fig.update_traces(
                                marker_line_width=1.5,
                                marker_line_color="white",
                                opacity=0.9
                            )

                            fig.update_layout(
                                margin=dict(l=20, r=20, t=50, b=30),
                                height=350,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color="#ffffff", size=14),
                                title={
                                    'text': 'Most Analyzed Job Roles',
                                    'y': 0.95,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 18, 'color': 'white'}
                                },
                                xaxis=dict(
                                    title="",
                                    tickangle=-45,
                                    tickfont=dict(size=12)
                                ),
                                yaxis=dict(
                                    title="Number of Analyses",
                                    gridcolor="rgba(255, 255, 255, 0.1)"
                                ),
                                coloraxis_showscale=False
                            )

                            st.plotly_chart(fig, use_container_width=True)

                            # Add a timeline chart for analysis over time (mock
                            # data for now)
                            st.markdown("### 📈 Analysis Trend")
                            st.info(
                                "This is a conceptual visualization. To implement actual time-based analysis, additional data collection would be needed.")

                            # Create mock data for timeline
                            import datetime
                            import numpy as np

                            today = datetime.datetime.now()
                            dates = [
    (today -
    datetime.timedelta(
        days=i)).strftime('%Y-%m-%d') for i in range(7)]
                            dates.reverse()

                            # Generate some random data that sums to
                            # total_analyses
                            total = ai_stats["total_analyses"]
                            if total > 7:
                                values = np.random.dirichlet(
                                    np.ones(7)) * total
                                values = [round(v) for v in values]
                                # Adjust to make sure sum equals total
                                diff = total - sum(values)
                                values[-1] += diff
                            else:
                                values = [0] * 7
                                for i in range(total):
                                    values[-(i % 7) - 1] += 1

                            trend_data = pd.DataFrame({
                                'Date': dates,
                                'Analyses': values
                            })

                            fig = px.line(
                                trend_data,
                                x='Date',
                                y='Analyses',
                                markers=True,
                                line_shape='spline',
                                color_discrete_sequence=["#38ef7d"]
                            )

                            fig.update_traces(
                                line=dict(width=3),
                                marker=dict(
    size=8, line=dict(
        width=2, color='white'))
                            )

                            fig.update_layout(
                                margin=dict(l=20, r=20, t=50, b=30),
                                height=300,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color="#ffffff", size=14),
                                title={
                                    'text': 'Analysis Activity (Last 7 Days)',
                                    'y': 0.95,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 18, 'color': 'white'}
                                },
                                xaxis=dict(
                                    title="",
                                    gridcolor="rgba(255, 255, 255, 0.1)"
                                ),
                                yaxis=dict(
                                    title="Number of Analyses",
                                    gridcolor="rgba(255, 255, 255, 0.1)"
                                )
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # Display score distribution if available
                        if ai_stats["score_distribution"]:
                            st.markdown("""
                            <h3 style='text-align: center; margin-bottom: 20px; background: linear-gradient(90deg, #4b6cb7, #182848); padding: 15px; border-radius: 10px; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>
                                📊 Score Distribution Analysis
                            </h3>
                            """, unsafe_allow_html=True)

                            score_data = pd.DataFrame(
                                ai_stats["score_distribution"])

                            # Create a more visually appealing bar chart for
                            # score distribution
                            fig = px.bar(
                                score_data,
                                x="range",
                                y="count",
                                color="range",
                                color_discrete_map={
                                    "0-20": "#FF5252",
                                    "21-40": "#FF7043",
                                    "41-60": "#FFEB3B",
                                    "61-80": "#8BC34A",
                                    "81-100": "#38ef7d"
                                },
                                labels={
    "range": "Score Range",
     "count": "Number of Resumes"},
                                text="count"  # Display count values on bars
                            )

                            fig.update_traces(
                                marker_line_width=2,
                                marker_line_color="white",
                                opacity=0.9,
                                textposition='outside',
                                textfont=dict(
    color="white", size=14, family="Arial, sans-serif"),
                                hovertemplate="<b>Score Range:</b> %{x}<br><b>Number of Resumes:</b> %{y}<extra></extra>"
                            )

                            # Add a gradient background to the chart
                            fig.update_layout(
                                margin=dict(l=20, r=20, t=50, b=30),
                                height=400,  # Increase height for better visibility
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(
    color="#ffffff", size=14, family="Arial, sans-serif"),
                                # title={
                                #     # 'text': 'Resume Score Distribution',
                                #     'y': 0.95,
                                #     'x': 0.5,
                                #     'xanchor': 'center',
                                #     'yanchor': 'top',
                                #     'font': {'size': 22, 'color': 'white', 'family': 'Arial, sans-serif', 'weight': 'bold'}
                                # },
                                xaxis=dict(
                                    title=dict(
    text="Score Range", font=dict(
        size=16, color="white")),
                                    categoryorder="array",
                                    categoryarray=[
    "0-20", "21-40", "41-60", "61-80", "81-100"],
                                    tickfont=dict(size=14, color="white"),
                                    gridcolor="rgba(255, 255, 255, 0.1)"
                                ),
                                yaxis=dict(
                                    title=dict(
    text="Number of Resumes", font=dict(
        size=16, color="white")),
                                    tickfont=dict(size=14, color="white"),
                                    gridcolor="rgba(255, 255, 255, 0.1)",
                                    zeroline=False
                                ),
                                showlegend=False,
                                bargap=0.2,  # Adjust gap between bars
                                shapes=[
                                    # Add gradient background
                                    dict(
                                        type="rect",
                                        xref="paper",
                                        yref="paper",
                                        x0=0,
                                        y0=0,
                                        x1=1,
                                        y1=1,
                                        fillcolor="rgba(26, 26, 44, 0.5)",
                                        layer="below",
                                        line_width=0,
                                    )
                                ]
                            )

                            # Add annotations for insights
                            if len(score_data) > 0:
                                max_count_idx = score_data["count"].idxmax()
                                max_range = score_data.iloc[max_count_idx]["range"]
                                max_count = score_data.iloc[max_count_idx]["count"]

                                fig.add_annotation(
                                    x=0.5,
                                    y=1.12,
                                    xref="paper",
                                    yref="paper",
                                    text=f"Most resumes fall in the {max_range} score range",
                                    showarrow=False,
                                    font=dict(size=14, color="#FFEB3B"),
                                    bgcolor="rgba(0,0,0,0.5)",
                                    bordercolor="#FFEB3B",
                                    borderwidth=1,
                                    borderpad=4,
                                    opacity=0.8
                                )

                            # Display the chart in a styled container
                            st.markdown("""
                            <div style='background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 20px; border-radius: 15px; margin: 10px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2);'>
                            """, unsafe_allow_html=True)

                            st.plotly_chart(fig, use_container_width=True)

                            # Add descriptive text below the chart
                            st.markdown("""
                            <p style='color: white; text-align: center; font-style: italic; margin-top: 10px;'>
                                This chart shows the distribution of resume scores across different ranges, helping identify common performance levels.
                            </p>
                            </div>
                            """, unsafe_allow_html=True)

                        # Display recent analyses if available
                        if ai_stats["recent_analyses"]:
                            st.markdown("""
                            <h3 style='text-align: center; margin-bottom: 20px; background: linear-gradient(90deg, #4b6cb7, #182848); padding: 15px; border-radius: 10px; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>
                                🕒 Recent Resume Analyses
                            </h3>
                            """, unsafe_allow_html=True)

                            # Create a more modern styled table for recent
                            # analyses
                            st.markdown("""
                            <style>
                            .modern-analyses-table {
                                width: 100%;
                                border-collapse: separate;
                                border-spacing: 0 8px;
                                margin-bottom: 20px;
                                font-family: 'Arial', sans-serif;
                            }
                            .modern-analyses-table th {
                                background: linear-gradient(135deg, #1e3c72, #2a5298);
                                color: white;
                                padding: 15px;
                                text-align: left;
                                font-weight: bold;
                                font-size: 14px;
                                text-transform: uppercase;
                                letter-spacing: 1px;
                                border-radius: 8px;
                            }
                            .modern-analyses-table td {
                                padding: 15px;
                                background-color: rgba(30, 30, 30, 0.7);
                                border-top: 1px solid rgba(255, 255, 255, 0.05);
                                border-bottom: 1px solid rgba(0, 0, 0, 0.2);
                                color: white;
                            }
                            .modern-analyses-table tr td:first-child {
                                border-top-left-radius: 8px;
                                border-bottom-left-radius: 8px;
                            }
                            .modern-analyses-table tr td:last-child {
                                border-top-right-radius: 8px;
                                border-bottom-right-radius: 8px;
                            }
                            .modern-analyses-table tr:hover td {
                                background-color: rgba(60, 60, 60, 0.7);
                                transform: translateY(-2px);
                                transition: all 0.2s ease;
                                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                            }
                            .model-badge {
                                display: inline-block;
                                padding: 6px 12px;
                                border-radius: 20px;
                                font-weight: bold;
                                text-align: center;
                                font-size: 12px;
                                letter-spacing: 0.5px;
                                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                            }
                            .model-gemini {
                                background: linear-gradient(135deg, #4e54c8, #8f94fb);
                                color: white;
                            }
                            .model-claude {
                                background: linear-gradient(135deg, #834d9b, #d04ed6);
                                color: white;
                            }
                            .score-pill {
                                display: inline-block;
                                padding: 8px 15px;
                                border-radius: 20px;
                                font-weight: bold;
                                text-align: center;
                                min-width: 70px;
                                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                            }
                            .score-high {
                                background: linear-gradient(135deg, #11998e, #38ef7d);
                                color: white;
                            }
                            .score-medium {
                                background: linear-gradient(135deg, #f2994a, #f2c94c);
                                color: white;
                            }
                            .score-low {
                                background: linear-gradient(135deg, #cb2d3e, #ef473a);
                                color: white;
                            }
                            .date-badge {
                                display: inline-block;
                                padding: 6px 12px;
                                border-radius: 20px;
                                background-color: rgba(255, 255, 255, 0.1);
                                color: #e0e0e0;
                                font-size: 12px;
                            }
                            .role-badge {
                                display: inline-block;
                                padding: 6px 12px;
                                border-radius: 8px;
                                background-color: rgba(33, 150, 243, 0.2);
                                color: #90caf9;
                                font-size: 13px;
                                max-width: 200px;
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                            }
                            </style>

                            <div style='background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 20px; border-radius: 15px; margin: 10px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2);'>
                            <table class="modern-analyses-table">
                                <tr>
                                    <th>AI Model</th>
                                    <th>Score</th>
                                    <th>Job Role</th>
                                    <th>Date</th>
                                </tr>
                            """, unsafe_allow_html=True)

                            for analysis in ai_stats["recent_analyses"]:
                                score = analysis["score"]
                                score_class = "score-high" if score >= 80 else "score-medium" if score >= 60 else "score-low"

                                # Determine model class
                                model_name = analysis["model"]
                                model_class = "model-gemini" if "Gemini" in model_name else "model-claude" if "Claude" in model_name else ""

                                # Format the date
                                try:
                                    from datetime import datetime
                                    date_obj = datetime.strptime(
                                        analysis["date"], "%Y-%m-%d %H:%M:%S")
                                    formatted_date = date_obj.strftime(
                                        "%b %d, %Y")
                                except:
                                    formatted_date = analysis["date"]

                                st.markdown(f"""
                                <tr>
                                    <td><div class="model-badge {model_class}">{model_name}</div></td>
                                    <td><div class="score-pill {score_class}">{score}/100</div></td>
                                    <td><div class="role-badge">{analysis["job_role"]}</div></td>
                                    <td><div class="date-badge">{formatted_date}</div></td>
                                </tr>
                                """, unsafe_allow_html=True)

                            st.markdown("""
                            </table>

                            <p style='color: white; text-align: center; font-style: italic; margin-top: 15px;'>
                                These are the most recent resume analyses performed by our AI models.
                            </p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info(
                            "No AI analysis data available yet. Upload and analyze resumes to see statistics here.")
                except Exception as e:
                    st.error(f"Error loading AI analysis statistics: {str(e)}")

                    
            # Job Role Selection for AI Analysis
            categories = list(self.job_roles.keys())
            selected_category = st.selectbox(
    "Job Category", categories, key="ai_category")

            roles = list(self.job_roles[selected_category].keys())
            selected_role = st.selectbox("Specific Role", roles, key="ai_role")

            role_info = self.job_roles[selected_category][selected_role]

            # Display role information
            st.markdown(f"""
            <div style='background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h3>{selected_role}</h3>
                <p>{role_info['description']}</p>
                <h4>Required Skills:</h4>
                <p>{', '.join(role_info['required_skills'])}</p>
            </div>
            """, unsafe_allow_html=True)

            # File Upload for AI Analysis
            uploaded_file = st.file_uploader(
    "Upload your resume", type=[
        'pdf', 'docx'], key="ai_file")

            if not uploaded_file:
            # Display empty state with a prominent upload button
                st.markdown(
                self.render_empty_state(
            "fas fa-robot",
                        "Upload your resume to get AI-powered analysis and recommendations"
        ),
        unsafe_allow_html=True
    )
            else:
                # Add a prominent analyze button
                analyze_ai = st.button("🤖 Analyze with AI",
                                type="primary",
                                use_container_width=True,
                                key="analyze_ai_button")

                if analyze_ai:
                    with st.spinner(f"Analyzing your resume with {ai_model}..."):
                        # Get file content
                        text = ""
                        try:
                            if uploaded_file.type == "application/pdf":
                                text = self.analyzer.extract_text_from_pdf(
                                    uploaded_file)
                            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                text = self.analyzer.extract_text_from_docx(
                                    uploaded_file)
                            else:
                                text = uploaded_file.getvalue().decode()
                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")
                            st.stop()

                        # Analyze with AI
                        try:
                            # Show a loading animation
                            with st.spinner("🧠 AI is analyzing your resume..."):
                                progress_bar = st.progress(0)
                                
                                # Get the selected model
                                selected_model = "Google Gemini"
                                
                                # Update progress
                                progress_bar.progress(10)
                                
                                # Extract text from the resume
                                analyzer = AIResumeAnalyzer()
                                if uploaded_file.type == "application/pdf":
                                    resume_text = analyzer.extract_text_from_pdf(
                                        uploaded_file)
                                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                    resume_text = analyzer.extract_text_from_docx(
                                        uploaded_file)
                                else:
                                    # For text files or other formats
                                    resume_text = uploaded_file.getvalue().decode('utf-8')
                                
                                # Initialize the AI analyzer (moved after text extraction)
                                progress_bar.progress(30)
                                
                                # Get the job role
                                job_role = selected_role if selected_role else "Not specified"
                                
                                # Update progress
                                progress_bar.progress(50)
                                
                                # Analyze the resume with Google Gemini
                                if use_custom_job_desc and custom_job_description:
                                    # Use custom job description for analysis
                                    analysis_result = analyzer.analyze_resume_with_gemini(
                                        resume_text, job_role=job_role, job_description=custom_job_description)
                                    # Show that custom job description was used
                                    st.session_state['used_custom_job_desc'] = True
                                else:
                                    # Use standard role-based analysis
                                    analysis_result = analyzer.analyze_resume_with_gemini(
                                        resume_text, job_role=job_role)
                                    st.session_state['used_custom_job_desc'] = False

                                
                                # Update progress
                                progress_bar.progress(80)
                                
                                # Save the analysis to the database
                                if analysis_result and "error" not in analysis_result:
                                    # Extract the resume score
                                    resume_score = analysis_result.get(
                                        "resume_score", 0)
                                    
                                    # Save to database
                                    save_ai_analysis_data(
                                        None,  # No user_id needed
                                        {
                                            "model_used": selected_model,
                                            "resume_score": resume_score,
                                            "job_role": job_role
                                        }
                                    )
                            
                                # Complete the progress
                                progress_bar.progress(100)
                                
                                # Display the analysis result
                                if analysis_result and "error" not in analysis_result:
                                    st.success("✅ Analysis complete!")
                                    
                                    # Extract data from the analysis
                                    full_response = analysis_result.get(
                                        "analysis", "")
                                    resume_score = analysis_result.get(
                                        "resume_score", 0)
                                    ats_score = analysis_result.get(
                                        "ats_score", 0)
                                    model_used = analysis_result.get(
                                        "model_used", selected_model)
                                    
                                    # Store the full response in session state for download
                                    st.session_state['full_analysis'] = full_response
                                    
                                    # Display the analysis in a nice format
                                    st.markdown("## Full Analysis Report")
                                    
                                    # Get current date
                                    from datetime import datetime
                                    current_date = datetime.now().strftime("%B %d, %Y")
                                    
                                    # Create a modern styled header for the report
                                    st.markdown(f"""
                                    <div style="background-color: #262730; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                                        <h2 style="color: #ffffff; margin-bottom: 10px;">AI Resume Analysis Report</h2>
                                        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                                            <div style="flex: 1; min-width: 200px;">
                                                <p style="color: #ffffff;"><strong>Job Role:</strong> {job_role if job_role else "Not specified"}</p>
                                                <p style="color: #ffffff;"><strong>Analysis Date:</strong> {current_date}</p>                                                                                                                                        </div>
                                            <div style="flex: 1; min-width: 200px;">
                                                <p style="color: #ffffff;"><strong>AI Model:</strong> {model_used}</p>
                                                <p style="color: #ffffff;"><strong>Overall Score:</strong> {resume_score}/100 - {"Excellent" if resume_score >= 80 else "Good" if resume_score >= 60 else "Needs Improvement"}</p>
                                                {f'<p style="color: #4CAF50;"><strong>✓ Custom Job Description Used</strong></p>' if st.session_state.get('used_custom_job_desc', False) else ''}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Add gauge charts for scores
                                    import plotly.graph_objects as go
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        # Resume Score Gauge
                                        fig1 = go.Figure(go.Indicator(
                                            mode="gauge+number",
                                            value=resume_score,
                                            domain={'x': [0, 1], 'y': [0, 1]},
                                            title={'text': "Resume Score", 'font': {'size': 16}},
                                            gauge={
                                                'axis': {'range': [0, 100], 'tickwidth': 1},
                                                'bar': {'color': "#4CAF50" if resume_score >= 80 else "#FFA500" if resume_score >= 60 else "#FF4444"},
                                                'bgcolor': "white",
                                                'borderwidth': 2,
                                                'bordercolor': "gray",
                                                'steps': [
                                                    {'range': [0, 40], 'color': 'rgba(255, 68, 68, 0.2)'},
                                                    {'range': [40, 60], 'color': 'rgba(255, 165, 0, 0.2)'},
                                                    {'range': [60, 80], 'color': 'rgba(255, 214, 0, 0.2)'},
                                                    {'range': [80, 100], 'color': 'rgba(76, 175, 80, 0.2)'}
                                                ],
                                                'threshold': {
                                                    'line': {'color': "red", 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 60
                                                }
                                            }
                                        ))
                                        
                                        fig1.update_layout(
                                            height=250,
                                            margin=dict(l=20, r=20, t=50, b=20),
                                        )
                                        
                                        st.plotly_chart(fig1, use_container_width=True)
                                        
                                        status = "Excellent" if resume_score >= 80 else "Good" if resume_score >= 60 else "Needs Improvement"
                                        st.markdown(f"<div style='text-align: center; font-weight: bold;'>{status}</div>", unsafe_allow_html=True)
                                    
                                    with col2:
                                        # ATS Score Gauge
                                        fig2 = go.Figure(go.Indicator(
                                            mode="gauge+number",
                                            value=ats_score,
                                            domain={'x': [0, 1], 'y': [0, 1]},
                                            title={'text': "ATS Optimization Score", 'font': {'size': 16}},
                                            gauge={
                                                'axis': {'range': [0, 100], 'tickwidth': 1},
                                                'bar': {'color': "#4CAF50" if ats_score >= 80 else "#FFA500" if ats_score >= 60 else "#FF4444"},
                                                'bgcolor': "white",
                                                'borderwidth': 2,
                                                'bordercolor': "gray",
                                                'steps': [
                                                    {'range': [0, 40], 'color': 'rgba(255, 68, 68, 0.2)'},
                                                    {'range': [40, 60], 'color': 'rgba(255, 165, 0, 0.2)'},
                                                    {'range': [60, 80], 'color': 'rgba(255, 214, 0, 0.2)'},
                                                    {'range': [80, 100], 'color': 'rgba(76, 175, 80, 0.2)'}
                                                ],
                                                'threshold': {
                                                    'line': {'color': "red", 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 60
                                                }
                                            }
                                        ))
                                        
                                        fig2.update_layout(
                                            height=250,
                                            margin=dict(l=20, r=20, t=50, b=20),
                                        )
                                        
                                        st.plotly_chart(fig2, use_container_width=True)
                                        
                                        status = "Excellent" if ats_score >= 80 else "Good" if ats_score >= 60 else "Needs Improvement"
                                        st.markdown(f"<div style='text-align: center; font-weight: bold;'>{status}</div>", unsafe_allow_html=True)

                                    # Add Job Description Match Score if custom job description was used
                                    if st.session_state.get('used_custom_job_desc', False) and custom_job_description:
                                        # Extract job match score from analysis result or calculate it
                                        job_match_score = analysis_result.get("job_match_score", 0)
                                        if not job_match_score and "job_match" in analysis_result:
                                            job_match_score = analysis_result["job_match"].get("score", 0)
                                        
                                        # If we have a job match score, display it
                                        if job_match_score:
                                            st.markdown("""
                                            <h3 style="background: linear-gradient(90deg, #4d7c0f, #84cc16); color: white; padding: 10px; border-radius: 5px; margin-top: 20px;">
                                                <i class="fas fa-handshake"></i> Job Description Match Analysis
                                            </h3>
                                            """, unsafe_allow_html=True)
                                            
                                            col1, col2 = st.columns(2)
                                            
                                            with col1:
                                                # Job Match Score Gauge
                                                fig3 = go.Figure(go.Indicator(
                                                    mode="gauge+number",
                                                    value=job_match_score,
                                                    domain={'x': [0, 1], 'y': [0, 1]},
                                                    title={'text': "Job Match Score", 'font': {'size': 16}},
                                                    gauge={
                                                        'axis': {'range': [0, 100], 'tickwidth': 1},
                                                        'bar': {'color': "#4CAF50" if job_match_score >= 80 else "#FFA500" if job_match_score >= 60 else "#FF4444"},
                                                        'bgcolor': "white",
                                                        'borderwidth': 2,
                                                        'bordercolor': "gray",
                                                        'steps': [
                                                            {'range': [0, 40], 'color': 'rgba(255, 68, 68, 0.2)'},
                                                            {'range': [40, 60], 'color': 'rgba(255, 165, 0, 0.2)'},
                                                            {'range': [60, 80], 'color': 'rgba(255, 214, 0, 0.2)'},
                                                            {'range': [80, 100], 'color': 'rgba(76, 175, 80, 0.2)'}
                                                        ],
                                                        'threshold': {
                                                            'line': {'color': "red", 'width': 4},
                                                            'thickness': 0.75,
                                                            'value': 60
                                                        }
                                                    }
                                                ))
                                                
                                                fig3.update_layout(
                                                    height=250,
                                                    margin=dict(l=20, r=20, t=50, b=20),
                                                )
                                                
                                                st.plotly_chart(fig3, use_container_width=True)
                                                
                                                match_status = "Excellent Match" if job_match_score >= 80 else "Good Match" if job_match_score >= 60 else "Low Match"
                                                st.markdown(f"<div style='text-align: center; font-weight: bold;'>{match_status}</div>", unsafe_allow_html=True)
                                            
                                            with col2:
                                                st.markdown("""
                                                <div style="background-color: #262730; padding: 20px; border-radius: 10px; height: 100%;">
                                                    <h4 style="color: #ffffff; margin-bottom: 15px;">What This Means</h4>
                                                    <p style="color: #ffffff;">This score represents how well your resume matches the specific job description you provided.</p>
                                                    <ul style="color: #ffffff; padding-left: 20px;">
                                                        <li><strong>80-100:</strong> Excellent match - your resume is highly aligned with this job</li>
                                                        <li><strong>60-79:</strong> Good match - your resume matches many requirements</li>
                                                        <li><strong>Below 60:</strong> Consider tailoring your resume more specifically to this job</li>
                                                    </ul>
                                                </div>
                                                """, unsafe_allow_html=True)
                                    

                                    # Format the full response with better styling
                                    formatted_analysis = full_response
                                    
                                    # Replace section headers with styled headers
                                    section_styles = {
                                        "## Overall Assessment": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-chart-line"></i> Overall Assessment
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Professional Profile Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #047857, #10b981); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-user-tie"></i> Professional Profile Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Skills Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #4f46e5, #818cf8); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-tools"></i> Skills Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Experience Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #9f1239, #e11d48); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-briefcase"></i> Experience Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Education Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #854d0e, #eab308); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-graduation-cap"></i> Education Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Key Strengths": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #166534, #22c55e); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-check-circle"></i> Key Strengths
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Areas for Improvement": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #9f1239, #fb7185); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-exclamation-circle"></i> Areas for Improvement
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## ATS Optimization Assessment": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #0e7490, #06b6d4); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-robot"></i> ATS Optimization Assessment
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Recommended Courses": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #5b21b6, #8b5cf6); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-book"></i> Recommended Courses
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Resume Score": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #0369a1, #0ea5e9); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-star"></i> Resume Score
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Role Alignment Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #7c2d12, #ea580c); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-bullseye"></i> Role Alignment Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Job Match Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #4d7c0f, #84cc16); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-handshake"></i> Job Match Analysis
                                            </h3>
                                            <div class="section-content">""",
                                    }
                                    
                                    # Apply the styling to each section
                                    for section, style in section_styles.items():
                                        if section in formatted_analysis:
                                            formatted_analysis = formatted_analysis.replace(
                                                section, style)
                                            # Add closing div tags
                                            next_section = False
                                            for next_sec in section_styles.keys():
                                                if next_sec != section and next_sec in formatted_analysis.split(style)[1]:
                                                    split_text = formatted_analysis.split(style)[1].split(next_sec)
                                                    formatted_analysis = formatted_analysis.split(style)[0] + style + split_text[0] + "</div></div>" + next_sec + "".join(split_text[1:])
                                                    next_section = True
                                                    break
                                            if not next_section:
                                                formatted_analysis = formatted_analysis + "</div></div>"
                                    
                                    # Remove any extra closing div tags that might have been added
                                    formatted_analysis = formatted_analysis.replace("</div></div></div></div>", "</div></div>")
                                    
                                    # Ensure we don't have any orphaned closing tags at the end
                                    if formatted_analysis.endswith("</div>"):
                                        # Count opening and closing div tags
                                        open_tags = formatted_analysis.count("<div")
                                        close_tags = formatted_analysis.count("</div>")
                                        
                                        # If we have more closing than opening tags, remove the extras
                                        if close_tags > open_tags:
                                            excess = close_tags - open_tags
                                            formatted_analysis = formatted_analysis[:-6 * excess]
                                    
                                    # Clean up any visible HTML tags that might appear in the text
                                    formatted_analysis = formatted_analysis.replace("&lt;/div&gt;", "")
                                    formatted_analysis = formatted_analysis.replace("&lt;div&gt;", "")
                                    formatted_analysis = formatted_analysis.replace("<div>", "<div>")  # Ensure proper opening
                                    formatted_analysis = formatted_analysis.replace("</div>", "</div>")  # Ensure proper closing
                                    
                                    # Add CSS for the report
                                    st.markdown("""
                                    <style>
                                        .report-section {
                                            margin-bottom: 25px;
                                            border: 1px solid #4B4B4B;
                                            border-radius: 8px;
                                            overflow: hidden;
                                        }
                                        .section-content {
                                            padding: 15px;
                                            background-color: #262730;
                                            color: #ffffff;
                                        }
                                        .report-section h3 {
                                            margin-top: 0;
                                            font-weight: 600;
                                        }
                                        
                                        .report-section ul {
                                            padding-left: 20px;
                                        }
                                        .report-section p {
                                            color: #ffffff;
                                            margin-bottom: 10px;
                                        }
                                        .report-section li {
                                            color: #ffffff;
                                            margin-bottom: 5px;
                                        }
                                    </style>
                                    """, unsafe_allow_html=True)

                                    # Display the formatted analysis
                                    st.markdown(f"""
                                    <div style="background-color: #262730; padding: 20px; border-radius: 10px; border: 1px solid #4B4B4B; color: #ffffff;">
                                        {formatted_analysis}
                                    </div>
                                    """, unsafe_allow_html=True)

                                    # Create a PDF report
                                    pdf_buffer = self.ai_analyzer.generate_pdf_report(
                                        analysis_result={
                                            "score": resume_score,
                                            "ats_score": ats_score,
                                            "model_used": model_used,
                                            "full_response": full_response,
                                            "strengths": analysis_result.get("strengths", []),
                                            "weaknesses": analysis_result.get("weaknesses", []),
                                            "used_custom_job_desc": st.session_state.get('used_custom_job_desc', False),
                                            "custom_job_description": custom_job_description if st.session_state.get('used_custom_job_desc', False) else ""
                                        },
                                        candidate_name=st.session_state.get(
                                            'candidate_name', 'Candidate'),
                                        job_role=selected_role
                                    )

                                    # PDF download button
                                    if pdf_buffer:
                                        st.download_button(
                                            label="📊 Download PDF Report",
                                            data=pdf_buffer,
                                            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                            mime="application/pdf",
                                            use_container_width=True,
                                        )
                                    else:
                                        st.error("PDF generation failed. Please try again later.")
                                else:
                                    st.error(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")
                        except Exception as ai_error:
                            st.error(f"Error during AI analysis: {str(ai_error)}")
                            import traceback as tb
                            st.code(tb.format_exc())
                   


    def render_home(self):
        apply_modern_styles()
    
        # Enhanced Hero Section with gradient background
        st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 4rem 2rem;
                        border-radius: 20px;
                        text-align: center;
                        margin-bottom: 3rem;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
                        position: relative;
                        overflow: hidden;
                    ">    
                        <div style="
                            position: absolute;
                            top: -50px;
                            right: -50px;
                            width: 200px;
                            height: 200px;
                            background: rgba(255,255,255,0.1);
                            border-radius: 50%;
                            z-index: 1;
                        "></div>
                        <div style="
                            position: absolute;
                            bottom: -30px;
                            left: -30px;
                            width: 150px;
                            height: 150px;
                            background: rgba(255,255,255,0.08);
                            border-radius: 50%;
                            z-index: 1;
                        "></div>
                        <div style="position: relative; z-index: 2;">
                            <h1 style="
                                font-size: 3.5rem; 
                                margin-bottom: 1rem; 
                                font-weight: 700;
                                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                                background: linear-gradient(90deg, #ff6ec4, #7873f5, #4ade80, #facc15, #f43f5e);
                                background-size: 300% 300%;
                                -webkit-background-clip: text;
                                -webkit-text-fill-color: transparent;
                                animation: gradientAnimation 6s ease infinite;
                            ">CareerIQ</h1>
                            <p style="
                                color: rgba(255,255,255,0.9); 
                                font-size: 1.3rem; 
                                max-width: 600px; 
                                margin: 0 auto;
                                line-height: 1.6;
                                font-weight: 300;
                            ">Transform your career with AI-powered resume magic! Get personalized insights, build stunning resumes, find dream jobs, and master interviews with our next-level features.</p>
                        </div>
                    </div>
                    
                    <style>
                    @keyframes gradientAnimation {
                        0% {background-position: 0% 50%;}
                        50% {background-position: 100% 50%;}
                        100% {background-position: 0% 50%;}
                    }
                    </style>
                    """, unsafe_allow_html=True)

    
        # Enhanced Features Section with animated cards
        st.markdown("""
        <div style="margin: 3rem 0;">
            <h2 style="
                text-align: center; 
                margin-bottom: 3rem; 
                color: #2c3e50; 
                font-size: 2.8rem;
                font-weight: 600;
                position: relative;
            ">
                Next-Level Features for Success
                <div style="
                    width: 120px;
                    height: 4px;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                    margin: 1rem auto;
                    border-radius: 2px;
                "></div>
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced responsive grid with hover effects - Main Features
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            st.markdown("""
            <div style="
                background: linear-gradient(145deg, #ffffff, #f8f9fa);
                padding: 2.5rem 1.5rem;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                text-align: center;
                height: 400px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border: 1px solid rgba(255,255,255,0.2);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #fd7e14, #e83e8c);
                "></div>
                <div style="
                    font-size: 4rem; 
                    margin-bottom: 1.5rem;
                    color: #fd7e14;
                ">🎨</div>
                <h3 style="
                    color: #2c3e50; 
                    margin-bottom: 1rem;
                    font-size: 1.4rem;
                    font-weight: 600;
                ">AI-Powered Resume Builder</h3>
                <div style="color: #6c757d; font-size: 0.9rem; line-height: 1.6; text-align: left;">
                    <strong>🢥 Themes that Shine.</strong><br>
                    <strong>🢥 Content Suggestions.</strong><br>
                    <strong>🢥 ATS-Optimized Formatting.</strong><br>
                    <strong>🢥 Customizable Sections.</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
        
        with col2:
            st.markdown("""
            <div style="
                background: linear-gradient(145deg, #ffffff, #f8f9fa);
                padding: 2.5rem 1.5rem;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                text-align: center;
                height: 400px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border: 1px solid rgba(255,255,255,0.2);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #28a745, #20c997);
                "></div>
                <div style="
                    font-size: 4rem; 
                    margin-bottom: 1.5rem;
                    color: #28a745;
                ">🕵️</div>
                <h3 style="
                    color: #2c3e50; 
                    margin-bottom: 1rem;
                    font-size: 1.4rem;
                    font-weight: 600;
                ">Deep Resume Analysis</h3>
                <div style="color: #6c757d; font-size: 0.9rem; line-height: 1.6; text-align: left;">
                    <strong>🢥 ATS Compatibility Score.</strong><br>
                    <strong>🢥 Keyword Gap Analysis.</strong><br>
                    <strong>🢥 Role-specific Feedback.</strong><br>
                    <strong>🢥 Skills Gap Breakdown.</strong><br><br>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: linear-gradient(145deg, #ffffff, #f8f9fa);
                padding: 2.5rem 1.5rem;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                text-align: center;
                height: 400px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border: 1px solid rgba(255,255,255,0.2);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #6f42c1, #e83e8c);
                "></div>
                <div style="
                    font-size: 4rem; 
                    margin-bottom: 1rem;
                    color: #6f42c1;
                ">💼</div>
                <h3 style="
                    color: #2c3e50; 
                    margin-bottom: 1.5rem;
                    font-size: 1.4rem;
                    font-weight: 600;
                ">Job Application Portal</h3>
                <div style="color: #6c757d; font-size: 0.9rem; line-height: 1.6; text-align: left; margin-bottom:1.7rem">
                    <strong>🢥 Multi-Portal Search.</strong><br>
                    <strong>🢥 AI Match Score.</strong><br>
                    <strong>🢥 Job Market Insights.</strong><br>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
        with col4:
            st.markdown("""
            <div style="
                background: linear-gradient(145deg, #ffffff, #f8f9fa);
                padding: 2.5rem 1.5rem;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                text-align: center;
                height: 400px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border: 1px solid rgba(255,255,255,0.2);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #17a2b8, #fd7e14);
                "></div>
                <div style="
                    font-size: 4rem; 
                    margin-bottom: 1.5rem;
                    color: #17a2b8;
                ">🧮</div>
                <h3 style="
                    color: #2c3e50; 
                    margin-bottom: 1rem;
                    font-size: 1.4rem;
                    font-weight: 600;
                ">Smart Quiz Master</h3>
                <div style="color: #6c757d; font-size: 0.9rem; line-height: 1.6; text-align: left;">
                    <strong>🢥 AI-Generated Quizzes.</strong><br>
                    <strong>🢥 Flexible Customization.</strong><br>
                    <strong>🢥 Adaptive Practice.</strong><br>
                    <strong>🢥 Wide Coverage.</strong><br><br>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    
        st.markdown("""
        <div style="
            text-align: center;
            margin: 4rem 0 2rem 0;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        ">
            <h3 style="
                color: white;
                font-size: 2.2rem;
                margin-bottom: 1rem;
                font-weight: 600;
            ">Ready to Launch Your Dream Career?</h3>
            <p style="
                color: rgba(255,255,255,0.9);
                font-size: 1.2rem;
                margin-bottom: 2rem;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            ">Join thousands of professionals who've already transformed their careers with our AI-powered platform. Your next opportunity is just one click away!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(" Start Your Journey Now!", key="get_started_btn", 
                        help="Click to start analyzing your resume with AI magic",
                        type="primary",
                        use_container_width=True):
                cleaned_name = "🔍 RESUME ANALYZER".lower().replace(" ", "_").replace("🔍", "").strip()
                st.session_state.page = cleaned_name
                st.rerun()
    
        # Add some spacing at the bottom
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    def render_job_search(self):
        """Render the job search page"""
        render_job_search()

    

    def render_feedback_page(self):
        """Render the feedback page"""
        apply_modern_styles()
        
        # Page Header
        page_header(
            "Feedback & Suggestions",
            "Help us improve by sharing your thoughts"
        )
        
        # Initialize feedback manager
        feedback_manager = FeedbackManager()
        st.markdown("""
                    <style>
                    /* Center align and style tab container */
                    .stTabs [data-baseweb="tab-list"] {
                        justify-content: center;
                        margin-top: 20px;
                        margin-bottom: 20px;
                        gap: 10px;
                    }
                
                    /* Base style for each tab */
                    .stTabs [data-baseweb="tab"] {
                        background-color: #f0f0f0;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 10px 24px;
                        font-size: 16px;
                        font-weight: 600;
                        color: #333;
                        transition: all 0.2s ease-in-out;
                    }
                
                    /* Hover effect */
                    .stTabs [data-baseweb="tab"]:hover {
                        background-color: #e0f5ec;
                        border-color: #00bfa5;
                        color: #111;
                        transform: translateY(-2px);
                        cursor: pointer;
                    }
                
                    /* Selected/active tab style */
                    .stTabs [aria-selected="true"] {
                        background-color: #00bfa5 !important;
                        color: white !important;
                        border: 1px solid #00bfa5;
                        font-weight: 700;
                        box-shadow: 0px 4px 12px rgba(0, 191, 165, 0.2);
                    }
                    </style>
                """, unsafe_allow_html=True)
        # Create tabs for form and stats
        form_tab, stats_tab = st.tabs(["Submit Feedback", "Feedback Stats"])
        
        with form_tab:
            feedback_manager.render_feedback_form()
            
        with stats_tab:
            feedback_manager.render_feedback_stats()


    def main(self):
        """Main application entry point"""
        self.apply_global_styles()
        
        # Admin login/logout in sidebar
        with st.sidebar:
            st_lottie(self.load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_xyadoh9h.json"), height=200, key="sidebar_animation")
            st.title("CareerIQ")
            st.markdown("---")
            
            # Navigation buttons
            for page_name in self.pages.keys():
                if st.button(page_name, use_container_width=True):
                    cleaned_name = page_name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("🎯", "").replace("💬", "").replace("ℹ️", "").strip()
                    st.session_state.page = cleaned_name
                    st.rerun()

            # Add some space before admin login
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")


        # Force home page on first load
        if 'initial_load' not in st.session_state:
            st.session_state.initial_load = True
            st.session_state.page = 'home'
            st.rerun()
        
        # Get current page and render it
        current_page = st.session_state.get('page', 'home')
        
        # Create a mapping of cleaned page names to original names
        page_mapping = {name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("🎯", "").replace("💬", "").replace("ℹ️", "").strip(): name 
                       for name in self.pages.keys()}
        
        # Render the appropriate page
        if current_page in page_mapping:
            self.pages[page_mapping[current_page]]()
        else:
            # Default to home page if invalid page
            self.render_home()
    

        # Add footer to every page
        self.add_footer()

if __name__ == "__main__":
    app = ResumeApp()
    app.main()