import uvicorn

from app.default_hooks import DefaultHooks
from app.factory import AppFactory

create_app = AppFactory(DefaultHooks())
app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
