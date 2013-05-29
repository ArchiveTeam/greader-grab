greader-grab
============

Seesaw script for archiveteam Google Reader grabbing.
You'll find this project on the Archive Team Warrior (http://tracker.archiveteam.org/greader/).


Running without a warrior
-------------------------

To run this outside the warrior, clone this repository and run:

(Ubuntu)

    sudo apt-get update
    sudo apt-get install -y build-essential lua5.1 liblua5.1-0-dev python python-setuptools python-dev git-core openssl libssl-dev python-pip rsync gcc make git screen
    pip install --user seesaw
    git clone https://github.com/ArchiveTeam/greader-grab
    cd greader-grab
    ./get-wget-lua.sh
    screen ~/.local/bin/run-pipeline --concurrent 2 pipeline.py YOURNICKNAME

(CentOS / RHEL / Amazon Linux)

    sudo yum install lua lua-devel python-devel python-distribute git openssl-devel rsync gcc make screen
    wget https://pypi.python.org/packages/source/p/pip/pip-1.3.tar.gz
    tar -xzvf pip-1.3.tar.gz
    cd pip-1.3
    python setup.py install --user
    cd ..
    ~/.local/bin/pip install --user seesaw
    git clone https://github.com/ArchiveTeam/greader-grab
    cd greader-grab
    ./get-wget-lua.sh
    screen ~/.local/bin/run-pipeline --concurrent 2 pipeline.py YOURNICKNAME

then start downloading with:

    screen ~/.local/bin/run-pipeline pipeline.py YOURNICKNAME

For more options, run:

    run-pipeline --help

