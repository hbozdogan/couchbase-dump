# couchbase-dump

Helpful scripts for dumping and recreating couchbase buckets and views

Dump all your couchbase buckets and views as javascript files in a directory hierarchy that you can commit to your repo.
Then you can recreate the couchbase buckets and views from previously dumped data.

# usage

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
