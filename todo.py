#!/usr/bin/env python

# TODO.TXT-CLI-python
# Copyright (C) 2011  Sigmavirus24
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# TLDR: This is licensed under the GPLv3. See LICENSE for more details.

import os
import re
import sys
from optparse import OptionParser
from datetime import datetime, date

VERSION = "development-branch"
REVISION = "$Id$"

try:
    import readline
except ImportError:
    # This isn't crucial to the execution of the script.
    # But it is a nice feature to have. Sucks to be an OSX user.
    pass

try:
    # Python 3 moved the built-in intern() to sys.intern()
    intern = sys.intern
except AttributeError:
    pass

try:
    input = raw_input
except NameError:
    # Python 3 renamed raw_input to input
    pass

try:
    from string import uppercase
except ImportError:
    # Python 3 again
    from string import ascii_uppercase as uppercase
PRIORITIES = uppercase[:24]

# concat() is necessary long before the grouping of function declarations
concat = lambda str_list, sep='': sep.join(str_list)
_path = lambda p: os.path.abspath(os.path.expanduser(p))
_pathc = lambda plist: _path(concat(plist))

TERM_COLORS = {
        "black": "\033[0;30m", "red": "\033[0;31m",
        "green": "\033[0;32m", "brown": "\033[0;33m",
        "blue": "\033[0;34m", "purple": "\033[0;35m",
        "cyan": "\033[0;36m", "light grey": "\033[0;37m",
        "dark grey": "\033[1;30m", "light red": "\033[1;31m",
        "light green": "\033[1;32m", "yellow": "\033[1;33m",
        "light blue": "\033[1;34m", "light purple": "\033[1;35m",
        "light cyan": "\033[1;36m", "white": "\033[1;37m",
        "default": "\033[0m", "reverse": "\033[7m",
        "bold": "\033[1m",
        }

TODO_DIR = _path("~/.todo")
CONFIG = {
        "TODO_DIR": TODO_DIR,
        "TODOTXT_DEFAULT_ACTION": "",
        "TODOTXT_CFG_FILE": _pathc([TODO_DIR, "/config"]),
        "TODO_FILE": _pathc([TODO_DIR, "/todo.txt"]),
        "TMP_FILE": _pathc([TODO_DIR, "/todo.tmp"]),
        "DONE_FILE": _pathc([TODO_DIR, "/done.txt"]),
        "REPORT_FILE": _pathc([TODO_DIR, "/report.txt"]),
        "USE_GIT": False,
        "PLAIN": False,
        "NO_PRI": False,
        "PRE_DATE": False,
        "INVERT": False,
        "HIDE_PROJ": False,
        "HIDE_CONT": False,
        "HIDE_DATE": False,
        "LEGACY": False,
        }

for p in PRIORITIES:
    CONFIG["PRI_{0}".format(p)] = "default"
del(p, TODO_DIR)


### Helper Functions
def todo_padding(include_done=False):
    lines = [line for line in iter_todos(include_done)]
    i = len(lines)
    pad = 1
    while i >= 10:
        pad += 1
        i /= 10
    return pad


def iter_todos(include_done=False):
    """
    Opens the file in read-only mode, and returns an iterator for the todos.
    """
    files = [CONFIG["TODO_FILE"]]
    if not os.path.isfile(files[0]):
        return
    if include_done and os.path.isfile(CONFIG["DONE_FILE"]):
        files.append(CONFIG["DONE_FILE"])
    for f in files:
        with open(f) as fd:
            for line in fd:
                yield line


def separate_line(number):
    """
    Takes an integer and returns a string and a list. The string is the item at
    that position in the list. The list is the rest of the todos.

    If the todo.txt file is empty, separate = lines = None. If the number is
    invalid separate = None, lines != None.
    """
    lines = [line for line in iter_todos()]
    separate = None
    if lines and number - 1 < len(lines) and 0 <= number - 1:
        separate = lines.pop(number - 1)
    return separate, lines


def rewrite_file(fd, lines):
    """
    Simple wrapper for three lines used all too frequently.
    Sets the access position to the beginning of the file, truncates the
    file's length to 0 and then writes all the lines to the file.
    """
    fd.seek(0, 0)
    fd.truncate(0)
    fd.writelines(lines)


