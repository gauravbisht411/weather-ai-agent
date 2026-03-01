# Weather Agentic AI Workshop

This repository demonstrates an **Agentic AI** workflow for weather forecasting using Amazon Bedrock (Claude 4.5 Sonnet) and the National Weather Service (NWS) API. It provides both a command-line interface (CLI) and a web interface (Streamlit) to showcase how an AI agent can reason, plan, act, and process real-world data.

## Features
- **AI Planning:** Uses Claude 4.5 Sonnet to interpret user locations and generate appropriate NWS API calls.
- **Action:** Automatically fetches weather data from the NWS API.
- **Processing:** Converts complex weather data into clear, human-readable summaries using AI.
- **Interfaces:**
  - `weather_agent_cli.py`: Interactive CLI agent.
  - `weather_agent_web.py`: Interactive web app (Streamlit).

## How It Works
1. **User Input:** Enter a location (city, ZIP, state, or description).
2. **AI Planning:** Claude generates the correct NWS API endpoint.
3. **API Calls:** The agent fetches weather data from the NWS.
4. **AI Processing:** Claude summarizes the weather data.
5. **Results:** The forecast is displayed in a user-friendly format.

## Setup
### Prerequisites
- Python 3.8+
- AWS credentials with access to Amazon Bedrock (for Claude)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/agentic-ai-workshop.git
   cd weather-ai-agent
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
### Command-Line Agent
Run the CLI agent:
```sh
python weather_agent_cli.py
```

### Web Agent (Streamlit)
Run the web app:
```sh
streamlit run weather_agent_web.py
```

## Example Queries
- Seattle
- 90210
- New York City
- Miami, FL
- National park near Homestead in Florida

## Notes
- This demo uses official NWS data for educational purposes.
- Claude 4.5 Sonnet access via Amazon Bedrock is required.

