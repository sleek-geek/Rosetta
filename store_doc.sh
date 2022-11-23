#! /bin/bash

sudo -u solr "${1}" -c "${2}" -type application/xml -d "${3}"
