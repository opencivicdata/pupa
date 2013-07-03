from pymongo import Connection

SERVER = "localhost"
DATABASE = "ocd"
PORT = 27017

db = None


def _update_connection():
    global db
    connection = Connection(SERVER, PORT)
    db = getattr(connection, DATABASE)

_update_connection()
