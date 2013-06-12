greader-grab
============

Seesaw script for Archive Team's Google Reader grab: http://www.archiveteam.org/index.php?title=Google_Reader

You'll find this project on the Archive Team Warrior: http://tracker.archiveteam.org/greader/

If you are not familiar with Archive Team grabs: this program repeatedly grabs a work item
containing 200 feed URLs from the tracker, downloads them using Google Reader's
anonymous API, then uploads the compressed archive (average ~5MB) to a collection
server.  You do not need more than ~2GB of free disk space to run this job.

The IRC channel for this grab is #donereading on efnet.


Running without a warrior
-------------------------

To run this outside the warrior:

(Ubuntu / Debian 7)

    sudo apt-get update
    sudo apt-get install -y build-essential lua5.1 liblua5.1-0-dev python python-setuptools python-dev git-core openssl libssl-dev python-pip rsync gcc make git screen
    pip install --user seesaw
    git clone https://github.com/ArchiveTeam/greader-grab
    cd greader-grab
    ./get-wget-lua.sh
    
    # Start downloading with:
    screen ~/.local/bin/run-pipeline --disable-web-server --concurrent 3 pipeline.py YOURNICKNAME

(Debian 6)

    sudo apt-get update
    sudo apt-get install -y build-essential lua5.1 liblua5.1-0-dev python python-setuptools python-dev git-core openssl libssl-dev python-pip rsync gcc make git screen
    wget --no-check-certificate https://pypi.python.org/packages/source/p/pip/pip-1.3.1.tar.gz
    tar -xzvf pip-1.3.1.tar.gz
    cd pip-1.3.1
    python setup.py install --user
    cd ..
    ~/.local/bin/pip install --user seesaw
    git clone https://github.com/ArchiveTeam/greader-grab
    cd greader-grab
    ./get-wget-lua.sh

    # Start downloading with:
    screen ~/.local/bin/run-pipeline --disable-web-server --concurrent 3 pipeline.py YOURNICKNAME

(CentOS / RHEL / Amazon Linux)

    sudo yum install lua lua-devel python-devel python-distribute git openssl-devel rsync gcc make screen
    wget https://pypi.python.org/packages/source/p/pip/pip-1.3.1.tar.gz
    tar -xzvf pip-1.3.1.tar.gz
    cd pip-1.3.1
    python setup.py install --user
    cd ..
    ~/.local/bin/pip install --user seesaw
    git clone https://github.com/ArchiveTeam/greader-grab
    cd greader-grab
    ./get-wget-lua.sh

    # Start downloading with:
    screen ~/.local/bin/run-pipeline --disable-web-server --concurrent 3 pipeline.py YOURNICKNAME

For more options, run:

    ~/.local/bin/run-pipeline --help

