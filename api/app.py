import logging
from api import create_app

app = create_app()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting API")
    app.run(debug=True)
