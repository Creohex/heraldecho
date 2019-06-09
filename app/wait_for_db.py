import common, time

while True:
    try:
        common.get_connection()
        print("successfully connected to DB")
        break
    except:
        print("couldn't connect to DB, waiting...")
        time.sleep(1)

time.sleep(1)
