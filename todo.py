#!/usr/bin/env python
#### TODO.TXT-CLI-python
#### Copyright (C) 2011  Sigmavirus24
####
#### This program is free software: you can redistribute it and/or modify
#### it under the terms of the GNU General Public License as published by
#### the Free Software Foundation, either version 3 of the License, or
#### (at your option) any later version.
####
#### This program is distributed in the hope that it will be useful,
#### but WITHOUT ANY WARRANTY; without even the implied warranty of
#### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#### GNU General Public License for more details.
####
#### You should have received a copy of the GNU General Public License
#### along with this program.  If not, see <http://www.gnu.org/licenses/>.

#### TLDR: This is licensed under the GPLv3. See LICENSE for more details.

import os
import re
import sys
from optparse import OptionParser
from datetime import datetime, date

VERSION = "0.0-master_dev"

try:
	import git
except ImportError:
	if sys.version_info < (3, 0):
		print("You must download and install GitPython from:\
http://pypi.python.org/pypi/GitPython")
	else:
		print("GitPython is not available for Python3 last I checked.")
	sys.exit(52)

# concat() is necessary long before the grouping of function declarations
concat = lambda str_list, sep='': sep.join(str_list)

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
	bkey = concat(["$", re.sub(' ', '_', key).upper()])
	FROM_CONFIG[bkey] = key
	TO_CONFIG[key] = bkey
del(key, bkey)  # If someone were to import this as a module, these show up.

HOME = os.getenv("HOME")
TODO_DIR = concat([HOME, "/.todo"])

CONFIG = {
		"HOME" : HOME,
		"TODO_DIR" : TODO_DIR,
		"TODOTXT_DEFAULT_ACTION" : "",
		"TODOTXT_CFG_FILE" : "",
		"TODO_FILE" : concat([TODO_DIR, "/todo.txt"]),
		"TMP_FILE" : concat([TODO_DIR, "/todo.tmp"]),
		"DONE_FILE" : concat([TODO_DIR, "/done.txt"]),
		"REPORT_FILE" : concat([TODO_DIR, "/report.txt"]),
		"GIT" : git.Git(TODO_DIR),
		"PRI_A" : "",
		"PRI_B" : "",
		"PRI_C" : "",
		"PRI_X" : ""
		}


### Helper Functions
def get_todos():
	"""
	Opens the file in read-only mode, reads all the lines and then closes the
	file before returning the lines.
	"""
	fd = open(CONFIG["TODO_FILE"])
	lines = fd.readlines()
	fd.close()
	return lines


def rewrite_file(fd, lines):
	"""
	Simple wrapper for three lines used all too frequently.
	Sets the access position to the beginning of the file, truncates the file's
	length to 0 and then writes all the lines to the file.
	"""
	fd.seek(0, 0)
	fd.truncate(0)
	fd.writelines(lines)


def _git_err(g):
	"""
	Print any errors that result from GitPython and exit.
	"""
	if g.stderr:
		print(g.stderr)
	else:
		print(g)
	sys.exit(g.status)


def _git_pull():
	"""
	Pull any commits that exist on the remote to the local repository.
	"""
	try:
		print(CONFIG["GIT"].pull())
	except git.exc.GitCommandError, g:
		_git_err(g)


def _git_push():
	"""
	Push commits made locally to the remote.
	"""
	try:
		s = CONFIG["GIT"].push()
	except git.exc.GitCommandError, g:
		_git_err(g)
	if s:
		print(s)
	else:
		print("TODO: 'git push' executed.")


def _git_status():
	"""
	Print the status of the local repository if the version of git is 1.7 or
	later.
	"""
	try:
		print(CONFIG["GIT"].status())
	except git.exc.GitCommandError, g:
		_git_err(g)


def _git_log():
	"""
	Print the two latest commits in the local repository's log.
	"""
	lines = CONFIG["GIT"].log("-2")
	flines = []
	for line in lines.split("\n"):
		if re.match("commit", line):
			flines.append(concat([TERM_COLORS["yellow"],
				line[:-1], TERM_COLORS["default"], "\n"]))
		else:
			flines.append(concat([line, "\n"]))
	flines[-1] = flines[-1][:-1]
	print(concat(flines))


