# couchbase-dump

Helpful scripts for dumping and recreating couchbase buckets and views

Dump all your couchbase buckets and views as javascript files in a directory hierarchy that you can commit to your repo.
Then you can recreate the couchbase buckets and views from previously dumped data.

The scripts use standard python libraries and have no dependencies.

# general usage

Dump your production couchbase like so:
```
dump_couchbase.py Administrator Password couchbase.example.com:8091 couchbase_buckets
```

Then create the couchbase buckets on a new couchbase instance

```
create_couchbase.py Administrator Password couchbase.example.com:8091 couchbase.example.com:8092 couchbase_buckets
```

# docker usage

Given is an example `docker-compose.yml` and `init_couchbase_image.sh` script for creating a new couchbase instance.
The script waits for the couchbase instance to load, as it may take a while, and then initializes it to a default username and password and runs `create_couchbase.py`.

## usage
if you have just ran dump_couchbase.py as describe above, run the following to create your couchbase image:
`docker-compose run init-couchbase`

## cleanup
remove the couchbase and data created by docker-compose
`docker-compose stop; docker-compose rm -f`


# Soon
* Will create a python package so these scripts can be installable via `pip`
* Will create a zip release to be able to wget the zip into your containers
