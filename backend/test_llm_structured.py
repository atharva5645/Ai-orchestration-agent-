import asyncio
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.shared.llm import gemini_client

class TestSchema(BaseModel):
    name: str
    age: int

async def test_llm():
    print("Testing ainvoke_structured...")
    sys_msg = SystemMessage(content="Extract information.")
    prompt = HumanMessage(content="John is 30 years old.")
    try:
        res = await gemini_client.ainvoke_structured([sys_msg, prompt], TestSchema)
        print("Success:", res)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test_llm())
