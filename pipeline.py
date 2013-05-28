# This file defines a seesaw pipeline for the ArchiveTeam Warrior.
# It can also be run standalone:
#
#   pip install seesaw
#   run-pipeline pipeline.py YOURNICKNAME
#
# (or run   run-pipeline --help   for more details)
#
import os
import json
import os.path
import shutil
import time
import urllib

from distutils.version import StrictVersion

# check the seesaw version before importing any other components
import seesaw
if StrictVersion(seesaw.__version__) < StrictVersion("0.0.12"):
	raise Exception("This pipeline needs seesaw version 0.0.12 or higher.")

from seesaw.project import Project
from seesaw.config import NumberConfigValue, realize
from seesaw.item import ItemInterpolation, ItemValue
from seesaw.task import SimpleTask, LimitConcurrent
from seesaw.pipeline import Pipeline
from seesaw.externalprocess import WgetDownload
from seesaw.tracker import TrackerRequest, UploadWithTracker, SendDoneToTracker, PrepareStatsForTracker

"""
This pipeline relies on this code inserted into your universal-tracker redis database:

# redis-cli
redis 127.0.0.1:6379> select 13
OK
redis 127.0.0.1:6379[13]> set greader:extra_parameters 'data["task_urls"] = ["http://127.0.0.1/", "http://127.0.0.2/"]; data["user_agent"] = "Wget/1.14 ArchiveTeam"; data["wget_timeout"] = "60"; data["wget_tries"] = "20"; data["wget_waitretry"] = "5";'
OK
"""


class GetItemFromTracker(TrackerRequest):
	def __init__(self, tracker_url, downloader, version = None):
		TrackerRequest.__init__(self, "GetItemFromTracker", tracker_url, "request", may_be_canceled=True)
		self.downloader = downloader
		self.version = version

	def data(self, item):
		data = {"downloader": realize(self.downloader, item), "api_version": "2"}
		if self.version:
			data["version"] = realize(self.version, item)
		return data

	def process_body(self, body, item):
		data = json.loads(body)
		if "item_name" in data:
			for (k,v) in data.iteritems():
				item[k] = v
			##print item
			item.log_output("Received item '%s' from tracker with %d URLs; first URL is %r\n" % (
				item["item_name"], len(item["task_urls"]), item["task_urls"][0]))
			self.complete_item(item)
		else:
			item.log_output("Tracker responded with empty response.\n")
			self.schedule_retry(item)


# stdin_data_function added in seesaw 0.14
class WgetDownloadWithStdin(WgetDownload):
	def __init__(self, args, max_tries=1, accept_on_exit_code=[0], retry_on_exit_code=None, env=None, stdin_data_function=None):
		super(WgetDownloadWithStdin, self).__init__(args, max_tries, accept_on_exit_code, retry_on_exit_code, env)
		self.stdin_data_function = stdin_data_function


#---------------------------------------
# This is an updated version of test_executable.
# This can be removed when all warriors have updated
# the seesaw-kit. (Needs at least version 0.0.15.)
#
import subprocess

def test_executable(name, version, path):
	print "Looking for %s in %s" % (name, path)
	try:
		process = subprocess.Popen([path, "-V"], stdout=subprocess.PIPE)
		result = process.communicate()[0]
		if not process.returncode == 0:
			print "%s: Returned code %d" % (path, process.returncode)
			return False

		if isinstance(version, basestring):
			if not version in result:
				print "%s: Incorrect %s version (want %s)." % (path, name, version)
				return False
		elif hasattr(version, "search"):
			if not version.search(result):
				print "%s: Incorrect %s version." % (path, name)
				return False
		elif hasattr(version, "__iter__"):
			if not any((v in result) for v in version):
				print "%s: Incorrect %s version (want %s)." % (path, name, str(version))
				return False

		print "Found usable %s in %s" % (name, path)
		return True
	except OSError as e:
		print "%s:" % path, e
		return False

def find_executable(name, version, paths):
	for path in paths:
		if test_executable(name, version, path):
			return path
	return None
#---------------------------------------

###########################################################################
# Find a useful Wget+Lua executable.
#
# WGET_LUA will be set to the first path that
# 1. does not crash with --version, and
# 2. prints the required version string
WGET_LUA = find_executable(
	"Wget+Lua",
	["GNU Wget 1.14.lua.20130523-9a5c"],
	[
		"./wget-lua",
		"./wget-lua-warrior",
		"./wget-lua-local",
		"../wget-lua",
		"../../wget-lua",
		"/home/warrior/wget-lua",
		"/usr/bin/wget-lua"
	]
)

if not WGET_LUA:
	raise Exception("No usable Wget+Lua found.")


###########################################################################
# The version number of this pipeline definition.
#
# Update this each time you make a non-cosmetic change.
# It will be added to the WARC files and reported to the tracker.
VERSION = "20130528.01"


###########################################################################
# This section defines project-specific tasks.
#
# Simple tasks (tasks that do not need any concurrency) are based on the
# SimpleTask class and have a process(item) method that is called for
# each item.

class PrepareDirectories(SimpleTask):
	"""
	  A task that creates temporary directories and initializes filenames.

	  It initializes these directories, based on the previously set item_name:
		item["item_dir"] = "%{data_dir}/%{item_name}"
		item["warc_file_base"] = "%{warc_prefix}-%{item_name}-%{timestamp}"

	  These attributes are used in the following tasks, e.g., the Wget call.

	  * set warc_prefix to the project name.
	  * item["data_dir"] is set by the environment: it points to a working
		directory reserved for this item.
	  * use item["item_dir"] for temporary files
	  """
	def __init__(self, warc_prefix):
		SimpleTask.__init__(self, "PrepareDirectories")
		self.warc_prefix = warc_prefix

	def process(self, item):
		dirname = "/".join((item["data_dir"], item["item_name"]))

		if os.path.isdir(dirname):
			shutil.rmtree(dirname)
		os.makedirs(dirname)

		item["item_dir"] = dirname
		item["warc_file_base"] = "%s-%s-%s" % (
			self.warc_prefix, item["item_name"], time.strftime("%Y%m%d-%H%M%S"))

		open("%(item_dir)s/%(warc_file_base)s.warc.gz" % item, "w").close()


