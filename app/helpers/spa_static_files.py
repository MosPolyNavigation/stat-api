from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.exceptions import HTTPException
from pathlib import Path

class SPAStaticFiles(StaticFiles):
    def __init__(self, directory: str, html: bool):
        self.index_file = "index.html"
        super().__init__(directory=directory, html=html)

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as ex:
            print(ex)
            if ex.status_code == 404:
                full_path = Path(self.directory) / self.index_file
                if full_path.exists():
                    return FileResponse(full_path)
            raise ex