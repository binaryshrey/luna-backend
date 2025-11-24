from fastapi import FastAPI
from app.api import users, venues, reco, plans

app = FastAPI(title="Luna Backend Track 2")

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(venues.router, prefix="/venues", tags=["venues"])
app.include_router(reco.router, prefix="/reco", tags=["recommendations"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
