from fastapi import FastAPI
from app.api import users, venues, reco, plans, health

app = FastAPI(title="Luna API Service")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(venues.router, prefix="/venues", tags=["venues"])
app.include_router(reco.router, prefix="/reco", tags=["recommendations"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