def rewrite_and_post(line_no, old_line, new_line, lines):
    """
    Wraps the following code used frequently in post-production functions.
    """
    with open(CONFIG["TODO_FILE"], "w") as fd:
        rewrite_file(fd, lines)
    post_success(line_no, old_line, new_line)


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
    except git.exc.GitCommandError as g:
        _git_err(g)


def _git_push():
    """
    Push commits made locally to the remote.
    """
    try:
        s = CONFIG["GIT"].push()
    except git.exc.GitCommandError as g:
        _git_err(g)
    if s:
        print(s)
    else:
        print("TODO: 'git push' executed.")


def _git_status():
    """
    Print the status of the local repository if the version of git is 1.7
    or later.
    """
    try:
        print(CONFIG["GIT"].status())
    except git.exc.GitCommandError as g:
        _git_err(g)


def _git_log():
    """
    Print the two latest commits in the local repository's log.
    """
    print(CONFIG["GIT"].log("-5", "--oneline"))


def _git_commit(files, message):
    """
    Make a commit to the git repository.
        * files should be a list like ['file_a', 'file_b'] or ['-a']
    """
    if len(message) > 49:
        message = concat([message[:45], "...'\n\n", message])
    try:
        CONFIG["GIT"].commit(files, "-m", message)
    except git.exc.GitCommandError as g:
        _git_err(g)
    committed = CONFIG["TODO_DIR"] if "-a" in files else concat(files, ", ")
    print(concat(["TODO: ", committed, " archived."]))


def prompt(*args, **kwargs):
    """
    Sanitize input collected with raw_input().
    Prevents someone from entering 'y\' to attempt to break the program.

    args can be any collection of strings that require formatting.
    kwargs will collect the tokens and values.
    """
    args = list(args)  # [a for a in args]
    args.append(' ')
    prompt_str = concat(args).format(**kwargs)
    raw = input(prompt_str)
    return re.sub(r"\\", "", raw)


def print_x_of_y(x, y):
    t_str = "--\nTODO: {0} of {1} tasks shown"
    if len(x) > len(y):  # EXTREMELY hack-ish
        print(t_str.format(len(y), len(y)))  # There can't logically be
            # more lines of items to do than there actually are.
    else:
        print(t_str.format(len(x), len(y)))


def test_separated(removed, lines, line_no):
    if not (removed or lines):
        print("{0}: No such todo.".format(line_no))
        return True
    return False
### End Helper Functions


### Configuration Functions
def get_config(config_name="", dir_name=""):
    """
    Read the config file
    """
    if config_name:
        CONFIG["TODOTXT_CFG_FILE"] = config_name
    if dir_name:
        dir_name = _path(dir_name)
        CONFIG["TODO_DIR"] = dir
        CONFIG["TODOTXT_CFG_FILE"] = _pathc([dir_name, "/config"])
        CONFIG["TODO_FILE"] = _pathc([dir_name, "/todo.txt"])
        CONFIG["DONE_FILE"] = _pathc([dir_name, "/done.txt"])

    os.environ["TODO_DIR"] = CONFIG["TODO_DIR"]

    if CONFIG["TODOTXT_CFG_FILE"]:
        config_file = CONFIG["TODOTXT_CFG_FILE"]

    config_file = _path(config_file)
    if not (os.access(CONFIG["TODO_DIR"],
        os.F_OK | os.R_OK | os.W_OK | os.X_OK) and \
                os.access(config_file, os.F_OK | os.R_OK | os.W_OK)):
        default_config()
    else:
        FROM_CONFIG = {}
        for key in list(TERM_COLORS.keys()):
            bkey = concat(["$", re.sub(' ', '_', key).upper()])
            FROM_CONFIG[bkey] = key

        skip_re = re.compile('^\s*(#|$)')
        strip_re = re.compile('\w+\s([A-Za-z_$="./]+).*')
        pri_re = re.compile('(PRI_[A-X]|DEFAULT)')

        with open(config_file, 'r') as f:
            for line in f:
                if not skip_re.match(line):
                    # Extract VAR=VAL and then split VAR and VAL
                    items = strip_re.sub('\g<1>', line.strip()).split('=')
                    items[1] = items[1].strip('"')

                    if pri_re.match(items[0]):
                        CONFIG[items[0]] = FROM_CONFIG[items[1]]
                    elif items[0] == "USE_GIT":
                        CONFIG["USE_GIT"] = False
                        if items[1] == "True":
                            CONFIG["USE_GIT"] = True
                    else:
                        items[1] = os.path.expandvars(items[1])
                        CONFIG[items[0]] = items[1]

                    # make expandvars work for our vars too
                    os.environ[items[0]] = items[1]

    if CONFIG["USE_GIT"]:
        global git
        try:
            import git
        except ImportError:
            if sys.version_info < (3, 0):
                print("You must download and install GitPython from: \
                        http://pypi.python.org/pypi/GitPython")
            else:
                print("GitPython is not available for Python3 last I checked.")
            CONFIG["USE_GIT"] = False
            return

        CONFIG["GIT"] = git.Git(CONFIG["TODO_DIR"])
        if CONFIG["TODOTXT_CFG_FILE"] not in CONFIG["GIT"].ls_files():
            CONFIG["GIT"].add([CONFIG["TODOTXT_CFG_FILE"]])
        git_functions()


