from fastapi import FastAPI
from routers import machines

app = FastAPI(
    title="Celium API",
    description="REST API for Celium Pods",
    version="0.1.0"
)

# Include routers
app.include_router(machines.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 