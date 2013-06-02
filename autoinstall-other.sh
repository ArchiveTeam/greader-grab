sudo yum install lua lua-devel python-devel python-distribute git openssl-devel rsync gcc make screen
wget https://pypi.python.org/packages/source/p/pip/pip-1.3.1.tar.gz
tar -xzvf pip-1.3.tar.gz
cd pip-1.3
python setup.py install --user
cd ..
~/.local/bin/pip install --user seesaw
git clone https://github.com/ArchiveTeam/greader-grab
cd greader-grab
./get-wget-lua.sh
