import uvicorn
import sys
from pathlib import Path

from server_app.api.v1.routes import app


if __name__ == "__main__":
    # 启动服务
    # uvicorn.run(r"server_app.main:app", host="127.0.0.1", port=8000, reload=True)
    uvicorn.run(app, host="127.0.0.1", port=8000)
