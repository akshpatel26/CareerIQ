import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import time
import re

class FeedbackManager:
    def __init__(self):
        self.db_path = "feedback/feedback.db"
        self.setup_database()

    def setup_database(self):
        """Create feedback table if it doesn't exist with all required fields"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
        table_exists = c.fetchone() is not None
        
        if not table_exists:
            # Create new table with all required fields
            c.execute('''
                CREATE TABLE feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    contact_no TEXT NOT NULL,
                    email TEXT NOT NULL,
                    branch TEXT NOT NULL,
                    rating INTEGER,
                    usability_score INTEGER,
                    feature_satisfaction INTEGER,
                    missing_features TEXT,
                    improvement_suggestions TEXT,
                    user_experience TEXT,
                    timestamp DATETIME
                )
            ''')
            print("✅ Created new feedback table with all required fields")
        else:
            # Check if new columns exist and add them if needed
            c.execute("PRAGMA table_info(feedback)")
            columns = [column[1] for column in c.fetchall()]
            
            required_columns = ['full_name', 'contact_no', 'branch']
            for col in required_columns:
                if col not in columns:
                    try:
                        c.execute(f'ALTER TABLE feedback ADD COLUMN {col} TEXT')
                        print(f"✅ Added {col} column")
                    except sqlite3.OperationalError as e:
                        print(f"❌ Failed to add {col} column: {e}")
        
        conn.commit()
        conn.close()

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        """Validate phone number format (Indian mobile numbers)"""
        # Remove any spaces, dashes, or parentheses
        phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check for Indian mobile number patterns
        patterns = [
            r'^[6-9]\d{9}$',  # 10 digit starting with 6-9
            r'^\+91[6-9]\d{9}$',  # +91 followed by 10 digits
            r'^91[6-9]\d{9}$',  # 91 followed by 10 digits
        ]
        
        return any(re.match(pattern, phone_clean) for pattern in patterns)

    def save_feedback(self, feedback_data):
        """Save feedback to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO feedback (
                full_name, contact_no, email, branch,
                rating, usability_score, feature_satisfaction,
                missing_features, improvement_suggestions,
                user_experience, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_data['full_name'],
            feedback_data['contact_no'],
            feedback_data['email'],
            feedback_data['branch'],
            feedback_data['rating'],
            feedback_data['usability_score'],
            feedback_data['feature_satisfaction'],
            feedback_data['missing_features'],
            feedback_data['improvement_suggestions'],
            feedback_data['user_experience'],
            datetime.now()
        ))
        conn.commit()
        conn.close()

    def get_feedback_stats(self):
        """Get feedback statistics"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM feedback", conn)
        conn.close()
        
        if df.empty:
            return {
                'avg_rating': 0,
                'avg_usability': 0,
                'avg_satisfaction': 0,
                'total_responses': 0,
                'branch_distribution': {}
            }
        
        branch_counts = df['branch'].value_counts().to_dict() if 'branch' in df.columns else {}
        
        return {
            'avg_rating': df['rating'].mean() if 'rating' in df.columns else 0,
            'avg_usability': df['usability_score'].mean() if 'usability_score' in df.columns else 0,
            'avg_satisfaction': df['feature_satisfaction'].mean() if 'feature_satisfaction' in df.columns else 0,
            'total_responses': len(df),
            'branch_distribution': branch_counts
        }

    def render_star_rating(self, label, key, default_value=5):
        """Render interactive star rating component"""
        st.markdown(f'<label class="feedback-label" style="color: #E0E0E0; font-weight: 600; display: block; margin-bottom: 10px;">{label}</label>', unsafe_allow_html=True)
        
        # Initialize session state for this rating if not exists
        if f"{key}_rating" not in st.session_state:
            st.session_state[f"{key}_rating"] = default_value
        
        # Create columns for star buttons
        cols = st.columns([1, 1, 1, 1, 1, 3])
        
        current_rating = st.session_state[f"{key}_rating"]
        
        # Create interactive star buttons
        for i in range(1, 6):
            with cols[i-1]:
                if i <= current_rating:
                    star_display = "⭐"
                else:
                    star_display = "☆"
                
                if st.button(star_display, key=f"{key}_star_{i}", 
                           help=f"Rate {i} out of 5",
                           use_container_width=True):
                    st.session_state[f"{key}_rating"] = i
                    st.rerun()
        
        # Display rating text
        with cols[5]:
            rating_labels = {1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent"}
            st.markdown(f'<div style="color: #E0E0E0; padding: 8px; font-weight: 500;">{current_rating}/5 - {rating_labels[current_rating]}</div>', 
                       unsafe_allow_html=True)
        
        return current_rating
    
    def render_feedback_form(self):
        """Render the Google Form-style feedback form"""
    
        # Custom CSS for Google Form styling
        st.markdown("""
        <style>
        .google-form-header {
            background: linear-gradient(135deg, #4285f4, #34a853, #ea4335, #fbbc05);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }
        .required-field {
            color: #ea4335;
            font-weight: bold;
        }
        .form-section {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #4285f4;
        }
        .feedback-label {
            color: #E0E0E0;
            font-weight: 600;
            display: block;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        </style>
        """, unsafe_allow_html=True)
    
        # Full Name
        st.markdown('<label class="feedback-label"> Full Name <span class="required-field">*</span></label>', unsafe_allow_html=True)
        full_name = st.text_input("", placeholder="Enter your full name", key="user_full_name", label_visibility="collapsed")
    
        # Contact Number
        st.markdown('<label class="feedback-label"> Contact No</label>', unsafe_allow_html=True)
        contact_no = st.text_input("", placeholder="Enter your mobile number (Optional)", key="user_contact", label_visibility="collapsed")
        if contact_no and contact_no.strip():
            if self.validate_phone(contact_no):
                st.markdown('<div style="color: #4CAF50; font-size: 0.9em;">✅ Valid phone number</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: #FF5722; font-size: 0.9em;">❌ Please enter a valid Indian mobile number</div>', unsafe_allow_html=True)
    
        # Email Address
        st.markdown('<label class="feedback-label"> Email Address <span class="required-field">*</span></label>', unsafe_allow_html=True)
        email = st.text_input("", placeholder="Enter your email address", key="user_email", label_visibility="collapsed")
        if email:
            if self.validate_email(email):
                st.markdown('<div style="color: #4CAF50; font-size: 0.9em;">✅ Valid email format</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: #FF5722; font-size: 0.9em;">❌ Please enter a valid email address</div>', unsafe_allow_html=True)
    
        # Branch
        st.markdown('<label class="feedback-label"> Branch <span class="required-field">*</span></label>', unsafe_allow_html=True)
        branch_options = [
            "Select your branch",
            "CE (Computer Engineering)",
            "IT (Information Technology)",
            "EC (Electronics & Communication)",
            "EE (Electrical Engineering)",
            "ME (Mechanical Engineering)",
            "Civil Engineering",
            "AUTO (Automobile Engineering)",
            "MCA (Master of Computer Applications)",
            "Other (Please specify in feedback)"
        ]
        branch = st.selectbox("", options=branch_options, key="user_branch", label_visibility="collapsed")
    
        # Ratings Section
        st.markdown("####  Overall Experience Rating ? <span class='required-field'>*</span>", unsafe_allow_html=True)
        rating = self.render_vertical_0_to_10_rating("overall")
    
        st.markdown("####  How easy was it to use our app ? <span class='required-field'>*</span>", unsafe_allow_html=True)
        usability_score = self.render_vertical_0_to_10_rating("usability")
    
        st.markdown("####  How satisfied are you with our features ? <span class='required-field'>*</span>", unsafe_allow_html=True)
        feature_satisfaction = self.render_vertical_0_to_10_rating("features")
    
        # Detailed Feedback (Now Optional)
        st.markdown('<label class="feedback-label"> Missing Features</label>', unsafe_allow_html=True)
        missing_features = st.text_area("", placeholder="What features would you like to see? (Optional)", key="missing_features", label_visibility="collapsed", height=100)
    
        st.markdown('<label class="feedback-label"> Improvement Suggestions</label>', unsafe_allow_html=True)
        improvement_suggestions = st.text_area("", placeholder="How can we make this better? (Optional)", key="improvements", label_visibility="collapsed", height=100)
    
        st.markdown('<label class="feedback-label"> Experience Journey</label>', unsafe_allow_html=True)
        user_experience = st.text_area("", placeholder="Tell us about your journey! (Optional)", key="experience", label_visibility="collapsed", height=120)
        st.markdown('</div>', unsafe_allow_html=True)
    
        # ✅ Required Fields Validation (Updated to exclude text areas)
        required_fields_filled = (
            full_name and full_name.strip() != "" and
            (not contact_no or self.validate_phone(contact_no)) and  # Only validate if provided
            email and self.validate_email(email) and
            branch and branch != "Select your branch" and
            rating is not None and
            usability_score is not None and
            feature_satisfaction is not None
        )
    
        # Missing fields list (Updated to exclude text areas)
        if not required_fields_filled:
            missing_fields = []
            if not full_name or full_name.strip() == "":
                missing_fields.append("Full Name")
            if contact_no and contact_no.strip() and not self.validate_phone(contact_no):
                missing_fields.append("Valid Contact Number Format")
            if not email or not self.validate_email(email):
                missing_fields.append("Valid Email Address")
            if not branch or branch == "Select your branch":
                missing_fields.append("Branch")
            if rating is None:
                missing_fields.append("Overall Experience Rating")
            if usability_score is None:
                missing_fields.append("Usability Rating")
            if feature_satisfaction is None:
                missing_fields.append("Feature Satisfaction Rating")
    
            st.markdown(
                f'<div style="color: #FF9800; text-align: center; margin: 15px 0; padding: 15px; background: rgba(255, 152, 0, 0.1); border-radius: 10px; border-left: 4px solid #FF9800;">⚠️ Please fill in the following required fields: <strong>{", ".join(missing_fields)}</strong></div>',
                unsafe_allow_html=True
            )
    
        # Submit Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(" Submit Feedback", key="submit_feedback", use_container_width=True, disabled=not required_fields_filled, type="primary"):
                try:
                    # Save feedback (handle optional fields with default empty strings)
                    feedback_data = {
                        'full_name': full_name.strip(),
                        'contact_no': contact_no.strip() if contact_no else "",
                        'email': email.strip().lower(),
                        'branch': branch,
                        'rating': rating,
                        'usability_score': usability_score,
                        'feature_satisfaction': feature_satisfaction,
                        'missing_features': missing_features.strip() if missing_features else "",
                        'improvement_suggestions': improvement_suggestions.strip() if improvement_suggestions else "",
                        'user_experience': user_experience.strip() if user_experience else ""
                    }
                    self.save_feedback(feedback_data)
    
                    st.success(f" Thank you {full_name.split()[0]}! Your feedback has been submitted successfully.")
    
                    # Reset form
                    for key in ['user_full_name', 'user_contact', 'user_email', 'user_branch',
                                'overall_rating', 'usability_rating', 'features_rating',
                                'missing_features', 'improvements', 'experience']:
                        if key in st.session_state:
                            del st.session_state[key]
    
                except Exception as e:
                    st.error(f" Oops! Something went wrong: {str(e)}")

    def render_vertical_0_to_10_rating(self, key):
        """Render vertical 1-10 rating scale similar to Google Forms"""
        
        # Initialize session state for this rating (1-10 scale)
        rating_key = f"{key}_rating"
        if rating_key not in st.session_state:
            st.session_state[rating_key] = None
        
        # Rating descriptions mapping (1-10 scale)
        rating_descriptions = {
            1: "Very bad",
            2: "Bad", 
            3: "Poor",
            4: "Below average",
            5: "Average",
            6: "Good",
            7: "Very good",
            8: "Great",
            9: "Excellent",
            10: "Outstanding"
        }
        
        # Create radio button-style selection for each rating 1-10
        # Use index parameter to set default to None (no selection)
        selected_rating = st.radio(
            label="Rating",
            options=list(range(1, 11)),
            format_func=lambda x: f"{x} - {rating_descriptions.get(x, '')}",
            key=f"{key}_radio",
            label_visibility="collapsed",
            horizontal=False,
            index=None  # This ensures no default selection
        )
        
        # Update session state
        st.session_state[rating_key] = selected_rating
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return selected_rating

    def render_feedback_stats(self):
        """Render enhanced feedback statistics with branch distribution"""
        stats = self.get_feedback_stats()
        
        st.markdown("""
            <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(33, 150, 243, 0.15)); border-radius: 20px; margin-bottom: 30px; border: 1px solid rgba(255, 255, 255, 0.1);">
                <h3 style="color: #E0E0E0; font-size: 1.8em; margin-bottom: 10px;">📊 Community Feedback Dashboard</h3>
                <p style="color: #B0B0B0; font-size: 1.1em;">Real-time insights from our amazing users across all branches</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Main metrics
        cols = st.columns(4)
        metrics = [
            {"label": "🗣️ Total Responses", "value": f"{stats['total_responses']:,}", "delta": "↗️", "color": "#4CAF50"},
            {"label": "⭐ Avg Rating", "value": f"{stats['avg_rating']:.1f}/10.0", "delta": "🌟", "color": "#FFD700"},
            {"label": "🎯 Usability", "value": f"{stats['avg_usability']:.1f}/10.0", "delta": "👍", "color": "#2196F3"},
            {"label": "😊 Satisfaction", "value": f"{stats['avg_satisfaction']:.1f}/10.0", "delta": "💖", "color": "#9C27B0"}
        ]
        
        for col, metric in zip(cols, metrics):
            col.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.08); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="color: #B0B0B0; font-size: 0.95em; margin-bottom: 8px; font-weight: 500;">{metric['label']}</div>
                    <div style="font-size: 1.8em; color: {metric['color']}; margin: 10px 0; font-weight: 700;">{metric['value']}</div>
                    <div style="color: #E0E0E0; font-size: 1.4em; margin-top: 5px;">{metric['delta']}</div>
                </div>
            """, unsafe_allow_html=True)
        
       

# Initialize and run the feedback form
def main():
    st.set_page_config(
        page_title="Smart Resume AI - Feedback",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    feedback_manager = FeedbackManager()
    
    # Tab navigation
    tab1, tab2 = st.tabs(["📝 Submit Feedback", "📊 View Statistics"])
    
    with tab1:
        feedback_manager.render_feedback_form()
    
    with tab2:
        feedback_manager.render_feedback_stats()

if __name__ == "__main__":
    main()