def _git_commit(files, message):
	"""
	Make a commit to the git repository.
		* files should be a list like ['file_a', 'file_b'] or ['-a']
	"""
	try:
		CONFIG["GIT"].commit(files, "-m", message)
	except git.exc.GitCommandError, g:
		_git_err(g)
	if "-a" not in files:
		print(concat(["TODO: ", concat(files, ", "), " archived."]))
	else:
		print(concat(["TODO: ", CONFIG["TODO_DIR"], " archived."]))


def print_x_of_y(x, y):
	t_str = "--\nTODO: {0} of {1} tasks shown"
	if len(x) > len(y):  # EXTREMELY hack-ish
		print(t_str.format(len(y), len(y)))  # There can't logically be more
			# lines of items to do than there actually are.
	else:
		print(t_str.format(len(x), len(y)))
### End Helper Functions


### Configuration Functions
def get_config(config_name=""):
	"""
	Read the config file
	"""
	if config_name:
		CONFIG["TODOTXT_CFG_FILE"] = config_name
	repo = CONFIG["GIT"]
	if not CONFIG["TODOTXT_CFG_FILE"]:
		config_file = concat([CONFIG["TODO_DIR"], "/config"])
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
				elif '/' in items[1] and '$' in items[1]:  # elision for path names
					i = items[1].find('/')
					if items[1][1:i] in CONFIG.keys():
						items[1] = concat([CONFIG[items[1][1:i]], items[1][i:]])
				elif items[0] == "TODO_DIR":
					CONFIG["GIT"] = git.Git(items[1])
				else:
					CONFIG[items[0]] = items[1]
		f.close()
	if CONFIG["TODOTXT_CFG_FILE"] not in repo.ls_files():
		repo.add([CONFIG["TODOTXT_CFG_FILE"]])


def parse_valid(valid_opts):
	"""
	Set configuration options based that are set from the command-line.
	"""
	CONFIG["PLAIN"] = valid_opts.plain
	CONFIG["NO_PRI"] = valid_opts.priority
	CONFIG["PRE_DATE"] = valid.prepend_date


