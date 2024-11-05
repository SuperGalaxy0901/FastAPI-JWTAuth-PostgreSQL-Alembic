from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import token, users, magazines, plans, subscriptions
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Magazine Subscription Service",
    description="A simplified magazine subscription service API",
    version="1.0.0",
)

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(token.router)
app.include_router(users.router)
app.include_router(magazines.router)
app.include_router(plans.router)
app.include_router(subscriptions.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
