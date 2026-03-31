import sys
import os

# Ensure `backend/` is in sys.path so `utils/` is importable on Render
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    is_render = os.environ.get("RENDER") is not None
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=not is_render)