def repo_config():
	"""
	Help the user configure their git repository.
	"""
	from getpass import getuser
	from os import getenv
	g = CONFIG["GIT"]
	# local configuration
	try:
		user_name = g.config("--global", "--get", "user.name")
	except:
		user_name = getuser()

	try:
		user_email = g.config("--global", "--get", "user.email")
	except:
		user_email = concat([user.name, "@", getenv("HOSTNAME")])
	print("First configure your local repository options.")
	ret = raw_input(concat(["git config user.name ", user_name, "? "]))
	if ret:
		user_name = ret
	ret = raw_input(concat(["git config user.email ", user_email, "? "]))
	if ret:
		user_email = ret

	g.config("user.name", user_name)
	g.config("user.email", user_email)

	# remote configuration
	ret = raw_input("Would you like to add a remote repository? ")
	if re.match(ret, "yes", flags=re.I):
		remote_host = None
		remote_path = None
		remote_user = None
		remote_branch = None

		while not remote_host:
			remote_host = raw_input("Remote hostname: ")
			if not remote_host:
				print("Please enter the remote's hostname.")
		while not remote_path:
			remote_path = raw_input("Remote path: ")
			if not remote_path:
				print("Please enter the path to the remote's repository.")
		while not remote_user:
			remote_user = raw_input("Remote user: ")
			if not remote_user:
				print("Please enter the user on the remote machine.")
		while not remote_branch:
			remote_branch = raw_input("Remote branch: ")
			if not remote_branch:
				print("Please enter the branch to push to on the remote machine.")
		raw_input(concat(["Press enter when you have initialized a bare",
				"repository on the remote or are ready to proceed."]))
		local_branch = g.branch()
		if not local_branch:
			local_branch = "master"
		else:
			for l in local_branch.split("\n"):
				if re.match("^\*\s.*", l):
					local_branch = re.sub("^\*\s", "", l)
					break

		g.remote("add", "origin", concat([remote_user, "@", remote_host,
				":", remote_path]))
		g.config(concat(["branch.", local_branch, ".remote"]), "origin")
		g.config(concat(["branch.", local_branch, ".merge"]),
				concat(["refs/heads/", remote_branch]))


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
	except git.exc.GitCommandError, g:
		val = raw_input(
			concat(["Would you like to create a new git repository in ",
				CONFIG["TODO_DIR"], "? [y/N] "]))
		if val == 'y':
			print(repo.init())
			val = raw_input(concat(
	["Would you like {prog} to help you".format(prog=CONFIG["TODO_PY"]),
	" configure your new git repository? [y/n] "]
			))
			if val == 'y':
				repo_config()

	# touch/create files needed for the operation of the script
	for item in ['TODO_FILE', 'TMP_FILE', 'DONE_FILE', 'REPORT_FILE']:
		touch(CONFIG[item])

	cfg = open(concat([CONFIG["TODO_DIR"], "/config"]), 'w')

	# set the defaults for the colors
	CONFIG["PRI_A"] = "yellow"
	CONFIG["PRI_B"] = "green"
	CONFIG["PRI_C"] = "light blue"
	CONFIG["PRI_X"] = "white"

	for k, v in CONFIG.items():
		if k != "GIT":
			if v in TO_CONFIG.keys():
				cfg.write(concat(["export ", k, "=", TO_CONFIG[v], "\n"]))
			else:
				cfg.write(concat(["export ", k, '="', v, '"\n']))
	repo.add([CONFIG["TODOTXT_CFG_FILE"], CONFIG["TODO_FILE"],
	CONFIG["TMP_FILE"], CONFIG["DONE_FILE"], CONFIG["REPORT_FILE"]])
	repo.commit("-m", CONFIG["TODO_PY"] + " initial commit.")
### End Config Functions


### New todo Functions
def add_todo(line):
	"""
	Add a new item to the list of things todo.
	"""
	prepend = CONFIG["PRE_DATE"]
	_git = CONFIG["GIT"]
	fd = open(CONFIG["TODO_FILE"], "r+")
	l = len(fd.readlines()) + 1
	if re.match("(\([ABC]\))", line) and prepend:
		line = re.sub("(\([ABC]\))", concat(["\g<1>",
			datetime.now().strftime(" %Y-%m-%d ")]),
			line)
	elif prepend:
		line = concat([datetime.now().strftime("%Y-%m-%d "), line])
	fd.write(concat([line, "\n"]))
	fd.close()
	s = "TODO: '{0}' added on line {1}.".format(
		line, l)
	print(s)
	_git_commit([CONFIG["TODO_FILE"]], s)


def addm_todo(todo):
	"""
	Add new items to the list of things todo.
	"""
	lines = todo.split("\n")
	for line in lines:
		add_todo(line)


def do_todo(mark_done):
	"""
	Mark an item on a specified line as done.
	"""
	if not mark_done.isdigit():
		print("Usage: {0} do item#".format(CONFIG["TODO_PY"]))
	else:
		_git = CONFIG["GIT"]
		fd = open(CONFIG["TODO_FILE"], "r+")
		lines = fd.readlines()
		removed = lines.pop(int(mark_done) - 1)
		rewrite_file(fd, lines)
		fd.close()
		today = datetime.now().strftime("%Y-%m-%d")
		removed = re.sub("\(?[ABCX]\)?\s?", "", removed)
		removed = "x " + today + " " + removed
		fd = open(CONFIG["DONE_FILE"], "a")
		fd.write(removed)
		fd.close()
		print(removed[:-1])
		print("TODO: Item {0} marked as done.".format(mark_done))
		_git_commit([CONFIG["DONE_FILE"]], removed)
### End new todo Functions