def git_functions():
    global repo_config

    def repo_config():
        """
        Help the user configure their git repository.
        """
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
            user_email = concat([user_name, "@", getenv("HOSTNAME")])

        print("First configure your local repository options.")
        ret = prompt("git config user.name ", user_name, "?")
        if ret:
            user_name = ret
        ret = prompt("git config user.email ", user_email, "?")
        if ret:
            user_email = ret

        g.config("user.name", user_name)
        g.config("user.email", user_email)

        # remote configuration
        ret = prompt("Would you like to add a remote repository?")
        yes_re = re.compile("y(?:es)?", re.I)
        if yes_re.match(ret):
            remote_host = None
            remote_path = None
            remote_user = None
            remote_branch = None

            def __while_prompt__(prompt_str, error_string):
                ret = None
                while not ret:
                    ret = prompt(prompt_str)
                    if not ret:
                        print(error_string)
                return ret

            remote_host = __while_prompt__("Remote hostname:",
                "Please enter the remote's hostname.")
            remote_path = __while_prompt__("Remote path:",
                "Please enter the path to the remote's repository.")
            remote_path = __while_prompt__("Remote user:",
                "Please enter the user on the remote machine.")
            remote_branch = __while_prompt__("Remote branch:",
                "Please enter the branch to push to on the remote machine.")

            prompt("Press enter when you have initialized a bare\n",
                " repository on the remote or are ready to proceed.")
            local_branch = g.branch()
            if not local_branch:
                local_branch = "master"
            else:
                branch_re = re.compile('^\*\s.*')
                for l in local_branch.split("\n"):
                    if branch_re.match(l):
                        local_branch = branch_re.sub("", l)
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

    if not os.path.exists(CONFIG["TODO_DIR"]):
        os.makedirs(CONFIG["TODO_DIR"])

    # touch/create files needed for the operation of the script
    for item in ['TODO_FILE', 'TMP_FILE', 'DONE_FILE', 'REPORT_FILE']:
        if CONFIG[item]:
            touch(CONFIG[item])

    cfg = open(concat([CONFIG["TODO_DIR"], "/config"]), 'w')

    # set the defaults for the colors
    CONFIG["PRI_A"] = "yellow"
    CONFIG["PRI_B"] = "green"
    CONFIG["PRI_C"] = "light blue"
    CONFIG["PRI_X"] = "white"

    TO_CONFIG = {}
    for key in list(TERM_COLORS.keys()):
        bkey = concat(["$", re.sub(' ', '_', key).upper()])
        TO_CONFIG[key] = bkey

    for k, v in CONFIG.items():
        if v and (k not in ("GIT", "INVERT", "LEGACY", "PLAIN", "PRE_DATE",
                "HIDE_DATE", "HIDE_CONT", "HIDE_PROJ", "NO_PRI")):
            if isinstance(v, bool):
                v = int(v)
            if v in list(TO_CONFIG.keys()):
                cfg.write(concat(["export ", k, "=", TO_CONFIG[v], "\n"]))
            else:
                cfg.write(concat(["export ", k, '="', str(v), '"\n']))

    val = prompt("Would you like to use git with your to manage\n ",
        CONFIG["TODO_DIR"], "? [y/N]")
    yes_re = re.compile('y(?:es)?', re.I)
    if yes_re.match(val):
        CONFIG["USE_GIT"] = True
        cfg.write("export USE_GIT=1\n")
        repo = CONFIG["GIT"] = git.Git(CONFIG["TODO_DIR"])
        # ^: Might not be necessary
        try:
            repo.status()
        except git.exc.GitCommandError as g:
            val = prompt("Would you like to create a new git repository in\n ",
                    CONFIG["TODO_DIR"], "? [y/N]")
            if yes_re.match(val):
                print(repo.init())
                val = prompt("Would you like {prog} to help\n you",
                        " configure your new git repository? [y/n]",
                        prog=CONFIG["TODO_PY"])
                if yes_re.match(val):
                    repo_config()
            # Untested addition
            else:
                val = prompt("Would you like {prog} to clone\n a",
                        " remote repository for you? [y/N]",
                        prog=CONFIG["TODO_PY"])
                if yes_re.match(val):
                    val = prompt("Please enter user@remote:/path/to/repo. ")
                    r = Repo.clone_from(val, CONFIG["TODO_DIR"])
        files = [CONFIG["TODOTXT_CFG_FILE"], CONFIG["TODO_FILE"]]
        for setting in ["TMP_FILE", "DONE_FILE", "REPORT_FILE"]:
            if CONFIG[setting]:
                files.append(CONFIG[setting])
        repo.add(files)
        repo.commit("-m", CONFIG["TODO_PY"] + " initial commit.")
    else:
        cfg.write("export USE_GIT=False\n")

    cfg.close()
    print(concat(["Default configuration completed. Please ",
        "re-run\n {prog} with '-h' and 'help' separately.".format(
            prog=CONFIG["TODO_PY"])]))
    sys.exit(0)
