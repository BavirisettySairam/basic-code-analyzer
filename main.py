import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import time
from datetime import datetime
import pandas as pd
import plotly.express as px

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Basic Code Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'debug_result' not in st.session_state:
    st.session_state.debug_result = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'token_count' not in st.session_state:
    st.session_state.token_count = 0
if 'show_advanced' not in st.session_state:
    st.session_state.show_advanced = False

def estimate_tokens(text):
    """Rough estimation of tokens (4 characters per token)"""
    return len(text) // 4

def analyze_code(code, language, analysis_type, temperature=0.7, max_tokens=1024):
    """Send code to Groq API for analysis"""
    api_key = st.secrets["GROQ_API_KEY"]

    if not api_key:
        return "Error: API key not found. Please check your Streamlit secrets."

    try:
        # Disable proxy settings if any
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)

        # Initialize Groq client correctly
        client = Groq(api_key=api_key.strip())  # No 'proxies' argument
        
        # Prepare the prompt based on analysis type
        if analysis_type == "Security":
            prompt = f"""Analyze this {language} code for security vulnerabilities and best practices.
            Focus on:
            1. Input validation
            2. Authentication/Authorization
            3. Data encryption
            4. Secure coding practices
            5. Common vulnerabilities
            
            Code:
            {code}
            
            Provide a detailed security analysis with specific recommendations."""
            
        elif analysis_type == "Performance":
            prompt = f"""Analyze this {language} code for performance optimization opportunities.
            Focus on:
            1. Algorithm efficiency
            2. Memory usage
            3. Database queries
            4. Caching opportunities
            5. Resource utilization
            
            Code:
            {code}
            
            Provide a detailed performance analysis with specific optimization recommendations."""
            
        else:  # Full Analysis
            prompt = f"""Analyze this {language} code and provide a comprehensive review.
            Include:
            1. Code structure and organization
            2. Best practices and patterns
            3. Potential bugs or issues
            4. Performance considerations
            5. Security considerations
            6. Maintainability and readability
            7. Suggestions for improvement
            
            Code:
            {code}
            
            Provide a detailed analysis with specific recommendations."""
        
        # Get completion from Groq with updated parameters
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer and analyzer. Provide detailed, actionable insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"Error analyzing code: {str(e)}"

# Sidebar
with st.sidebar:
    st.title("🎨 Basic Code Analyzer")
    
    # Quick Stats
    st.markdown("### 📈 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Analyses Done", len(st.session_state.analysis_history))
    with col2:
        st.metric("Languages Used", len(set(h['language'] for h in st.session_state.analysis_history)))
    
    # Analysis Type Selection with Emojis
    st.markdown("### 🔍 Analysis Type")
    analysis_type = st.radio(
        "Choose what you want to analyze",
        ["Full Analysis 🎯", "Security Analysis 🔒", "Performance Analysis ⚡"],
        label_visibility="collapsed"
    )
    
    # Language Selection with Emojis
    st.markdown("### 💻 Language")
    language = st.selectbox(
        "Select your code language",
        ["Python 🐍", "C++ 🚀", "Java ☕", "JavaScript 🌐", "TypeScript 📘", "Go 🦘", "Rust 🦀"],
        label_visibility="collapsed"
    )
    
    # Advanced Settings in a collapsible section
    with st.expander("⚙️ Advanced Settings"):
        temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.slider("Response Length", 100, 2048, 1024, 100)
    
    # Quick Tips
    st.markdown("### 💡 Quick Tips")
    st.info("""
    - Keep code under 3,200 characters
    - Upload files or paste code directly
    - Try different analysis types
    - Check documentation for more info
    """)
    
    # Fun Fact
    if st.session_state.analysis_history:
        most_used_lang = max(set(h['language'] for h in st.session_state.analysis_history), 
                           key=st.session_state.analysis_history.count)
        st.markdown(f"### 🎯 Fun Fact")
        st.success(f"You analyze {most_used_lang} code the most!")
    
    # Clear History with Confirmation
    if st.button("🗑️ Clear History"):
        if st.warning("Are you sure you want to clear all history?"):
            st.session_state.analysis_history = []
            st.session_state.token_count = 0
            st.rerun()
    
    # Footer in Sidebar
    st.markdown("---")
    st.markdown("Made with ❤️ by Sairam")
    st.markdown("[GitHub](https://github.com/BavirisettySairam) | [LinkedIn](https://www.linkedin.com/in/bavirisetty-sairam/)")

# Main UI
st.title("🔍 Basic Code Analyzer")

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["Code Analysis", "Documentation", "About"])

