import os
import time
from pymongo import MongoClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_mongo_client(max_retries=3, retry_delay=2):
    """Get MongoDB client instance with retry logic."""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to MongoDB at {settings.MONGODB_URI} (attempt {attempt + 1}/{max_retries})")
            client = MongoClient(
                settings.MONGODB_URI,
                **settings.MONGODB_CLIENT_SETTINGS
            )
            # Test connection
            client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("All connection attempts failed")
                return None

def get_mongo_db():
    """Get MongoDB database instance."""
    try:
        client = get_mongo_client()
        if client:
            db = client[settings.MONGODB_DB_NAME]
            logger.info(f"Successfully got database: {settings.MONGODB_DB_NAME}")
            return db
        return None
    except Exception as e:
        logger.error(f"Failed to get MongoDB database: {str(e)}")
        return None

def get_collection(collection_name):
    """Get MongoDB collection instance."""
    try:
        db = get_mongo_db()
        if db:
            collection = db[settings.MONGODB_COLLECTIONS.get(collection_name, collection_name)]
            logger.info(f"Successfully got collection: {collection_name}")
            return collection
        return None
    except Exception as e:
        logger.error(f"Failed to get {collection_name} collection: {str(e)}")
        return None

def ensure_collections():
    """Ensure all required collections exist."""
    try:
        db = get_mongo_db()
        if db:
            for collection_name in settings.MONGODB_COLLECTIONS.values():
                if collection_name not in db.list_collection_names():
                    db.create_collection(collection_name)
                    logger.info(f"Created collection: {collection_name}")
                else:
                    logger.info(f"Collection already exists: {collection_name}")
    except Exception as e:
        logger.error(f"Failed to ensure collections: {str(e)}") 