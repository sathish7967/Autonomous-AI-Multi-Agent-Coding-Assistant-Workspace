import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Core Agent Processing Drivers
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = FastAPI(title="Autonomous Multi-Agent Engineering Workspace")

# Configure CORS boundaries for robust browser UI connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = "Your_Groq_API_Key_Here"  # Replace with your actual Groq API key

print("[SYSTEM]: Spinning up local engineering mesh array nodes...")
llm = ChatGroq(
    temperature=0.0,  # Dropped to 0 for maximum structural constraint adherence
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant"
)

class AgentGenerationRequest(BaseModel):
    prompt: str

@app.post("/execute-workflow")
async def execute_agent_workflow(request: AgentGenerationRequest):
    try:
        # =========================================================================
        # AGENT NODE 1: The Architectural Planner
        # =========================================================================
        planner_prompt = ChatPromptTemplate.from_template(
            "You are an Elite Software Architect. Break down the requirements and create a short, "
            "sequential logic execution plan to build: {task}. Return only the clean, numbered steps."
        )
        planner_chain = planner_prompt | llm | StrOutputParser()
        plan_text = planner_chain.invoke({"task": request.prompt})

        # =========================================================================
        # AGENT NODE 2: The Senior Core Developer (Raw String + Safe JSON Extract)
        # =========================================================================
        developer_prompt = ChatPromptTemplate.from_template(
            "You are a Senior Systems Engineer. Write clean, complete, runnable Python code based "
            "on this software implementation plan:\n{plan}.\n"
            "Return ONLY the raw python script blocks. Do not add explanations, conversational text, "
            "or markdown backticks."
        )
        developer_chain = developer_prompt | llm | StrOutputParser()
        generated_code = developer_chain.invoke({"plan": plan_text})

        # =========================================================================
        # AGENT NODE 3: The Automated QA Compilation Tester
        # =========================================================================
        qa_prompt = ChatPromptTemplate.from_template(
            "You are an automated code compilation agent. Audit this script for syntax mistakes, "
            "edge case failures, or logic bugs:\n{code}.\n"
            "Provide your final feedback as a short list of bullet points. Start the very first line of your "
            "response with either the exact word PASSED or FIX_REQUIRED followed by a newline."
        )
        qa_chain = qa_prompt | llm | StrOutputParser()
        qa_res_raw = qa_chain.invoke({"code": generated_code})
        
        # Parse status dynamically via raw string line indexing
        lines = [line.strip() for line in qa_res_raw.split("\n") if line.strip()]
        qa_status = "PASSED" if lines and "PASSED" in lines[0].upper() else "FIX_REQUIRED"
        qa_feedback = "\n".join(lines[1:]) if len(lines) > 1 else qa_res_raw
        
        return {
            "status": "Workflow Cycle Complete",
            "plan": plan_text,
            "code": generated_code,
            "qa_status": qa_status,
            "qa_feedback": qa_feedback
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