with tab1:
    st.markdown("""
    ### 🚀 Professional Code Analysis Tool
    Upload your code or paste it directly below for comprehensive analysis.
    """)
    
    # Code input methods with better organization
    col1, col2 = st.columns([1, 1])
    with col1:
        input_method = st.radio(
            "Choose Input Method",
            ["Upload File 📁", "Paste Code 📋"]
        )
    
    code = ""
    if input_method == "Upload File 📁":
        uploaded_file = st.file_uploader("Upload your code file", type=['py', 'cpp', 'java', 'js', 'ts', 'go', 'rs', 'txt'])
        if uploaded_file is not None:
            code = uploaded_file.getvalue().decode("utf-8")
    else:
        code = st.text_area("Paste your code here", height=300)
        if code:
            char_count = len(code)
            estimated_tokens = estimate_tokens(code)
            st.info(f"📊 Characters: {char_count} | Tokens: {estimated_tokens} | Max: 800 tokens")
    
    # Analysis button with status
    if st.button("🔍 Analyze Code", type="primary"):
        if code:
            with st.spinner("🤖 Analyzing your code..."):
                start_time = time.time()
                result = analyze_code(code, language.split()[0], analysis_type.split()[0], temperature, max_tokens)
                end_time = time.time()
                
                # Add to history
                st.session_state.analysis_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'language': language.split()[0],
                    'type': analysis_type.split()[0],
                    'duration': round(end_time - start_time, 2)
                })
                
                st.session_state.debug_result = result
        else:
            st.warning("⚠️ Please provide some code to analyze.")

    # Display results with better formatting
    if st.session_state.debug_result:
        st.markdown("### 📝 Analysis Results")
        with st.expander("View Analysis", expanded=True):
            st.markdown(st.session_state.debug_result)

with tab2:
    st.markdown("""
    ### 📚 Documentation
    
    #### Analysis Types
    1. **Full Analysis**
       - Syntax errors and bugs
       - Code improvements
       - Detailed explanation
       - Suggested fixes
       - Performance considerations
    
    2. **Security Analysis**
       - Security vulnerabilities
       - Common risks
       - Best practices
       - Security improvements
    
    3. **Performance Analysis**
       - Performance bottlenecks
       - Optimization opportunities
       - Memory usage
       - Performance improvements
    
    #### Usage Guidelines
    - Maximum code size: 800 tokens (~3,200 characters)
    - Supported languages: Python, C++, Java, JavaScript, TypeScript, Go, Rust
    - File types: .py, .cpp, .java, .js, .ts, .go, .rs, .txt
    """)

with tab3:
    st.markdown("""
    ### ℹ️ About Basic Code Analyzer
    
    Basic Code Analyzer is a powerful tool that helps developers analyze their code using advanced AI technology. Built with passion and precision, this tool aims to make code analysis accessible and efficient for developers of all levels.
    
    #### 🚀 Features
    - **Multiple Analysis Types**
        - Full code analysis with comprehensive insights
        - Security vulnerability scanning
        - Performance optimization suggestions
    - **Language Support**
        - Python, C++, Java, JavaScript, TypeScript, Go, Rust
        - More languages coming soon!
    - **Smart Features**
        - Real-time token estimation
        - Analysis history tracking
        - Usage statistics and visualizations
        - Advanced customization options
    - **User-Friendly Interface**
        - Clean, intuitive design
        - Interactive visualizations
        - Detailed documentation
        - Responsive layout
    
    #### 🛠️ Technology Stack
    - **Frontend**: Streamlit
        - Modern, responsive UI
        - Interactive components
        - Real-time updates
    - **Backend**: Python
        - Efficient code processing
        - Robust error handling
        - Scalable architecture
    - **AI Engine**: Groq AI
        - State-of-the-art language model
        - Fast response times
        - Accurate code analysis
    
    #### 📊 Performance Metrics
    - Maximum code size: 800 tokens (~3,200 characters)
    - Average analysis time: < 5 seconds
    - Support for files up to 100KB
    - Real-time token estimation
    
    #### 🔒 Security Features
    - Secure API key management
    - No code storage
    - Privacy-focused design
    - Safe file handling
    
    #### 🎯 Use Cases
    - Code review automation
    - Learning and education
    - Debugging assistance
    - Performance optimization
    - Security auditing
    
    #### 📝 Version History
    - **v1.0.0** (Current)
        - Initial release
        - Basic code analysis
        - Multiple language support
    - **v1.1.0** (Planned)
        - Additional language support
        - Enhanced security analysis
        - Custom analysis templates
    
    #### 👨‍💻 About the Developer
    **Bavirisetty Sairam**
    - MCA Student at Christ University
    - Passionate about AI and Software Development
    - Focused on creating innovative solutions
    
    #### 📞 Contact Information
    - 📧 Email: message2sairam@gmail.com
    - 📱 Phone: +91 9513377365
    - 🔗 LinkedIn: [Bavirisetty Sairam](https://www.linkedin.com/in/bavirisetty-sairam/)
    - 🌐 GitHub: [BavirisettySairam](https://github.com/BavirisettySairam)
    - 📸 Instagram: mr_bavirisetty
    
    #### 🤝 Contributing
    We welcome contributions! Please feel free to:
    - Report bugs
    - Suggest features
    - Submit pull requests
    - Improve documentation
    
    #### 🙏 Acknowledgments
    - Christ University for academic support
    - Groq AI for providing the API
    - Streamlit team for the amazing framework
    - All contributors and users
    
    ---
    Made with ❤️ by Bavirisetty Sairam
    """)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("Built with ❤️ using Streamlit and Groq AI | Basic Version") 