class MoveFiles(SimpleTask):
	"""
	  After downloading, this task moves the warc file from the
	  item["item_dir"] directory to the item["data_dir"], and removes
	  the files in the item["item_dir"] directory.
	  """
	def __init__(self):
		SimpleTask.__init__(self, "MoveFiles")

	def process(self, item):
		os.rename("%(item_dir)s/%(warc_file_base)s.warc.gz" % item,
				"%(data_dir)s/%(warc_file_base)s.warc.gz" % item)

		shutil.rmtree("%(item_dir)s" % item)




###########################################################################
# Initialize the project.
#
# This will be shown in the warrior management panel. The logo should not
# be too big. The deadline is optional.
project = Project(
	title="Google Reader",
	project_html="""
	<h2>Google Reader <span class="links"><a href="http://www.google.com/reader/">Website</a> &middot; <a
href="http://tracker.archiveteam.org/greader/">Leaderboard</a></span></h2>
	<p><i>Google Reader</i> is closing July 1st, 2013</p>
  """
)

###########################################################################
TRACKER_URL = "http://127.0.0.1:9292/greader"
#TRACKER_URL = "http://tracker.archiveteam.org/greader"


###########################################################################
# The pipeline.
#
# Items move through each task on the pipeline.
# Items are dicts, so tasks can set properties and can use properties set
# by earlier tasks and (such as the item["item_name"] property).
#
pipeline = Pipeline(
	# request an item from the tracker (using the universal-tracker protocol)
	# the downloader variable will be set by the warrior environment
	#
	# this task will wait for an item and sets item["item_name"] to the item name
	# before finishing
	GetItemFromTracker(TRACKER_URL, downloader, VERSION),

	# create the directories and initialize the filenames (see above)
	# warc_prefix is the first part of the warc filename
	#
	# this task will set item["item_dir"] and item["warc_file_base"]
	PrepareDirectories(warc_prefix="greader"),

	# execute Wget+Lua
	#
	# the ItemInterpolation() objects are resolved during runtime
	# (when there is an Item with values that can be added to the strings)
	WgetDownloadWithStdin([
			# TODO: cert-pin
			WGET_LUA,
			"-U", ItemInterpolation("%(user_agent)s"),
			"-nv",
			"-o", ItemInterpolation("%(item_dir)s/wget.log"),
			"--output-document", ItemInterpolation("%(item_dir)s/wget.tmp"),
			"--truncate-output",
			"-e", "robots=off",
			"--rotate-dns",
			"--timeout", ItemInterpolation("%(wget_timeout)s"),
			"--tries", ItemInterpolation("%(wget_tries)s"),
			"--waitretry", ItemInterpolation("%(wget_waitretry)s"),
			"--lua-script", "greader.lua",
			"--warc-file", ItemInterpolation("%(item_dir)s/%(warc_file_base)s"),
			"--warc-header", "operator: Archive Team",
			"--warc-header", "greader-dld-script-version: " + VERSION,
			"--input", "-"
		],
		max_tries=2,
		accept_on_exit_code=[0, 8], # which Wget exit codes count as a success?
		stdin_data_function=(lambda item: "\n".join(u.encode("utf-8") for u in item["task_urls"]) + "\n"),
	),

	# this will set the item["stats"] string that is sent to the tracker (see below)
	PrepareStatsForTracker(
		# there are a few normal values that need to be sent
		defaults={"downloader": downloader, "version": VERSION},
		# this is used for the size counter on the tracker:
		# the groups should correspond with the groups set configured on the tracker
		file_groups={
			# there can be multiple groups with multiple files
			# file sizes are measured per group
			"data": [ItemInterpolation("%(item_dir)s/%(warc_file_base)s.warc.gz")]
		},
		id_function=(lambda item: {"ua": item["user_agent"] })
	),

	# remove the temporary files, move the warc file from
	# item["item_dir"] to item["data_dir"]
	MoveFiles(),

	# there can be multiple items in the pipeline, but this wrapper ensures
	# that there is only one item uploading at a time
	#
	# the NumberConfigValue can be changed in the configuration panel
	LimitConcurrent(
		NumberConfigValue(
			min=1, max=4, default="1", name="shared:rsync_threads", title="Rsync threads",
			description="The maximum number of concurrent uploads."),
		# this upload task asks the tracker for an upload target
		# this can be HTTP or rsync and can be changed in the tracker admin panel
		UploadWithTracker(
			TRACKER_URL,
			downloader=downloader,
			version=VERSION,
			# list the files that should be uploaded.
			# this may include directory names.
			# note: HTTP uploads will only upload the first file on this list
			files=[
				ItemInterpolation("%(data_dir)s/%(warc_file_base)s.warc.gz")
			],
			# the relative path for the rsync command
			# (this defines if the files are uploaded to a subdirectory on the server)
			rsync_target_source_path=ItemInterpolation("%(data_dir)s/"),
			# extra rsync parameters (probably standard)
			rsync_extra_args=[
				"--recursive",
				"--partial",
				"--partial-dir", ".rsync-tmp"
			]
		),
	),

	# if the item passed every task, notify the tracker and report the statistics
	SendDoneToTracker(
		tracker_url=TRACKER_URL,
		stats=ItemValue("stats")
	)
)
