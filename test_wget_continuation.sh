VERSION="20130627.01"
SSL_CERT_DIR=`pwd`/certs ./wget-lua \
--restrict-file-names=windows \
-e robots=off \
-U "Wget/1.14 gzip ArchiveTeam" \
--lua-script=greader.lua \
--warc-file="test_download" \
--header='Accept-Encoding: gzip' \
--warc-header="operator: Archive Team" \
--warc-header="greader-dld-script-version: $VERSION" \
"https://www.google.com/reader/api/0/stream/contents/feed/http%3A%2F%2Ffeeds.arstechnica.com%2Farstechnica%2FBAaf?r=n&n=1000&hl=en&likes=true&comments=true&client=ArchiveTeam"

# Google needs a "gzip" in the UA to believe our "Accept-Encoding: gzip", though other
# browser UAs should probably work.
