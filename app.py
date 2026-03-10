import streamlit as st
import sqlite3
import os
import pandas as pd
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

# --- Page Config ---
st.set_page_config(page_title="Beverage Analytics AI", page_icon="🥤", layout="wide")
st.title("🥤 Beverage Analytics Assistant")
st.markdown("Query sales, promotions, and inventory using natural language.")

# --- Load API Key ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

@st.cache_resource
def init_analytics_engine():
    # 1. Knowledge Base (RAG)
    campaign_docs = [
        "The 'South Summer Kick-off' (Promo ID P002) ran from weeks W04 to W06.",
        "REGION MAPPING: 'R02' in Promo Master = 'S' (South) in Sales tables.",
        "REVENUE: Sum 'gross_sales_gbp' in pos_transactions table."
    ]
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(campaign_docs, embeddings)

    # 2. Tool Logic
    def run_sql(query):
        conn = sqlite3.connect("enterprise_data.db")
        try:
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_string() if not df.empty else "No records found."
        except Exception as e:
            conn.close()
            return f"SQL Error: {str(e)}"

    def safe_search(query):
        # Type Guard: Ensure query is a string to prevent AttributeError
        if isinstance(query, list):
            query = " ".join(map(str, query))
        res = vector_store.similarity_search(str(query), k=1)
        return res[0].page_content if res else "No context found."

    tools = [
        Tool(name="Database_Query", func=run_sql, description="Access sales and product data."),
        Tool(name="Knowledge_Search", func=safe_search, description="Lookup business rules and campaign IDs.")
    ]

    # 3. Brain (Gemini 3.1 Flash Lite)
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-3.1-flash-lite-preview", 
        google_api_key=api_key, 
        temperature=0
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Analyst mode. Return ONLY a clean natural language report.
        Format using:
        ### Executive Summary
        ### Raw Data
        ### Logic Used"""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=15)

# Initialize the persistent engine
agent_executor = init_analytics_engine()

# --- Chat Interface ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display conversation
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# User Interaction
if user_query := st.chat_input("Ask about your beverage data..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.chat_message("user").markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing datasets..."):
            # --- THE CLEANING LAYER ---
            result = agent_executor.invoke({"input": user_query})
            
            # Extract final text from dictionary/list response
            if isinstance(result, dict):
                output = result.get("output", "")
                if isinstance(output, list) and len(output) > 0:
                    final_answer = output[0].get('text', str(output))
                else:
                    final_answer = str(output)
            elif isinstance(result, list) and len(result) > 0:
                final_answer = result[0].get('text', str(result))
            else:
                final_answer = str(result)

            st.markdown(final_answer)
            st.session_state.chat_history.append({"role": "assistant", "content": final_answer})