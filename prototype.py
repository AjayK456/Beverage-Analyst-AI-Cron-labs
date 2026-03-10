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

# --- Load API Key ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# --- Step 1: Knowledge Base (RAG) ---
campaign_documents = [
    "The 'South Summer Kick-off' (Promo ID P002) ran from weeks W04 to W06.",
    "REGION MAPPING: 'R02' in Promo Master = 'S' (South) in Sales tables.",
    "REVENUE: Sum 'gross_sales_gbp' in pos_transactions table."
]

# --- Step 2: Tool Logic ---
def execute_sql(query):
    conn = sqlite3.connect("enterprise_data.db")
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_string() if not df.empty else "No results found."
    except Exception as e:
        conn.close()
        return str(e)

def safe_search(query):
    if isinstance(query, list):
        query = " ".join(map(str, query))
    docs = vector_store.similarity_search(str(query), k=1)
    return docs[0].page_content if docs else "No context found."

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_texts(campaign_documents, embeddings)

tools = [
    Tool(name="Database_Query", func=execute_sql, description="SQL access."),
    Tool(name="Knowledge_Search", func=safe_search, description="Context lookup.")
]

# --- Step 3: Agent Setup ---
llm = ChatGoogleGenerativeAI(model="models/gemini-3.1-flash-lite-preview", google_api_key=api_key, temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Analyst mode. Return ONLY the final natural language answer.
    Do NOT include any technical metadata, dictionaries, or brackets.
    Format your response neatly using these headers:
    ### Executive Summary
    ### Raw Data
    ### Logic Used"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
# Set verbose=False to remove internal logic logs from the output
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=15)

# --- Step 4: The Polished Cleaning Layer ---
def get_clean_answer(user_input):
    # This is the single source of truth for the response
    result = agent_executor.invoke({"input": user_input})
    
    # Logic to dig through the Gemini 3.1 message list
    if isinstance(result, dict):
        # Case A: Dictionary with 'output' key
        output = result.get("output", "")
        # If 'output' is a list (Gemini style), extract the text
        if isinstance(output, list) and len(output) > 0:
            return output[0].get('text', str(output))
        return str(output)
    
    elif isinstance(result, list) and len(result) > 0:
        # Case B: Direct list of messages
        return result[0].get('text', str(result))
    
    return str(result)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 AI ANALYTICS: PROFESSIONAL MODE")
    print("="*50)
    
    while True:
        question = input("\nQuestion (or 'exit'): ")
        if question.lower() == 'exit': break
        
        print("Processing...")
        
        # FIX: We now exclusively use the cleaning function
        final_answer = get_clean_answer(question)
        
        print("\n" + "-"*50)
        print(final_answer)
        print("-"*50)