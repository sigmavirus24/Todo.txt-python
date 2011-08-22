#!/usr/bin/env python
import os, re, sys
from optparse import OptionParser
from datetime import datetime, date

try:
	import git
except ImportError:
	if sys.version_info < (3, 0):
		print("You must download and install GitPython from:\
	http://pypi.python.org/pypi/GitPython")
	else:
		print("GitPython is not available for Python3 last I checked.")
	sys.exit(52)

TERM_COLORS = { 
		"black" : "\033[0;30m", "red" : "\033[0;31m", 
		"green" : "\033[0;32m", "brown" : "\033[0;33m", 
		"blue" : "\033[0;34m", "purple" : "\033[0;35m", 
		"cyan" : "\033[0;36m", "light grey" : "\033[0;37m", 
		"dark grey" : "\033[1;30m", "light red" : "\033[1;31m",
		"light green" : "\033[1;32m", "yellow" : "\033[1;33m",
		"light blue" : "\033[1;34m", "light purple" : "\033[1;35m",
		"light cyan" : "\033[1;36m", "white" : "\033[1;37m",
		"default" : "\033[0m"
		}

FROM_CONFIG = {}
TO_CONFIG = {}
for key in TERM_COLORS.keys():
	bkey = "$" + re.sub(' ', '_', key).upper()
	FROM_CONFIG[bkey] = key
	TO_CONFIG[key] = bkey

HOME = os.getenv("HOME")
TODO_DIR = HOME + "/.todo"

CONFIG = {
		"HOME" : HOME,
		"TODO_DIR" : TODO_DIR,
		"TODOTXT_DEFAULT_ACTION" : "",
		"TODOTXT_CFG_FILE" : "",
		"TODO_FILE" : TODO_DIR + "/todo.txt",
		"TMP_FILE" : TODO_DIR + "/todo.tmp",
		"DONE_FILE" : TODO_DIR + "/done.txt",
		"REPORT_FILE" : TODO_DIR + "/report.txt",
		"GIT" : git.Git(TODO_DIR),
		"PRI_A" : "",
		"PRI_B" : "",
		"PRI_C" : "",
		"PRI_X" : ""
		}

### Helper Functions 
def get_todos():
	_file = open(CONFIG["TODO_FILE"])
	lines = _file.readlines()
	_file.close()
	return lines
### End Helper Functions

def get_config(config_name=""):
	"""
	Read the config file
	"""
	if config_name:
		CONFIG["TODOTXT_CFG_FILE"] = config_name
	repo = CONFIG["GIT"]
	if not CONFIG["TODOTXT_CFG_FILE"]:
		config_file = CONFIG["TODO_DIR"] + "/config"
	else:
		config_file = CONFIG["TODOTXT_CFG_FILE"]
	if not os.path.exists(CONFIG["TODO_DIR"]) or not os.path.exists(config_file):
		default_config()
	else:
		f = open(config_file, 'r')
		for line in f.readlines():
			if not (re.match('#', line) or re.match('^$', line)):
				line = line.strip()
				i = line.find(' ') + 1
				if i > 0:
					line = line[i:]
				items = re.split('=', line)
				items[1] = items[1].strip('"')
				i = items[1].find(' ')
				if i > 0:
					items[1] = items[1][:i]
				if re.match("PRI_[ABCX]", items[0]):
					CONFIG[items[0]] = FROM_CONFIG[items[1]]
				elif '/' in items[1] and '$' in items[1]: # elision for path names
					i = items[1].find('/')
					if items[1][1:i] in CONFIG.keys():
						items[1] = CONFIG[items[1][1:i]] + items[1][i:]
				elif items[0] == "TODO_DIR":
					CONFIG["GIT"] = git.Git(items[1])
				else:
					CONFIG[items[0]] = items[1]
		f.close()
	if CONFIG["TODOTXT_CFG_FILE"] not in repo.ls_files():
		repo.add([CONFIG["TODOTXT_CFG_FILE"]])


def default_config():
	"""
	Set up the default configuration file.
	"""
	def touch(filename):
		"""
		Create files if they aren't already there.
		"""
		open(filename, "w").close()

	repo = CONFIG["GIT"]
	if not os.path.exists(CONFIG["TODO_DIR"]):
		os.makedirs(CONFIG["TODO_DIR"])
	try:
		repo.status()
	except:
		val = raw_input("Would you like to create a new git repository in " + \
				CONFIG["TODO_DIR"] + "? [y/N] ")
		if val == 'y':
			print(repo.init())

	# touch/create files needed for the operation of the script
	for item in ['TODO_FILE', 'TMP_FILE', 'DONE_FILE', 'REPORT_FILE']:
		touch(CONFIG[item])

	cfg = open(CONFIG["TODO_DIR"] + "/config", 'w')

	# set the defaults for the colors
	CONFIG["PRI_A"] = "yellow"
	CONFIG["PRI_B"] = "green"
	CONFIG["PRI_C"] = "light blue"
	CONFIG["PRI_X"] = "white"

	for k, v in CONFIG.items():
		if k != "repo":
			if v in TO_CONFIG.keys():
				cfg.write("export " + k + "=" + TO_CONFIG[v] + "\n")
			else:
				cfg.write("export " + k + '="' + v + '"\n')
	repo.add([CONFIG["TODOTXT_CFG_FILE"], CONFIG["TODO_FILE"],
	CONFIG["TMP_FILE"], CONFIG["DONE_FILE"], CONFIG["REPORT_FILE"]])