### End Config Functions


### New todo Functions
def add_todo(args):
    """
    Add a new item to the list of things todo.
    """
    if str(args) == args:
        line = args
    elif len(args) >= 1:
        line = concat(args, " ")
    else:
        line = prompt("Add:")
    prepend = CONFIG["PRE_DATE"]
    l = len([1 for l in iter_todos()]) + 1
    pri_re = re.compile('(\([A-X]\))')
    if pri_re.match(line) and prepend:
        line = pri_re.sub(concat(["\g<1>",
            datetime.now().strftime(" %Y-%m-%d ")]),
            line)
    elif prepend:
        line = concat([datetime.now().strftime("%Y-%m-%d "), line])
    with open(CONFIG["TODO_FILE"], "a") as fd:
        fd.write(concat([line, "\n"]))
    s = "TODO: '{0}' added on line {1}.".format(
        line, l)
    print(s)
    if CONFIG["USE_GIT"]:
        _git_commit([CONFIG["TODO_FILE"]], s)


def addm_todo(args):
    """
    Add new items to the list of things todo.
    """
    if str(args) == args:
        lines = args
    else:
        lines = concat(args, " ")
    lines = lines.split("\n")
    list(map(add_todo, lines))  # Python 3 requirement
### End new todo functions


### Start do/del functions
def do_todo(line):
    """
    Mark an item on a specified line as done.
    """
    if not line.isdigit():
        print("Usage: {0} do item#".format(CONFIG["TODO_PY"]))
    else:
        removed, lines = separate_line(int(line))
        if test_separated(removed, lines, line):
            return

        fd = open(CONFIG["TODO_FILE"], "w")
        rewrite_file(fd, lines)
        fd.close()

        today = datetime.now().strftime("%Y-%m-%d")
        removed = concat(["x", today,
            re.sub("\([A-X]\)\s?", "", removed)], " ")

        files = [CONFIG["TODO_FILE"]]
        if CONFIG["DONE_FILE"]:
            with open(CONFIG["DONE_FILE"], "a") as fd:
                fd.write(removed)
            files.append(CONFIG["DONE_FILE"])

        print(removed[:-1])
        print("TODO: Item {0} marked as done.".format(line))
        if CONFIG["USE_GIT"]:
            _git_commit(files, removed)


def delete_todo(line):
    """
    Delete an item without marking it as done.
    """
    if not line.isdigit():
        print("Usage: {0} (del|rm) item#".format(CONFIG["TODO_PY"]))
    else:
        removed, lines = separate_line(int(line))
        if test_separated(removed, lines, line):
            return

        with open(CONFIG["TODO_FILE"], "w") as fd:
            rewrite_file(fd, lines)

        removed = "'{0}' deleted.".format(removed[:-1])
        print(removed)
        print("TODO: Item {0} deleted.".format(line))
        if CONFIG["USE_GIT"]:
            _git_commit([CONFIG["TODO_FILE"]], removed)
