#!/usr/bin/env python
import os
import ConfigParser
try:
	import git
except ImportError:
	print "You must download and install GitPython from:\
		http://pypi.python.org/pypi/GitPython"

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

HOME = os.getenv("HOME")
TODO_DIR = HOME + "/.todo"
GIT = git.Git(TODO_DIR)

def get_config():
	exists = true
	try:
		os.lstat(TODO_DIR)
	except:
		exists = false
	if exists:
		config_file = TODO_DIR + "/config"
		config = ConfigParser.ConfigParser()
		config.read(config_file)

def default_config():
	try:
		os.lstat(TODO_DIR)
	except:
		val = raw_input("Would you like to create a new git repository in " + \
				os.getcwd() + "? [y/N] ")
		if val == 'y':
			os.mkdirs(TODO_DIR)
			print(GIT.init())

# vim: set noet
