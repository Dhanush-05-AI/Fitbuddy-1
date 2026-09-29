import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()


def main():
    default_reload = "false" if os.name == "nt" else "true"
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", default_reload).lower() == "true",
    )


if __name__ == "__main__":
    main()
