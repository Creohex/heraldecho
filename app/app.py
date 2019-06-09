import os, time, datetime, requests, re, json, psycopg2, random, traceback



required_env_vars = ['PGHOST', 'PGUSER', 'PGPORT', 'PGPASSWORD', 'PGDATABASE', 'DEBUG']
missing_variables = [_ for _ in required_env_vars if _ not in os.environ.keys()]
if len(missing_variables) > 0:
    raise Exception("Error: missing required variables: %s" % missing_variables)


CYCLE_TIMEOUT = 41
DEBUG = os.environ['DEBUG'] == "true"


def debug(msg):
    if DEBUG:
        print("%s: %s" % (datetime.datetime.now(), msg))

def get_env_vars():
    """ Return dict containing required environemnt variables """
    missing_vars = [_ for _ in required_env_vars if _ not in os.environ.keys()]
    if len(missing_vars) > 0:
        raise Exception("Error: missing required variables: %s" 
                        % ', '.join(missing_vars))
    else:
        return {key: os.environ[key] for key in required_env_vars}

def get_connection():
    """ Return connection based on current environment variables """
    params = get_env_vars()
    return psycopg2.connect(host=params['PGHOST'], port=params['PGPORT'], 
                user=params['PGUSER'], password=params['PGPASSWORD'], 
                database=params['PGDATABASE'])

def query_db(query_str):
    """ Execute db query and return results """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query_str)
                conn.commit()
                try:
                    return cursor.fetchall()
                except Exception:
                    return []
    except psycopg2.DatabaseError as e:
        raise Exception("query_db error:\n%s" % str(e))


class Hook(object):
    def __init__(self, hook_id, token_id, day, announce_at, announced_today):
        self.hook_id = hook_id
        self.token_id = token_id
        self.day = int(day)
        self.announce_at = [int(_) for _ in re.split(r' ', announce_at)]
        self.announced_today = announced_today

    def __str__(self):
        return "%s, %s, %s, %s, %s" \
               % (self.hook_id, self.token_id, self.day, self.announce_at, self.announced_today)
    
    def id_short(self):
        return self.hook_id if len(self.hook_id) <= 5 else "~%s" % self.hook_id[-5:]

    def get_link(self):
        return "https://discordapp.com/api/webhooks/%s/%s" % (self.hook_id, self.token_id)

    def set_announce_time(self, day, announce_at):
        query_db("UPDATE announcer "
            "SET day = %s, announce_at = '%s', announced_today = 'no' "
            "WHERE hook_id = '%s'" % (day, announce_at, self.hook_id))

    def announce(self, message):
        try:
            requests.post(url=self.get_link(), params={}, json={"content": message})
            query_db("UPDATE announcer SET announced_today = 'yes' WHERE hook_id = '%s'"
                % self.hook_id)

        except Exception as e:
            print("announce exception: %s" % str(e))
    
    @classmethod
    def get_hooks(cls):
        return [Hook(hook_id, hook_token, day, announce_at, announced_today)
            for hook_id, hook_token, day, announce_at, announced_today
            in query_db("SELECT hook_id, token, day, announce_at, announced_today FROM announcer")]

class Message(object):
    def __init__(self, msg_id, msg):
        self.msg_id = msg_id
        self.message = msg
    
    @classmethod
    def get_messages(cls):
        return [Message(m[0], m[1]) for m in query_db("SELECT id, msg FROM message")]

# cycle
print("starting...")

while True:
    # do stuff
    try:
        hooks = Hook.get_hooks()
        messages = Message.get_messages()
        debug("%s hooks found" % len(hooks))
        for hook in hooks:
            debug("current hook: %s" % hook.id_short())
            d = datetime.datetime.now().day
            if d != hook.day:
                rh = random.randint((12 if datetime.datetime.today().weekday() in [6, 7] else 18), 23)
                rm = random.randint(0, 59)
                debug("^ hasn't announced today yet, setting announce time at: %s:%s" % (rh, rm))
                hook.set_announce_time(d, "%s %s" % (rh, rm))
            elif d == hook.day and hook.announced_today != 'yes':
                rh, rm = hook.announce_at[0], hook.announce_at[1]
                h, m = datetime.datetime.now().hour + 3, datetime.datetime.now().minute
                diff = ((h - rh) * 60) + (m - rm)
                if diff >= 0:
                    debug("^ announcing now")
                    msg = messages[random.randint(0, len(messages) - 1)].message
                    hook.announce(msg)
    except Exception as e:
        traceback.print_exc()
    
    # wait
    time.sleep(CYCLE_TIMEOUT)

print("exiting...")
