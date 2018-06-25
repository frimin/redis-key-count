#!/usr/bin/env bash

redis_port=7777
key_file=all_keys
out_file=output.log

# launch redis server
redis-server --port $redis_port --daemonize yes || exit 255

# add some test content
redis-cli -p $redis_port MSET module_a:{1..100}
redis-cli -p $redis_port MSET module_b:{1..200}
redis-cli -p $redis_port MSET module_c:{1..20}
redis-cli -p $redis_port HMSET module_d long_str_1234567890123456789:{1..500}
redis-cli -p $redis_port ZADD module_e {1..1000}
redis-cli -p $redis_port LPUSH module_f str_123456:{1..200}

redis-cli -p $redis_port keys '*' > $key_file

echo ""

python redis-key-count.py -p "$redis_port" --key-num "$(wc -l < $key_file)" --key-file "$key_file" --output "$out_file";

redis-cli -p $redis_port SHUTDOWN NOSAVE

echo "shutdown redis."
echo ""

if [[ -a "$out_file" ]]; then
    cat $out_file
    /bin/rm -f $out_file
fi

[[ -a $key_file ]] && /bin/rm -f $key_file