### Post-production todo functions
def post_error(command, arg1, arg2):
	"""
	If one of the post-production todo functions isn't given the proper
	arguments, the function calls this to notify the user of what they need to
	supply.
	"""
	if arg2:
		print(concat(["'", CONFIG["TODO_PY"], " ", command, "' requires a(n) ",
			arg1, " then a ", arg2, "."]))
	else:
		print(concat(["'", CONFIG["TODO_PY"], " ", command, "' requires a(n) ",
			arg1, "."]))


def post_success(item_no, old_line, new_line):
	"""
	After changing a line, pring a standard line and commit the change.
	"""
	print_str = "TODO: Item {0} changed from '{1}' to '{2}'.".format(
		item_no + 1, old_line, new_line)
	print(print_str)
	_git_commit([CONFIG["TODO_FILE"]], print_str)


def append_todo(args):
	"""
	Append text to the item specified.
	"""
	if args[0].isdigit():
		line_no = int(args.pop(0)) - 1
		fd = open(CONFIG["TODO_FILE"], "r+")
		lines = fd.readlines()
		old_line = lines[line_no][:-1]
		lines[line_no] = concat([old_line, concat(args, " "), "\n"], " ")
		new_line = lines[line_no][:-1]
		rewrite_file(fd, lines)
		fd.close()
		post_success(line_no, old_line, new_line)
	else:
		post_error('append', 'NUMBER', 'string')
	sys.exit(0)


def prioritize_todo(args):
	"""
	Add or modify the priority of the specified item.
	"""
	if args[0].isdigit():
		line_no = int(args.pop(0)) - 1
		fd = open(CONFIG["TODO_FILE"], "r+")
		lines = fd.readlines()
		old_line = lines[line_no][:-1]
		new_pri = concat(["(", args[0], ") "])
		r = re.match("(\([ABC]\)\s).*", old_line)
		if r:
			lines[line_no] = re.sub(re.escape(r.groups()[0]), new_pri,
					lines[line_no])
		else:
			lines[line_no] = concat([new_pri, lines[line_no]])
		new_line = lines[line_no][:-1]
		rewrite_file(fd, lines)
		fd.close()
		post_success(line_no, old_line, new_line)
	else:
		post_error('pri', 'NUMBER', 'capital letter')
	sys.exit(0)


def de_prioritize_todo(number):
	"""
	Remove priority markings from the beginning of the line if they're there.
	Don't complain otherwise.
	"""
	if number.isdigit():
		number = int(number) - 1
		fd = open(CONFIG["TODO_FILE"], "r+")
		lines = fd.readlines()
		old_line = lines[number][:-1]
		lines[number] = re.sub("(\([ABC]\)\s)", "", lines[number])
		new_line = lines[number][:-1]
		rewrite_file(fd, lines)
		fd.close()
		post_success(number, old_line, new_line)
	else:
		post_err('depri', 'NUMBER', None)
	sys.exit(0)


def prepend_todo(args):
	"""
	Take in the line number and prepend the rest of the arguments to the item
	specified by the line number.
	"""
	if args[0].isdigit():
		line_no = int(args.pop(0)) - 1
		prepend_str = concat(args, " ") + " "
		fd = open(CONFIG["TODO_FILE"], "r+")
		lines = fd.readlines()
		old_line = lines[line_no][:-1]
		if re.match("\([ABC]\)", lines[line_no]):
			lines[line_no] = re.sub("^(\([ABC]\)\s)",
					concat(["\g<1>", prepend_str]), lines[line_no])
		else:
			lines[line_no] = concat([prepend_str, lines[line_no]])
		new_line = lines[line_no][:-1]
		rewrite_file(fd, lines)
		post_success(line_no, old_line, new_line)
	else:
		post_error('prepend', 'NUMBER', 'string')
	sys.exit(0)

### End Post-production todo functions


