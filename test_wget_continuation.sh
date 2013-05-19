VERSION="0.01"
SSL_CERT_DIR=`pwd`/certs ./wget-lua \
-e robots=off \
-U "Wget/1.14 ArchiveTeam" \
--lua-script=greader.lua \
--warc-file="test_download" \
--warc-header="operator: Archive Team" \
--warc-header="greader-dld-script-version: $VERSION" \
"https://www.google.com/reader/api/0/stream/contents/feed/http%3A%2F%2Ffeeds.arstechnica.com%2Farstechnica%2FBAaf?r=n&n=1000&hl=en&likes=true&comments=true&client=ArchiveTeam"
