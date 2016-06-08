#!/bin/sh
# init new couchbase docker instance
# assumes couchbase image is linked as "couchbase"

#set -e
#set -x

URL="couchbase:8091"
REST_URL="couchbase:8092"

USER=Administrator
PASS=12345678

printf "Waiting for Couchbase to start"
until $(curl -sIfo /dev/null $URL); do sleep 1; printf "."; done
echo

# the following line is a PATCH for couchbase:4.1.0 bug on OSX which causes the error:
# ERROR: unable to setup services (400) Bad Request
# ["insufficient memory to satisfy memory quota for the services (requested quota is 4519MB, maximum allowed quota for the node is 1601MB)"]
curl -s -u $USER:$PASS -X POST http://$URL/pools/default -d memoryQuota=500

couchbase-cli cluster-init -c $URL --cluster-ramsize=1000 --cluster-username=$USER --cluster-password=$PASS

./create_couchbase.py $USER $PASS $URL $REST_URL couchbase_buckets