### End do/del Functions


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
    old_line = old_line.rstrip()
    new_line = new_line.rstrip()
    print_str = "TODO: Item {0} changed from '{1}' to '{2}'.".format(
        item_no, old_line, new_line)
    print(print_str)
    if CONFIG["USE_GIT"]:
        _git_commit([CONFIG["TODO_FILE"]], print_str)


def append_todo(args):
    """
    Append text to the item specified.
    """
    if args[0].isdigit():
        line_no = int(args.pop(0))
        old_line, lines = separate_line(line_no)
        if test_separated(old_line, lines, line_no):
            return

        new_line = concat([concat([old_line[:-1],
            concat(args, " ")], " "), "\n"])
        lines.insert(line_no - 1, new_line)

        rewrite_and_post(line_no, old_line, new_line, lines)
    else:
        post_error('append', 'NUMBER', 'string')


def prioritize_todo(args):
    """
    Add or modify the priority of the specified item.
    """
    if args[0].isdigit() and len(args[1]) == 1 and args[1] in PRIORITIES:
        line_no = int(args.pop(0))
        old_line, lines = separate_line(line_no)
        if test_separated(old_line, lines, line_no):
            return

        new_pri = concat(["(", args[0], ") "])
        r = re.match("(\([A-X]\)\s).*", old_line)
        if r:
            new_line = re.sub(re.escape(r.groups()[0]), new_pri, old_line)
        else:
            new_line = concat([new_pri, old_line])

        lines.insert(line_no - 1, new_line)

        rewrite_and_post(line_no, old_line, new_line, lines)
    else:
        post_error('pri', 'NUMBER', 'capital letter in [A-X]')


def de_prioritize_todo(number):
    """
    Remove priority markings from the beginning of the line if they're there.
    Don't complain otherwise.
    """
    if number.isdigit():
        number = int(number)
        old_line, lines = separate_line(number)
        if test_separated(old_line, lines, number):
            return

        new_line = re.sub("(\([A-X]\)\s)", "", old_line)
        lines.insert(number - 1, new_line)

        rewrite_and_post(number, old_line, new_line, lines)
    else:
        post_err('depri', 'NUMBER', None)


def prepend_todo(args):
    """
    Take in the line number and prepend the rest of the arguments to the item
    specified by the line number.
    """
    if args[0].isdigit():
        line_no = int(args.pop(0))
        prepend_str = concat(args, " ") + " "
        old_line, lines = separate_line(line_no)
        if test_separated(old_line, lines, line_no):
            return

        pri_re = re.compile('^(\([A-X]\)\s)')

        if pri_re.match(old_line):
            new_line = pri_re.sub(concat(["\g<1>", prepend_str]), old_line)
        else:
            new_line = concat([prepend_str, old_line])

        lines.insert(line_no - 1, new_line)

        rewrite_and_post(line_no, old_line, new_line, lines)
    else:
        post_error('prepend', 'NUMBER', 'string')
### End Post-production todo functions


