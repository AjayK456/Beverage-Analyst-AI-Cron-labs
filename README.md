# Beverage-Analyst-AI-Cron-labs
This AI Analyst uses a ReAct Agent with Gemini 3.1 Flash-Lite to bridge natural language and SQL data. By combining FAISS for business-rule retrieval (RAG) and SQLite for exact sales aggregation, it delivers accurate, formatted reports from complex datasets with a self-correcting logic loop.
# AI Sales Analyst Prototype

Follow these steps to set up the environment and run the application.

## 1. Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
Note: Key libraries include langchain, langchain-google-genai, faiss-cpu, sentence-transformers, pandas, and streamlit.
pip install -r requirements.txt
python setup_data.py
python ingest_data.py
streamlit run app.py
Environment Variables: Create a file named .env in the root directory and add your API key:
GOOGLE_API_KEY=your_actual_key_here
