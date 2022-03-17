import os
import logging

logger = logging.getLogger(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path)
        logger.info(f"Loaded environment file: {dotenv_path}")
    except Exception as e:
        logger.warn(f"{e}\nUnable to load environment file: {dotenv_path}")


from app import create_app


app = create_app()

if __name__ == "__main__":
    app.run(port=5000)
