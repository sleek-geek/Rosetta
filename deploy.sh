#! /bin/bash

reinstall="${1:-0}"
install_zk="${2:-1}"
collection="OAG"

function install_packages()
{
	apt-get update
	apt-get install -y ${1}
}

engpkgs="wget nano openjdk-11-jdk lsof curl git man screen python3-pip jq rsync"
install_packages "${engpkgs}"

if [[ "${reinstall}" -eq '1' ]]
then
	echo "Resetting old environment ..."
	[[ -d "/root/zookeeper-config" ]] && rm -r "/root/zookeeper-config"

	# Uninstalling Solr.
	[[ -f "/etc/init.d/solr" ]] && /etc/init.d/solr stop
	[[ -d "/var/solr" ]] && rm -r "/var/solr"
	rm -r /opt/solr*
	[[ -f "/etc/init.d/solr" ]] && rm "/etc/init.d/solr"

	deluser --remove-home solr
	deluser --group solr
	update-rc.d -f solr remove
	[[ -f "/etc/default/solr.in.sh" ]] && rm "/etc/default/solr.in.sh"

	# Uninstalling Zookeeper.

	if [[ "${install_zk}" -eq "1" ]]
	then
		/root/zookeeper/bin/zkServer.sh stop
		[[ -d "/root/zookeeper" ]] && rm -r "/root/zookeeper"
		[[ -d "/var/log/zookeeper" ]] && rm -r "/var/log/zookeeper"
		[[ -d "/var/lib/zookeeper" ]] && rm -r "/var/lib/zookeeper"
	fi
fi

# Installing Solr

# Checking that JAVA_HOME is setup.

javaDir=`ls /usr/lib/jvm/ | head -n1`
export JAVA_HOME=/usr/lib/jvm/"${javaDir}"

[[ -d "/tmp/solr" ]] && rm -r "/tmp/solr"
mkdir "/tmp/solr"
cd "/tmp/solr/"

#solrVer=`curl https://downloads.apache.org/lucene/solr/ | grep -o "8.[0-9].[0-9]" | tail -n 1`
solrVer=`curl https://downloads.apache.org/lucene/solr/ | grep img | awk -F '>' '{print $3}' | awk -F '/' '{print $1}' | tr -dc '[0-9] | . | \n' | sort -r | head -n 1 | tr -d '\n'`
wget "https://downloads.apache.org/lucene/solr/$solrVer/solr-$solrVer.tgz"

if [[ ! -f "solr-${solrVer}.tgz" ]]
then
	echo "Couldn't fetch Solr. Exiting ..."
	exit 255
fi

tar xzf "solr-$solrVer.tgz" "solr-$solrVer/bin/install_solr_service.sh" --strip-components=2
/tmp/solr/install_solr_service.sh "/tmp/solr/solr-$solrVer.tgz"
/etc/init.d/solr stop

# Configuring Solr

cd /root/
git clone https://gitlab.com/Mo_samy/zookeeper-config.git

cp -R "/root/zookeeper-config" "/opt/solr-$solrVer/server/solr/configsets/"
chown -R solr:solr /opt/solr
echo 'SOLR_HEAP="16384m"' >> "/etc/default/solr.in.sh"

# Installing Zookeeper

zkservers=()
zknodes=""

if [[ "${install_zk}" == 1 ]]
then
	cd "/tmp/solr/"
	wget 'https://downloads.apache.org/zookeeper/zookeeper-3.7.0/apache-zookeeper-3.7.0-bin.tar.gz'
	tar xvf apache-zookeeper-3.7.0-bin.tar.gz
	mv apache-zookeeper-3.7.0-bin "/root/zookeeper"
	mkdir -p "/var/log/zookeeper"

	ip=`hostname -I | tr -d ' ' | tr -d '\n'`
	zkservers+=("${ip}")
	/root/zookeeper-config/genZkConf.sh "${zkservers[@]}"

	# TODO: Add command to update other servers with zk config here.
	/root/zookeeper/bin/zkServer.sh start
fi


# Starting Solr

for i in "${!zkservers[@]}"; do zknodes+="${zkservers[$i]}:2181,"; done

zknodes="${zknodes%?}"

sudo -u solr /opt/solr/bin/solr start -cloud -z ${zknodes}
sudo -u solr /opt/solr/bin/solr zk upconfig -n zookeeper-config -d zookeeper-config -z ${zknodes}

nodesips=`hostname -I | tr -d ' ' | tr -d '\n'`

if [[ "${#nodesips[@]}" == "1" ]]
then
    # Create new collection.
    echo "Creating a new collection ..."
    sudo -u solr /opt/solr/bin/solr create -c ${collection} -n zookeeper-config -p 8983

elif [[ "${#nodesips[@]}" -gt "1" ]]
then
    # TODO: Add a replica from another node.
    :
fi

mkdir -p /tmp/solr/index_files/
ulimit -n 2048
