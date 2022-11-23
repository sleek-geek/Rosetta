#! /bin/bash

status=`curl -s -o /dev/null -I -w '%{http_code}' http://localhost:8983/solr/admin/cores?action=STATUS`

if [ ! "${status}" -eq '200' ]; then
	sudo -u solr /opt/solr/bin/solr stop
	pids=`ps aux | grep solr| grep -v grep | awk '{print $2}'`
	for pid in $pids; do sudo kill -9 $pid; done
	sudo -u solr /opt/solr/bin/solr start -cloud -z localhost:2181
fi
