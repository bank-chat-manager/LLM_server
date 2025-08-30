from fastapi import FastAPI
from app.api.endpoints import summary, tagging

app = FastAPI(title="LLM Service for Banking Consultation")

app.include_router(summary.router, prefix="/api", tags=["Summary"])
app.include_router(tagging.router, prefix="/api", tags=["Tagging"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the LLM service."}
