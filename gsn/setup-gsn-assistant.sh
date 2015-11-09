#!/bin/sh

#set -e -x
mkdir -p ~/vagrant
chmod 777 ~/vagrant
echo "Starting cloud-init..." >> ~/vagrant/install.log

#make_sudo.sh
read -d '' String0 <<"EOF"
#!/bin/sh
# Add gsn to sudoers list if not present
grep gsn /etc/sudoers
if [ $? -eq 1 ]
then
        echo "gsn ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers
fi
EOF

echo "${String0}" >> ~/vagrant/make_sudo.sh


#restart.sh
read -d '' Script <<"EOF"
#!/bin/bash
file="/root/vagrant/bootflag"
if [ -f "$file" ]
then
    su - postgres -c '/usr/pgsql-9.4/bin/pg_ctl  -D /opt/gsn_data -l logfile start'
    if [ $? -eq 0 ]
    then
        echo "Started postgres service" >> /root/vagrant/install.log
    fi
    echo "Started postgres service" >> /root/vagrant/install.log
    rm -rf /opt/gsn/gsn-assistant-1.0/RUNNING_PID
    su - gsn -c '/bin/bash -c "
    cd /opt/gsn/gsn
    ant gsn
    export GSN_HOME=/opt/gsn/gsn
    export GSN_DATA_DIR=/opt/gsn/gsn/data
    cd ..
    nohup gsn-assistant-1.0/bin/gsn-assistant -DapplyEvolutions.default=true &"'
fi
EOF

echo "${Script}" >> ~/vagrant/restart.sh

echo  "sh /root/vagrant/restart.sh" >> /etc/rc.local



#yum-update.sh
read -d '' String <<"EOF"
#!/bin/bash
# Required for Postgres installation
sed -i \"19i exclude=postgresql*\" /etc/yum.repos.d/CentOS-Base.repo
sed -i \"28i exclude=postgresql*\" /etc/yum.repos.d/CentOS-Base.repo
EOF

echo "${String}" >> ~/vagrant/yum-update.sh

#setup-gsn-assistant.sh
read -d '' String8 <<"EOF"
#!/bin/bash
yum install  -y wget
if [ $? -eq 0 ]
then
    echo "Installed wget" >> ~/gsn-assist.log
fi
su - gsn
cd /opt/gsn/
wget cs.ucsb.edu/~kylejorgensen/gsn-assistant-1.0.tgz
if [ $? -eq 0 ]
then
    echo "gsn assistant fetched" >> ~/gsn-assist.log
fi

tar -zxvf gsn-assistant-1.0.tgz
if [ $? -eq 0 ]
then
    echo "gsn assistant untarred" >> ~/gsn-assist.log
fi

chown gsn:gsn -R /opt/gsn/gsn-assistant-1.0
su - gsn -c '/bin/bash -c "
export GSN_HOME=/opt/gsn/gsn
export GSN_DATA_DIR=${GSN_HOME}/data

nohup gsn-assistant-1.0/bin/gsn-assistant -DapplyEvolutions.default=true &"'
EOF

echo "${String8}" >> ~/vagrant/startgsn-assistant.sh



#init.pp
read -d '' String1 <<"EOF"
package { "vim-enhanced":
          ensure => installed,
}

package { "java-1.7.0-openjdk-devel":
                  ensure => installed,
}


user { 'gsn':
        ensure => present,
        password => '$6$50Ie13fe$PB7qhEATOWu4ugCEplwE271eZ9As3SJm9sprDIxPDYDxDcJ1/mtpMnxUbU5gTBnd9jo85wBgdWQMkDv01pgHd/',
        shell => "/bin/bash",
        home => "/home/gsn",
        managehome => true,
}

exec { "ec2-sudo":
        command => "/bin/sh ~/vagrant/make_sudo.sh",
        logoutput => true,
        require => [User["gsn"]],
}


file { "/root/vagrant/bootflag" :
        ensure => "present",
     }

file { "/root/.m2" :
	  ensure => "directory",
	  owner => "root",
}	  

file { "/root/.m2/repository":
       ensure => "link",
       owner  => "root",
       target => "/opt/gsn/gsn-jars/repository",
       require => [Exec["git-jar-clone"], File["/root/.m2"]] ,
}

