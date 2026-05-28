import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

async def check_gemini():
    load_dotenv(".env.dev")
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: No GOOGLE_API_KEY found in .env.dev")
        return
        
    print(f"Testing Google Gemini API Key ending in: ...{api_key[-4:]}")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=api_key,
            temperature=0.2
        )
        print("Sending test message to Gemini...")
        response = await llm.ainvoke([HumanMessage(content="Say the word 'Success!'")])
        print(f"\\n[SUCCESS] The API Key works perfectly. Gemini says: {response.content}")
    except Exception as e:
        print(f"\\n[FAILED] Error from Google API:\\n{str(e)}")

if __name__ == "__main__":
    asyncio.run(check_gemini())