### HELP
def cmd_help():
    print(concat(["Use", CONFIG["TODO_PY"], "-h for option help"], " "))
    print("")
    print(concat(["Usage:", CONFIG["TODO_PY"], "command [arg(s)]"], " "))
    print('\tadd | a "Item to do +project @context #{yyyy-mm-dd}"')
    print(concat(["\t\tAdds 'Item to do +project @context",
        " #{yyyy-mm-dd}' to your todo.txt"]))
    print("\t\tfile.")
    print("\t\t+project, @context, #{yyyy-mm-dd} are optional")
    print("")
    print('\taddm "First item to do +project @context #{yyyy-mm-dd}')
    print("\t\tSecond item to do +project @context #{yyyy-mm-dd}")
    print("\t\t...")
    print("\t\tLast item to do +project @context #{yyyy-mm-dd}")
    print("\t\tAdds each line as a separate item to your todo.txt file.")
    print("")
    print('\tappend | app NUMBER "text to append"')
    print('\t\tAppend "text to append" to item NUMBER.')
    print("")
    print("\tdepri | dp NUMBER")
    print("\t\tRemove the priority of the item on line NUMBER.")
    print("")
    print("\tdo NUMBER")
    print("\t\tMarks item with corresponding number as done and moves it to")
    print("\t\tyour done.txt file.")
    print("")
    print("\tlist | ls")
    print("\t\tLists all items in your todo.txt file sorted by priority.")
    print("")
    print("\tlistcon | lsc")
    print("\t\tLists all items in your todo.txt file sorted by context.")
    print("")
    print("\tlistdate | lsd")
    print("\t\tLists all items in your todo.txt file sorted by date.")
    print("")
    print("\tlistproj | lsp")
    print("\t\tLists all items in your todo.txt file sorted by project title.")
    print("")
    print("\thelp | h")
    print("\t\tDisplay this message and exit.")
    print("")
    print('\tprepend | pre NUMBER "text to prepend"')
    print('\t\tAdd "text to prepend" to the beginning of the item.')
    print("")
    print("\tpri | p NUMBER [A-X]")
    print("\t\tAdd priority specified (A, B, C, etc.) to item NUMBER.")
    if CONFIG["USE_GIT"]:
        print("")
        print("\tpull")
        print("\t\tPulls from the remote for your git repository.")
        print("")
        print("\tpush")
        print("\t\tPushes to the remote for your git repository.")
        print("")
        print("\tstatus")
        print("\t\tIf using $(git --version) > 1.7, shows the status of your")
        print("\t\tlocal git repository.")
        print("")
        print("\tlog")
        print("\t\tShows the last five commits in your local git repository.")
    sys.exit(0)
### HELP


### List Printing Functions
def format_lines(color_only=False, include_done=False):
    """
    Take in a list of lines to do, return them formatted with the TERM_COLORS
    and organized based upon priority.
    """
    plain = CONFIG["PLAIN"]
    no_priority = CONFIG["NO_PRI"]
    default = CONFIG.get("DEFAULT", "default")
    default = TERM_COLORS[default] if not plain else ""
    invert = TERM_COLORS["reverse"] if CONFIG["INVERT"] else ""
    pri_re = re.compile('^\(([A-W])\)\s')
    category = ""
    pad = todo_padding(include_done)
    colors = set(TERM_COLORS.keys())  # Supposedly sets are faster for look-ups

    formatted = []
    if not color_only:
        formatted = dict(zip(PRIORITIES, [[] for i in PRIORITIES]))

    for (i, line) in enumerate(iter_todos(include_done)):
        category = "X"
        color = default

        r = pri_re.match(line)
        if r:
            category = r.groups()[0]
            color_name = CONFIG["PRI_{0}".format(category)]

            if not plain and color_name in colors:
                color = TERM_COLORS[color_name]
            if no_priority:
                line = pri_re.sub("", line)

        i = str(i + 1).zfill(pad)
        l = concat([color, invert, i, " ", line[:-1], default, "\n"])

        if color_only:
            formatted.append(l)
        else:
            formatted[category].append(l)

    return formatted


def _legacy_sort(items):
    """
    Sort items alphabetically, i.e.
    # (pri_a) Abc
    # (pri_a) Bcd
    # (pri_b) Abc
    # (pri_c) Bcd
    etc., etc., etc.
    """
    line_re = re.compile('^.*\d+\s(\([A-X]\)\s)?')
    # The .* in the regexp is needed for the \033[* codes
    items = [(line_re.sub("", i), i) for i in items]
    items.sort()
    items = [line for (k, line) in items]
    return items


