import os

from motor.motor_asyncio import AsyncIOMotorClient

_client = None


# Cliente único de MongoDB (mongomock:// sirve para pruebas sin servidor)
def get_client():
    global _client

    if _client is None:
        url = os.getenv("MONGO_URL", "mongodb://localhost:27017")

        if url.startswith("mongomock://"):
            from mongomock_motor import AsyncMongoMockClient
            _client = AsyncMongoMockClient()
        else:
            _client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=3000)

    return _client


def set_client(client):
    global _client
    _client = client


# Cada servicio usa su propia base de datos
def get_db(name):
    return get_client()[name]
