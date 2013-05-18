#!/usr/bin/env bash
#
# This script downloads and compiles wget-lua.
#

set -e

# first, try to detect gnutls or openssl
CONFIGURE_SSL_OPT=""
if builtin type -p pkg-config &>/dev/null
then
  if pkg-config gnutls
  then
    echo "Compiling wget with GnuTLS."
    CONFIGURE_SSL_OPT="--with-ssl=gnutls"
  elif pkg-config openssl
  then
    echo "Compiling wget with OpenSSL."
    CONFIGURE_SSL_OPT="--with-ssl=openssl"
  fi
fi

TARVERSION=1.14.lua.20130427-92d2
TARFILE=wget-$TARVERSION.tar.bz2
EXPECTED_SHA1=00705ce59e3cb14dee3c4b93c51377199cf2e2e8
TARDIR=wget-$TARVERSION

rm -rf $TARFILE $TARDIR/

wget http://warriorhq.archiveteam.org/downloads/wget-lua/$TARFILE
if [ "$(sha1sum $TARFILE | awk '{print $1}')" = "$EXPECTED_SHA1" ]; then
  echo "sha1sum OK for $TARFILE"
else
  echo "sha1sum BAD for $TARFILE"
  exit
fi
tar xjf $TARFILE
cd $TARDIR/
if ./configure $CONFIGURE_SSL_OPT --disable-nls && make && src/wget -V | grep -q lua
then
  cp src/wget ../wget-lua
  cd ../
  echo
  echo
  echo "###################################################################"
  echo
  echo "wget-lua successfully built."
  echo
  ./wget-lua --help | grep -iE "gnu|warc|lua"
  rm -rf $TARFILE $TARDIR/
else
  echo
  echo "wget-lua not successfully built."
  echo
fi

