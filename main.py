from fastapi import FastAPI
from app.models import Base
from app.database import engine
from app.state import AppState
from app.routes import get
from app.routes import stat
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.state = AppState()

app.include_router(get.router)
app.include_router(stat.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
