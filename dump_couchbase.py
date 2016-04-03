#!/usr/bin/env python
import requests
import sys
from collections import namedtuple


Bucket = namedtuple('Bucket', ('name', 'type', 'ddocs_uri'))
View = namedtuple('View', ('name', 'map', 'reduce'))
DDoc = namedtuple('DDoc', ('name', 'views'))

MEMCACHED = 'memcached'
COUCHBASE = 'couchbase'


class Connection(object):
    def __init__(self, user, password, host):
        self.user = user
        self.password = password
        self.host = host

    def _req(self, path):
        return requests.get('http://%s%s' % (self.host, path),
                            auth=(self.user, self.password)).json()

    def get_buckets(self):
        res = self._req('/pools/default/buckets')
        return [Bucket(b['name'], b['bucketType'], b['ddocs']['uri']) for b in res]

    def get_ddocs(self, bucket):
        rows = self._req(bucket.ddocs_uri)['rows']
        res = []
        for row in rows:
            doc_name = row['doc']['meta']['id']
            views = [View(view_name, view.get('map'), view.get('reduce'))
                     for view_name, view
                     in row['doc']['json']['views'].items()]
            res.append(DDoc(doc_name, views))
        return res


def mkdir_p(path):
    import errno
    import os
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def create_dirs(data, basedir='couchbase_buckets'):
    for bucket, ddocs in data.items():
        if bucket.type == MEMCACHED:
            dirname = '%s/memcached/%s' % (basedir, bucket.name)
            mkdir_p(dirname)
            continue
        # for couchbase buckets
        for ddoc in ddocs:
            dirname = '%s/couchbase/%s/%s' % (basedir, bucket.name, ddoc.name.replace('_design/', ''))
            mkdir_p(dirname)
            for view in ddoc.views:
                if view.map:
                    filename = '%s/%s.map.js' % (dirname, view.name)
                    with open(filename, 'w') as f:
                        f.write(view.map)
                if view.reduce:
                    filename = '%s/%s.reduce.js' % (dirname, view.name)
                    with open(filename, 'w') as f:
                        f.write(view.reduce)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'usage: %s <user> <pass> <host> <output-dir=couchbase_buckets/>' % sys.argv[0]
        sys.exit(1)

    user = sys.argv[1]
    password = sys.argv[2]
    host = sys.argv[3]  # couchbase.example.com:8091
    basedir = 'couchbase_buckets' if len(sys.argv) < 5 else sys.argv[4]

    conn = Connection(user, password, host)
    buckets = conn.get_buckets()
    res = {}
    for bucket in buckets:
        if bucket.type != MEMCACHED:
            res[bucket] = conn.get_ddocs(bucket)
        else:
            res[bucket] = []

    create_dirs(res, basedir)

    print 'created %s' % basedir