def _list_(by, regexp):
    """
    Master list_*() function.
    """
    nonetype = concat(["no", by])
    todo = {nonetype: []}
    by_list = []
    sorted = []

    if by in ["date", "project", "context"]:
        lines = format_lines(color_only=True)
        regexp = re.compile(regexp)
        for line in lines:
            match = regexp.findall(line)
            if match:
                line = concat(["\t", line])
                for i in match:
                    if by == "date":
                        i = date(int(i[0]), int(i[1]), int(i[2]))
                    if i not in by_list:
                        by_list.append(i)
                        todo[i] = [line]
                    else:
                        todo[i].append(line)
            else:
                todo[nonetype].append(line)
    elif by == "pri":
        lines = format_lines()
        todo.update(lines)
        by_list = list(PRIORITIES)

    by_list.sort()

    regstr = '(\+\w+\s?)' if CONFIG["HIDE_PROJ"] else ''
    hide_proj_re = re.compile(regstr)
    regstr = '(@\w+\s?)' if CONFIG["HIDE_CONT"] else ''
    hide_cont_re = re.compile(regstr)
    regstr = '(#\{\d+-\d+-\d+\}\s?)' if CONFIG["HIDE_DATE"] else ''
    hide_date_re = re.compile(regstr)

    for b in by_list:
        todo[b] = [hide_proj_re.sub("", l) for l in todo[b]]
        todo[b] = [hide_cont_re.sub("", l) for l in todo[b]]
        todo[b] = [hide_date_re.sub("", l) for l in todo[b]]
        if CONFIG["LEGACY"]:
            todo[b] = _legacy_sort(todo[b])
        if by != "pri":
            sorted.append(concat([str(b), ":\n"]))
        sorted.extend(todo[b])

    sorted.extend(todo[nonetype])
    return (lines, sorted)


def _list_by_(*args):
    """
    Print lines matching items in args
    Called when the user does:
        todo.py ls search-term1 search-term2 ...
    """
    esc = re.escape  # keep line length down
    relist = [re.compile(concat(["\s?(", esc(arg), ")\s?"]), re.I) for arg in args]
    del(esc)  # don't need it anymore

    alines = format_lines()  # Retrieves all lines.
    lines = []
    for p in PRIORITIES:
        lines.extend(alines[p])

    alines = lines[:]
    matched_lines = []

    for regexp in relist:
        matched_lines = [line for line in lines if regexp.search(line)]
        lines = matched_lines[:]

    if lines:
        print(concat(lines)[:-1])
    print_x_of_y(lines, alines)


def list_todo(args=None, plain=False, no_priority=False):
    """
    Print the list of todo items in order of priority and position in the
    todo.txt file.
    """
    if not args:
        lines, sorted = _list_("pri", "")
        print(concat(sorted)[:-1])
        print_x_of_y(sorted, sorted)
    else:
        _list_by_(*args)


def list_all():
    """
    Print the list of todo items in order of priority and then print the
    done.txt file.
    """
    formatted = format_lines(include_done=True)
    lines = []
    for p in PRIORITIES:
        lines.extend(formatted[p])
    if lines:
        print(concat(lines)[:-1])
    print_x_of_y(lines, lines)


def list_date():
    """
    List todo items by date #{yyyy-mm-dd}.
    """
    lines, sorted = _list_("date", "#\{(\d{4})-(\d{1,2})-(\d{1,2})\}")
    print(concat(sorted)[:-1])
    print_x_of_y(sorted, lines)


def list_project():
    """
    Organizes items by project +prj they belong to.
    """
    lines, sorted = _list_("project", "\+(\w+)")
    print(concat(sorted)[:-1])
    print_x_of_y(sorted, lines)


def list_context():
    """
    Organizes items by context @context associated with them.
    """
    lines, sorted = _list_("context", "@(\w+)")
    print(concat(sorted)[:-1])
    print_x_of_y(sorted, lines)
### End LP Functions


