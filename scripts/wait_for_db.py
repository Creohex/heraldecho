import app, time

while True:
    try:
        app.get_connection()
        app.query_db("SELECT 1")
        print("successfully connected to DB")
        break
    except:
        print("couldn't connect to DB, waiting...")
        time.sleep(1)

time.sleep(1)