### HELP
def cmd_help():
	print(concat(["Use", CONFIG["TODO_PY"], """-h for option help

Usage:""", CONFIG["TODO_PY"], """command [arg(s)]
	add "Item to do +project @context @{yyyy-mm-dd}"
		Adds 'Item to do +project @context @{yyyy-mm-dd}' to your todo.txt
		file.
		+project, @context, @{yyyy-mm-dd} are optional

	addm "First item to do +project @context @{yyyy-mm-dd}
		Second item to do +project @context @{yyyy-mm-dd}
		...
		Last item to do +project @context @{yyyy-mm-dd}"
		Adds each line as a separate item to your todo.txt file.

	append | app NUMBER "text to append"
		Append "text to append" to item NUMBER.

	depri | dp NUMBER
		Remove the priority of the item on line NUMBER.

	do NUMBER
		Marks item with corresponding number as done and moves it to your
		done.txt file.

	list | ls
		Lists all items in your todo.txt file sorted by priority.

	listdate | lsd
		Lists all items in your todo.txt file sorted by date.

	help | h
		Shows this message and exits.

	prepend | pre NUMBER "text to prepend"
		Add "text to prepend" to the beginning of the item.

	pri | p NUMBER [ABC]
		Add priority specified (A, B, or C) to item NUMBER.

	pull
		Pulls from the remote for your git repository.

	push
		Pushs to the remote for your git repository.

	status
		If using $(git --version) > 1.7, shows the status of your local
		git repository.

	log
		Shows the last two commits in your local git repository."""], " "))
	sys.exit(0)
### HELP


### List Printing Functions
def format_lines(lines, color_only=False):
	"""
	Take in a list of lines to do, return them formatted with the TERM_COLORS
	and organized based upon priority.
	"""
	i = 1
	default = TERM_COLORS["default"]
	plain = CONFIG["PLAIN"]
	no_priority = CONFIG["NO_PRI"]
	category = ""

	if color_only:
		formatted = []
	else:
		formatted = {"A" : [], "B" : [], "C" : [], "X" : []}

	for line in lines:
		r = re.match("\(([ABC])\)", line)
		if r:
			category = r.groups()[0]
			if plain:
				color = default
			else:
				color = TERM_COLORS[CONFIG["PRI_{0}".format(category)]]
			if no_priority:
				line = re.sub("^\([ABC]\)\s", "", line)
		else:
			category = "X"
			color = default

		l = concat([color, str(i), " ", line[:-1], default])
		if color_only:
			formatted.append(l)
		else:
			formatted[category].append(l)
		i += 1
	return formatted


def list_todo(plain=False, no_priority=False):
	"""
	Print the list of todo items in order of priority and position in the
	todo.txt file.
	"""
	lines = get_todos()
	formatted_lines = format_lines(lines)
	for category in ["A", "B", "C", "X"]:
		for line in formatted_lines[category]:
			print(line)
	print_x_of_y(lines, lines)


def _list_by_(by, regexp):
	lines = get_todos()
	nonetype = concat(["no", by])
	todo = {nonetype : []}
	by_list = []

	lines = format_lines(lines, color_only=True)
	for line in lines:
		#r = re.search(regexp, line)
		r = re.findall(regexp, line)
		line = concat([line, "\n"])
		if r:
			line = concat(["\t", line])
			if by == "date":
				for tup in r:
					#tup = r.groups()
					d = date(int(tup[0]), int(tup[1]), int(tup[2]))
					if d not in by_list:
						by_list.append(d)
						todo[d] = [line]
					else:
						todo[d].append(line)
			elif by == "project":
				for project in r:
					if project not in by_list:
						by_list.append(project)
						todo[project] = [line]
					else:
						todo[project].append(line)
		else:
			todo[nonetype].append(line)
	
	by_list.sort()
	sorted = []

	for b in by_list:
		sorted.append(concat([str(b), ":\n"]))
		sorted.extend(todo[b])
	
	sorted.extend(todo[nonetype])
	return (lines, sorted)


def list_date():
	"""
	List todo items by date @{yyyy-mm-dd}.
	"""
	lines, sortedl = _list_by_("date", "@\{(\d{4})-(\d{1,2})-(\d{1,2})\}")
	print(concat(sortedl)[:-1])
	print_x_of_y(sortedl, lines)


