from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    message: str


@app.post("/api/query")
async def query(req: QueryRequest):
    result = graph.invoke({
        "user_input": req.message,
        "classification": None,
        "web_search_result": None,
        "final_answer": None,
        "debug": []
    })

    return result