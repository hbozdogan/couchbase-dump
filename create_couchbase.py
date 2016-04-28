#!/usr/bin/env python
import base64
import os
import json
import sys
import urllib2, urllib

from collections import namedtuple


DDoc = namedtuple('DDoc', ('name', 'design'))

MEMCACHED = 'memcached'
COUCHBASE = 'couchbase'
IGNORE = '.ignore'


E_ALREADY_EXISTS = 'Bucket with given name already exists'


class Connection(object):
    def __init__(self, user, password, api, rest_api):
        self.user = user
        self.password = password
        self.api = api
        self.rest_api = rest_api

    def _req(self, url, method, data, content_type=None):
        """requests package isn't installed by default so we have to do this mess."""
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=data)
        if content_type:
            request.add_header('Content-Type', content_type)

        base64string = base64.encodestring('%s:%s' % (self.user, self.password)).replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)
        request.get_method = lambda: method
        for i in range(3):
            try:
                return opener.open(request)
            except urllib2.HTTPError as e:
                content = e.read()
                if e.code == 500:
                    print 'got error', content
                    continue
                elif E_ALREADY_EXISTS in content:
                    return 'already exists'  # OK
                else:
                    print 'got error', content
                    raise
        raise

    def post(self, path, data):
        url = 'http://%s%s' % (self.api, path)
        self._req(url, 'POST', urllib.urlencode(data))
        # res = requests.post(url,
        #                    data=data,
        #                    auth=(self.user, self.password))

    def put(self, path, data):
        url = 'http://%s%s' % (self.rest_api, path)
        self._req(url, 'PUT', json.dumps(data), 'application/json')
        # res = requests.put(url,
        #                    json=data,
        #                    auth=(self.user, self.password))

    def create_bucket(self, name, type='couchbase'):
        data = {'name': name,
                'bucketType': type,
                'ramQuotaMB': 100,
                'authType': 'sasl',
                'replicaNumber': 0,
                'saslPassword': '',
                'flushEnabled': 1}
        self.post('/pools/default/buckets', data)

    def create_memcache(self, name):
        self.create_bucket(name, 'memcached')

    def create_ddoc(self, bucket, ddoc):
        self.put('/%s/_design/%s' % (bucket, ddoc.name),
                 ddoc.design)


def get_buckets(basedir):
    buckets = {}
    for bucket in os.listdir(basedir):
        ddoc_dir = '%s/%s' % (basedir, bucket)
        ddocs = []
        for ddoc in os.listdir(ddoc_dir):
            views_dir = '%s/%s' % (ddoc_dir, ddoc)
            views = {name.split('.')[0] for name in os.listdir(views_dir) if name != IGNORE}
            design = {'views': {}}
            for view in views:
                design['views'][view] = {}

                map_filename = '%s/%s.map.js' % (views_dir, view)
                if os.path.isfile(map_filename):
                    design['views'][view]['map'] = open(map_filename).read()

                reduce_filename = '%s/%s.reduce.js' % (views_dir, view)
                if os.path.isfile(reduce_filename):
                    design['views'][view]['reduce'] = open(reduce_filename).read()
            ddocs.append(DDoc(ddoc, design))
        buckets[bucket] = ddocs

    return buckets



if __name__ == '__main__':
    if len(sys.argv) < 5:
        print 'usage: %s <user> <pass> <api> <rest_api> <dir=couchbase_buckets/>' % sys.argv[0]
        print 'example \t%s Administrator Password couchbase.example.com:8091 couchbase.example.com:8092 couchbase_buckets' % sys.argv[0]
        sys.exit(1)

    user = sys.argv[1]
    password = sys.argv[2]
    api = sys.argv[3]       # couchbase.example.com:8091
    rest_api = sys.argv[4]  # couchbase.example.com:8092
    basedir = 'couchbase_buckets' if len(sys.argv) < 6 else sys.argv[5]

    conn = Connection(user, password, api, rest_api)

    if COUCHBASE in os.listdir(basedir):
        buckets = get_buckets('%s/%s' % (basedir, COUCHBASE))
        for bucket, ddocs in buckets.items():
            conn.create_bucket(bucket)
            print 'created', bucket
            for ddoc in ddocs:
                conn.create_ddoc(bucket, ddoc)
                print '  * created', ddoc.name

    if MEMCACHED in os.listdir(basedir):
        for bucket in os.listdir('%s/%s' % (basedir, MEMCACHED)):
            conn.create_memcache(bucket)
            print 'created', bucket
