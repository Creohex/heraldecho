#!/bin/bash
# wait for host
#/bin/bash /opt/scripts/wait-for-it.sh db:5432 --timeout=2 -- echo "db is up"

# migrate:
./flyway migrate -connectRetries=60 -user=$PGUSER -password=$PGPASSWORD \
    -url="jdbc:postgresql://db:5432/${PGDATABASE}" -locations='filesystem:/opt/migrations'