exec { "git-jar-clone":
                command => "/usr/bin/git clone https://github.com/MAYHEM-Lab/gsn-jars.git",
                creates => "/opt/gsn/gsn-jars",
		cwd	=> "/opt/gsn",
                logoutput => true,
                user => 'gsn',
                require => [Package["git"], Class["git"], User["gsn"]],
}

package {"ant":
             ensure => installed,
             require => [Package["java-1.7.0-openjdk-devel"], Exec["git-jar-clone"]],
}

include git

class git {
        package { "git":
                  ensure => installed,
        }
        file { "/home/gsn" :
                ensure => present,
		    require => User["gsn"],
        }

        file { "/opt/gsn":
            ensure => "directory",
            owner => "gsn",
            mode => "777",
        }   

        exec { "git-clone":
                command => "/usr/bin/git clone -b gsn-assistant-compatible https://github.com/UCSB-CS-RACELab/gsn.git gsn",
		cwd     => "/opt/gsn/",
                creates => "/opt/gsn/gsn",
                user => 'gsn',
                require => [Package["git"], File["/opt/gsn/"], User["gsn"]],
        }
}



package {
                "pgdg-centos94":
                provider => "rpm",
                source => "http://yum.postgresql.org/9.4/redhat/rhel-6-x86_64/pgdg-centos94-9.4-1.noarch.rpm",
                ensure => installed,
}

package { "postgresql94-server":
                   ensure => installed,
                   require => Package["pgdg-centos94"],
}

file { "/opt/gsn_data":
    ensure => "directory",
    owner  => "postgres",
    mode   => 777,
}

exec { "initdb":
        command => "su - postgres -c '/usr/pgsql-9.4/bin/initdb  -D /opt/gsn_data'",
        path => [ "/usr/local/bin/", "/bin/", "/usr/bin/", "/sbin" ],
        require => [Package["postgresql94-server"], File["/opt/gsn_data"]],
}


file { "/opt/gsn_data/pg_hba.conf":
        ensure => present,
    source => "/root/vagrant/pg_hba.conf",
        owner => "postgres",
        require => [Package["postgresql94-server"], Exec["initdb"]],
}

file { "/opt/gsn_data/postgresql.conf":
        ensure => present,
    source => "/root/vagrant/postgresql.conf",
        owner => "postgres",
        require => [Package["postgresql94-server"], Exec["initdb"]],
}

exec { "postgresql-9.4":
      command => "su - postgres -c '/usr/pgsql-9.4/bin/pg_ctl  -D /opt/gsn_data -l logfile start'",
          path => [ "/usr/local/bin/", "/bin/", "/usr/bin/", "/sbin" ],
      require   => [Package["postgresql94-server"], File["/opt/gsn_data/pg_hba.conf"], File["/opt/gsn_data/postgresql.conf"]],
}

exec { "wait_for_postgre_to_start":
        command => "sleep 5",
        path => [ "/usr/local/bin/", "/bin/", "/usr/bin/", "/sbin" ],
        require => [Exec["postgresql-9.4"]],
}

#create postgres db
exec { "setup-postgres":
        command => "/bin/sh /root/vagrant/setup-postgres.sh",
	logoutput => true,
        require => [Package["postgresql94-server"], Exec["postgresql-9.4"], Exec["wait_for_postgre_to_start"]],
}

#start GSN
file { "/opt/gsn/gsn/conf/gsn.xml":
        ensure => present,
        source => "/root/vagrant/gsn.xml",
        owner => "gsn",
        require => [Package["postgresql94-server"], Exec["setup-postgres"], Class["git"], User["gsn"]],
}



exec { "ant":
        cwd     => "/opt/gsn/gsn",
    command => "/usr/bin/ant",
        timeout => 6000,
        logoutput => true,
        user => 'gsn',
    require => [Package['ant'], Exec["setup-postgres"], File["/opt/gsn/gsn/conf/gsn.xml"], Exec["git-jar-clone"]],
}

exec { "ant-gsn":
        cwd     => "/opt/gsn/gsn",
        command => "/usr/bin/ant gsn",
        logoutput => true,
        user => 'gsn',
    require => [Package["postgresql94-server"], Class["git"], Exec['ant']],
}


service { "iptables":
      ensure    => "stopped",
      enable    => false,
          require => [Exec["ant-gsn"]]
}

