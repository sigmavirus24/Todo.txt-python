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
	fd = open(CONFIG["TODO_FILE"])
	lines = fd.readlines()
	fd.close()
	return lines

def concat(list, separator=''):
	return separator.join(list)

def _git_err(g):
	if g.stderr:
		print(g.stderr)
	else:
		print(g)
	sys.exit(g.status)


def _git_pull():
	try:
		print(CONFIG["GIT"].pull())
	except git.exc.GitCommandError, g:
		_git_err(g)


def _git_push():
	try:
		s = CONFIG["GIT"].push()
	except git.exc.GitCommandError, g:
		_git_err(g)
	if s:
		print(s)
	else:
		print("TODO: 'git push' executed.")


def _git_status():
	try:
		print(CONFIG["GIT"].status())
	except git.exc.GitCommandError, g:
		_git_err(g)


def _git_log():
	lines = CONFIG["GIT"].log("-2")
	flines = []
	for line in lines.split("\n"):
		if re.match("commit", line):
			flines.append(concat([TERM_COLORS["yellow"],
				line[:-1], TERM_COLORS["default"], "\n"]))
		else:
			flines.append(line + "\n")
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
		print("TODO: " + concat(files, " ") + " archived.")
	else:
		print("TODO: " + CONFIG["TODO_DIR"] + " archived.")


def print_x_of_y(x, y):
	print("--\nTODO: {0} of {1} tasks shown".format(len(x), len(y)))
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
				elif '/' in items[1] and '$' in items[1]:  # elision for path names
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
		user_email = user.name + "@" + getenv("HOSTNAME")
	print("First configure your local repository options.")
	ret = raw_input("git config user.name " + user_name + "? ")
	if ret:
		user_name = ret
	ret = raw_input("git config user.email " + user_email + "? ")
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
		raw_input("Press enter when you have initialized a bare" +\
				"repository on the remote or are ready to proceed.")
		local_branch = g.branch()
		if not local_branch:
			local_branch = "master"
		else:
			for l in local_branch.split("\n"):
				if re.match("^\*\s.*", l):
					local_branch = re.sub("^\*\s", "", l)
					break

		g.remote("add", "origin", remote_user + "@" + remote_host +\
				":" + remote_path)
		g.config("branch." + local_branch + ".remote", "origin")
		g.config("branch." + local_branch + ".merge", "refs/heads/" +\
				remote_branch)


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
		val = raw_input("Would you like to create a new git repository in " + \
				CONFIG["TODO_DIR"] + "? [y/N] ")
		if val == 'y':
			print(repo.init())
			val = raw_input(concat(
	["Would you like {prog} to help you".format(prog = CONFIG["TODO_PY"]),
	" configure your new git repository? [y/n] "]
			))
			if val == 'y':
				repo_config()

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
		if k != "GIT":
			if v in TO_CONFIG.keys():
				cfg.write("export " + k + "=" + TO_CONFIG[v] + "\n")
			else:
				cfg.write("export " + k + '="' + v + '"\n')
	repo.add([CONFIG["TODOTXT_CFG_FILE"], CONFIG["TODO_FILE"],
	CONFIG["TMP_FILE"], CONFIG["DONE_FILE"], CONFIG["REPORT_FILE"]])
	repo.commit("-m", CONFIG["TODO_PY"] + " initial commit.")
	#repo.push()
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
		line = re.sub("(\([ABC]\))", "\g<1>" + datetime.now().strftime(" %Y-%m-%d "),
			line)
	elif prepend:
		line = datetime.now().strftime("%Y-%m-%d ") + line
	fd.write(line + "\n")
	fd.close()
	s = "TODO: '{0}' added on line {1}.".format(
		line, l)
	#_git.add(CONFIG["TODO_FILE"])
	#_git.commit("-m", s)
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
		fd.seek(0, 0)
		fd.truncate(0)
		fd.writelines(lines)
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
	if arg2:
		print("'" + CONFIG["TODO_PY"] + " " + command + "' requires a(n) " +\
			arg1 + " then a " + arg2 + ".")
	else:
		print("'" + CONFIG["TODO_PY"] + " " + command + "' requires a(n) " +\
			arg1 + ".")


def post_success(item_no, old_line, new_line):
	print_str = "TODO: Item {0} changed from '{1}' to '{2}'.".format(
		item_no + 1, old_line, new_line)
	print(print_str)
	_git_commit([CONFIG["TODO_FILE"]], print_str)


def append_todo(args):
	if args[0].isdigit():
		line_no = int(args.pop(0)) - 1
		fd = open(CONFIG["TODO_FILE"], "r+")
		lines = fd.readlines()
		fd.seek(0, 0)
		fd.truncate(0)
		old_line = lines[line_no][:-1]
		lines[line_no] = old_line + " " + concat(args, " ") + "\n"
		new_line = lines[line_no][:-1]
		fd.writelines(lines)
		fd.close()
		post_success(line_no, old_line, new_line)
	else:
		post_error('append', 'NUMBER', 'string')
	sys.exit(0)


def prioritize_todo(args):
	if args[0].isdigit():
		line_no = int(args.pop(0)) - 1
		fd = open(CONFIG["TODO_FILE"], "r+")
		lines = fd.readlines()
		fd.seek(0, 0)
		fd.truncate(0)
		old_line = lines[line_no][:-1]
		new_pri = "(" + args[0] + ") "
		r = re.match("(\([ABC]\)\s).*", old_line)
		if r:
			lines[line_no] = re.sub(re.escape(r.groups()[0]), new_pri,
					lines[line_no])
		else:
			lines[line_no] = new_pri + lines[line_no]
		new_line = lines[line_no][:-1]
		fd.writelines(lines)
		fd.close()
		post_success(line_no, old_line, new_line)
	else:
		post_error('pri', 'NUMBER', 'capital letter')
	sys.exit(0)


