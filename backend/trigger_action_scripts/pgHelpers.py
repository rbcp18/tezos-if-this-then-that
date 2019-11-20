
def runQueryAndGetResults(connPool, queryText, numResults = 0):
    try:
        conn = connPool.getconn()
        cursor = conn.cursor()        
        cursor.execute(queryText)
        colnames = [desc[0] for desc in cursor.description]
        if (numResults > 0):
            return (colnames, cursor.fetchmany(numResults))
        else:
            return (colnames, cursor.fetchall())

    except (Exception, psycopg2.DatabaseError) as error:
        print ("Error while running PostgreSQL query: ", error)

    finally:        
        if(conn):
            cursor.close()
            connPool.putconn(conn)


def runGenericStatement(connPool, queryText, doCommit = True):
    try:
        conn = connPool.getconn()
        cursor = conn.cursor()        
        cursor.execute(queryText)
        if doCommit:
            conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print ("Error while running PostgreSQL insert: ", error)

    finally:        
        if(conn):
            cursor.close()
            connPool.putconn(conn)


# Expected query format: "INSERT INTO table1 (col1, col2, col3) VALUES %s",
def runMultipleInsert(connPool, queryText, values, doCommit = True):
    try:
        conn = connPool.getconn()
        cursor = conn.cursor()        
        psycopg2.extras.execute_values(cursor, queryText, values)
        if doCommit:
            conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print ("Error while running PostgreSQL insert: ", error)

    finally:        
        if(conn):
            cursor.close()
            connPool.putconn(conn)