exec { "gsn-assist":
        command => "/bin/sh /root/vagrant/startgsn-assistant.sh",
        logoutput => true,
        require => [Exec['ant-gsn']],
}


EOF
echo "${String1}" >> ~/vagrant/init.pp

#setup-postgres.sh
read -d '' String2 <<"EOF"
#!/bin/bash

export JAVA_HOME=/usr/lib/jvm/java          
echo "export JAVA_HOME=/usr/lib/jvm/java" >> ~/.bashrc
echo "export PGDATA=/opt/gsn_data" >> ~/.bashrc
source ~/.bashrc

#psql -U postgres createdb gsn
#psql -U postgres -c "psql -c \"CREATE USER gsn WITH PASSWORD 'gsnpassword';\""

su - postgres -c "psql -c \\"CREATE USER gsn WITH PASSWORD 'gsnpassword';\\""
su - postgres -c "createdb gsn" 
EOF

echo "${String2}" >> ~/vagrant/setup-postgres.sh

#gsn.xml
read -d '' String3 <<"EOF"
<sensor-server>
   <name>GSN Server</name>
   <author>GSN Development Team.</author>
   <email>my email address</email>
   <description>Not Provided</description>
   <port>22001</port>
   <zmq-enable>false</zmq-enable>
   <zmqproxy>22022</zmqproxy>
   <zmqmeta>22023</zmqmeta>
   <access-control>true</access-control>
   <storage user="gsn" password="gsnpassword" driver="org.postgresql.Driver" url="jdbc:postgresql://localhost/gsn" /> -->
</sensor-server>
EOF

echo "${String3}" >> ~/vagrant/gsn.xml

#pg_hba.conf
read -d '' String4 <<"EOF"
# PostgreSQL Client Authentication Configuration File
# ===================================================
#
# Refer to the "Client Authentication" section in the PostgreSQL
# documentation for a complete description of this file.  A short
# synopsis follows.
#
# This file controls: which hosts are allowed to connect, how clients
# are authenticated, which PostgreSQL user names they can use, which
# databases they can access.  Records take one of these forms:
#
# local      DATABASE  USER  METHOD  [OPTIONS]
# host       DATABASE  USER  ADDRESS  METHOD  [OPTIONS]
# hostssl    DATABASE  USER  ADDRESS  METHOD  [OPTIONS]
# hostnossl  DATABASE  USER  ADDRESS  METHOD  [OPTIONS]
#
# (The uppercase items must be replaced by actual values.)
#
# The first field is the connection type: "local" is a Unix-domain
# socket, "host" is either a plain or SSL-encrypted TCP/IP socket,
# "hostssl" is an SSL-encrypted TCP/IP socket, and "hostnossl" is a
# plain TCP/IP socket.
#
# DATABASE can be "all", "sameuser", "samerole", "replication", a
# database name, or a comma-separated list thereof. The "all"
# keyword does not match "replication". Access to replication
# must be enabled in a separate record (see example below).
#
# USER can be "all", a user name, a group name prefixed with "+", or a
# comma-separated list thereof.  In both the DATABASE and USER fields
# you can also write a file name prefixed with "@" to include names
# from a separate file.
#
# ADDRESS specifies the set of hosts the record matches.  It can be a
# host name, or it is made up of an IP address and a CIDR mask that is
# an integer (between 0 and 32 (IPv4) or 128 (IPv6) inclusive) that
# specifies the number of significant bits in the mask.  A host name
# that starts with a dot (.) matches a suffix of the actual host name.
# Alternatively, you can write an IP address and netmask in separate
# columns to specify the set of hosts.  Instead of a CIDR-address, you
# can write "samehost" to match any of the server's own IP addresses,
# or "samenet" to match any address in any subnet that the server is
# directly connected to.
#
# METHOD can be "trust", "reject", "md5", "password", "gss", "sspi",
# "ident", "peer", "pam", "ldap", "radius" or "cert".  Note that
# "password" sends passwords in clear text; "md5" is preferred since
# it sends encrypted passwords.
#
# OPTIONS are a set of options for the authentication in the format
# NAME=VALUE.  The available options depend on the different
# authentication methods -- refer to the "Client Authentication"
# section in the documentation for a list of which options are
# available for which authentication methods.
#
# Database and user names containing spaces, commas, quotes and other
# special characters must be quoted.  Quoting one of the keywords
# "all", "sameuser", "samerole" or "replication" makes the name lose
# its special character, and just match a database or username with
# that name.
#
# This file is read on server startup and when the postmaster receives
# a SIGHUP signal.  If you edit the file on a running system, you have
# to SIGHUP the postmaster for the changes to take effect.  You can
# use "pg_ctl reload" to do that.

