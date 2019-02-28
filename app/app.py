import os, time, datetime, requests, re, json, pymysql, random

# env variables:
required_variables = [
    'db_host',
    'db_username',
    'db_password'
]
missing_variables = [_ for _ in required_variables if _ not in os.environ.keys()]
if len(missing_variables) > 0:
    raise Exception("Error: missing required variables: %s" % missing_variables)

db_host = os.environ['db_host']
db_db = 'deeprock'
db_user = os.environ['db_username']
db_pass = os.environ['db_password']
cycle_timeout = 2

# functions:
def db_connector():
    return pymysql.connect(host=db_host, port=3306, user=db_user, passwd=db_pass, db=db_db)

def query_db(query):
    """ queries local db and returns cursor containing data """
    conn = db_connector()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.close()
    return cursor

def query_db_commit(query):
    """ queries local db, commits any changes and returns cursor containing data (or changes) """
    conn = db_connector()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()
    return cursor


class Hook():
    def __init__(self, hook_id, token_id, day, announced_today):
        self.hook_id = hook_id
        self.token_id = token_id
        self.day = day
        self.announced_today = announced_today

    def __str__(self):
        return "%s, %s, %s, %s" % (self.hook_id, self.token_id, self.day, self.announced_today)

    def get_link(self):
        return "https://discordapp.com/api/webhooks/%s/%s" % (self.hook_id, self.token_id)

    def announce(self, message):
        try:
            requests.post(url=self.get_link(), params={}, json=message)
            query_db_commit("UPDATE announcer SET announced_today = 'yes' WHERE hook_id = '%s'" % self.hook_id)
        except Exception as e:
            print("announce exception: %s" % str(e))

class Msg():
    def __init__(self, m):
        self.message = m

# cycle
print("starting...")
while True:
    # do stuff
    try:
        hooks = [Hook(hook_id, hook_token, int(day), announced_today) for hook_id, hook_token, day, announced_today
                 in query_db("SELECT hook_id, token, day, announced_today FROM announcer")]
        messages = [Msg(m) for m in query_db("SELECT msg FROM message")]

        for hook in hooks:
            if hook.announced_today == 'yes' and datetime.datetime.now().day != hook.day:
                query_db_commit("UPDATE announcer SET announced_today = 'no' WHERE hook_id = '%s'" % hook.hook_id)
            else:
                h = random.randint(10, 23)
                m = random.randint(0, 59)
                if datetime.datetime.now().hour >= h and datetime.datetime.now().minute >= m:
                    msg = messages[random.randint(0, len(messages) - 1)].message
                    hook.announce(msg)
    except Exception as e:
        print("Exception: %s" % str(e))
    
    # wait
    time.sleep(cycle_timeout)
