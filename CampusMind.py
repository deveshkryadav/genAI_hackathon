import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os
import google.generativeai as genai
import json
from datetime import datetime, date, timedelta
import plotly.express as px
import time
#===================================================PAGE CONFIGURATION================================================================================
st.set_page_config(
    page_title="CampusMind - Student Mental Health Support",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
#===================================================AUTHENTICATION================================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'auth_page' not in st.session_state:
    st.session_state.auth_page = 'login'
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

auth_css = """
<style>
    .auth-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .auth-header {
        text-align: center;
        color: #6B9080;
        margin-bottom: 2rem;
    }
    .auth-button {
        background-color: #6B9080;
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1rem;
        margin-top: 1rem;
        width: 100%;
    }
    .auth-button:hover {
        background-color: #5A7F70;
    }
    .auth-switch {
        text-align: center;
        margin-top: 1.5rem;
        color: #666;
    }
    .auth-switch a {
        color: #6B9080;
        text-decoration: none;
        cursor: pointer;
    }
    .admin-button {
        background-color: #FF6B6B;
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1rem;
        margin-top: 0.5rem;
        width: 100%;
    }
    .admin-button:hover {
        background-color: #E55A5A;
    }
</style>
"""

def show_login_page():
    """Display login page"""
    st.markdown(auth_css, unsafe_allow_html=True)
    st.markdown('<div class="auth-header"><h1>🔐 Login</h1></div>', unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password") 
        login_btn = st.form_submit_button("Login", use_container_width=True) 
        if login_btn:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("Login successful! Redirecting...")
            st.rerun()
    if st.button("Login as Administrator", key="admin_btn", use_container_width=True):
        st.session_state.auth_page = "admin_login"
        st.rerun() 
    st.markdown(
        '<div class="auth-switch">Don\'t have an account? <a>Sign up here</a></div>', 
        unsafe_allow_html=True
    )
def show_signup_page():
    """Display signup page"""
    st.markdown(auth_css, unsafe_allow_html=True)
    st.markdown('<div class="auth-header"><h1>👤 Sign Up</h1></div>', unsafe_allow_html=True)
    
    with st.form("signup_form"):
        name = st.text_input("👤 Full Name", placeholder="Enter your full name")
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        
        signup_btn = st.form_submit_button("Create Account", use_container_width=True)        
        if signup_btn:
            st.success("Account created successfully! You can now login.")
            st.session_state.auth_page = "login"
            st.rerun()   
    st.markdown(
        '<div class="auth-switch">Already have an account? <a>Login here</a></div>', 
        unsafe_allow_html=True
    )

def show_admin_login_page():
    """Display admin login page"""
    st.markdown(auth_css, unsafe_allow_html=True)
    st.markdown('<div class="auth-header"><h1>👨‍💼 Admin Login</h1></div>', unsafe_allow_html=True)
    
    with st.form("admin_login_form"):
        admin_email = st.text_input("📧 Admin Email", placeholder="Enter admin email")
        admin_password = st.text_input("🔒 Admin Password", type="password", placeholder="Enter admin password")
        
        admin_login_btn = st.form_submit_button("Login as Admin", use_container_width=True)
        
        if admin_login_btn:
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.session_state.user_email = admin_email
            st.success("Admin login successful! Redirecting...")
            st.rerun()
    
    st.markdown(
        '<div class="auth-switch"><a>Back to regular login</a></div>', 
        unsafe_allow_html=True
    )

#====================================================================================================================================
# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #4A90E2;
        border-bottom: 2px solid #4A90E2;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: #f0f7ff;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .urgent {
        background-color: #ffcccc;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .chat-bubble {
        background-color: #e6f2ff;
        padding: 12px 18px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
    }
    .user-bubble {
        background-color: #d9f0d1;
        margin-left: 20%;
    }
    .resource-card {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #4A90E2;
    }
</style>
""", unsafe_allow_html=True)
#===================================================SESSION STATE VARIABLES================================================================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'phq_score' not in st.session_state:
    st.session_state.phq_score = None
if 'gad_score' not in st.session_state:
    st.session_state.gad_score = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Navigation function
def navigate_to(page):
    st.session_state.current_page = page

# Sample data for demonstration
counselors = [
    {"name": "Dr. Priya Sharma", "specialty": "Anxiety & Stress", "availability": "Mon, Wed, Fri", "rating": 4.8},
    {"name": "Dr. Rajesh Kumar", "specialty": "Academic Pressure", "availability": "Tue, Thu", "rating": 4.6},
    {"name": "Ms. Anjali Singh", "specialty": "Relationship Issues", "availability": "Mon-Fri", "rating": 4.9},
    {"name": "Dr. Amit Patel", "specialty": "Depression", "availability": "Wed, Thu, Sat", "rating": 4.7}
]

resources = [
    {"title": "Coping with Exam Stress", "type": "Video", "duration": "12 min", "language": "English/Hindi"},
    {"title": "Mindfulness Meditation", "type": "Audio", "duration": "15 min", "language": "English"},
    {"title": "Managing Anxiety", "type": "Guide", "duration": "10 min read", "language": "English/Tamil"},
    {"title": "Improving Sleep Quality", "type": "Article", "duration": "8 min read", "language": "English/Telugu"}
]

forum_topics = [
    {"title": "How to deal with homesickness?", "replies": 24, "user": "Anonymous", "date": "2 days ago"},
    {"title": "Tips for managing coursework stress", "replies": 42, "user": "Anonymous", "date": "5 days ago"},
    {"title": "Looking for study buddies", "replies": 15, "user": "Anonymous", "date": "1 week ago"},
    {"title": "Coping with anxiety before presentations", "replies": 33, "user": "Anonymous", "date": "3 days ago"}
]

# Home Page
def home_page():
    # Modern header with gradient and subtle animation
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2.5rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .feature-card {
        background: white;
        padding: 1.75rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .quick-action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none !important;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .testimonial-card {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid #667eea;
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .assessment-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header section
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; font-size: 3.5rem; font-weight: 700; margin-bottom: 0.5rem;">CampusMind</h1>
        <h3 style="color: rgba(255, 255, 255, 0.9); font-weight: 300; margin-top: 0;">
            Your compassionate mental health companion
        </h3>
        <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem; max-width: 600px; margin: 1rem auto;">
            Supporting students through their academic journey with accessible, confidential, 
            and stigma-free mental health resources
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick actions with beautiful buttons
    st.markdown("""
    <style>
    .stButton > button {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 style="text-align: center; color: #333; margin-bottom: 1.5rem;">Quick Access</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🤖 AI First Aid", width="stretch", key="ai_btn"):
            navigate_to("AI First Aid")
    with col2:
        if st.button("📅 Book Session", width="stretch", key="appt_btn"):
            navigate_to("Book Appointment")
    with col3:
        if st.button("📚 Resources", width="stretch", key="resources_btn"):
            navigate_to("Resources")
    with col4:
        if st.button("👥 Peer Support", width="stretch", key="peer_btn"):
            navigate_to("Peer Support")

    # Features grid
    st.markdown("""
    <div style="margin: 3rem 0;">
        <h2 style="text-align: center; color: #333; margin-bottom: 2rem;">How We Support You</h2>
    </div>
    """, unsafe_allow_html=True)
    
    features = [
        {
            "icon": "🤖",
            "title": "AI-Guided Support",
            "description": "Instant, confidential chat support with personalized coping strategies and guidance"
        },
        {
            "icon": "📅",
            "title": "Professional Sessions",
            "description": "Easy booking with certified campus counselors in a private, secure environment"
        },
        {
            "icon": "📚",
            "title": "Learning Resources",
            "description": "Curated videos, audio guides, and articles in multiple regional languages"
        },
        {
            "icon": "👥",
            "title": "Peer Community",
            "description": "Connect with trained student volunteers in a safe, moderated space"
        },
        {
            "icon": "📊",
            "title": "Self-Assessment",
            "description": "Anonymous screening tools to understand your mental wellbeing"
        },
        {
            "icon": "🔒",
            "title": "Complete Privacy",
            "description": "Your data is encrypted and never shared without your consent"
        }
    ]
    
    cols = st.columns(3)
    for i, feature in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">{feature['icon']}</div>
                <h3 style="color: #333; margin-bottom: 0.75rem;">{feature['title']}</h3>
                <p style="color: #666; line-height: 1.6;">{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Self-assessment section
    st.markdown("""
    <div class="assessment-section">
        <h2 style="color: white; margin-bottom: 1rem;">Start Your Wellness Journey</h2>
        <p style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1.5rem;">
            Take a quick anonymous assessment to understand your current mental wellbeing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🧠 Depression Screen", width="stretch", key="phq_btn"):
            navigate_to("Self Assessment")
    with col2:
        if st.button("😰 Anxiety Screen", width="stretch", key="gad_btn"):
            navigate_to("Self Assessment")
    with col3:
        if st.button("📋 All Assessments", width="stretch", key="all_btn"):
            navigate_to("Self Assessment")

    # Testimonials
    st.markdown("""
    <div style="margin: 4rem 0;">
        <h2 style="text-align: center; color: #333; margin-bottom: 2rem;">Student Stories</h2>
    </div>
    """, unsafe_allow_html=True)
    
    testimonials = [
        {
            "text": "The AI chat helped me through a panic attack before my exam. So grateful for this resource!",
            "author": "Engineering Student",
            "rating": "⭐️⭐️⭐️⭐️⭐️"
        },
        {
            "text": "Booking a counselor was so easy and private. Finally got the help I needed without the stigma.",
            "author": "Arts Student",
            "rating": "⭐️⭐️⭐️⭐️⭐️"
        },
        {
            "text": "The resources in my regional language made all the difference. Thank you for being inclusive!",
            "author": "Medical Student",
            "rating": "⭐️⭐️⭐️⭐️⭐️"
        }
    ]
    
    testimonial_cols = st.columns(3)
    for i, testimonial in enumerate(testimonials):
        with testimonial_cols[i]:
            st.markdown(f"""
            <div class="testimonial-card">
                <div style="font-size: 1.2rem; color: #667eea; margin-bottom: 1rem;">{testimonial['rating']}</div>
                <p style="font-style: italic; color: #555; line-height: 1.6; margin-bottom: 1rem;">
                    "{testimonial['text']}"
                </p>
                <p style="font-weight: 600; color: #667eea; margin: 0;">- {testimonial['author']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Statistics
    st.markdown("""
    <div style="margin: 4rem 0;">
        <h2 style="text-align: center; color: #333; margin-bottom: 2rem;">Our Impact</h2>
    </div>
    """, unsafe_allow_html=True)
    
    stats = [
        {"number": "2,500+", "label": "Students Supported"},
        {"number": "500+", "label": "Sessions Completed"},
        {"number": "15+", "label": "Campuses Served"},
        {"number": "24/7", "label": "Support Available"}
    ]
    
    stats_cols = st.columns(4)
    for i, stat in enumerate(stats):
        with stats_cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div class="stats-number">{stat['number']}</div>
                <p style="color: #666; font-weight: 500;">{stat['label']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Final CTA
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0; padding: 2rem; background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%); border-radius: 16px;">
        <h2 style="color: #333; margin-bottom: 1rem;">Ready to Prioritize Your Mental Health?</h2>
        <p style="color: #666; margin-bottom: 1.5rem; font-size: 1.1rem;">
            Join thousands of students who have taken the first step toward better mental wellbeing
        </p>
        <button style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; border: none; padding: 1rem 2rem; border-radius: 12px; 
                      font-size: 1.1rem; font-weight: 500; cursor: pointer; transition: all 0.3s ease;"
                onmouseover="this.style.transform='scale(1.05)'" 
                onmouseout="this.style.transform='scale(1)'"
                onclick="window.location='#quick-access'">
            Get Started Today
        </button>
    </div>
    """, unsafe_allow_html=True)

    # Footer note
    st.markdown("""
    <div style="text-align: center; color: #999; padding: 2rem 0; border-top: 1px solid #eee;">
        <p>Confidential • Secure • Student-Focused</p>
        <p>If you're in crisis, please contact emergency services immediately</p>
    </div>
    """, unsafe_allow_html=True)


# --- Safety constants ---
CRISIS_KEYWORDS = ['suicide', 'kill myself', 'end it all', 'want to die', 'harm myself', 'suicidal']
CRISIS_RESPONSE = """
**I'm deeply concerned about what you've shared. Please know your life is precious.**

**Please connect with a trained professional immediately. They are free, confidential, and available 24/7:**
- **Crisis Text Line:** Text HOME to 741741
- **988 Suicide & Crisis Lifeline:** Call or text 988
- **The Trevor Project:** 1-866-488-7386 (for LGBTQ youth)

*This is an automated response. This tool cannot provide crisis care.*
"""
DISCLAIMER = "*I'm an AI practice tool, not a licensed therapist. Please seek professional help if needed.*"

# --- Off-topic detection ---
OFF_TOPIC_KEYWORDS = [
    'capital', 'weather', 'sports', 'movie', 'music', 'food', 'recipe', 
    'politics', 'news', 'celebrity', 'game', 'score', 'stock', 'price',
    'shopping', 'buy', 'purchase', 'movie', 'film', 'actor', 'actress',
    'restaurant', 'recipe', 'cook', 'sport', 'team', 'player', 'trivia'
]

OFF_TOPIC_RESPONSE = "I'm here to focus on your mental well-being. Let's talk about how you're feeling or any concerns you might have."

def is_off_topic(message):
    """Check if the message is off-topic from mental health"""
    message_lower = message.lower()
    
    # Check for off-topic keywords
    if any(keyword in message_lower for keyword in OFF_TOPIC_KEYWORDS):
        return True
        
    # Check if it's a factual question (starts with who, what, when, where, why, how, is, are)
    question_words = ['who ', 'what ', 'when ', 'where ', 'why ', 'how ', 'is ', 'are ', 'do ', 'does ']
    if any(message_lower.startswith(word) for word in question_words):
        # But allow mental health related questions
        mental_health_terms = ['feel', 'anxious', 'stress', 'worry', 'sad', 'depress', 'happy', 'mental']
        if not any(term in message_lower for term in mental_health_terms):
            return True
            
    return False
@st.cache_resource(show_spinner="Loading the AI assistant. This may take a moment...")
def configure_gemini():
    """
    Configures and returns the Gemini model with appropriate settings.
    Returns the model object if successful, None otherwise.
    """
    try:
        # Try to get API key from environment variable (for Streamlit Cloud)
        api_key = os.environ.get('GEMINI_API_KEY')
        
        # If not found, try to get from secrets (for local testing)
        if not api_key:
            try:
                api_key = st.secrets['GEMINI_API_KEY']
            except:
                st.error("Gemini API key not found. Please set GEMINI_API_KEY in your environment variables or Streamlit secrets.")
                return None
        
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Create the model instance with safety settings adjusted for mental health context
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 500,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        # Create and return the model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",  # Fixed: added 'gemini-' prefix
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Test the configuration with a simple call
        try:
            # Quick test to verify the API key works
            test_response = model.generate_content("Hello")
            st.sidebar.success("✅ Gemini AI configured successfully!")
            return model
        except Exception as test_error:
            st.error(f"Gemini API test failed: {test_error}")
            st.info("Please check your API key and ensure it has access to the Gemini API")
            return None
        
    except Exception as e:
        st.error(f"Gemini configuration failed. Error: {e}")
        return None
def generate_gemini_response(user_input, chat_history, model):
    """Generate a response using Gemini API"""
    # Crisis check
    if any(keyword in user_input.lower() for keyword in CRISIS_KEYWORDS):
        return CRISIS_RESPONSE
    
    # Off-topic check
    if is_off_topic(user_input):
        return OFF_TOPIC_RESPONSE
    
    # Prepare conversation history (last 6 messages)
    conversation_history = []
    for msg in chat_history[-6:]:
        if msg["role"] == "user":
            conversation_history.append({"role": "user", "parts": [msg["content"]]})
        else:  # AI messages
            conversation_history.append({"role": "assistant", "parts": [msg["content"]]})

    # Add system instruction as the very first user message
    system_instruction = (
        "You are a mental health first aid assistant. Provide empathetic, "
        "supportive, and non-judgmental responses. Focus on active listening, "
        "validation, and gentle guidance. Keep responses concise (2-3 sentences). "
        "If someone shares something concerning, gently suggest professional resources. "
        "Always maintain a caring and compassionate tone."
    )
    conversation_history.insert(0, {"role": "user", "parts": [system_instruction]})

    # Generate response
    try:
        chat = model.start_chat(history=conversation_history)
        gemini_response = chat.send_message(user_input)

        # Safely extract text
        if hasattr(gemini_response, "text") and gemini_response.text:
            return gemini_response.text
        elif hasattr(gemini_response, "candidates"):
            return gemini_response.candidates[0].content.parts[0].text
        else:
            return "I'm here for you, but I couldn’t generate a proper response this time."

    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "I'm having trouble responding right now. Please try again."

def ai_first_aid():
    # Configure Gemini
    model = configure_gemini()
    if model is None:
        st.error("Failed to initialize AI assistant. Please check your API key.")
        return
    
    # Custom CSS for the chat interface
    st.markdown("""
    <style>
    .chat-header {
        font-size: 2.2rem;
        color: #6B9080;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #EAF4F4;
    }
    .chat-container {
        background-color: #F6FFF8;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #EAF4F4;
    }
    .user-message {
        background-color: #EAF4F4;
        color: #4A4A4A;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        margin-left: 20%;
        border-bottom-right-radius: 4px;
    }
    .ai-message {
        background-color: white;
        color: #4A4A4A;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        margin-right: 20%;
        border-bottom-left-radius: 4px;
        border: 1px solid #EAF4F4;
    }
    .quick-option {
        background-color: white;
        color: #6B9080;
        border: 1px solid #6B9080;
        padding: 8px 12px;
        border-radius: 20px;
        margin: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 14px;
        display: inline-block;
    }
    .quick-option:hover {
        background-color: #EAF4F4;
    }
    .crisis-expander {
        background-color: #FFE8E8;
        border: 1px solid #FFCCCC;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown('<div class="chat-header">AI-Guided Mental Health First Aid</div>', unsafe_allow_html=True)
    
    # Info box with improved styling
    st.markdown("""
    <div style="background-color: #EAF4F4; color: #4A4A4A; padding: 1rem; border-radius: 8px; border-left: 4px solid #6B9080; margin-bottom: 1.5rem;">
        <strong>Note:</strong> This is a supportive chat system that provides initial guidance. It is not a replacement for professional help.
    </div>
    """, unsafe_allow_html=True)

    # Crisis resources with improved styling
    with st.expander("⚠️ Immediate Crisis Resources", expanded=False):
        st.markdown("""
        <div style="background-color: #FFF3F3; padding: 1rem; border-radius: 8px;">
            <p style="color: #D32F2F; font-weight: bold; margin-top: 0;">
            If you're in crisis or having thoughts of self-harm, please contact these resources immediately:
            </p>
            <ul style="color: #4A4A4A;">
                <li>College Counseling Center: +91-XXX-XXXX-XXXX</li>
                <li>Crisis Helpline: 9152987821 (24/7)</li>
                <li>Emergency Services: 112 or 102</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "ai", "content": "Hello, I'm here to listen and support you. How are you feeling today?"}
        ]

    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "ai":
            st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Pre-defined quick questions with improved styling
    quick_questions = [
        "I'm feeling anxious about exams",
        "I've been feeling sad lately",
        "I'm having trouble sleeping",
        "I'm feeling overwhelmed"
    ]

    st.markdown("**Quick options:**")
    cols = st.columns(2)
    for i, question in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(question, key=f"quick_{i}", use_container_width=True):
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": question})
                
                # Generate AI response
                with st.spinner("🧠 Thinking..."):
                    response = generate_gemini_response(question, st.session_state.chat_history, model)
                
                # Add AI response to chat history
                st.session_state.chat_history.append({"role": "ai", "content": response})
                
                # Refresh to display the new message
                st.rerun()

    # User input box with improved styling
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Generate AI response
        with st.spinner("🧠 Thinking..."):
            response = generate_gemini_response(user_input, st.session_state.chat_history, model)

        # Add AI message to chat history
        st.session_state.chat_history.append({"role": "ai", "content": response})

        # Refresh to display the new message
        st.rerun()

    # Clear conversation option with improved styling
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.chat_history = [
                {"role": "ai", "content": "Hello, I'm here to listen and support you. How are you feeling today?"}
            ]
            st.rerun()



# Self Assessment with Gemini Integration
def self_assessment():
    # Configure Gemini
    gemini_configured = configure_gemini()
    
    st.markdown("""
    <style>
    .sub-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
    }
    .insight-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .assessment-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .score-display {
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .minimal-score {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    .mild-score {
        background-color: #FFF9C4;
        color: #F57F17;
    }
    .moderate-score {
        background-color: #FFE0B2;
        color: #EF6C00;
    }
    .severe-score {
        background-color: #FFEBEE;
        color: #C62828;
    }
    .stRadio > div {
        flex-direction: row;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .stRadio [role="radiogroup"] {
        flex-direction: row;
        gap: 15px;
    }
    .stRadio label {
        background-color: #f0f2f6;
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid #dcdcdc;
        margin-right: 5px;
    }
    .stRadio input:checked + label {
        background-color: #1E88E5;
        color: white;
        border-color: #1E88E5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sub-header">Mental Health Self-Assessment</div>', unsafe_allow_html=True)
    
    # Introduction
    with st.expander("About These Assessments", expanded=False):
        st.info("""
        These screening tools are not diagnostic but can help you understand your symptoms better.
        - **PHQ-9**: Assesses depression symptoms based on the DSM-5 criteria
        - **GAD-7**: Measures anxiety symptoms severity
        
        Your responses are confidential. For a formal diagnosis, please consult a qualified mental health professional.
        """)
    
    assessment_type = st.radio("Choose assessment type:", 
                              ["PHQ-9 (Depression)", "GAD-7 (Anxiety)"], index=0,
                              label_visibility="collapsed")
    
    st.markdown("---")
    
    if assessment_type == "PHQ-9 (Depression)":
        st.markdown("#### PHQ-9 Depression Screening")
        st.caption("Over the last 2 weeks, how often have you been bothered by the following problems?")
        
        questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading the newspaper or watching television",
            "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
            "Thoughts that you would be better off dead or of hurting yourself in some way"
        ]
        
        options = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
        scores = []
        responses = []
        
        # Create a container for questions
        with st.container():
            for i, question in enumerate(questions):
                st.markdown(f"**{i+1}. {question}**")
                score = st.radio(
                    f"{i+1}. {question}",
                    options, 
                    key=f"phq_{i}", 
                    index=0, 
                    horizontal=True,
                    label_visibility="collapsed"
                )
                scores.append(options.index(score))
                responses.append(f"{i+1}. {question}: {score}")
                
                if i < len(questions) - 1:
                    st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Calculate PHQ-9 Score", width="stretch", type="primary"):
                total_score = sum(scores)
                st.session_state.phq_score = total_score
                st.session_state.phq_responses = responses
                
                st.markdown("### Assessment Results")
                
                # Determine score category and display appropriately
                if total_score < 5:
                    st.markdown(f'<div class="score-display minimal-score">Your PHQ-9 Score: {total_score} - Minimal depression</div>', unsafe_allow_html=True)
                    st.success("Your responses suggest minimal depression symptoms. Continue to monitor your mood and practice good self-care.")
                elif total_score < 10:
                    st.markdown(f'<div class="score-display mild-score">Your PHQ-9 Score: {total_score} - Mild depression</div>', unsafe_allow_html=True)
                    st.warning("Your responses suggest mild depression symptoms. Consider self-care strategies and check back in a week. If symptoms persist, consider speaking with a counselor.")
                elif total_score < 15:
                    st.markdown(f'<div class="score-display moderate-score">Your PHQ-9 Score: {total_score} - Moderate depression</div>', unsafe_allow_html=True)
                    st.warning("Your responses suggest moderate depression symptoms. Consider speaking with a counselor or mental health professional for support.")
                elif total_score < 20:
                    st.markdown(f'<div class="score-display severe-score">Your PHQ-9 Score: {total_score} - Moderately severe depression</div>', unsafe_allow_html=True)
                    st.error("Your responses suggest moderately severe depression symptoms. It is recommended to speak with a mental health professional.")
                else:
                    st.markdown(f'<div class="score-display severe-score">Your PHQ-9 Score: {total_score} - Severe depression</div>', unsafe_allow_html=True)
                    st.error("Your responses suggest severe depression symptoms. We strongly recommend consulting with a mental health professional as soon as possible.")
                    
                if total_score >= 10:
                    st.info("Based on your score, we recommend connecting with a counselor. Would you like to book an appointment?")
                    if st.button("Book Appointment with Counselor", width="stretch"):
                        st.session_state.current_page = "Book Appointment"
                        st.rerun()
        
        with col2:
            if st.button("Get AI Insights", type="secondary", key="phq_know_more", width="stretch"):
                if 'phq_score' in st.session_state:
                    if not gemini_configured:
                        st.warning("Gemini API is not configured. Using sample insights.")
                        display_sample_phq_insights(st.session_state.phq_score, st.session_state.phq_responses)
                    else:
                        # Prepare data for Gemini
                        assessment_data = {
                            "assessment_type": "PHQ-9 Depression",
                            "score": st.session_state.phq_score,
                            "responses": st.session_state.phq_responses,
                            "user_context": "college student"
                        }
                        
                        # Get insights from Gemini
                        with st.spinner("Getting personalized insights from Gemini AI..."):
                            gemini_response = get_gemini_insights(assessment_data)
                        
                        # Display Gemini response
                        st.markdown("### 📋 Personalized Insights from Gemini AI")
                        st.markdown("---")
                        st.markdown(f'<div class="insight-box">{gemini_response}</div>', unsafe_allow_html=True)
                        
                        # Save to session state
                        st.session_state.last_gemini_response = gemini_response
                else:
                    st.warning("Please calculate your score first to get personalized insights.")
    
    else:  # GAD-7 assessment
        st.markdown("#### GAD-7 Anxiety Screening")
        st.caption("Over the last 2 weeks, how often have you been bothered by the following problems?")
        
        questions = [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it is hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid as if something awful might happen"
        ]
        
        options = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
        scores = []
        responses = []
        
        # Create a container for questions
        with st.container():
            for i, question in enumerate(questions):
                st.markdown(f"**{i+1}. {question}**")
                score = st.radio(
                    f"{i+1}. {question}",
                    options, 
                    key=f"gad_{i}", 
                    index=0, 
                    horizontal=True,
                    label_visibility="collapsed"
                )
                scores.append(options.index(score))
                responses.append(f"{i+1}. {question}: {score}")
                
                if i < len(questions) - 1:
                    st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Calculate GAD-7 Score", width='stretch', type="primary"):
                total_score = sum(scores)
                st.session_state.gad_score = total_score
                st.session_state.gad_responses = responses
                
                st.markdown("### Assessment Results")
                
                # Determine score category and display appropriately
                if total_score < 5:
                    st.markdown(f'<div class="score-display minimal-score">Your GAD-7 Score: {total_score} - Minimal anxiety</div>', unsafe_allow_html=True)
                    st.success("Your responses suggest minimal anxiety symptoms. Continue to monitor your feelings and practice stress management.")
                elif total_score < 10:
                    st.markdown(f'<div class="score-display mild-score">Your GAD-7 Score: {total_score} - Mild anxiety</div>', unsafe_allow_html=True)
                    st.warning("Your responses suggest mild anxiety symptoms. Consider stress management techniques and check back in a week.")
                elif total_score < 15:
                    st.markdown(f'<div class="score-display moderate-score">Your GAD-7 Score: {total_score} - Moderate anxiety</div>', unsafe_allow_html=True)
                    st.warning("Your responses suggest moderate anxiety symptoms. Consider speaking with a counselor for support.")
                else:
                    st.markdown(f'<div class="score-display severe-score">Your GAD-7 Score: {total_score} - Severe anxiety</div>', unsafe_allow_html=True)
                    st.error("Your responses suggest severe anxiety symptoms. It is recommended to consult with a mental health professional.")
                    
                if total_score >= 10:
                    st.info("Based on your score, we recommend learning some anxiety management techniques. Would you like to access our resources?")
                    if st.button("View Anxiety Resources", width='stretch'):
                        st.session_state.current_page = "Resources"
                        st.rerun()
        
        with col2:
            if st.button("Get AI Insights", type="secondary", key="gad_know_more", width='stretch'):
                if 'gad_score' in st.session_state:
                    if not gemini_configured:
                        st.warning("Gemini API is not configured. Using sample insights.")
                        display_sample_gad_insights(st.session_state.gad_score, st.session_state.gad_responses)
                    else:
                        # Prepare data for Gemini
                        assessment_data = {
                            "assessment_type": "GAD-7 Anxiety",
                            "score": st.session_state.gad_score,
                            "responses": st.session_state.gad_responses,
                            "user_context": "college student"
                        }
                        
                        # Get insights from Gemini
                        with st.spinner("Getting personalized insights from Gemini AI..."):
                            gemini_response = get_gemini_insights(assessment_data)
                        
                        # Display Gemini response
                        st.markdown("### 📋 Personalized Insights from Gemini AI")
                        st.markdown("---")
                        st.markdown(f'<div class="insight-box">{gemini_response}</div>', unsafe_allow_html=True)
                        
                        # Save to session state
                        st.session_state.last_gemini_response = gemini_response
                else:
                    st.warning("Please calculate your score first to get personalized insights.")
    
    # Add disclaimer at the bottom
    st.markdown("---")
    st.caption("""
    **Disclaimer**: This self-assessment is provided for informational purposes only and is not a substitute for professional diagnosis or treatment. 
    If you're experiencing a mental health crisis or having thoughts of harming yourself, please contact a mental health professional immediately or call a crisis hotline.
    """)
# Add to your imports at the top

# Update the journal_page function with correct datetime usage:
def journal_page():
    st.markdown("""
    <style>
    .journal-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .entry-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1E88E5;
    }
    .ai-insight {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="journal-header">Personal Journal</div>', unsafe_allow_html=True)
    st.info("📖 Your private space for reflection. All entries are confidential and only visible to you.")
    
    # Initialize journal entries in session state
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    
    # Journal creation section
    st.markdown("### ✍️ New Entry")
    
    with st.form("journal_form", clear_on_submit=True):
        # Optional prompts for inspiration
        prompts = [
            "What's on your mind today?",
            "Describe something that made you smile recently",
            "What challenges are you facing?",
            "What are you grateful for today?",
            "Free write - whatever comes to mind"
        ]
        
        selected_prompt = st.selectbox("Need inspiration? Choose a prompt (optional)", 
                                      [""] + prompts)
        
        if selected_prompt:
            st.caption(f"Prompt: {selected_prompt}")
        
        # Mood selection
        mood = st.radio("How are you feeling today? (optional)", 
                       ["", "😔 Difficult", "😐 Neutral", "🙂 Good", "😄 Great"], 
                       horizontal=True)
        
        # Journal content
        journal_content = st.text_area("Write your entry here:", 
                                      placeholder="Take a moment to reflect on your day, thoughts, and feelings...",
                                      height=200)
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Entry", type="primary")
        
        if submitted:
            if journal_content.strip():
                # Create new entry with correct datetime usage
                new_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "content": journal_content,
                    "mood": mood,
                    "prompt": selected_prompt if selected_prompt else None,
                    "ai_insights": None  # Will be filled when analyzed
                }
                # Add to entries
                st.session_state.journal_entries.insert(0, new_entry)
                st.success("Entry saved successfully!")
                
                # Auto-analyze if Gemini is configured
                if configure_gemini():
                    with st.spinner("Getting AI insights..."):
                        insights = analyze_journal_entry(new_entry)
                        new_entry["ai_insights"] = insights
                        st.session_state.journal_entries[0] = new_entry  # Update with insights
                        st.rerun()
            else:
                st.warning("Please write something before saving.")
    
    st.markdown("---")
    
    # Journal history section
    st.markdown("### 📚 Past Entries")
    
    if not st.session_state.journal_entries:
        st.info("You haven't written any journal entries yet. Your reflections will appear here.")
    else:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_mood = st.selectbox("Filter by mood", 
                                      ["All", "😔 Difficult", "😐 Neutral", "🙂 Good", "😄 Great"])
        with col2:
            search_text = st.text_input("Search entries")
        
        # Display filtered entries
        filtered_entries = st.session_state.journal_entries
        
        if filter_mood != "All":
            filtered_entries = [e for e in filtered_entries if e["mood"] == filter_mood]
        
        if search_text:
            filtered_entries = [e for e in filtered_entries if search_text.lower() in e["content"].lower()]
        
        for i, entry in enumerate(filtered_entries):
            # Create a unique key using timestamp to avoid duplicate keys
            timestamp_key = entry["date"].replace(" ", "_").replace(":", "-")
            
            with st.expander(f"{entry['date']} {entry['mood'] if entry['mood'] else ''}", expanded=i==0):
                st.markdown(f"**Entry:**")
                st.write(entry["content"])
                
                if entry["prompt"]:
                    st.caption(f"Prompt: {entry['prompt']}")
                
                if entry["ai_insights"]:
                    st.markdown("**AI Insights:**")
                    st.markdown(f'<div class="ai-insight">{entry["ai_insights"]}</div>', unsafe_allow_html=True)
                    
                    # Option to get new insights
                    if st.button("🔄 Get Fresh Insights", key=f"reanalyze_{timestamp_key}"):
                        with st.spinner("Getting new insights..."):
                            new_insights = analyze_journal_entry(entry)
                            # Update the entry in the list
                            for j, e in enumerate(st.session_state.journal_entries):
                                if e["date"] == entry["date"]:
                                    st.session_state.journal_entries[j]["ai_insights"] = new_insights
                                    break
                            st.rerun()
                else:
                    if st.button("🤖 Get AI Insights", key=f"analyze_{timestamp_key}"):
                        with st.spinner("Analyzing your entry..."):
                            insights = analyze_journal_entry(entry)
                            # Update the entry in the list
                            for j, e in enumerate(st.session_state.journal_entries):
                                if e["date"] == entry["date"]:
                                    st.session_state.journal_entries[j]["ai_insights"] = insights
                                    break
                            st.rerun()
                
                # Delete option
                if st.button("🗑️ Delete", key=f"delete_{timestamp_key}"):
                    st.session_state.journal_entries = [e for e in st.session_state.journal_entries 
                                                       if e["date"] != entry["date"]]
                    st.rerun()
        
        # Export option
        if st.button("📥 Export All Entries"):
            # Create a downloadable JSON file
            json_str = json.dumps(st.session_state.journal_entries, indent=2)
            st.download_button(
                label="Download Journal",
                data=json_str,
                file_name=f"campusmind_journal_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

# Function to analyze journal entry with Gemini
def analyze_journal_entry(entry):
    """
    Send journal entry to Gemini AI for analysis and insights
    """
    try:
        gemini_configured = configure_gemini()
        # Configure Gemini
        if not configure_gemini():
            return "Gemini API not configured. Insights unavailable."
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create prompt for Gemini
        prompt = f"""
        As a mental health assistant for college students, provide supportive, compassionate, 
        and clinically-informed reflections on this journal entry. Focus on:
        
        1. Validating the writer's experiences and emotions
        2. Identifying potential patterns or themes
        3. Suggesting gentle coping strategies or reframing techniques
        4. Noting strengths or positive aspects in the writing
        5. Recommending campus resources if appropriate
        
        Important guidelines:
        - Be non-judgmental and supportive
        - Avoid diagnostic language
        - Keep response under 150 words
        - Focus on the student's strengths
        - Suggest simple, actionable strategies
        
        Journal Entry:
        {entry['content']}
        
        Mood: {entry['mood'] if entry['mood'] else 'Not specified'}
        
        Please provide a compassionate response that makes the student feel heard and supported.
        """
        
        # Generate response from Gemini
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"I encountered an error analyzing your entry. Please try again later. Error: {str(e)}"
# Function to get insights from Gemini AI
def get_gemini_insights(assessment_data):
    """
    Send assessment data to Gemini AI and get personalized insights
    """
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create prompt for Gemini
        prompt = f"""
        As a mental health assistant for college students, provide compassionate, supportive, and educational insights 
        based on this assessment data. Remember that this user is a student who might be experiencing academic stress.
        
        Assessment Type: {assessment_data['assessment_type']}
        Total Score: {assessment_data['score']}
        User Context: {assessment_data.get('user_context', 'general user')}
        Responses:
        {chr(10).join(assessment_data['responses'])}
        
        Please provide:
        1. A brief interpretation of what the score means in simple, non-alarming terms
        2. 3-4 specific, practical suggestions based on the specific responses (focus on actionable items)
        3. Guidance on when to consider professional help (with encouragement)
        4. Campus-friendly resources or strategies that might be available to students
        5. Encouraging, non-judgmental language throughout
        6. A clear mention that this is not a diagnosis
        
        Keep the response under 400 words and use a supportive, hopeful tone.
        Focus on strengths and coping strategies rather than just symptoms.
        """
        
        # Generate response from Gemini
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        st.error(f"Error getting insights from Gemini: {str(e)}")
        # Fallback to sample insights
        if assessment_data['assessment_type'] == "PHQ-9 Depression":
            return display_sample_phq_insights(assessment_data['score'], assessment_data['responses'], True)
        else:
            return display_sample_gad_insights(assessment_data['score'], assessment_data['responses'], True)

# Fallback functions for when Gemini is not available
def display_sample_phq_insights(score, responses, return_text=False):
    insight_text = """
    **Understanding Your PHQ-9 Results**
    
    Your score suggests you're experiencing some depression symptoms. This is more common than many people realize, especially among students, and it's brave of you to check in with yourself.

    **Based on your responses:**
    - You might benefit from establishing a consistent sleep routine (try to wake up and sleep at the same time daily)
    - Consider incorporating light physical activity - even a 15-minute daily walk can help improve mood
    - Practice self-compassion - what would you say to a friend feeling this way?
    - Try connecting with campus clubs or activities that align with your interests

    **When to seek help:**
    If these feelings persist for more than 2 weeks or interfere with your studies/daily life, consider speaking with a campus counselor. Many students find therapy helpful during stressful academic periods.

    **Campus resources that might help:**
    - Student counseling services (often free for enrolled students)
    - Peer support groups
    - Wellness workshops on stress management

    Remember: This screening isn't a diagnosis, but a tool for awareness. You've taken an important step by checking in with yourself today.
    """
    
    if return_text:
        return insight_text
    else:
        st.markdown("### 📋 Sample Insights (Gemini not configured)")
        st.markdown("---")
        st.markdown(f'<div class="insight-box">{insight_text}</div>', unsafe_allow_html=True)


def display_sample_gad_insights(score, responses, return_text=False):
    insight_text = """
    **Understanding Your GAD-7 Results**
    
    Your score indicates some anxiety symptoms. It's completely normal to experience anxiety, especially during stressful periods like college with exams and assignments.

    **Based on your responses:**
    - Try the 4-7-8 breathing technique (inhale 4s, hold 7s, exhale 8s) when feeling overwhelmed
    - Schedule "worry time" - 15 minutes daily to process concerns, then set them aside
    - Practice grounding techniques like the 5-4-3-2-1 method (notice 5 things you see, 4 things you feel, etc.)
    - Break studying into smaller chunks with scheduled breaks to prevent overwhelm

    **When to consider help:**
    If anxiety frequently interferes with your studies or social life, a campus counselor can teach effective coping strategies tailored to student life.

    **Campus resources that might help:**
    - Mindfulness and meditation workshops
    - Study skills centers that can help with academic planning
    - Stress management groups specifically for students

    Remember: This is a screening tool, not a diagnosis. Many effective strategies exist for managing anxiety, and seeking help is a sign of strength.
    """
    
    if return_text:
        return insight_text
    else:
        st.markdown("### 📋 Sample Insights (Gemini not configured)")
        st.markdown("---")
        st.markdown(f'<div class="insight-box">{insight_text}</div>', unsafe_allow_html=True)
from datetime import datetime, date, timedelta
import re
import streamlit as st

def book_appointment():
    # Custom CSS
    st.markdown("""
    <style>
    .sub-header { font-size:28px; font-weight:bold; color:#1f77b4; margin-bottom:20px; padding-bottom:10px; border-bottom:2px solid #1f77b4; }
    .counselor-card { padding:15px; border-radius:10px; border:1px solid #ddd; margin-bottom:15px; background-color:#f9f9f9; }
    .selected-counselor { background-color:#e6f2ff; border:2px solid #1f77b4; }
    .success-box { padding:20px; background-color:#d4edda; border-radius:10px; border:1px solid #c3e6cb; margin:20px 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sub-header">Book Appointment with Counselor</div>', unsafe_allow_html=True)

    # Sample counselor data
    counselors = [
        {"name": "Dr. Sarah Johnson","specialty": "Anxiety & Depression","rating": 4.8,"availability": "Mon, Wed, Fri","bio": "Licensed clinical psychologist...","photo": "👩‍⚕️"},
        {"name": "Dr. Michael Chen","specialty": "Relationship Counseling","rating": 4.7,"availability": "Tue, Thu","bio": "Marriage and family therapist...","photo": "👨‍⚕️"},
        {"name": "Dr. Priya Patel","specialty": "Trauma & PTSD","rating": 4.9,"availability": "Mon, Tue, Wed, Thu","bio": "Trauma specialist certified in EMDR...","photo": "👩‍⚕️"}
    ]

    # Init session state
    if 'selected_counselor' not in st.session_state:
        st.session_state.selected_counselor = None
    if 'booking_confirmed' not in st.session_state:
        st.session_state.booking_confirmed = False

    # Counselor selection
    st.markdown("### Available Counselors")
    cols = st.columns(len(counselors))
    for i, (col, counselor) in enumerate(zip(cols, counselors)):
        with col:
            card_class = "counselor-card selected-counselor" if st.session_state.selected_counselor == counselor else "counselor-card"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align:center;'>{counselor['photo']} {counselor['name']}</h4>", unsafe_allow_html=True)
            st.markdown(f"**Specialty:** {counselor['specialty']}")
            st.markdown(f"**Rating:** ⭐{counselor['rating']}")
            st.markdown(f"**Availability:** {counselor['availability']}")

            if st.button("Select", key=f"select_{i}"):
                st.session_state.selected_counselor = counselor
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Booking form
    if st.session_state.selected_counselor:
        counselor = st.session_state.selected_counselor
        st.markdown(f"### Booking with {counselor['name']}")
        st.markdown(f"*{counselor['bio']}*")

        with st.form("booking_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Your Name *")
                email = st.text_input("Email for confirmation *")
                phone = st.text_input("Phone *")
            with col2:
                min_date = date.today()
                max_date = min_date + timedelta(days=14)
                preferred_date = st.date_input(
                    "Preferred Date *", 
                    min_value=min_date, 
                    max_value=max_date, 
                    value=min_date + timedelta(days=3)
                )

                day_name = preferred_date.strftime("%a")
                availability_days = [d.strip() for d in counselor['availability'].split(",")]
                if day_name not in availability_days:
                    st.warning(f"{counselor['name']} is not typically available on {preferred_date.strftime('%A')}s.")

                preferred_time = st.selectbox("Preferred Time *", ["9:00 AM","10:00 AM","11:00 AM","2:00 PM","3:00 PM","4:00 PM"])
                meeting_type = st.radio("Meeting Type *", ["Video Call","In-Person"])

            concerns = st.text_area("What would you like to discuss? (Optional)", height=100)
            submitted = st.form_submit_button("Request Appointment", type="primary")

            if submitted:
                errors = []
                if not name.strip(): errors.append("Please enter your name")
                if not email.strip() or not re.match(r"[^@]+@[^@]+\.[^@]+", email): errors.append("Please enter a valid email address")
                if not phone.strip(): errors.append("Please enter your phone number")

                if errors:
                    for e in errors: st.error(e)
                else:
                    st.session_state.booking_confirmed = True
                    st.session_state.booking_details = {
                        "counselor": counselor['name'],
                        "date": preferred_date.strftime("%B %d, %Y"),
                        "time": preferred_time,
                        "type": meeting_type,
                        "client_name": name,
                        "client_email": email
                    }

    # Confirmation message
    if st.session_state.get('booking_confirmed', False):
        details = st.session_state.booking_details
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("### ✅ Appointment Request Submitted!")
        st.markdown(
            f"**Counselor:** {details['counselor']}  \n"
            f"**Date:** {details['date']}  \n"
            f"**Time:** {details['time']}  \n"
            f"**Type:** {details['type']}  \n"
            f"**Client:** {details['client_name']}  \n"
            f"**Email:** {details['client_email']}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("**Next Steps:**\n• You will receive a confirmation email within 24 hours\n• Check your spam folder\n• If urgent, contact the counseling center directly")
        st.balloons()

        if st.button("Book Another Appointment"):
            st.session_state.selected_counselor = None
            st.session_state.booking_confirmed = False
            st.rerun()


def resources_page():
    st.markdown("""
    <style>
    .resource-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border-left: 4px solid #1E88E5;
        transition: transform 0.2s ease;
    }
    .resource-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .resource-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .resource-type {
        background-color: #e3f2fd;
        color: #1E88E5;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .resource-duration {
        color: #666;
        font-size: 0.9rem;
    }
    .crisis-box {
        background-color: #fff3e0;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin-bottom: 1rem;
    }
    .support-box {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin-bottom: 1rem;
    }
    .audio-player {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .filter-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sub-header">Mental Health Resources</div>', unsafe_allow_html=True)
    st.caption("Access curated mental health resources, tools, and support materials tailored for students")
    
    # Enhanced resources data with duration in minutes for filtering
    resources = [
        {"title": "Coping with Exam Stress", "type": "Video", "duration": 12, "language": "English/Hindi", 
         "description": "Practical techniques to manage stress during exam season", "url": "#", "icon": "🎬"},
        {"title": "Mindfulness Meditation", "type": "Audio", "duration": 15, "language": "English", 
         "description": "Guided meditation for anxiety relief and focus", "url": "#", "icon": "🎧"},
        {"title": "Managing Anxiety", "type": "Guide", "duration": 10, "language": "English/Tamil", 
         "description": "Step-by-step guide to understanding and managing anxiety", "url": "#", "icon": "📋"},
        {"title": "Improving Sleep Quality", "type": "Article", "duration": 8, "language": "English/Telugu", 
         "description": "Evidence-based strategies for better sleep", "url": "#", "icon": "📚"},
        {"title": "5-Minute Breathing Exercise", "type": "Audio", "duration": 5, "language": "English", 
         "description": "Quick breathing technique for immediate calm", "url": "#", "icon": "🎧"},
        {"title": "Building Resilience", "type": "Video", "duration": 18, "language": "Hindi/English", 
         "description": "Learn how to bounce back from academic setbacks", "url": "#", "icon": "🎬"},
        {"title": "Digital Detox Guide", "type": "Article", "duration": 7, "language": "English", 
         "description": "How to reduce screen time for better mental health", "url": "#", "icon": "📚"},
        {"title": "Yoga for Stress Relief", "type": "Video", "duration": 22, "language": "English/Tamil", 
         "description": "Gentle yoga sequences to release tension", "url": "#", "icon": "🎬"}
    ]
    
    # Filter section
    st.markdown("### 🔍 Find Resources")
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            resource_type = st.selectbox("Resource Type", ["All", "Video", "Audio", "Article", "Guide"])
        with col2:
            language = st.selectbox("Language", ["All", "English", "Hindi", "Tamil", "Telugu", "Bengali"])
        with col3:
            duration_filter = st.selectbox("Duration", ["All", "Short (<5 min)", "Medium (5-15 min)", "Long (>15 min)"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display resources with filtering
    st.markdown("### 📚 Available Resources")
    
    filtered_resources = []
    for resource in resources:
        # Apply filters
        display = True
        
        # Type filter
        if resource_type != "All" and resource_type != resource["type"]:
            display = False
        
        # Language filter
        if language != "All" and language not in resource["language"]:
            display = False
        
        # Duration filter
        if duration_filter != "All":
            if duration_filter == "Short (<5 min)" and resource["duration"] >= 5:
                display = False
            elif duration_filter == "Medium (5-15 min)" and (resource["duration"] < 5 or resource["duration"] > 15):
                display = False
            elif duration_filter == "Long (>15 min)" and resource["duration"] <= 15:
                display = False
        
        if display:
            filtered_resources.append(resource)
    
    # Display message if no resources match filters
    if not filtered_resources:
        st.info("No resources match your selected filters. Try adjusting your criteria.")
    
    # Display filtered resources in cards
    for resource in filtered_resources:
        st.markdown(f"""
        <div class="resource-card">
            <div class="resource-header">
                <h4 style="margin: 0;">{resource['icon']} {resource['title']}</h4>
                <span class="resource-type">{resource['type']}</span>
            </div>
            <p class="resource-duration">Duration: {resource['duration']} min • Language: {resource['language']}</p>
            <p>{resource['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add a button to access the resource
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("Access", key=f"access_{resource['title']}"):
                st.success(f"Opening: {resource['title']}")
                # In a real application, this would navigate to the actual resource
        st.markdown("---")
    
    # Meditation audio players
    st.markdown("### 🎧 Relaxation Exercises")
    st.caption("Listen to these guided exercises for immediate stress relief")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="audio-player">
            <h4>🧘 Guided Breathing Exercise</h4>
            <p style="color: #666; margin-bottom: 0.5rem;">10 minutes • English</p>
        </div>
        """, unsafe_allow_html=True)
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")
        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 12px; border-radius: 8px; margin: 10px 0;">
        <b>Instructions:</b> Follow the audio guidance for deep breathing to reduce anxiety and stress.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="audio-player">
            <h4>🌿 Body Scan Meditation</h4>
            <p style="color: #666; margin-bottom: 0.5rem;">15 minutes • English/Hindi</p>
        </div>
        """, unsafe_allow_html=True)
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", format="audio/mp3")
        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 12px; border-radius: 8px; margin: 10px 0;">
        <b>Instructions:</b> Gradually bring awareness to each part of your body to release tension.
        </div>
        """, unsafe_allow_html=True)
    
    # Crisis resources
    st.markdown("### 🆘 Immediate Help Resources")
    st.caption("If you're in crisis or need immediate support, these resources are available 24/7")
    
    crisis_col1, crisis_col2 = st.columns(2)
    
    with crisis_col1:
        st.markdown("""
        <div class="crisis-box">
            <h4 style="color: #e65100; margin-top: 0;">Emergency Contacts</h4>
            <ul style="padding-left: 20px;">
                <li><b>🌐 Crisis Helpline:</b> 9152987821 (24/7)</li>
                <li><b>🏫 Campus Counseling Center:</b> +91-XXX-XXXX-XXXX</li>
                <li><b>🚨 Emergency Services:</b> 112 or 102</li>
                <li><b>👥 Student Support Cell:</b> +91-YYY-YYYY-YYYY</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with crisis_col2:
        st.markdown("""
        <div class="support-box">
            <h4 style="color: #2e7d32; margin-top: 0;">Online Resources</h4>
            <ul style="padding-left: 20px;">
                <li><b>💻 Therapy Assistance Online:</b> <a href="https://www.taoconnect.org/" target="_blank">TAO Connect</a></li>
                <li><b>🇮🇳 Mental Health India:</b> <a href="https://www.mhindia.org/" target="_blank">MHIndia</a></li>
                <li><b>📞 iCall Psychosocial Helpline:</b> <a href="mailto:icall@tiss.edu">icall@tiss.edu</a></li>
                <li><b>🤝 Vandrevala Foundation:</b> <a href="https://www.vandrevalafoundation.com/" target="_blank">Website</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional information
    st.markdown("### 💡 Need Something Specific?")
    st.markdown("""
    <div style="background-color: #e3f2fd; padding: 1.5rem; border-radius: 10px;">
        <p style="margin: 0;">Can't find what you're looking for? Our resource library is constantly growing. 
        Please email <a href="mailto:resources@campusmind.in">resources@campusmind.in</a> with suggestions for additional resources.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer note
    st.markdown("---")
    st.caption("Note: These resources are provided for informational purposes only and are not a substitute for professional medical advice, diagnosis, or treatment.")
    
# Peer Support Forum
def peer_support():
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .forum-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e6e6e6;
    }
    .topic-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .reply-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 3px solid #4CAF50;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .user-badge {
        background-color: #1E88E5;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .date-text {
        color: #6c757d;
        font-size: 0.9rem;
    }
    .reply-count {
        background-color: #FF9800;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    .new-post-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="forum-header">Peer Support Forum</div>', unsafe_allow_html=True)
    st.info("🤝 Connect with other students in a moderated, supportive environment. All posts are anonymous.")
    
    # Initialize forum topics in session state if not exists
    if 'forum_topics' not in st.session_state:
        st.session_state.forum_topics = [
            {
                'id': '1',
                'title': 'Coping with exam stress',
                'content': 'I\'ve been having trouble sleeping and focusing with finals coming up. Any tips?',
                'user': 'Anonymous',
                'date': '2023-10-15',
                'replies': [
                    {'content': 'I find that scheduling breaks really helps me. Try the Pomodoro technique!', 'user': 'Anonymous', 'date': '2023-10-16'},
                    {'content': 'Exercise has been a game changer for my stress levels. Even just a 20 min walk!', 'user': 'Anonymous', 'date': '2023-10-17'}
                ]
            },
            {
                'id': '2',
                'title': 'Balancing social life and studies',
                'content': 'How do you all manage to maintain friendships while keeping up with coursework?',
                'user': 'Anonymous',
                'date': '2023-10-18',
                'replies': [
                    {'content': 'Study groups! That way you can socialize while being productive.', 'user': 'Anonymous', 'date': '2023-10-19'}
                ]
            },
            {
                'id': '3',
                'title': 'Dealing with homesickness',
                'content': 'First year here and really missing home. Any advice from those who\'ve been through this?',
                'user': 'Anonymous',
                'date': '2023-10-20',
                'replies': []
            }
        ]
    
    # Set current topic if not in session state
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = None
    
    # Display specific topic if selected
    if st.session_state.current_topic:
        topic = next((t for t in st.session_state.forum_topics if t['id'] == st.session_state.current_topic), None)
        if topic:
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("← Back to Forum", width='stretch'):
                    st.session_state.current_topic = None
                    st.rerun()
            
            st.markdown(f"# {topic['title']}")
            st.markdown(f"<span class='user-badge'>{topic['user']}</span> <span class='date-text'>{topic['date']}</span>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"<div style='padding: 1rem; background-color: #f8f9fa; border-radius: 8px;'>{topic['content']}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"### 💬 Replies ({len(topic['replies'])})")
            
            if not topic['replies']:
                st.info("No replies yet. Be the first to respond!")
            
            for reply in topic['replies']:
                st.markdown(f"""
                <div class='reply-card'>
                    <div><span class='user-badge'>{reply['user']}</span> <span class='date-text'>{reply['date']}</span></div>
                    <div style='margin-top: 0.5rem;'>{reply['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Reply form
            st.markdown("---")
            st.markdown("### 📝 Post a reply")
            reply_content = st.text_area("Your response", placeholder="Share your thoughts...", height=120)
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("Post Reply", width='stretch', type="primary"):
                    if reply_content.strip():
                        topic['replies'].append({
                            'content': reply_content,
                            'user': 'Anonymous',
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        st.success("✅ Your reply has been posted!")
                        st.rerun()
                    else:
                        st.warning("Please write something before posting.")
        else:
            st.error("Topic not found")
            st.session_state.current_topic = None
        return
    
    # Search and filter options
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search discussions", placeholder="Type keywords to search...")
    with col2:
        sort_option = st.selectbox("Sort by", ["Newest", "Most replies", "Oldest"])
    
    # Filter and sort topics
    filtered_topics = st.session_state.forum_topics
    if search_query:
        filtered_topics = [t for t in filtered_topics 
                          if search_query.lower() in t['title'].lower() 
                          or search_query.lower() in t['content'].lower()]
    
    if sort_option == "Newest":
        filtered_topics = sorted(filtered_topics, key=lambda x: x['date'], reverse=True)
    elif sort_option == "Oldest":
        filtered_topics = sorted(filtered_topics, key=lambda x: x['date'])
    elif sort_option == "Most replies":
        filtered_topics = sorted(filtered_topics, key=lambda x: len(x['replies']), reverse=True)
    
    # Display forum topics
    st.markdown("### 📌 Recent Discussions")
    
    if not filtered_topics:
        st.info("No discussions found matching your search. Start a new one below!")
    
    for topic in filtered_topics:
        st.markdown(f"""
        <div class='topic-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h3 style='margin: 0;'>{topic['title']}</h3>
                <span class='reply-count'>{len(topic['replies'])} replies</span>
            </div>
            <div style='margin: 0.5rem 0;'>{topic['content'][:120]}{'...' if len(topic['content']) > 120 else ''}</div>
            <div><span class='user-badge'>{topic['user']}</span> <span class='date-text'>{topic['date']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("💬 Join Discussion", key=f"view_{topic['id']}", width='stretch'):
                st.session_state.current_topic = topic['id']
                st.rerun()
        st.markdown("---")
    
    # Create new post
    st.markdown("### 📢 Start a New Discussion")
    
    with st.form("new_post_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_title = st.text_input("Topic Title", placeholder="What's your question or topic?")
        with col2:
            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
            anonymous = st.checkbox("Post anonymously", value=True)
        
        new_content = st.text_area("What would you like to discuss?", 
                                  placeholder="Share your thoughts, questions, or experiences...", 
                                  height=150)
        
        submitted = st.form_submit_button("📤 Post Discussion", type="primary")
        if submitted:
            if new_title and new_content:
                user = "Anonymous" if anonymous else "User"
                new_topic = {
                    'id': str(len(st.session_state.forum_topics) + 1),
                    'title': new_title,
                    'content': new_content,
                    'user': user,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'replies': []
                }
                st.session_state.forum_topics.insert(0, new_topic)
                st.success("✅ Posted! Your discussion is now live.")
                st.rerun()
            else:
                st.warning("Please add both a title and content for your post.")
# Admin Dashboard (simplified for demo)
def admin_dashboard():
    st.markdown("""
    <style>
    .admin-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        text-align: center;
        border-left: 4px solid #667eea;
    }
    .metric-number {
        font-size: 2rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        color: #666;
        font-weight: 500;
    }
    .metric-trend {
        font-size: 0.9rem;
        font-weight: 600;
    }
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }
    .tab-content {
        padding: 1.5rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-top: 1rem;
    }
    .user-table {
        width: 100%;
        border-collapse: collapse;
    }
    .user-table th {
        background: #f8f9fa;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        color: #333;
    }
    .user-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #eee;
    }
    .status-active {
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .status-inactive {
        background: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="admin-header">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">Admin Dashboard</h1>
        <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0;">Comprehensive platform analytics and management</p>
    </div>
    """, unsafe_allow_html=True)

    # Security warning
    st.warning("🔒 Restricted access - Admin privileges required. All data is anonymized for privacy protection.")

    # Quick stats row
    st.markdown("### 📊 Platform Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">1,243</div>
            <div class="metric-label">Active Users</div>
            <div class="metric-trend" style="color: #28a745;">↑ 12%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">87</div>
            <div class="metric-label">Appointments</div>
            <div class="metric-trend" style="color: #28a745;">↑ 5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">324</div>
            <div class="metric-label">Resources Accessed</div>
            <div class="metric-trend" style="color: #28a745;">↑ 8%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">568</div>
            <div class="metric-label">Chat Sessions</div>
            <div class="metric-trend" style="color: #ffc107;">↑ 15%</div>
        </div>
        """, unsafe_allow_html=True)

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Analytics", "👥 Users", "📅 Appointments", "📊 Content", "⚙️ Settings"])

    with tab1:
        st.markdown("### 📈 Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Common Concerns")
            concerns_data = pd.DataFrame({
                "Concern": ["Academic Stress", "Anxiety", "Sleep Issues", "Relationships", "Depression"],
                "Percentage": [45, 32, 15, 5, 3]
            })
            fig = px.bar(concerns_data, x='Percentage', y='Concern', orientation='h',
                        color='Percentage', color_continuous_scale='Blues')
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.markdown("#### Resource Utilization")
            resource_data = pd.DataFrame({
                "Resource Type": ["Videos", "Articles", "Audio", "Self-Assessment"],
                "Usage": [120, 85, 65, 54]
            })
            fig = px.pie(resource_data, values='Usage', names='Resource Type',
                        color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig, width='stretch')

        # Trend data
        st.markdown("#### 📈 Mental Health Trends (Anonymous Aggregated Data)")
        trend_data = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Avg. PHQ-9 Score": [6.2, 7.1, 6.8, 8.3, 7.9, 7.2],
            "Avg. GAD-7 Score": [5.8, 6.4, 6.1, 7.2, 6.9, 6.3],
            "Active Users": [890, 950, 1020, 1100, 1180, 1243]
        })
        
        fig = px.line(trend_data, x='Month', y=['Avg. PHQ-9 Score', 'Avg. GAD-7 Score'],
                     title='Mental Health Scores Trend', markers=True)
        st.plotly_chart(fig, width='stretch')

        # Additional metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Session Duration", "12.4 min", "1.2 min")
        with col2:
            st.metric("Peak Usage Hours", "2-4 PM", "-0.5 hrs")
        with col3:
            st.metric("Satisfaction Score", "4.7/5", "0.2")

    with tab2:
        st.markdown("### 👥 User Management")
        
        # Simulated user data
        users_data = pd.DataFrame({
            "User ID": ["STU001", "STU002", "STU003", "STU004", "STU005"],
            "Name": ["Student A", "Student B", "Student C", "Student D", "Student E"],
            "Department": ["Engineering", "Arts", "Science", "Medicine", "Business"],
            "Last Active": ["2 hours ago", "1 day ago", "3 hours ago", "5 days ago", "12 hours ago"],
            "Status": ["Active", "Active", "Active", "Inactive", "Active"],
            "Sessions": [12, 8, 15, 3, 7]
        })
        
        st.dataframe(users_data, width='stretch')
        
        # User analytics
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Department Distribution")
            dept_data = pd.DataFrame({
                "Department": ["Engineering", "Arts", "Science", "Medicine", "Business", "Other"],
                "Users": [350, 280, 220, 180, 150, 63]
            })
            fig = px.pie(dept_data, values='Users', names='Department')
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.markdown("#### User Engagement")
            engagement_data = pd.DataFrame({
                "Activity Level": ["High", "Medium", "Low", "Inactive"],
                "Users": [450, 380, 250, 163]
            })
            fig = px.bar(engagement_data, x='Activity Level', y='Users', color='Activity Level')
            st.plotly_chart(fig, width='stretch')

    with tab3:
        st.markdown("### 📅 Appointment Management")
        
        # Appointment data
        appointments = pd.DataFrame({
            "Date": ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18", "2024-01-19"],
            "Time": ["10:00 AM", "2:30 PM", "11:00 AM", "4:00 PM", "3:00 PM"],
            "Counselor": ["Dr. Sharma", "Dr. Patel", "Dr. Kumar", "Dr. Singh", "Dr. Gupta"],
            "Student": ["STU001", "STU002", "STU003", "STU004", "STU005"],
            "Status": ["Completed", "Scheduled", "Completed", "Cancelled", "Scheduled"],
            "Type": ["Video", "In-person", "Phone", "Video", "In-person"]
        })
        
        st.dataframe(appointments, width='stretch')
        
        # Appointment analytics
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Appointment Status")
            status_data = pd.DataFrame({
                "Status": ["Completed", "Scheduled", "Cancelled", "No-show"],
                "Count": [45, 25, 12, 5]
            })
            fig = px.bar(status_data, x='Status', y='Count', color='Status')
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.markdown("#### Session Type Distribution")
            type_data = pd.DataFrame({
                "Type": ["Video", "In-person", "Phone"],
                "Count": [52, 25, 10]
            })
            fig = px.pie(type_data, values='Count', names='Type')
            st.plotly_chart(fig, width='stretch')

    with tab4:
        st.markdown("### 📊 Content Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top Resources")
            top_resources = pd.DataFrame({
                "Resource": ["Exam Stress Guide", "Sleep Meditation", "Anxiety Workbook", "Breathing Exercise"],
                "Views": [156, 132, 98, 87],
                "Rating": [4.8, 4.9, 4.6, 4.7]
            })
            st.dataframe(top_resources, width='stretch')
        
        with col2:
            st.markdown("#### Resource Performance")
            performance_data = pd.DataFrame({
                "Metric": ["Completion Rate", "Satisfaction Score", "Return Users", "Recommendation Rate"],
                "Value": [78, 4.7, 65, 82],
                "Target": [75, 4.5, 70, 80]
            })
            fig = px.bar(performance_data, x='Metric', y='Value', color='Metric')
            st.plotly_chart(fig, width='stretch')

    with tab5:
        st.markdown("### ⚙️ System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Platform Configuration")
            st.checkbox("Enable new user registrations", True)
            st.checkbox("Maintenance mode", False)
            st.checkbox("Email notifications", True)
            st.checkbox("Analytics tracking", True)
            
            st.slider("Session timeout (minutes)", 15, 120, 30)
            st.slider("Max appointments per user", 1, 10, 3)
        
        with col2:
            st.markdown("#### System Health")
            st.progress(85)
            st.caption("System load: 85%")
            
            st.progress(92)
            st.caption("Storage: 92%")
            
            st.progress(99)
            st.caption("Uptime: 99.9%")
            
            st.markdown("#### Quick Actions")
            if st.button("Clear Cache", width='stretch'):
                st.success("Cache cleared successfully!")
            if st.button("Backup Database", width='stretch'):
                st.success("Backup completed!")
            if st.button("Generate Report", width='stretch'):
                st.success("Report generated!")

    # Real-time monitoring section
    st.markdown("---")
    st.markdown("### 📡 Real-time Monitoring")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Current Activity")
        st.metric("Active Sessions", "23")
        st.metric("Live Chats", "8")
        st.metric("Ongoing Appointments", "3")
    
    with col2:
        st.markdown("#### System Status")
        st.success("API: Operational")
        st.success("Database: Connected")
        st.success("Storage: Normal")
    
    with col3:
        st.markdown("#### Alerts")
        if st.button("View Recent Alerts (2)", width='stretch'):
            st.info("""
            - High memory usage detected (15 min ago)
            - Unusual login pattern detected (2 hrs ago)
            """)

    # Export and reporting
    st.markdown("---")
    st.markdown("### 📋 Reports & Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.selectbox("Report Type", ["Usage Analytics", "User Activity", "Appointment Summary", "Resource Performance"])
    
    with col2:
        st.selectbox("Time Range", ["Last 7 days", "Last 30 days", "Last 90 days", "Custom Range"])
    
    with col3:
        st.selectbox("Format", ["PDF", "CSV", "Excel", "JSON"])
    
    if st.button("Generate Report", type="primary"):
        st.success("Report generation started! You'll be notified when it's ready.")

# Note: This requires Plotly - make sure to add: pip install plotly
# Main app logic
def main():
    # Check if user is logged in
    if not st.session_state.logged_in:
        # Show authentication pages
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        if st.session_state.auth_page == 'login':
            show_login_page()
        elif st.session_state.auth_page == 'signup':
            show_signup_page()
        elif st.session_state.auth_page == 'admin_login':
            show_admin_login_page()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle page navigation via clickable links
        if st.session_state.auth_page == 'login':
            if st.button("Sign up here", key="signup_link"):
                st.session_state.auth_page = "signup"
                st.rerun()
        elif st.session_state.auth_page == 'signup':
            if st.button("Login here", key="login_link"):
                st.session_state.auth_page = "login"
                st.rerun()
        elif st.session_state.auth_page == 'admin_login':
            if st.button("Back to regular login", key="back_link"):
                st.session_state.auth_page = "login"
                st.rerun()
                
        return  # Stop execution here if not logged in
    
    # User is logged in - show the main app
    # Sidebar navigation
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/brain.png", width=80)
        st.title("CampusMind")
        
        # Display user info
        if st.session_state.is_admin:
            st.markdown(f"**👨‍💼 Admin:** {st.session_state.user_email}")
        else:
            st.markdown(f"**👤 User:** {st.session_state.user_email}")
            
        st.markdown("---")
        
        # Navigation buttons
        if st.button("🏠 Home", width='stretch'):
            navigate_to("Home")
        if st.button("🤖 AI First Aid", width='stretch'):
            navigate_to("AI First Aid")
        if st.button("📊 Self Assessment", width='stretch'):
            navigate_to("Self Assessment")
        if st.button("📅 Book Appointment", width='stretch'):
            navigate_to("Book Appointment")
        if st.button("📚 Resources", width='stretch'):
            navigate_to("Resources")
        if st.button("👥 Peer Support", width='stretch'):
            navigate_to("Peer Support")
        if st.button("📔 Journal", width='stretch'):
            navigate_to("Journal")

        # Admin access (only show if user is admin)
        if st.session_state.is_admin and st.button("🔒 Admin Dashboard", width='stretch'):
            navigate_to("Admin Dashboard")
        
        st.markdown("---")
        st.markdown("### Need Immediate Help?")
        st.markdown("""
        - Crisis Helpline: 9152987821
        - Campus Counseling: +91-XXX-XXXX-XXXX
        - Emergency: 112 or 102
        """)
        
        # Logout button
        if st.button("🚪 Logout", width='stretch'):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.user_email = None
            st.session_state.auth_page = "login"
            st.rerun()
        
        st.markdown("---")
        st.caption("Confidential • Anonymous • Secure")
    
    # Display the current page based on navigation
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "AI First Aid":
        ai_first_aid()
    elif st.session_state.current_page == "Self Assessment":
        self_assessment()
    elif st.session_state.current_page == "Book Appointment":
        book_appointment()
    elif st.session_state.current_page == "Resources":
        resources_page()
    elif st.session_state.current_page == "Peer Support":
        peer_support()
    elif st.session_state.current_page == "Journal":
        journal_page()
    elif st.session_state.current_page == "Admin Dashboard" and st.session_state.is_admin:
        admin_dashboard()
    elif st.session_state.current_page == "Admin Dashboard" and not st.session_state.is_admin:
        st.error("You don't have permission to access the admin dashboard.")
        st.session_state.current_page = "Home"
        st.rerun()

if __name__ == "__main__":
    main()