# Put your actual configuration here
# ----------------------------------
#
# If you want to allow non-local connections, you need to add more
# "host" records.  In that case you will also need to make PostgreSQL
# listen on a non-local interface via the listen_addresses
# configuration parameter, or via the -i or -h command line switches.



# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             0.0.0.0/0           md5 
# IPv6 local connections:
host    all             all             ::1/128                 trust
# Allow replication connections from localhost, by a user with the
# replication privilege.
#local   replication     postgres                                peer
#host    replication     postgres        127.0.0.1/32            ident
#host    replication     postgres        ::1/128                 ident
#local	all	all	trust
#host	all	127.0.0.1/32	trust

EOF

echo "${String4}" >> ~/vagrant/pg_hba.conf

#postgresql.conf
read -d '' String6 <<"EOF"

# -----------------------------
# PostgreSQL configuration file
# -----------------------------
#
# This file consists of lines of the form:
#
#   name = value
#
# (The "=" is optional.)  Whitespace may be used.  Comments are introduced with
# "#" anywhere on a line.  The complete list of parameter names and allowed
# values can be found in the PostgreSQL documentation.
listen_addresses = '*'
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix
log_destination = 'stderr'      # Valid values are combinations of
logging_collector = on          # Enable capturing of stderr and csvlog
log_directory = 'pg_log'        # directory where log files are written,
log_filename = 'postgresql-%a.log'  # log file name pattern,
#log_file_mode = 0600           # creation mode for log files,
log_truncate_on_rotation = on       # If on, an existing log file with the
log_rotation_age = 1d           # Automatic rotation of logfiles will
log_rotation_size = 0           # Automatic rotation of logfiles will

log_line_prefix = '< %m >'
log_timezone = 'UTC'
datestyle = 'iso, mdy'
timezone = 'UTC'
lc_messages = 'en_US.UTF-8'         # locale for system error message
                    # strings
lc_monetary = 'en_US.UTF-8'         # locale for monetary formatting
lc_numeric = 'en_US.UTF-8'          # locale for number formatting
lc_time = 'en_US.UTF-8'             # locale for time formatting

# default configuration for text search
default_text_search_config = 'pg_catalog.english'

EOF

echo "${String6}" >> ~/vagrant/postgresql.conf


echo "Required files written to /root/vagrant" >> ~/vagrant/install.log

if [ -f ~/vagrant/yum-update.sh ]
then
    chmod +x ~/vagrant/yum-update.sh
fi




if [ -f ~/vagrant/setup-postgres.sh ]
then
    chmod +x ~/vagrant/setup-postgres.sh
fi

# strang that /opt is missing in the cloud image
mkdir -p /opt
chmod 777 /opt
if [ $? -eq 0 ]
then
   echo "opt done proeprly ..." >> ~/vagrant/install.log
fi
chmod 777 /tmp
	
echo "changing permissions of certain directories" >> ~/vagrant/install.log

#sh /root/vagrant/yum-update.sh
setenforce 0
yum update -y 
echo "yum update done..." >> ~/vagrant/install.log
rpm -ivh http://yum.puppetlabs.com/puppetlabs-release-el-6.noarch.rpm
yum install -y puppet
if [ $? -eq 0 ]
then
  echo "puppet installed succesfully" >> ~/vagrant/install.log
fi
echo "puppet installed ..?" >> ~/vagrant/install.log
if [ -f /usr/bin/puppet ]
then
   echo "puppet installed..." >> ~/vagrant/install.log
   echo "Apply puppet" >> ~/vagrant/install.log	
   puppet apply ~/vagrant/init.pp 2>&1 >> ~/vagrant/puppet.log
   echo "puppet done" >> ~/vagrant/install.log	
fi


echo "All installtation done.. Puppet might be in progress" >> ~/vagrant/install.log



