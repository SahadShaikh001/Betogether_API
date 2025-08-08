from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, users, category, search
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="BETOGETHER API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(search.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "BETOGETHER API is running"}
