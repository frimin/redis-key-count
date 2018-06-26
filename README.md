# Redis-Key-Count

A simple Python script for count all key bytes from redis.

It can't give you accurate memory conditions, but you can get some important information from it.

## INSTALL

	git clone https://github.com/frimin/redis-key-count
	cd redis-key-count && git submodule init && git submodule update

## USAGE 

First export all redis key to file (if you want to analyze a large redis instacne, it's too slowly for each time):

	redis-cli -p 7777 keys '*' > all_keys

Put `all_keys` file to script for count all key and key content bytes (similar bytes), you need give `all_keys` file lines to option `--key-num` for print progress:

	python redis-key-count.py \
		-p 7777 \
		--key-num "$(wc -l < $key_file)" \
		--key-file "$key_file"
	
Get results from file `redis_key_count.log`:

	module_d 0.02MB 15900B 60.929%
	module_e 0.00MB 3901B 14.949%
	module_f 0.00MB 2700B 10.346%
	module_b 0.00MB 2292B 8.783%
	module_a 0.00MB 1092B 4.185%
	module_c 0.00MB 211B 0.809%
	
You can also read test script **test.bash**.
	
## LICENSE

MIT