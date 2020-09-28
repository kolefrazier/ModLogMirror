import sqlite3
from Config import SQL as config
from os import path

"""Tools, utilities and helper functions for SQL database interaction."""

# --- Properties ---
Connection = sqlite3.connect(config.DatabaseName)
Cursor = Connection.cursor()
LastError = None

# Try creating database using setup script. Should only run if the db file does not already exist.
if path.isfile(config.DatabaseName) is False or path.getsize(config.DatabaseName) is 0:
    print ('[DEBUG] Creating DB file.')
    TablesSetupScript = open('./SQL/Setup Scripts/SQLiteTables.sql', 'r').read()
    Cursor.executescript(TablesSetupScript)
    Connection.commit()
    #Connection.close()
else:
    print ('[DEBUG] DB file already exists!')
        
# --- Generic Methods ---
### Function ExecuteQuery
### Parameters: Query (string)
### Return: None
### Description: Generic wrapper function to execute queries in other modules without worrying about transactions or connection state.
###     Returns Cursor after query completes for row or status retrieval.
def ExecuteQuery(Query, Values):
    LastError = None
    try:
        with Connection:
            Cursor.execute(Query, Values)
            Connection.commit()
        return Cursor
    except Exception as e:
        Connection.rollback()
        LastError = str(e)

def SelectAllFrom(TableName):
    ResponseTemplate = "{0}: {1}\t-\t{2}"
    Query = "SELECT * FROM :tableName"
    Cursor.execute(Query, {"tableName", TableName})
    response = Cursor.fetchall()
    for row in response:
        print(ResponseTemplate.format(row.id, row.name, row.number))

### Function: InsertInto
### Parameters: TableName (string), Columns (array), Values (zipped dataset (zip(arr1, arr2))
###     Consider using zip() to create sets of values.
### Return: None
### Description: Inserts values into the given table for the given table and values.
###     If any of the values arrays (values[0], ...) are not the same length as the columns table, a ValueError exception will be raised.
def InsertInto(TableName, Columns, Values):
    try:
        if(len(Columns) is 0):
            raise ValueError("Columns set is empty, no columns given for insert definition.")

        #Convert Columns and Values arrays to formatted strings using set joins. 
        #   The leading string is the separator value. If only one element, it won't insert this separator.
        #   Creating a set from values will automatically create bracketed (parenthese'd?) sets. e.g., (1,'a',123),(2,'b',234)
        # References and Sources: 
        #   * https://stackoverflow.com/a/7277102
        #   * https://www.geeksforgeeks.org/zip-in-python/
        ColumnsFormatted = ','.join('[{0}]'.format(col) for col in Columns)
        ValuesFormatted = ','.join(str(val) for val in set(Values))

        #Checked after the format, as zip/set results don't have a "length" to quickly check against. (That I'm aware of currently.)
        if(len(ValuesFormatted) is 0):
            raise ValueError("Values set is empty, no values given to insert.")
        if(len(ValuesFormatted) is not len(ColumnsFormatted)):
            raise ValueError("Values set length does not match columns set length.")
        
        # !!! IS THIS SAFE TO DO? IT'S NOT A PARAMETERIZED QUERY!!
        Cursor.execute("INSERT INTO dbo.{0} ({1}) VALUES ({2})".format(TableName, ColumnsFormatted, ValuesFormatted))
        Connection.commit()
    except Exception as e:
        Connection.rollback()
        LastError = str(e)

def InsertIntoIgnoreConflict(Tablename, Columns, Values):
    try:
        if(len(Columns) is 0):
            raise ValueError("Columns set is empty, no columns given for insert definition.")

        ColumnsFormatted = ','.join('[{0}]'.format(col) for col in Columns)
        ValuesFormatted = ','.join(str(val) for val in set(Values))

        if(len(ValuesFormatted) is 0):
            raise ValueError("Values set is empty, no values given to insert.")
        if(len(ValuesFormatted) is not len(ColumnsFormatted)):
            raise ValueError("Values set length does not match columns set length.")
        
        # !!! IS THIS SAFE TO DO? IT'S NOT A PARAMETERIZED QUERY!!
        Cursor.execute("INSERT OR IGNORE INTO dbo.{0} ({1}) VALUES ({2})".format(TableName, ColumnsFormatted, ValuesFormatted))
        Connection.commit()
    except Exception as e:
        Connection.rollback()
        LastError = str(e)

# --- Utility Methods ---
def QuotifyString(s):
    return "'{0}'".format(s.replace("'", "\'"))