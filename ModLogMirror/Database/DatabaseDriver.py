import psycopg2
#from Config import Database as config
import Config.Database as config
from os import path

"""Tools, utilities and helper functions for SQL database interaction."""

# --- Properties ---
Connection = psycopg2.connect(host=config.Host, port=config.Port, database=config.Database, user=config.User, password=config.Password)
Cursor = Connection.cursor()
LastError = None

# --- Debug Stats ---
_queriesExecuted = 0
        
# --- Generic Methods ---
### Function ExecuteQuery
### Parameters: Query (string)
### Return: None
### Description: Generic wrapper function to execute queries in other modules without worrying about transactions or connection state.
###     Returns Cursor after query completes for row or status retrieval.
def ExecuteQuery(Query, Values):
    global _queriesExecuted

    LastError = None
    try:
        with Connection:
            Cursor.execute(Query, Values)
            Connection.commit()

        _queriesExecuted += 1
        return Cursor
    except Exception as e:
        Connection.rollback()
        LastError = str(e)

def printStats():
    global _queriesExecuted
    print(f"[DatabaseDriver] Queries Executed: {_queriesExecuted}")

def resetStats():
    global _queriesExecuted
    _queriesExecuted = 0

# --- Utility Methods ---
def QuotifyString(s):
    return "'{0}'".format(s.replace("'", "\'"))