### Callback functions for options
def version(option, opt, value, parser):
    print("""TODO.TXT Command Line Interface v{version}-{id}

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
        version=VERSION, id=REVISION))
    sys.exit(0)


def toggle_opt(option, opt_str, val, parser):
    """
    Check opt_str to see if it's one of ['-+', '-@', '-#', '-p', '-P', '-t',
    '--plain-mode', '--no-priority', '--prepend-date', '-i',
    '--invert-colors'] and toggle that option in CONFIG.
    """
    toggle_dict = {"-+": "HIDE_PROJ", "-@": "HIDE_CONT", "-#": "HIDE_DATE",
            "-p": "PLAIN", "-P": "NO_PRI", "-t": "PRE_DATE",
            "--plain-mode": "PLAIN", "--no-priority": "NO_PRI",
            "--prepend-date": "PRE_DATE", "-i": "INVERT",
            "--invert-colors": "INVERT", "-l": "LEGACY",
            "--legacy": "LEGACY",
            }
    if opt_str in list(toggle_dict.keys()):
        CONFIG[toggle_dict[opt_str]] = not CONFIG[toggle_dict[opt_str]]
### End callback functions


### Main components
def opt_setup():
    opts = OptionParser("Usage: %prog [options] action [arg(s)]")
    opts.add_option("-c", "--config", dest="config", default="",
            type="string",
            nargs=1,
            help=concat(["Supply your own configuration file,",
                "must be an absolute path"])
            )
    opts.add_option("-d", "--dir", dest="todo_dir", default="",
            type="string",
            nargs=1,
            help="Directory you wish {prog} to use.".format(
                prog=CONFIG["TODO_PY"])
            )
    opts.add_option("-p", "--plain-mode", action="callback",
            callback=toggle_opt,
            help="Toggle coloring of items"
            )
    opts.add_option("-P", "--no-priority", action="callback",
            callback=toggle_opt,
            help="Toggle display of priority labels"
            )
    opts.add_option("-t", "--prepend-date", action="callback",
            callback=toggle_opt,
            help="Toggle whether the date is prepended to new items."
            )
    opts.add_option("-V", "--version", action="callback",
            callback=version,
            nargs=0,
            help="Print version, license, and credits"
            )
    opts.add_option("-i", "--invert-colors", action="callback",
            callback=toggle_opt,
            help="Toggle coloring the text of items or background of items."
            )
    opts.add_option("-l", "--legacy", action="callback",
            callback=toggle_opt,
            help="Toggle organization of items in the old manner."
            )
    opts.add_option("-+", action="callback", callback=toggle_opt,
            help="Toggle display of +projects in-line with items."
            )
    opts.add_option("-@", action="callback", callback=toggle_opt,
            help="Toggle display of @contexts in-line with items."
            )
    opts.add_option("-#", action="callback", callback=toggle_opt,
            help="Toggle display of #{dates} in-line with items."
            )
    return opts


if __name__ == "__main__":
    CONFIG["TODO_PY"] = sys.argv[0]
    opts = opt_setup()

    valid, args = opts.parse_args()

    get_config(valid.config, valid.todo_dir)

    commands = {
            # command 	: ( Args, Function),
            "a"			: (True, add_todo),
            "add"		: (True, add_todo),
            "addm"		: (True, addm_todo),
            "app"		: (True, append_todo),
            "append"	: (True, append_todo),
            "do"		: (True, do_todo),
            "p"			: (True, prioritize_todo),
            "pri"		: (True, prioritize_todo),
            "pre"		: (True, prepend_todo),
            "prepend"	: (True, prepend_todo),
            "dp"		: (True, de_prioritize_todo),
            "depri"		: (True, de_prioritize_todo),
            "del"		: (True, delete_todo),
            "rm"		: (True, delete_todo),
            "ls"		: (True, list_todo),
            "list"		: (True, list_todo),
            "listall"	: (False, list_all),
            "lsa"		: (False, list_all),
            "lsc"		: (False, list_context),
            "listcon"	: (False, list_context),
            "lsd"		: (False, list_date),
            "listdate"	: (False, list_date),
            "lsp"		: (False, list_project),
            "listproj"	: (False, list_project),
            "h"			: (False, cmd_help),
            "help"		: (False, cmd_help),
            }
    if CONFIG["USE_GIT"]:
        commands.update(
                [("push", 	(False, _git_push)),
                ("pull", 	(False, _git_pull)),
                ("status", 	(False, _git_status)),
                ("log", 	(False, _git_log))]
                )

    commandsl = [intern(key) for key in list(commands.keys())]

    if not len(args) > 0:
        args.append(CONFIG["TODOTXT_DEFAULT_ACTION"])

    all_re = re.compile('((app|pre)(?:end)?|p(?:ri)?)')
    all_set = set(["ls", "list", "a", "add", "addm"])

    while args:
        # ensure this doesn't error because of a faulty CAPS LOCK key
        arg = args.pop(0).lower()
        if arg in commandsl:
            if not commands[arg][0]:
                commands[arg][1]()
            else:
                if all_re.match(arg) or arg in all_set:
                    commands[arg][1](args)
                    args = None
                else:
                    commands[arg][1](args.pop(0))
        else:
            commandsl.sort()
            commandsl = ["\t" + i for i in commandsl]
            print("Unable to find command: {0}".format(arg))
            print("Valid commands: ")
            print(concat(commandsl, "\n"))
            sys.exit(1)
