# ~*~ encoding: utf-8 ~*~

from pymongo import Connection
from pymongo.errors import ConnectionFailure

SERVER = "localhost"
DATABASE = "ocd"
PORT = 27017

db = None


def _update_connection():
    global db
    connection = Connection(SERVER, PORT)
    db = getattr(connection, DATABASE)


try:
    _update_connection()
except ConnectionFailure as e:
    pass
    #print(u"[scruffy] Scruffy can't connect to the database. Mmmmhum.")
    #print(u"           ⤷ %s" % (str(e)))
