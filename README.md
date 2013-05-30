greader-grab
============

Seesaw script for Archive Team's [Google Reader project](http://www.archiveteam.org/index.php?title=Google_Reader).

You'll find this project on the [Archive Team Warrior](http://tracker.archiveteam.org/greader/).


Use Without Warrior
-------------------------

### Install

#### Ubuntu

Manually:

    $ sudo apt-get update
    $ sudo apt-get install -y build-essential lua5.1 liblua5.1-0-dev python python-setuptools python-dev git-core openssl libssl-dev python-pip rsync gcc make git screen
    $ pip install --user seesaw
    $ git clone https://github.com/ArchiveTeam/greader-grab
    $ cd greader-grab
    $ ./get-wget-lua.sh
    
Automatically:

    $ wget -O - https://gist.github.com/citruspi/5675678/raw/85fb1e43b965b0fcc36b6a5843c5485006108489/greader-grab-ubuntu.sh | bash

#### CentOS / RHEL / Amazon Linux

Manually:

    $ sudo yum install lua lua-devel python-devel python-distribute git openssl-devel rsync gcc make screen
    $ wget https://pypi.python.org/packages/source/p/pip/pip-1.3.1.tar.gz
    $ tar -xzvf pip-1.3.tar.gz
    $ cd pip-1.3
    $ python setup.py install --user
    $ cd ..
    $ ~/.local/bin/pip install --user seesaw
    $ git clone https://github.com/ArchiveTeam/greader-grab
    $ cd greader-grab
    $ ./get-wget-lua.sh
    
Automatically:

    $ wget -O - https://gist.github.com/citruspi/5675678/raw/2e958708063a885abd1e317415e97506dd6fe0f4/greader-grab-other.sh | bash

### Start Downloading

    $ screen ~/.local/bin/run-pipeline --concurrent 2 pipeline.py YOURNICKNAME

### More Options

     $ ~/.local/bin/run-pipeline --help

