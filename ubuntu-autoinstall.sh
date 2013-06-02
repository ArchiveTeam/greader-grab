sudo apt-get update
sudo apt-get install -y build-essential lua5.1 liblua5.1-0-dev python python-setuptools python-dev git-core openssl libssl-dev python-pip rsync gcc make git screen
pip install --user seesaw
git clone https://github.com/ArchiveTeam/greader-grab
cd greader-grab
./get-wget-lua.sh
