from fastapi import FastAPI

from backend.api.policy_management.routes import router as policy_router
from backend.db import Base, engine


app = FastAPI(title="SpendPilot Backend")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(policy_router)

