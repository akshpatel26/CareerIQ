import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import time

class FeedbackManager:
    def __init__(self):
        self.db_path = "feedback/feedback.db"
        self.setup_database()

    def setup_database(self):
        """Create feedback table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rating INTEGER,
                usability_score INTEGER,
                feature_satisfaction INTEGER,
                missing_features TEXT,
                improvement_suggestions TEXT,
                user_experience TEXT,
                timestamp DATETIME
            )
        ''')
        conn.commit()
        conn.close()

    def save_feedback(self, feedback_data):
        """Save feedback to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO feedback (
                rating, usability_score, feature_satisfaction,
                missing_features, improvement_suggestions,
                user_experience, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
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
                'total_responses': 0
            }
        
        return {
            'avg_rating': df['rating'].mean(),
            'avg_usability': df['usability_score'].mean(),
            'avg_satisfaction': df['feature_satisfaction'].mean(),
            'total_responses': len(df)
        }

    def render_star_rating(self, label, key, default_value=5):
        """Render interactive star rating component"""
        st.markdown(f'<label class="feedback-label">{label}</label>', unsafe_allow_html=True)
        
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
        """Render the enhanced feedback form"""
    
        
        # st.markdown('<h2 class="feedback-header">✨ Share Your Amazing Feedback ✨</h2>', unsafe_allow_html=True)

        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        rating = self.render_star_rating("🌟 Overall Experience Rating", "overall", 5)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        usability_score = self.render_star_rating("🎯 How easy was it to use our app?", "usability", 5)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        feature_satisfaction = self.render_star_rating("💡 How satisfied are you with our features?", "features", 5)
        st.markdown('</div>', unsafe_allow_html=True)

        # Text Feedback Sections
        st.markdown('<div class="style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown('<label class="feedback-label">🚀 What features would you like to see added?</label>', unsafe_allow_html=True)
        missing_features = st.text_area("", placeholder="✨ Share your creative feature ideas that would make this app even more amazing...", 
                                       key="missing_features", label_visibility="collapsed", height=100)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown('<label class="feedback-label">💫 How can we make this experience better?</label>', unsafe_allow_html=True)
        improvement_suggestions = st.text_area("", placeholder="🎨 Your suggestions help us create magic! Tell us how we can improve...", 
                                             key="improvements", label_visibility="collapsed", height=100)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown('<label class="feedback-label">🎉 Tell us about your experience journey</label>', unsafe_allow_html=True)
        user_experience = st.text_area("", placeholder="📖 Share your story! What was your experience like using our app?...", 
                                     key="experience", label_visibility="collapsed", height=120)
        st.markdown('</div>', unsafe_allow_html=True)

        # Enhanced Submit Button with better feedback
        if st.button("🚀 Submit My Awesome Feedback", key="submit_feedback", use_container_width=True):
            try:
                # Animated progress with better messaging
                progress_container = st.container()
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    progress_messages = [
                        ("📝 Receiving your valuable feedback...", 0, 20),
                        ("🔍 Analyzing your insights...", 20, 40),
                        ("🎨 Processing your suggestions...", 40, 60),
                        ("💾 Securely saving to our database...", 60, 80),
                        ("✨ Adding your voice to our community...", 80, 95),
                        ("🎉 Finalizing your contribution...", 95, 100)
                    ]
                    
                    for message, start, end in progress_messages:
                        for i in range(start, end):
                            progress_bar.progress(i + 1)
                            status_text.markdown(f'<div class="pulse-animation" style="color: #4CAF50; font-weight: 600; text-align: center;">{message}</div>', 
                                               unsafe_allow_html=True)
                            time.sleep(0.02)

                # Save feedback
                feedback_data = {
                    'rating': rating,
                    'usability_score': usability_score,
                    'feature_satisfaction': feature_satisfaction,
                    'missing_features': missing_features,
                    'improvement_suggestions': improvement_suggestions,
                    'user_experience': user_experience
                }
                self.save_feedback(feedback_data)
                
                # Clear progress elements
                progress_bar.empty()
                status_text.empty()
                
                # Enhanced success message with animation
                success_container = st.empty()
                success_container.markdown("""
                    <div class="success-animation" style="text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(33, 150, 243, 0.2), rgba(156, 39, 176, 0.2)); border-radius: 20px; margin: 20px 0; backdrop-filter: blur(10px); border: 2px solid rgba(76, 175, 80, 0.3);">
                        <h2 style="color: #4CAF50; font-size: 2.5em; margin-bottom: 15px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🎉 Thank You! 🎉</h2>
                        <p style="color: #E0E0E0; font-size: 1.3em; margin-bottom: 10px;">Your feedback is the fuel that powers our innovation!</p>
                        <p style="color: #B0B0B0; font-size: 1.1em;">Smart Resume AI gets better because of amazing users like you! 🚀</p>
                        <div style="margin-top: 20px;">
                            <span style="font-size: 1.5em;">⭐ ⭐ ⭐ ⭐ ⭐</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Multiple celebration effects
                st.balloons()
                time.sleep(1)
                # st.snow()
                
                # Keep success message visible longer
                time.sleep(3)
                
                # Reset ratings for next user
                for key in ['overall_rating', 'usability_rating', 'features_rating']:
                    if key in st.session_state:
                        del st.session_state[key]
                
            except Exception as e:
                st.error(f"🚨 Oops! Something went wrong: {str(e)}")
                st.info("💡 Please try again or contact support if the issue persists.")

        st.markdown('</div>', unsafe_allow_html=True)

    def render_feedback_stats(self):
        """Render enhanced feedback statistics"""
        stats = self.get_feedback_stats()
        
        st.markdown("""
            <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(33, 150, 243, 0.15), rgba(156, 39, 176, 0.15)); border-radius: 20px; margin-bottom: 30px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1);">
                <h3 style="color: #E0E0E0; font-size: 1.8em; margin-bottom: 10px;">📊 Community Feedback Dashboard</h3>
                <p style="color: #B0B0B0; font-size: 1.1em;">Real-time insights from our amazing users</p>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(4)
        metrics = [
            {"label": "🗣️ Total Voices", "value": f"{stats['total_responses']:,}", "delta": "↗️", "color": "#4CAF50"},
            {"label": "⭐ Avg Rating", "value": f"{stats['avg_rating']:.1f}/5.0", "delta": "🌟", "color": "#FFD700"},
            {"label": "🎯 Usability", "value": f"{stats['avg_usability']:.1f}/5.0", "delta": "🚀", "color": "#2196F3"},
            {"label": "😊 Satisfaction", "value": f"{stats['avg_satisfaction']:.1f}/5.0", "delta": "💖", "color": "#9C27B0"}
        ]
        
        for col, metric in zip(cols, metrics):
            col.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.08); padding: 20px; border-radius: 15px; text-align: center; transition: all 0.3s ease; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); cursor: pointer;" 
                     onmouseover="this.style.transform='translateY(-5px) scale(1.05)'; this.style.boxShadow='0 10px 25px rgba(0,0,0,0.2)'"
                     onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='none'">
                    <div style="color: #B0B0B0; font-size: 0.95em; margin-bottom: 8px; font-weight: 500;">{metric['label']}</div>
                    <div style="font-size: 1.8em; color: {metric['color']}; margin: 10px 0; font-weight: 700; text-shadow: 0 1px 3px rgba(0,0,0,0.3);">{metric['value']}</div>
                    <div style="color: #E0E0E0; font-size: 1.4em; margin-top: 5px;">{metric['delta']}</div>
                </div>
            """, unsafe_allow_html=True)


