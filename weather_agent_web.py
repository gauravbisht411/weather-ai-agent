import streamlit as st
import boto3
import subprocess
import json
import time
from datetime import datetime
from PIL import Image
import os

# Page configuration
st.set_page_config(
    page_title="Weather AI Agent",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .step-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .step-header {
        font-size: 18px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .success-box {
        border-left: 5px solid #28a745;
        background-color: #d4edda;
        padding: 10px;
        margin: 10px 0;
        color: #000000;
    }
    .error-box {
        border-left: 5px solid #dc3545;
        background-color: #f8d7da;
        padding: 10px;
        margin: 10px 0;
        color: #000000;
    }
    .info-box {
        border-left: 5px solid #17a2b8;
        background-color: #d1ecf1;
        padding: 10px;
        margin: 10px 0;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

def call_claude_sonnet(prompt):
    """
    Connect to Claude 4.5 Sonnet via Amazon Bedrock
    """
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2'
    )
    
    try:
        response = bedrock.converse(
            modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.7
            }
        )
        
        return True, response['output']['message']['content'][0]['text']
        
    except Exception as e:
        return False, f"Error calling Claude: {str(e)}"

def execute_curl_command(url):
    """
    Execute curl command to fetch API data
    """
    try:
        result = subprocess.run(
            ['curl', '-s', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"Curl command failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "Request timed out after 30 seconds"
    except Exception as e:
        return False, f"Error executing curl: {str(e)}"

def generate_weather_api_calls(location):
    """
    Use Claude to generate NWS API calls
    """
    prompt = f"""
You are an expert at working with the National Weather Service (NWS) API.

Your task: Generate the NWS API URL to get weather forecast data for "{location}".

Instructions:
1. First, determine the approximate latitude and longitude coordinates for this location
2. Generate the NWS Points API URL: https://api.weather.gov/points/{{lat}},{{lon}}

For the coordinates, use your knowledge to estimate:
- Major cities: Use well-known coordinates
- ZIP codes: Estimate based on the area
- States: Use approximate center coordinates
- In case a location description is provided instead of a location name, please use the most likely city and state name as the location for the coordinates

Example for Seattle:
https://api.weather.gov/points/47.6062,-122.3321

Example for largest city in USA:
Based on your knowledge, you will establish location is New York City
https://api.weather.gov/points/40.7128,-74.0060

Now generate the API call (Points API) for the established location. 
Return ONLY the complete Points API URL, nothing else.
Format: https://api.weather.gov/points/LAT,LON
"""
    
    success, response = call_claude_sonnet(prompt)
    
    if success:
        api_url = response.strip()
        if api_url.startswith('https://api.weather.gov/points/'):
            return True, [api_url]
        else:
            return False, f"AI generated invalid URL: {api_url}"
    else:
        return False, response

def get_forecast_url_from_points_response(points_json):
    """
    Extract forecast URL from Points API response
    """
    try:
        data = json.loads(points_json)
        forecast_url = data['properties']['forecast']
        return True, forecast_url
    except (json.JSONDecodeError, KeyError) as e:
        return False, f"Error parsing Points API response: {str(e)}"

def process_weather_response(raw_json, location):
    """
    Use Claude to process NWS API response
    """
    prompt = f"""
You are a weather information specialist. I have raw National Weather Service forecast data for "{location}" that needs to be converted into a clear, helpful summary for a general audience.

Raw NWS API Response:
{raw_json}

Please create a weather summary that includes:
1. A brief introduction with the location
2. Current conditions and today's forecast
3. The next 2-3 days outlook with key details (temperature, precipitation, wind)
4. Any notable weather patterns or alerts
5. Format the response to be easy to read and understand

Make it informative and practical for someone planning their activities. Focus on being helpful and clear.
"""
    
    success, response = call_claude_sonnet(prompt)
    return success, response

# Sidebar with information
st.sidebar.title("🤖 About This Agent")
st.sidebar.markdown("""
This AI agent demonstrates **Agentic AI** principles:

**🧠 Intelligence**: Uses Claude 4.5 Sonnet to understand locations and plan API calls

**🔗 Action**: Automatically calls the National Weather Service API

**📊 Processing**: Converts complex weather data into readable forecasts

**💬 Response**: Provides helpful, practical weather information
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏗️ Architecture")
st.sidebar.markdown("""
1. **User Input** → Location name
2. **AI Planning** → Generate API calls
3. **Points API** → Get forecast office  
4. **Forecast API** → Get weather data
5. **AI Processing** → Create summary
6. **Display Results** → Show to user
""")

# Main application
st.title("🌤️ Weather AI Agent")
st.markdown("### Powered by Claude 4.5 Sonnet on Amazon Bedrock")

st.markdown("""
This intelligent agent helps you get weather forecasts using the National Weather Service API. 
Enter any location below and watch the AI agent work through its reasoning process!
""")

# Initialize session state for results
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Input section
st.markdown("---")
location = st.text_input(
    "🔍 Enter a location name or description:",
    placeholder="e.g., Seattle, 90210, New York City, National park near Homestead in Florida",
    help="You can enter city names, ZIP codes, state names, or location descriptions"
)

# Create columns for the buttons
button_col1, button_col2 = st.columns([2, 1])

with button_col1:
    get_forecast = st.button("🚀 Get Weather Forecast", type="primary")

with button_col2:
    clear_results = st.button("🗑️ Clear Results", type="secondary")

# Clear results functionality
if clear_results:
    st.session_state.show_results = False
    st.success("🗑️ Results cleared! Enter a new location to get a fresh forecast.")

if get_forecast:
    st.session_state.show_results = True

if st.session_state.show_results and get_forecast:
    if not location:
        st.error("❌ Please enter a location name or description.")
    else:
        # Create columns for better layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"## Weather Analysis for: **{location}**")
            
            # Step 1: AI Planning
            with st.container():
                st.markdown('<div class="step-container">', unsafe_allow_html=True)
                st.markdown('<div class="step-header">🧠 Step 1: AI Planning Phase</div>', unsafe_allow_html=True)
                
                with st.spinner("Claude is analyzing the location and planning the API calls..."):
                    success, api_calls = generate_weather_api_calls(location)
                
                if success:
                    points_url = api_calls[0]
                    st.markdown('<div class="success-box">✅ Points API URL generated successfully!</div>', unsafe_allow_html=True)
                    st.code(points_url, language="text")
                else:
                    st.markdown(f'<div class="error-box">❌ Failed to generate API calls: {api_calls}</div>', unsafe_allow_html=True)
                    st.stop()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 2: Points API Execution
            with st.container():
                st.markdown('<div class="step-container">', unsafe_allow_html=True)
                st.markdown('<div class="step-header">🔗 Step 2: Points API Execution</div>', unsafe_allow_html=True)
                
                with st.spinner("Fetching location data from National Weather Service..."):
                    success, points_response = execute_curl_command(points_url)
                
                if success:
                    st.markdown('<div class="success-box">✅ Received location data from NWS</div>', unsafe_allow_html=True)
                    
                    # Show a preview of the raw data
                    with st.expander("🔍 View Raw Points API Response (first 500 characters)"):
                        st.code(points_response[:500] + "..." if len(points_response) > 500 else points_response, language="json")
                else:
                    st.markdown(f'<div class="error-box">❌ Failed to fetch points data: {points_response}</div>', unsafe_allow_html=True)
                    st.stop()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 3: Extract Forecast URL
            with st.container():
                st.markdown('<div class="step-container">', unsafe_allow_html=True)
                st.markdown('<div class="step-header">📍 Step 3: Extracting Forecast URL</div>', unsafe_allow_html=True)
                
                success, forecast_url = get_forecast_url_from_points_response(points_response)
                
                if success:
                    st.markdown('<div class="success-box">✅ Forecast URL extracted successfully!</div>', unsafe_allow_html=True)
                    st.code(forecast_url, language="text")
                else:
                    st.markdown(f'<div class="error-box">❌ Failed to extract forecast URL: {forecast_url}</div>', unsafe_allow_html=True)
                    st.stop()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 4: Forecast API Execution
            with st.container():
                st.markdown('<div class="step-container">', unsafe_allow_html=True)
                st.markdown('<div class="step-header">🌦️ Step 4: Forecast API Execution</div>', unsafe_allow_html=True)
                
                with st.spinner("Fetching weather forecast data..."):
                    success, forecast_response = execute_curl_command(forecast_url)
                
                if success:
                    st.markdown(f'<div class="success-box">✅ Received {len(forecast_response):,} characters of forecast data</div>', unsafe_allow_html=True)
                    
                    # Show a preview of the raw data
                    with st.expander("🔍 View Raw Forecast API Response (first 500 characters)"):
                        st.code(forecast_response[:500] + "..." if len(forecast_response) > 500 else forecast_response, language="json")
                else:
                    st.markdown(f'<div class="error-box">❌ Failed to fetch forecast data: {forecast_response}</div>', unsafe_allow_html=True)
                    st.stop()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 5: AI Processing
            with st.container():
                st.markdown('<div class="step-container">', unsafe_allow_html=True)
                st.markdown('<div class="step-header">📊 Step 5: AI Analysis Phase</div>', unsafe_allow_html=True)
                
                with st.spinner("Claude is processing the weather data and creating a summary..."):
                    success, summary = process_weather_response(forecast_response, location)
                
                if success:
                    st.markdown('<div class="success-box">✅ Weather analysis complete!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ Failed to process data: {summary}</div>', unsafe_allow_html=True)
                    st.stop()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 6: Results
            st.markdown("---")
            st.markdown("## 🌤️ Weather Forecast")
            st.markdown(summary)
            
        with col2:
            # Real-time status updates
            st.markdown("### 📊 Process Status")
            
            status_container = st.container()
            with status_container:
                st.markdown("""
                <div class="info-box">
                <strong>🔄 Agent Workflow:</strong><br>
                ✅ Planning Phase<br>
                ✅ Points API Call<br>
                ✅ URL Extraction<br>
                ✅ Forecast API Call<br>
                ✅ Data Processing<br>
                ✅ Results Generated
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 🎯 What Makes This Agentic?")
            st.markdown("""
            - **🧠 Reasoning**: AI understands location formats
            - **📋 Planning**: Generates appropriate API call sequences
            - **🔧 Action**: Executes real-world API requests
            - **📊 Processing**: Converts raw data to insights
            - **🔄 Adaptation**: Handles different location types
            """)

# Footer
st.markdown("---")
st.markdown("""
### 🔬 About This Demo

This application demonstrates **Agentic AI** principles using:
- **Amazon Bedrock** with Claude 4.5 Sonnet for intelligent reasoning
- **National Weather Service API** for real-time weather data
- **Streamlit** for interactive web interface

**⚠️ Important**: This uses official NWS data for educational purposes. For critical weather decisions, consult official sources.
""")

# Add some example queries
st.markdown("### 💡 Try These Examples:")
st.markdown("""
**Suggested locations to test:**
- **Seattle** - Major city (tests city name recognition)
- **90210** - ZIP code (tests postal code handling)  
- **New York City** - Multi-word city (tests complex location parsing)
- **Miami, FL** - City with state (tests state abbreviations)
- **Chicago** - Another major city (tests different coordinates)
- **National park near Homestead in Florida** - Location description (tests AI reasoning)
- **Largest City in California** - Descriptive query (tests knowledge-based location finding)

Simply copy any of these into the location input above and click "Get Weather Forecast"!
""")