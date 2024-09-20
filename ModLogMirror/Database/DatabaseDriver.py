import psycopg2
import Config.Database as config
from os import path
import pprint
import logging

"""Tools, utilities and helper functions for SQL database interaction."""

# --- Properties ---
Connection = psycopg2.connect(host=config.Host, port=config.Port, database=config.Database, user=config.User, password=config.Password)
Cursor = Connection.cursor()

# --- Debug Stats ---
_queriesExecuted = {}
pp = pprint.PrettyPrinter(indent=4)

def EnableStats():
    config.EnableStats()

def DisableStats():
    config.DisableStats()

# Parameters: 
#       Query (string): The query to be executed
#       Values (dict): Values to fill placeholders in the query
#       Source (string): Defaults to "Unspecified," code module or location executing the query. Not used if stats tracking is disabled. (False by default.)
# Return: Connection cursor, used for query result retrieval or status retrieval.
# Description: Generic wrapper function to execute queries in other modules without worrying about transactions or connection state.
def ExecuteQuery(Query, Values={}, Source="Unspecified"):
    try:
        with Connection:
            Cursor.execute(Query, Values)
            Connection.commit()

        if config.TrackStats:
            UpdateStat(Source)
        
        return Cursor
    except Exception as e:
        # Rollback the last query, then re-raise the error with more context.
        # This way, the appropriate logger can capture the error, rather than
        # trying to figure out what's using this module and where to send the error.
        Connection.rollback()
        raise Exception(f"[DatabaseDriver->ExecuteQuery] Error from source {Source}: {str(e)}")

def UpdateStat(Source):
    if(Source not in _queriesExecuted):
        _queriesExecuted[Source] = 0
    _queriesExecuted[Source] += 1

def printStats():
    print(f"[DatabaseDriver] Queries Executed:")
    pp.pprint(str(_queriesExecuted))

def resetStats():
    global _queriesExecuted
    _queriesExecuted = {}

# --- Utility Methods ---
def QuotifyString(s):
    return "'{0}'".format(s.replace("'", "\'"))
