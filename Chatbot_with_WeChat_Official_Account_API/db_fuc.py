import pymysql

# connect_to_database: link to the database chatbot_users
def connect_to_database():
    db = pymysql.connect(
        host = 'localhost', 
        user = 'chatbot_admin', 
        password = 'admin', 
        database = 'chatbot_users'
    )
    return db

# search_table_USERS: search from the table USERS and get the result
# - cursor: the cursor point to the database
# - want: the element name user want
# - tag: the tag to identify want
# - id: the value of the tag
def search_table_USERS(cursor, want, tag, id):
    sql = "select " + want + " from USERS" + " where " + tag + "= '" + id +"'"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# insert_into_USERS: insert new list into table USERS
# - db: the database we use
# - cursor: the cursor point to the database
# - name: value of NAME column
# - last_text: value of LAST_TEXT column
# - rasa_server: value of RASA_SERVER column
def insert_into_USERS(db, cursor, name, last_text, rasa_server):
    sql = "insert into USERS( \
            NAME, LAST_TEXT, RASA_SERVER) \
            VALUES ('"+str(name)+"',"+str(last_text)+","+str(rasa_server)+")"
    cursor.execute(sql)
    db.commit()

# update_set_USERS: update LAST_TEXT value for existing record
# - db: the database we use
# - cursor: the cursor point to the database
# - name: value of NAME column
# - last_text: value of LAST_TEXT column
def update_set_USERS(db, cursor, name, last_text):
    sql = "update USERS set LAST_TEXT = "+str(last_text)+" where NAME = '"+str(name)+"'"
    cursor.execute(sql)
    db.commit()

# delete_early_USERS: evict the timeout users
# - db: the database we use
# - cursor: the cursor point to the database
# - time_bond: the earliest time value of LAST_TEXT,
#               if the record's LAST_TEXT is less than
#               it, then the user should be evicted
def delete_early_USERS(db, cursor, time_bond):
    sql = "delete from USERS where LAST_TEXT < "+str(time_bond)
    cursor.execute(sql)
    db.commit()

# find_suitable_SERVERS: find the rasa bot server ip for the new coming user
# - cursor: the cursor point to the database
# - n: the number of rasa bot servers
def find_suitable_SERVERS(cursor, n):
    min_count = 9223372036854775807
    target = 1
    for i in range(1,n):
        sql1 = "select COUNT(*) from USERS where RASA_SERVER = "+str(i)
        cursor.execute(sql1)
        result = cursor.fetchall()
        count = result[0][0]
        if count < min_count:
            min_count = count
            target = i
        if not count:
            min_count = count
            target = i
            break
    return target