def de_prioritize_todo(number):
	if number.isdigit():
		number = int(number) - 1
		fd = open(CONFIG["TODO_FILE"], "r+")
		lines = fd.readlines()
		old_line = lines[number][:-1]
		lines[number] = re.sub("(\([ABC]\)\s)", "", lines[number])
		new_line = lines[number][:-1]
		fd.seek(0, 0)
		fd.truncate(0)
		fd.writelines(lines)
		fd.close()
		post_success(number, old_line, new_line)
	else:
		post_err('depri', 'NUMBER', None)
	sys.exit(0)


def prepend_todo(args):
	if args[0].isdigit():
		line_no = int(args.pop(0)) - 1
		prepend_str = " ".join(args) + " "
		fd = open(CONFIG["TODO_FILE"], "r+")
		lines = fd.readlines()
		old_line = lines[line_no][:-1]
		if re.match("\([ABC]\)", lines[line_no]):
			lines[line_no] = re.sub("^(\([ABC]\)\s)",
					''.join(["\g<1>", prepend_str]), lines[line_no])
		else:
			lines[line_no] = prepend_str + lines[line_no]
		fd.seek(0, 0)
		fd.truncate(0)
		new_line = lines[line_no][:-1]
		fd.writelines(lines)
		post_success(line_no, old_line, new_line)
	else:
		post_error('prepend', 'NUMBER', 'string')
	sys.exit(0)

### End Post-production todo functions


### HELP
def cmd_help():
	print("Use " + CONFIG["TODO_PY"] + """ -h for option help

Usage: """ + CONFIG["TODO_PY"] + """ command [arg(s)]
	add "Item to do +project @context @{yyyy-mm-dd}"
		Adds 'Item to do +project @context @{yyyy-mm-dd}' to your todo.txt
		file.
		+project, @context, @{yyyy-mm-dd} are optional

	addm "First item to do +project @context @{yyyy-mm-dd}
		Second item to do +project @context @{yyyy-mm-dd}
		...
		Last item to do +project @context @{yyyy-mm-dd}"
		Adds each line as a separate item to your todo.txt file.

	do NUMBER
		Marks item with corresponding number as done and moves it to your
		done.txt file.

	list | ls
		Lists all items in your todo.txt file sorted by priority.

	listdate | lsd
		Lists all items in your todo.txt file sorted by date.

	help | h
		Shows this message and exits.

	pull
		Pulls from the remote for your git repository.

	push
		Pushs to the remote for your git repository.

	status
		If using $(git --version) > 1.7, shows the status of your local
		git repository.

	log
		Shows the last two commits in your local git repository.""")
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

		l = color + str(i) + " " + line[:-1] + default
		if color_only:
			formatted.append(l)
		else:
			formatted[category].append(l)
		i += 1
	return formatted


def list_todo(plain = False, no_priority = False):
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


def list_date():
	"""
	List todo items by date @{yyyy-mm-dd}.
	"""
	lines = get_todos()
	todo = {"nodate" : []}
	dates = []

	lines = format_lines(lines, color_only = True)
	for line in lines:
		_re = re.search("@\{(\d{4})-(\d{1,2})-(\d{1,2})\}", line)
		line += "\n"
		if _re:
			tup = _re.groups()
			d = date(int(tup[0]), int(tup[1]), int(tup[2]))
			if d not in dates:
				dates.append(d)
				todo[d] = [line]
			else:
				todo[d].append(line)
		else:
			todo["nodate"].append(line)

	dates.sort()
	sortedl = []

	for d in dates:
		for l in todo[d]:
			sortedl.append(l)

	sortedl += todo["nodate"]
	print("".join(sortedl)[:-1])
	print_x_of_y(sortedl, lines)
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
	version = VERSION))
	sys.exit(0)
### End callback functions


if __name__ == "__main__" :
	CONFIG["TODO_PY"] = sys.argv[0]

	opts = OptionParser("Usage: %prog [options] action [arg(s)]")
	opts.add_option("-c", "--config", dest = "config",
			type = "string",
			nargs = 1,
			help = \
			"Supply your own configuration file, must be an absolute path"
			)
	opts.add_option("-p", "--plain-mode", action = "store_true",
			dest = "plain",
			default = False,
			help = "Turn off colors"
			)
	opts.add_option("-P", "--no-priority", action = "store_true",
			dest = "priority",
			default = False,
			help = "Hide priority labels in list output"
			)
	opts.add_option("-t", "--prepend-date", action = "store_true",
			dest = "prepend_date",
			default = False,
			help = \
			"Prepend the current date to a task automattically when it's added."
			)
	opts.add_option("-V", "--version", action = "callback",
			callback = version,
			nargs = 0,
			help = "Print version, license, and credits"
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
			"h"			: (False, cmd_help),
			"help"		: (False, cmd_help),
			# Git functions:
			"push"		: (False, _git_push),
			"pull"		: (False, _git_pull),
			"status"	: (False, _git_status),
			"log"		: (False, _git_log),
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
				if re.match("app(end)?", arg):
					#print("APPEND: " + " ".join(args))
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
			print("\n".join(commandsl))
			sys.exit(1)


# vim:set noet:
