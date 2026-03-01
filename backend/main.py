from fastapi import FastAPI
from pydantic import BaseModel
from graph import graph

app = FastAPI()

class QueryRequest(BaseModel):
    message: str


@app.post("/api/query")
async def query(req: QueryRequest):
    result = graph.invoke({
        "user_input": req.message,
        "classification": None,
        "final_answer": None,
        "debug": []
    })

    return result