def format_lines(lines):
	"""
	Take in a list of lines to do, return them formatted with the TERM_COLORS
	and organized based upon priority.
	"""
	i = 1
	default = TERM_COLORS["default"]
	category = ""
	formatted = { "A" : [], "B" : [], "C" : [], "X" : [] }
	for line in lines:
		r = re.match("\(([ABC])\)", line)
		if r:
			category = r.groups()[0]
			color = TERM_COLORS[CONFIG["PRI_{0}".format(category)]]
		else:
			category = "X"
			color = default
		formatted[category].append(color + str(i) + " " + line[:-1] + default)
		i += 1
	return formatted


def list_todo():
	"""
	Print the list of todo items in order of priority and position in the
	todo.txt file.
	"""
	lines = get_todos()
	formatted_lines = format_lines(lines)
	for category in ["A", "B", "C", "X"]:
		for line in formatted_lines[category]:
			print(line)
	print("--\nTODO: {0} of {1} tasks shown".format(len(lines), len(lines)))
	#sys.exit(0)

def add_todo(line):
	"""
	Add a new item to the list of things to do.
	"""
	_git = CONFIG["GIT"]
	_file = open(CONFIG["TODO_FILE"], "r+")
	l = len(_file.readlines()) + 1
	_file.write(line + "\n")
	_file.close()
	s = "TODO: '{0}' added on line {1}.".format(
		line, l)
	_git.add(CONFIG["TODO_FILE"])
	_git.commit("-m", s)
	print(s)

def do_todo(mark_done):
	"""
	Mark an item on a specified line as done.
	"""
	if not mark_done.isdigit():
		print("Usage: {0} do item#".format(CONFIG["TODO_PY"]))
	else:
		_git = CONFIG["GIT"]
		_file = open(CONFIG["TODO_FILE"], "r+")
		lines = _file.readlines()
		removed = lines.pop(int(mark_done) - 1)
		_file.seek(0, 0)
		_file.truncate(0)
		_file.writelines(lines)
		_file.close()
		today = datetime.now().strftime("%Y-%m-%d")
		removed = re.sub("\(?[ABCX]\)?\s?", "", removed)
		removed = "x " + today + " " + removed
		_file = open(CONFIG["DONE_FILE"], "a")
		_file.write(removed)
		_file.close()
		_git.commit("-a", "-m", removed)
		print(removed[:-1])
		print("TODO: Item {0} marked as done.".format(mark_done))
		print("TODO: {0} archived.".format(CONFIG["DONE_FILE"]))

def list_date():
	"""
	List todo items by date @{yyyy-mm-dd}.
	"""
	lines = get_todos()
	todo = {"nodate" : []}
	dates = []
	i = 1

	for line in lines:
		_re = re.search("@\{(\d{4})-(\d{1,2})-(\d{1,2})\}", line)
		if _re:
			tup = _re.groups()
			dates.append(date(int(tup[0]), int(tup[1]), int(tup[2])))
			todo[dates[-1]] = "{0} ".format(i) + line
		else:
			j = lines.index(line)
			todo["nodate"].append("{0} ".format(i) + line)
		i += 1 

	dates.sort()
	sortedl = []

	for d in dates:
		sortedl.append(todo[d])

	sortedl += todo["nodate"]
	print("".join(sortedl)[:-1])
	print("--\nTODO: {0} of {1} tasks shown".format(len(sortedl), len(sortedl)))


if __name__ == "__main__" :
	CONFIG["TODO_PY"] = sys.argv[0]

	opts = OptionParser("Usage: %prog [options] action [arg(s)]")
	opts.add_option("-c", "--config", dest = "config",
			type = "string", 
			help = \
			"Supply your own configuration file, must be an absolute path"
			)
	valid, args = opts.parse_args()

	get_config(valid.config)

	commands = {
			# command 	: ( Args, Function),
			"add"		: ( True, add_todo),
			"do"		: ( True, do_todo),
			"ls"		: (False, list_todo),
			"list"		: (False, list_todo),
			"lsd"		: (False, list_date),
			"listdate"	: (False, list_date),
			"push"		: (False, CONFIG["GIT"].push)
			}
	commandsl = commands.keys()
	#list_todo()
	if not len(args) > 0:
		args.append(CONFIG["TODOTXT_DEFAULT_ACTION"])
	while args:
		# ensure this doesn't error because of a faulty CAPS LOCK key
		arg = args.pop(0).lower() 
		if arg in commandsl:
			if not commands[arg][0]:
				commands[arg][1]()
			else:
				commands[arg][1](args.pop(0))
		else:
			commandsl.sort()
			commandsl = ["\t" + i for i in commandsl]
			print("Unable to find command: {0}".format(arg))
			print("Valid commands: ")
			print("\n".join(commandsl))
			sys.exit(1)

# vim:set noet:
