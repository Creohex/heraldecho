#!/bin/bash
echo "starting server..."

# wait for db to be accessible
python ./wait_for_db.py

# start app
python ./app.py
