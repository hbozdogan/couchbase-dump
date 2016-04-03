#!/bin/sh
# init new couchbase docker instance
# assumes couchbase image is linked as "couchbase"

#set -e
#set -x

HOST="couchbase"
URL="$HOST:$COUCHBASE_PORT_8091_TCP_PORT"
REST_URL="$HOST:$COUCHBASE_PORT_8092_TCP_PORT"

USER=Administrator
PASS=12345678

echo "Waiting for Couchbase to start..."
until $(curl -sIfo /dev/null $URL); do sleep 1; done

couchbase-cli cluster-init -c $URL --cluster-ramsize=1000 --cluster-username=$USER --cluster-password=$PASS

./create_couchbase.py $USER $PASS $URL $REST_URL couchbase_buckets
