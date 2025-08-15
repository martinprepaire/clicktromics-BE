from pymongo import MongoClient
from src.config import MONGO_URL, MONGO_DATABASE
import logging

log = logging.getLogger(__name__)

class SandboxMongo:
    _mongo_client = None
    _mongo_client_sync = None

    @classmethod
    def _initialize_client(cls):
        """Initialize async MongoDB client"""
        try:
            if cls._mongo_client is None:
                cls._mongo_client = MongoClient(MONGO_URL)
                log.info("✅ MongoDB async client initialized successfully.")
        except Exception as e:
            log.error(f"❌ Error initializing MongoDB async client: {str(e)}")
            raise

    @classmethod
    def _initialize_sync_client(cls):
        """Initialize sync MongoDB client"""
        try:
            if cls._mongo_client_sync is None:
                cls._mongo_client_sync = MongoClient(MONGO_URL)
                log.info("✅ MongoDB sync client initialized successfully.")
        except Exception as e:
            log.error(f"❌ Error initializing MongoDB sync client: {str(e)}")
            raise

    @classmethod
    def get_genes_collection(cls):
        """Get the genes collection"""
        if cls._mongo_client_sync is None:
            raise ValueError("Synchronous MongoDB client is not initialized. Call Mongo.get_client_sync() first.")
        db = cls._mongo_client_sync[MONGO_DATABASE]
        return db['genes']
    
    @classmethod
    def get_diseases_collection(cls):
        """Get the diseases collection."""
        if cls._mongo_client_sync is None:
            raise ValueError("Synchronous MongoDB client is not initialized. Call Mongo.get_client_sync() first.")
        db = cls._mongo_client_sync[MONGO_DATABASE]
        return db['diseases']

    @classmethod
    def get_drugs_collection(cls):
        """Get the drugs collection."""
        if cls._mongo_client_sync is None:
            raise ValueError("Synchronous MongoDB client is not initialized. Call Mongo.get_client_sync() first.")
        db = cls._mongo_client_sync[MONGO_DATABASE]
        return db['drugs']
    
    @classmethod
    def get_antibodies_collection(cls):
        """Get the antibodies collection."""
        if cls._mongo_client_sync is None:
            raise ValueError("Synchronous MongoDB client is not initialized. Call Mongo.get_client_sync() first.")
        db = cls._mongo_client_sync[MONGO_DATABASE]
        return db['antibodies']

    @classmethod
    def get_malacards_collection(cls):
        """Get the malacards collection"""
        if cls._mongo_client_sync is None:
            raise ValueError("Synchronous MongoDB client is not initialized. Call Mongo.get_client_sync() first.")
        db = cls._mongo_client_sync[MONGO_DATABASE]
        return db['malacards']