#!/bin/bash/env python
# -*- coding:utf-8 -*-

import sys
import redis
import time
from optparse import OptionParser

STEP_SIZE = 10000

all_type_size = {}


def query_list(keys):
    pipe = r.pipeline()

    for key in keys:
        pipe.type(key)

    types = pipe.execute()

    pipe = r.pipeline()

    for i, key in enumerate(keys):
        type = types[i]

        if type == 'string':
            pipe.get(key)
        elif type == 'hash':
            pipe.hgetall(key)
        elif type == 'set':
            pipe.smembers(key)
        elif type == 'zset':
            pipe.zrange(key, 0, -1, withscores=True)
        elif type == "list":
            pipe.lrange(key, 0, -1)
        else:
            pipe.type(key)  # do something
            print 'ignore key: %s typeis %s' % (key, type)

    rt = pipe.execute()

    for i, key in enumerate(keys):
        type = types[i]
        value = rt[i]
        logic_type = key.split(':')[0]

        if logic_type not in all_type_size:
            all_type_size[logic_type] = 0

        all_type_size[logic_type] += len(key)  # record key length

        if type == "string":
            all_type_size[logic_type] += len(value)
        elif type == "hash":
            all_type_size[logic_type] += len(''.join(value.keys())) + len(''.join(value.values()))
        elif type == "set":
            all_type_size[logic_type] += len(''.join(value))
        elif type == "zset":
            len_count = 0
            for member, score in value:
                len_count += len(member) + len(str(score))
            all_type_size[logic_type] += len_count
        elif type == "list":
            all_type_size[logic_type] += len(''.join(value))
        else:
            print "ignore key: %s" % key


if __name__ == '__main__':
    parser = OptionParser(add_help_option=False)

    parser.add_option("-h", action="store", type="string", metavar="REDIS_HOST", dest="redis_host")
    parser.add_option("-p", action="store", type="string", metavar="REDIS_PORT", dest="redis_port")
    parser.add_option("-a", action="store", type="string", metavar="REDIS_AUTH", dest="redis_auth")

    parser.add_option("--key-num", action="store", type="int", metavar="KEY_NUM", dest="key_num")
    parser.add_option("--key-file", action="store", type="string", metavar="FILE", dest="key_file")
    parser.add_option("--output", action="store", type="string", metavar="FILE", dest="output_file")

    (options, args) = parser.parse_args(sys.argv[1:])

    r = redis.Redis(host=options.redis_host, port=int(options.redis_port), password=options.redis_auth, db=0)

    total_line = options.key_num

    with open(options.key_file, 'r') as f:
        keys = []
        i = 0
        step = 0

        startTime = time.time()

        for key in f:
            key = key.strip()

            i += 1
            step += 1
            keys.append(key)

            if step >= STEP_SIZE:
                step = 0
                endTime = time.time()
                sec = endTime - startTime

                progress = float(i) / total_line

                speed = sec/progress

                time_remaining = (1 - progress) * speed

                print "[ %.4f%% ] current = %d, total = %d，%d seconds usage, speed: %d sec per 1%%，time remaining %d sec." % \
                      (progress * 100, i, total_line, sec, speed / 100, time_remaining)
                query_list(keys)
                keys = []

        if len(keys) > 0:
            endTime = time.time()
            sec = endTime - startTime
            print "[-] last step: current = %d, total = %d，%d seconds usage" % (i, total_line, sec)
            query_list(keys)
            keys = []

        endTime = time.time()

        print "%d seconds usage." % (endTime - startTime)

    if options.output_file is None:
        options.output_file = 'redis_key_count.log'

    with open(options.output_file, 'wb') as f:
        total_bytes = 0

        for byte in all_type_size.values():
            total_bytes += byte

        for k, v in sorted(all_type_size.items(), key=lambda kv: kv[1], reverse=True):
            f.write('%s %.2fMB %sB %.3f%%\n' % (k, float(v)/1024/1024, v, float(v)/total_bytes * 100))
