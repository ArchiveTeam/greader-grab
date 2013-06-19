#!/usr/bin/env python

"""
warc2warc_greader - convert one warc to another, can be used to re-compress things
"""

import os
import sys
import re
import bz2

from optparse import OptionParser

# hack hack hack
sys.path.append(os.path.join(os.path.dirname(__file__), "warc-tools"))

from hanzo.warctools import WarcRecord
from hanzo.httptools import RequestMessage, ResponseMessage

parser = OptionParser(usage="%prog [options] input_file (input_file ...)")

parser.add_option("-o", "--output", dest="output", help="output warc file")
parser.add_option("-l", "--limit", dest="limit")
parser.add_option("-I", "--input", dest="input_format", help="(ignored)")
parser.add_option("-Z", "--gzip", dest="gzip", action="store_true", help="compress output, record by record")
parser.add_option("-D", "--decode_http", dest="decode_http", action="store_true", help="decode http messages (strip chunks, gzip)")
parser.add_option("-L", "--log-level", dest="log_level")
parser.add_option("-S", "--strip-404s", dest="strip_404s", action="store_true", help="strip out 404 request/response pairs, but do leave them in the wget log")
parser.add_option("-J", "--json-hrefs-file", dest="json_hrefs_file", help="extract Google Reader-style hrefs embedded in JSON responses and write them to this .bz2 file")
parser.add_option("--wget-chunk-fix", dest="wget_workaround", action="store_true", help="skip transfer-encoding headers in http records, when decoding them (-D)")

parser.set_defaults(output_directory=None, limit=None, log_level="info", gzip=False, decode_http=False, wget_workaround=False)


JSON_HREF_RE = re.compile(r'href\\u003d\\"[^\\]+\\"')

WGET_IGNORE_HEADERS = ['Transfer-Encoding']

def process(record, previous_record, out, options, found_hrefs):
	ignore_headers = WGET_IGNORE_HEADERS if options.wget_workaround else ()
	if options.decode_http:
		if record.type == WarcRecord.RESPONSE:
			content_type, content = record.content

			message = None
			if content_type == ResponseMessage.CONTENT_TYPE:
				# technically, a http request needs to know the request to be parsed
				# because responses to head requests don't have a body.
				# we assume we don't store 'head' responses, and plough on 
				message = ResponseMessage(RequestMessage(), ignore_headers=ignore_headers)
			if content_type == RequestMessage.CONTENT_TYPE:
				message = RequestMessage(ignore_headers=ignore_headers)

			if message:
				leftover = message.feed(content)
				message.close()
				##print "Code", message.header.code

				if not leftover and message.complete():
					content = message.get_decoded_message()

					if found_hrefs is not None and message.header.code == 200:
						found_hrefs.update(match[12:-3] for match in JSON_HREF_RE.findall(content))

					record.content = content_type, content
				else:
					error = []
					if leftover:
						error.append("%d bytes unparsed"%len(leftover))
					if not message.complete():
						error.append("incomplete message (at %s, %s)"%(message.mode, message.header.mode))
					print >> sys.stderr, 'errors decoding http in record', record.id, ",".join(error)

	if options.strip_404s:
		# We don't write out a request until we confirm its associated response is not 404
		if record.type == WarcRecord.REQUEST:
			pass
		elif record.type == WarcRecord.RESPONSE:
			if message.header.code == 404:
				# If 404, don't write out either the request or the response
				pass
			else:
				if previous_record is None:
					raise RuntimeError("Need to write out previous record as well, but it isn't present")
				if previous_record.type != WarcRecord.REQUEST:
					raise RuntimeError("Expected previous record to be a "
						"WarcRecord.REQUEST, was a %r" % (previous_record.type,))
				# Note that if a request is made multiple times, we will only write out the last
				# attempt at it.
				previous_record.write_to(out, gzip=options.gzip)
				record.write_to(out, gzip=options.gzip)
		else: # metadata
			record.write_to(out, gzip=options.gzip)
	else:
		record.write_to(out, gzip=options.gzip)


def main(argv):
	(options, input_files) = parser.parse_args(args=argv[1:])

	if options.strip_404s and not options.decode_http:
		raise RuntimeError("--strip-404s requires --decode_http")

	if options.json_hrefs_file and not options.decode_http:
		raise RuntimeError("--json-hrefs-file requires --decode_http")

	if options.json_hrefs_file:
		found_hrefs = set()
	else:
		found_hrefs = None

	with open(options.output, "wb") as out:
		if len(input_files) < 1:
			fh = WarcRecord.open_archive(file_handle=sys.stdin, gzip=None, mode="rb")
			try:
				previous_record = None
				for record in fh:
					process(record, previous_record, out, options, found_hrefs)
					previous_record = record
			finally:
				fh.close()
		else:
			for name in input_files:
				previous_record = None
				fh = WarcRecord.open_archive(name, gzip="auto", mode="rb")
				try:
					for record in fh:
						process(record, previous_record, out, options, found_hrefs)
						previous_record = record
				finally:
					fh.close()

	if found_hrefs is not None:
		fh = bz2.BZ2File(options.json_hrefs_file, "wb")
		try:
			fh.write("\n".join(sorted(found_hrefs)) + "\n")
		finally:
			fh.close()

	return 0


if __name__ == '__main__':
	sys.exit(main(sys.argv))