def list_project():
	"""
	Organizes items by project +prj they belong to.
	"""
	lines, sorted = _list_by_("project", "\+(\w+)")
	print(concat(sorted)[:-1])
	print_x_of_y(sorted, lines)
### End LP Functions


### Callback functions for options
def version(option, opt, value, parser):
	print("""TODO.TXT Command Line Interface v{version}

First release:
Original conception by: Gina Trapani (http://ginatrapani.org)
Original version project: https://github.com/ginatrapani/todo.txt-cli/
Contributors to original: https://github.com/ginatrapani/todo.txt-cli/network
Python version: https://github.com/sigmavirus24/Todo.txt-python/
Contributors to python version: \
https://github.com/sigmavirus24/Todo.txt-python/network
License: GPLv3
Code repository: \
https://github.com/sigmavirus24/Todo.txt-python/tree/master""".format(
	version=VERSION))
	sys.exit(0)
### End callback functions


if __name__ == "__main__" :
	CONFIG["TODO_PY"] = sys.argv[0]

	opts = OptionParser("Usage: %prog [options] action [arg(s)]")
	opts.add_option("-c", "--config", dest="config",
			type="string",
			nargs=1,
			help=\
			"Supply your own configuration file, must be an absolute path"
			)
	opts.add_option("-p", "--plain-mode", action="store_true",
			dest="plain",
			default=False,
			help="Turn off colors"
			)
	opts.add_option("-P", "--no-priority", action="store_true",
			dest="priority",
			default=False,
			help="Hide priority labels in list output"
			)
	opts.add_option("-t", "--prepend-date", action="store_true",
			dest="prepend_date",
			default=False,
			help=\
			"Prepend the current date to a task automattically when it's added."
			)
	opts.add_option("-V", "--version", action="callback",
			callback=version,
			nargs=0,
			help="Print version, license, and credits"
			)

	valid, args = opts.parse_args()

	get_config(valid.config)

	parse_valid(valid)

	commands = {
			# command 	: ( Args, Function),
			"add"		: ( True, add_todo),
			"addm"		: ( True, addm_todo),
			"app"		: ( True, append_todo),
			"append"	: ( True, append_todo),
			"do"		: ( True, do_todo),
			"p"			: ( True, prioritize_todo),
			"pri"		: ( True, prioritize_todo),
			"pre"		: ( True, prepend_todo),
			"prepend"	: ( True, prepend_todo),
			"dp"		: ( True, de_prioritize_todo),
			"depri"		: ( True, de_prioritize_todo),
			"ls"		: (False, list_todo),
			"list"		: (False, list_todo),
			"lsd"		: (False, list_date),
			"listdate"	: (False, list_date),
			"lsp"		: (False, list_project),
			"listproj"	: (False, list_project),
			"h"			: (False, cmd_help),
			"help"		: (False, cmd_help),
			# Git functions:
			"push"		: (False, _git_push),
			"pull"		: (False, _git_pull),
			"status"	: (False, _git_status),
			"log"		: (False, _git_log),
			}
	commandsl = commands.keys()

	if not len(args) > 0:
		args.append(CONFIG["TODOTXT_DEFAULT_ACTION"])
	while args:
		# ensure this doesn't error because of a faulty CAPS LOCK key
		arg = args.pop(0).lower()
		if arg in commandsl:
			if not commands[arg][0]:
				commands[arg][1]()
			else:
				if re.match("app(end)?", arg):
					commands[arg][1](args)
				elif re.match("p(ri)?", arg) or re.match("pre(pend)?", arg):
					commands[arg][1](args[:2])
				else:
					commands[arg][1](args.pop(0))
		else:
			commandsl.sort()
			commandsl = ["\t" + i for i in commandsl]
			print("Unable to find command: {0}".format(arg))
			print("Valid commands: ")
			print(concat(commandsl, "\n"))
			sys.exit(1)


# vim:set noet:
