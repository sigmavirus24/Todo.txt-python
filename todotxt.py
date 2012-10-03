# -*- coding: utf-8 -*-
"""
    PyCharm	
    ~~~~~~

    :copyright: (c) 2011 by ytjohn
    :license: GPLv3, see LICENSE for more details.
"""

import os
import re
import sys
from optparse import OptionParser
from datetime import datetime, date

class TodoDotTxt():

    # concat = lambda str_list, sep='': sep.join([str(i) for i in str_list])
    concat = lambda str_list, sep='': sep.join([str(i) for i in str_list])

    def __init__(self, config):
        self.config = config
        self.concat = lambda str_list, sep='': sep.join([str(i) for i in
                                                     str_list])
        self._path = lambda p: os.path.abspath(os.path.expanduser(p))
        self._pathc = lambda plist: self._path(self.concat(plist))
        self.term_colors = config['TERM_COLORS']
        self.commands = {
            # command 	: ( Args, Function),
            "a"			: (True, self.add_todo),
            "add"		: (True, self.add_todo),
            "addm"		: (True, self.addm_todo),
            "app"		: (True, self.append_todo),
            "append"	: (True, self.append_todo),
            "do"		: (True, self.do_todo),
            "p"			: (True, self.prioritize_todo),
            "pri"		: (True, self.prioritize_todo),
            "pre"		: (True, self.prepend_todo),
            "prepend"	: (True, self.prepend_todo),
            "dp"		: (True, self.de_prioritize_todo),
            "depri"		: (True, self.de_prioritize_todo),
            "del"		: (True, self.delete_todo),
            "rm"		: (True, self.delete_todo),
            "ls"		: (True, self.list_todo),
            "list"		: (True, self.list_todo),
            "listall"	: (False, self.list_all),
            "lsa"		: (False, self.list_all),
            "lsc"		: (False, self.list_context),
            "listcon"	: (False, self.list_context),
            "lsd"		: (False, self.list_date),
            "listdate"	: (False, self.list_date),
            "lsp"		: (False, self.list_project),
            "listproj"	: (False, self.list_project),
            "h"			: (False, self.cmd_help),
            "help"		: (False, self.cmd_help),
            }



    def get_commands(self):
        return self.commands

    def update_commands(self, newcommands):
        self.commands.update(newcommands)
        return self.commands

    def todo_padding(self, include_done=False):
        lines = [line for line in self.iter_todos(include_done)]
        i = len(lines)
        pad = 1
        while i >= 10:
            pad += 1
            i /= 10
        return pad


    def iter_todos(self, include_done=False):
        """Opens the file in read-only mode; returns an iterator for the todos."""
        files = [self.config["TODO_FILE"]]
        if not os.path.isfile(files[0]):
            return
        if include_done and os.path.isfile(self.config["DONE_FILE"]):
            files.append(self.config["DONE_FILE"])
        for f in files:
            with open(f) as fd:
                for line in fd:
                    yield line


    def separate_line(self, number):
        """Takes an integer and returns a string and a list. The string is
        the item at that position in the list. The list is the rest of the todos.

        If the todo.txt file is empty, separate = lines = None. If the number is
        invalid separate = None, lines != None."""
        lines = [line for line in self.iter_todos()]
        separate = None
        if lines and len(lines) > 1 - number >= 0:
            separate = lines.pop(number - 1)
        return separate, lines


    def rewrite_file(self, fd, lines):
        """Simple wrapper for three lines used all too frequently. Sets the access
        position to the beginning of the file, truncates the file's length to 0 and
        then writes all the lines to the file."""
        fd.seek(0, 0)
        fd.truncate(0)
        fd.writelines(lines)


    def rewrite_and_post(self, line_no, old_line, new_line, lines):
        """Wrapper for frequently used semantics for "post-production"."""
        with open(self.config["TODO_FILE"], "w") as fd:
            self.rewrite_file(fd, lines)
        self.post_success(line_no, old_line, new_line)

    def usage(*args):
        """Set the usage string printed out in ./todo.py help."""

        def usage_decorator(func):
            """Function that actually sets the usage string."""
            # TODO: supposed to concat a usage string
            # func.__usage__ = concat(args, '\n').expandtabs(3)
            # func.__usage__ = concat(args, '\n')
            return func
        return usage_decorator



    def _git_err(self, g):
        """Print any errors that result from GitPython and exit."""
        if g.stderr:
            print(g.stderr)
        else:
            print(g)
        sys.exit(g.status)


    @usage('\tpull', '\t\tPulls from your remote git repository.\n')
    def _git_pull(self):
        """Equivalent to running git pull on the command line."""
        try:
            print(self.config["GIT"].pull())
        except git.exc.GitCommandError as g:
            self._git_err(g)



    @usage('\tpush', '\t\tPushes to your remote git repository.\n')
    def _git_push(self):
        """Push commits made locally to the remote."""
        try:
            s = self.config["GIT"].push()
        except git.exc.GitCommandError as g:
            self._git_err(g)
        if s:
            print(s)
        else:
            print("TODO: 'git push' executed.")


    @usage('\tstatus',
        '\t\t"git status" of the repository containing your todo files.',
        '\t\tRequires git version 1.7.4 or newer.\n')
    def _git_status(self):
        """Print the status of the local repository if the version of git is 1.7
        or later."""
        if self.config["GIT"].version_info >= (1, 7, 3):
            print(self.config["GIT"].status())
        else:
            print("status only works for git version 1.7.4 or higher.")


    @usage('\tlog', '\t\tShows the last five commits in your repository.\n')
    def _git_log(self):
        """Print the two latest commits in the local repository's log."""
        print(self.config["GIT"].log("-5", "--oneline"))


    def _git_commit(self, files, message):
        """Make a commit to the git repository.

        files -- should be an iterable like ['file_a', 'file_b'] or ['-a']"""
        if len(message) > 49:
            message = self.concat([message[:45], "...\n\n", message])
        try:
            self.config["GIT"].commit(files, "-m", message)
        except git.exc.GitCommandError as g:
            self._git_err(g)
        committed = self.config["TODO_DIR"] if "-a" in files else self.concat(files, ", ")
        print(self.concat(["TODO: ", committed, " archived."]))


    def prompt(self, *args, **kwargs):
        """Sanitize input collected with raw_input().
        Prevents someone from entering 'y\' to attempt to break the program.

        args -- can be any collection of strings that require formatting.
        kwargs -- will collect the tokens and values."""
        args = list(args)  # [a for a in args]
        args.append(' ')
        prompt_str = self.concat(args).format(**kwargs)
        raw = input(prompt_str)
        return re.sub(r"\\", "", raw)


    def print_x_of_y(self, x, y):
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
    def _iter_actual_lines_(self, config_file):
        """Return only the actual lines of the config file. This skips commented or
        blank lines."""
        skip_re = re.compile('^\s*(#|$)')

        with open(config_file, 'r') as f:
            for line in f:
                if not skip_re.match(line):
                    yield line


    def get_config(self, config_name="", dir_name=""):
        """Read the config file"""
        if dir_name:
            dir_name = self._path(dir_name)
            self.config["TODO_DIR"] = dir_name
            self.config["TODOTXT_CFG_FILE"] = self._pathc([dir_name, "/config"])
            self.config["TODO_FILE"] = self._pathc([dir_name, "/todo.txt"])
            self.config["DONE_FILE"] = self._pathc([dir_name, "/done.txt"])
        if config_name:
            self.config["TODOTXT_CFG_FILE"] = self._path(config_name)

        os.environ["TODO_DIR"] = self.config["TODO_DIR"]

        if self.config["TODOTXT_CFG_FILE"]:
            config_file = self.config["TODOTXT_CFG_FILE"]

        config_file = self._path(config_file)
        perms = os.F_OK | os.R_OK | os.W_OK
        if not (os.access(self.config["TODO_DIR"], perms | os.X_OK) and
                os.access(config_file, perms)) and\
           not config_name:
            self.default_config()
        else:
            strip_re = re.compile('\w+\s([A-Za-z_$="./01]+).*')
            pri_re = re.compile('(PRI_[A-X]|DEFAULT)')

            for line in self._iter_actual_lines_(config_file):
                # Extract VAR=VAL and then split VAR and VAL
                var = strip_re.sub('\g<1>', line.strip()).split('=')
                var[1] = var[1].strip('"')

                if var[1] in ("True", "1"):
                    self.config[var[0]] ^= True
                elif var[1] in ("False", "0"):
                    self.config[var[0]] ^= False
                elif pri_re.match(var[0]):
                    self.config[var[0]] = var[1].strip('$').lower().replace('_', ' ')
                else:
                    self.config[var[0]] = os.path.expandvars(var[1])

                # make expandvars work for our vars too
                os.environ[var[0]] = str(self.config[var[0]])

        if self.config["USE_GIT"]:
            if not self.__import_git__():
                return

            self.config["GIT"] = git.Git(self.config["TODO_DIR"])
            tracked_files = set(self.config["GIT"].ls_files().split())
            i = self.config["TODOTXT_CFG_FILE"].rfind('/') + 1
            if self.config["TODOTXT_CFG_FILE"][i:] not in tracked_files:
                self.config["GIT"].add([self.config["TODOTXT_CFG_FILE"][i:]])


    def __import_git__(self):
        self.git_functions()
        global git
        try:
            import git
        except ImportError:
            if sys.version_info < (3, 0):
                print("You must download and install GitPython from: \
                        http://pypi.python.org/pypi/GitPython")
            else:
                print("GitPython is not available for Python3 last I checked.")
            self.config["USE_GIT"] = False
            return False
        return True


    def git_functions(self):
        global repo_config
        # TODO - redo all the git sections
        def repo_config(self):
            """Help the user configure their git repository."""
            from os import getenv
            g = self.config["GIT"]
            # local configuration
            try:
                user_name = g.config("--global", "--get", "user.name")
            except:
                user_name = getuser()

            try:
                user_email = g.config("--global", "--get", "user.email")
            except:
                user_email = self.concat([user_name, "@", getenv("HOSTNAME")])

            print("First configure your local repository options.")
            ret = self.prompt("git config user.name ", user_name, "?")
            if ret:
                user_name = ret
            ret = self.prompt("git config user.email ", user_email, "?")
            if ret:
                user_email = ret

            g.config("user.name", user_name)
            g.config("user.email", user_email)

            # remote configuration
            ret = self.prompt("Would you like to add a remote?")
            yes_re = re.compile("y(?:es)?", re.I)
            if yes_re.match(ret):
                remote_host = None
                remote_path = None
                remote_user = None
                remote_branch = None

                def __while_prompt__(prompt_str, error_string):
                    ret = None
                    while not ret:
                        ret = self.prompt(prompt_str)
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

                self.prompt("Press enter when you have initialized a bare\n",
                    " repository on the remote or are ready to proceed.")

                local_branch = git.Repo(self.config["TODO_DIR"]).heads[0].name
                if not local_branch:
                    local_branch = "master"

                g.remote("add", "origin", self.concat([remote_user, "@", remote_host,
                                                  ":", remote_path]))
                g.config(self.concat(["branch.", local_branch, ".remote"]), "origin")
                g.config(self.concat(["branch.", local_branch, ".merge"]),
                    self.concat(["refs/heads/", remote_branch]))


    def default_config(self):
        """Set up the default configuration file."""
        def touch(filename):
            """Create files if they aren't already there."""
            open(filename, "w").close()

        if not os.path.exists(self.config["TODO_DIR"]):
            os.makedirs(self.config["TODO_DIR"])

        # touch/create files needed for the operation of the script
        for item in ['TODO_FILE', 'DONE_FILE', 'REPORT_FILE']:
            if self.config[item]:
                touch(self.config[item])

        cfg = open(self.concat([self.config["TODO_DIR"], "/config"]), 'w')

        # set the defaults for the colors
        self.config["PRI_A"] = "yellow"
        self.config["PRI_B"] = "green"
        self.config["PRI_C"] = "light blue"

        TO_self.config = {True: 1, False: 0}
        for key in self.term_colors.keys():
            bkey = self.concat(["$", key.replace(' ', '_').upper()])
            TO_self.config[key] = bkey

        val = self.prompt("Would you like to use git with your to manage\n ",
            self.config["TODO_DIR"], "? [y/N]")
        yes_re = re.compile('y(?:es)?', re.I)
        if yes_re.match(val):
            self.config["USE_GIT"] = True

        for k, v in self.config.items():
            if k != "GIT":
                if v in TO_self.config.keys():
                    cfg.write("export {0}={1}\n".format(k, TO_self.config[v]))
                else:
                    cfg.write("export {0}=\"{1}\"\n".format(k, str(v)))

        if self.config["USE_GIT"]:
            if not self.__import_git__():
                sys.exit(0)
            self.config["GIT"] = git.Git(self.config["TODO_DIR"])
            try:
                repo = git.Repo(self.config["TODO_DIR"])
            except git.exc.InvalidGitRepositoryError:
                val = self.prompt("Would you like to create a new git repository in\n ",
                    self.config["TODO_DIR"], "? [y/N]")
                if yes_re.match(val):
                    print(self.config["GIT"].init())
                    val = self.prompt("Would you like {prog} to help\n you",
                        " configure your new git repository? [y/n]",
                        prog=self.config["TODO_PY"])

                    if yes_re.match(val):
                        repo_config()
                        files = [self.config["TODOTXT_CFG_FILE"], self.config["TODO_FILE"]]
                        for setting in ["TMP_FILE", "DONE_FILE", "REPORT_FILE"]:
                            if self.config[setting]:
                                files.append(self.config[setting])
                        self.config["GIT"].add(files)
                        self.config["GIT"].commit("-m", self.concat(['"', self.config["TODO_PY"],
                                                           " initial commit.\""]))
                else:
                    val = self.prompt("Would you like {prog} to clone\n a",
                        " remote repository for you? [y/N]",
                        prog=self.config["TODO_PY"])
                    if yes_re.match(val):
                        from shutil import rmtree
                        rmtree(self.config["TODO_DIR"])
                        val = self.prompt("Please enter user@remote:/path/to/repo.")
                        git.Repo.clone_from(val, self.config["TODO_DIR"])

        cfg.close()

        print(self.concat(["Default configuration completed. Please ",
                      "re-run\n ", self.config["TODO_PY"], " with '-h' and 'help' separately."]))
        sys.exit(0)
    ### End Config Functions


    ### New todo Functions
    @usage('\tadd | a "Item to do +project @context #{yyyy-mm-dd}"',
        concat(["\t\tAdds 'Item to do +project @context #{yyyy-mm-dd}'",
                "to your todo.txt"], ' '), "\t\tfile.",
        "\t\t+project, @context, #{yyyy-mm-dd} are optional\n")
    def add_todo(self, args):
        """Add a new item to the list of things todo."""
        if str(args) == args:
            line = args
        elif len(args) >= 1:
            line = self.concat(args, " ")
        else:
            line = self.prompt("Add:")

        prepend = self.config["PRE_DATE"]
        l = len([1 for l in self.iter_todos()]) + 1
        pri_re = re.compile('(\([A-X]\))')

        if pri_re.match(line) and prepend:
            line = pri_re.sub(self.concat(["\g<1>",
                                      datetime.now().strftime(" %Y-%m-%d ")]), line)
        elif prepend:
            line = self.concat([datetime.now().strftime("%Y-%m-%d "), line])

        with open(self.config["TODO_FILE"], "a") as fd:
            fd.write(self.concat([line, "\n"]))

        s = "TODO: '{0}' added on line {1}.".format(line, l)
        print(s)
        if self.config["USE_GIT"]:
            self._git_commit([self.config["TODO_FILE"]], s)


    @usage('\taddm "First item to do +project @context #{yyyy-mm-dd}',
        '\t\tSecond item to do +project @context #{yyyy-mm-dd}',
        '\t\t...', '\t\tLast item to do +project @context #{yyyy-mm-dd}',
        '\t\tAdds each line as a separate item to your todo.txt file.\n')
    def addm_todo(self, args):
        """Add new items to the list of things todo."""
        if str(args) == args:
            lines = args
        else:
            lines = self.concat(args, " ")
        lines = lines.split("\n")
        list(map(self.add_todo, lines))  # Necessary for python 3000
    ### End new todo functions


    ### Start do/del functions
    @usage('\tdo NUMBER',
        '\t\tMarks item with corresponding number as done and moves it to',
        '\t\tyour done.txt file.\n')
    def do_todo(self, line):
        """Mark an item on a specified line as done."""
        if not line.isdigit():
            print("Usage: {0} do item#".format(self.config["TODO_PY"]))
        else:
            removed, lines = self.separate_line(int(line))
            if self.test_separated(removed, lines, line):
                return

            fd = open(self.config["TODO_FILE"], "w")
            self.rewrite_file(fd, lines)
            fd.close()

            today = datetime.now().strftime("%Y-%m-%d")
            removed = self.concat(["x", today,
                              re.sub("\([A-X]\)\s?", "", removed)], " ")

            files = [self.config["TODO_FILE"]]
            if self.config["DONE_FILE"]:
                with open(self.config["DONE_FILE"], "a") as fd:
                    fd.write(removed)
                files.append(self.config["DONE_FILE"])

            print(removed[:-1])
            print("TODO: Item {0} marked as done.".format(line))
            if self.config["USE_GIT"]:
                self._git_commit(files, removed)


    @usage('\tdel | rm NUMBER', '\t\tDeletes the item on line NUMBER in todo.txt',
        '')
    def delete_todo(self, line):
        """Delete an item without marking it as done."""
        if not line.isdigit():
            print("Usage: {0} (del|rm) item#".format(self.config["TODO_PY"]))
        else:
            removed, lines = self.separate_line(int(line))
            if self.test_separated(removed, lines, line):
                return

            with open(self.config["TODO_FILE"], "w") as fd:
                self.rewrite_file(fd, lines)

            removed = "'{0}' deleted.".format(removed[:-1])
            print(removed)
            print("TODO: Item {0} deleted.".format(line))
            if self.config["USE_GIT"]:
                self._git_commit([self.config["TODO_FILE"]], removed)
    ### End do/del Functions


    ### Post-production todo functions
    def post_error(self, command, arg1, arg2):
        """If one of the post-production todo functions isn't given the proper
        arguments, the function calls this to notify the user of what they need to
        supply."""
        if arg2:
            print(self.concat(["'", self.config["TODO_PY"], " ", command, "' requires a(n) ",
                          arg1, " then a ", arg2, "."]))
        else:
            print(self.concat(["'", self.config["TODO_PY"], " ", command, "' requires a(n) ",
                          arg1, "."]))


    def post_success(self, item_no, old_line, new_line):
        """After changing a line, pring a standard line and commit the change."""
        old_line = old_line.rstrip()
        new_line = new_line.rstrip()
        print_str = "TODO: Item {0} changed from '{1}' to '{2}'.".format(
            item_no, old_line, new_line)
        print(print_str)
        if self.config["USE_GIT"]:
            self._git_commit([self.config["TODO_FILE"]], print_str)


    @usage('\tappend | app NUMBER "text to append"',
        '\t\tAppend "text to append" to item NUMBER.\n')
    def append_todo(self, args):
        """Append text to the item specified."""
        if args[0].isdigit():
            line_no = int(args.pop(0))
            old_line, lines = self.separate_line(line_no)
            if self.test_separated(old_line, lines, line_no):
                return

            new_line = self.concat([self.concat([old_line[:-1],
                                       self.concat(args, " ")], " "), "\n"])
            lines.insert(line_no - 1, new_line)

            self.rewrite_and_post(line_no, old_line, new_line, lines)
        else:
            self.post_error('append', 'NUMBER', 'string')


    @usage('\tpri | p NUMBER [A-X]',
        '\t\tAdd priority specified (A, B, C, etc.) to item NUMBER.\n')
    def prioritize_todo(self, args):
        """Add or modify the priority of the specified item."""
        args = [arg.upper() for arg in args]
        if args[1:] and args[0].isdigit()\
           and len(args[1]) == 1 and args[1] in self.config['PRIORITIES']:
            line_no = int(args.pop(0))
            old_line, lines = self.separate_line(line_no)
            if self.test_separated(old_line, lines, line_no):
                return

            new_pri = self.concat(["(", args[0], ") "])
            r = re.match("(\([A-X]\)\s).*", old_line)
            if r:
                new_line = re.sub(re.escape(r.groups()[0]), new_pri, old_line)
            else:
                new_line = self.concat([new_pri, old_line])

            lines.insert(line_no - 1, new_line)
            self.rewrite_and_post(line_no, old_line, new_line, lines)
        else:
            self.post_error('pri', 'NUMBER', 'capital letter in [A-X]')


    @usage('\tdepri | dp NUMBER',
        '\t\tRemove the priority of the item on line NUMBER.\n')
    def de_prioritize_todo(self, number):
        """Remove priority markings from the beginning of the line if they're
        there. Don't complain otherwise."""
        if number.isdigit():
            number = int(number)
            old_line, lines = self.separate_line(number)
            if self.test_separated(old_line, lines, number):
                return

            new_line = re.sub("(\([A-X]\)\s)", "", old_line)
            lines.insert(number - 1, new_line)

            self.rewrite_and_post(number, old_line, new_line, lines)
        else:
            self.post_error('depri', 'NUMBER', None)


    @usage('\tprepend | pre NUMBER "text to prepend"',
        '\t\tAdd "text to prepend" to the beginning of the item.\n')
    def prepend_todo(self, args):
        """Take in the line number and prepend the rest of the arguments to the
        item specified by the line number."""
        if args[0].isdigit():
            line_no = int(args.pop(0))
            prepend_str = self.concat(args, " ") + " "
            old_line, lines = self.separate_line(line_no)
            if self.test_separated(old_line, lines, line_no):
                return

            pri_re = re.compile('^(\([A-X]\)\s)')

            if pri_re.match(old_line):
                new_line = pri_re.sub(self.concat(["\g<1>", prepend_str]), old_line)
            else:
                new_line = self.concat([prepend_str, old_line])

            lines.insert(line_no - 1, new_line)

            self.rewrite_and_post(line_no, old_line, new_line, lines)
        else:
            self.post_error('prepend', 'NUMBER', 'string')
    ### End Post-production todo functions


    ### HELP
    @usage('\thelp | h',
        '\t\tDisplay this message and exit.\n')
    def cmd_help(self):
        print(
        self.concat(["Use", self.config["TODO_PY"], "-h for option help\n"], " "))
        print(
        self.concat(["Usage:", self.config["TODO_PY"], "command [arg(s)]"], " "))
        d = {}
        for (key, val) in self.get_commands().items():
            d[val[1]] = (key, val[1])
            # By using the function, only one command name will be added
        cmds = sorted(d.values())  # Only get the tuples
        for (_, f) in cmds:
            print(f.__usage__)
        sys.exit(0)
    ### HELP


    ### List Printing Functions
    def format_lines(self, color_only=False, include_done=False):
        """Take in a list of lines to do, return them formatted with the
        TERM_COLORS and organized based upon priority."""
        plain = self.config["PLAIN"]
        no_priority = self.config["NO_PRI"]
        default = self.config.get("DEFAULT", "default")
        default = self.term_colors[default] if not plain else ""
        invert = self.term_colors["reverse"] if self.config["INVERT"] else ""
        pri_re = re.compile('^\(([A-W])\)\s')
        category = ""
        pad = self.todo_padding(include_done)
        colors = set(self.term_colors.keys())  # Supposedly sets are faster for look-ups

        formatted = []
        if not color_only:
            formatted = dict(zip(self.config["PRIORITIES"],
                [[] for i in self.config["PRIORITIES"]]))

        for (i, line) in enumerate(self.iter_todos(include_done)):
            category = "X"
            color = default

            r = pri_re.match(line)
            if r:
                category = r.groups()[0]
                color_name = self.config["PRI_{0}".format(category)]

                if not plain and color_name in colors:
                    color = self.term_colors[color_name]
                if no_priority:
                    line = pri_re.sub("", line)

            i = str(i + 1).zfill(pad)
            l = self.concat([color, invert, i, " ", line[:-1], default, "\n"])

            if color_only:
                formatted.append(l)
            else:
                formatted[category].append(l)

        return formatted


    def _legacy_sort(self, items):
        """Sort items alphabetically, i.e.

        # (pri_a) Abc
        # (pri_a) Bcd
        # (pri_b) Abc
        # (pri_c) Bcd
        etc., etc., etc."""
        line_re = re.compile('^.*\d+\s(\([A-X]\)\s)?')
        # The .* in the regexp is needed for the \033[* codes
        items = sorted([(line_re.sub("", i), i) for i in items])
        items = [line for (k, line) in items]
        return items


    def _list_(self, by, regexp):
        """Master list_*() function."""
        nonetype = self.concat(["no", by])
        todo = {nonetype: []}
        by_list = []
        sorted = []

        if by in ["date", "project", "context"]:
            lines = self.format_lines(color_only=True)
            regexp = re.compile(regexp)
            for line in lines:
                match = regexp.findall(line)
                if match:
                    line = self.concat(["\t", line])
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
            lines = self.format_lines()
            todo.update(lines)
            by_list = list(self.config['PRIORITIES'])

        by_list.sort()

        regstr = '(\+\w+\s?)' if self.config["HIDE_PROJ"] else ''
        hide_proj_re = re.compile(regstr)
        regstr = '(@\w+\s?)' if self.config["HIDE_CONT"] else ''
        hide_cont_re = re.compile(regstr)
        regstr = '(#\{\d+-\d+-\d+\}\s?)' if self.config["HIDE_DATE"] else ''
        hide_date_re = re.compile(regstr)

        for b in by_list:
            todo[b] = [hide_proj_re.sub("", l) for l in todo[b]]
            todo[b] = [hide_cont_re.sub("", l) for l in todo[b]]
            todo[b] = [hide_date_re.sub("", l) for l in todo[b]]
            if self.config["LEGACY"]:
                todo[b] = self._legacy_sort(todo[b])
            if by != "pri":
                sorted.append(self.concat([b, ":\n"]))
            sorted.extend(todo[b])

        sorted.extend(todo[nonetype])
        return lines, sorted


    def _list_by_(self, *args):
        """
        Print lines matching items in args
        Called when the user does:
            todo.py ls search-term1 search-term2 ...
        """
        esc = re.escape  # keep line length down
        relist = [re.compile(self.concat(["\s?(", esc(a), ")\s?"]), re.I) for a in args]
        del esc  # don't need it anymore

        alines = self.format_lines()  # Retrieves all lines.
        lines = []
        for p in self.config['PRIORITIES']:
            lines.extend(alines[p])

        alines = lines[:]
        matched_lines = []

        for regexp in relist:
            matched_lines = [line for line in lines if regexp.search(line)]
            lines = matched_lines[:]

        if lines:
            print(self.concat(lines)[:-1])
        self.print_x_of_y(lines, alines)


    @usage('\tlist | ls',
        '\t\tLists all items in your todo.txt file sorted by priority.\n')
    def list_todo(self, args=None, plain=False, no_priority=False):
        """Print the list of todo items in order of priority and position in the
        todo.txt file."""
        if not args:
            lines, sorted = self._list_("pri", "")
            print(self.concat(sorted)[:-1])
            self.print_x_of_y(sorted, sorted)
        else:
            self._list_by_(*args)


    @usage('\tlistall | lsa',
        '\t\tLists all items in your todo.txt file sorted by priority followed',
        '\t\tby the items in your done.txt file.\n')
    def list_all(self):
        """Print the list of todo items in order of priority and then print the
        done.txt file."""
        formatted = self.format_lines(include_done=True)
        lines = []
        for p in self.config['PRIORITIES']:
            lines.extend(formatted[p])
        if lines:
            print(self.concat(lines)[:-1])
        self.print_x_of_y(lines, lines)


    @usage('\tlistdate | lsd',
        '\t\tLists all items in your todo.txt file sorted by date.\n')
    def list_date(self):
        """List todo items by date #{yyyy-mm-dd}."""
        lines, sorted = self._list_("date", "#\{(\d{4})-(\d{1,2})-(\d{1,2})\}")
        print(self.concat(sorted)[:-1])
        self.print_x_of_y(sorted, lines)


    @usage('\tlistproj | lsp',
        '\t\tLists all items in your todo.txt file sorted by project title.\n')
    def list_project(self):
        """Organizes items by project +prj they belong to."""
        lines, sorted = self._list_("project", "\+(\w+)")
        print(self.concat(sorted)[:-1])
        self.print_x_of_y(sorted, lines)


    @usage('\tlistcon | lsc',
        '\t\tLists all items in your todo.txt file sorted by context.\n')
    def list_context(self):
        """Organizes items by context @context associated with them."""
        lines, sorted = self._list_("context", "@(\w+)")
        print(self.concat(sorted)[:-1])
        self.print_x_of_y(sorted, lines)
    ### End LP Functions


    ### Callback functions for options
    def version(self, option, opt, value, parser):
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
    https://github.com/sigmavirus24/Todo.txt-python/tree/master
    Running on {python} {pyversion}""".format(version=self.config["VERSION"],
            id=self.config["REVISION"],
            python=sys.subversion[0], pyversion=self.concat(sys.version_info[:3],
                '.')))
        sys.exit(0)


    def toggle_opt(self, option, opt_str, val, parser):
        """
        Check opt_str to see if it's one of ['-+', '-@', '-#', '-p', '-P', '-t',
        '--plain-mode', '--no-priority', '--prepend-date', '-i',
        '--invert-colors'] and toggle that option in self.config.
        """
        toggle_dict = {"-+": "HIDE_PROJ", "-@": "HIDE_CONT", "-#": "HIDE_DATE",
                       "-p": "PLAIN", "-P": "NO_PRI", "-t": "PRE_DATE",
                       "--plain-mode": "PLAIN", "--no-priority": "NO_PRI",
                       "--prepend-date": "PRE_DATE", "-i": "INVERT",
                       "--invert-colors": "INVERT", "-l": "LEGACY",
                       "--legacy": "LEGACY",
                       }
        if opt_str in toggle_dict.keys():
            k = toggle_dict[opt_str]
            self.config[k] ^= True
    ### End callback functions


    ### Add-on functionality
    def load_actions(self):
        if self.config.get("TODO_ACTIONS_DIR"):
            action_dir = self.config["TODO_ACTIONS_DIR"]
        else:
            action_dir = self._pathc([self.config["TODO_DIR"], "/actions"])
        actions = self.config["ACTIONS"].split(",")

        if not (os.path.exists(action_dir) and any(actions)):
            return

        sys.path.insert(0, action_dir)

        for action in actions:
            try:
                tmp = __import__(action)
                if hasattr(tmp, "commands"):
                    self.update_commands(tmp.commands)
                else:
                    print("Error loading {0}: No commands found.".format(action))
            except ImportError:
                print("No module named {0} available.".format(action))
            except ValueError:
                # For some reason there is a '' in the list `actions`
                pass
    ### End Add-on functionality


    ### Main components
    def opt_setup(self):
        opts = OptionParser("Usage: %prog [options] action [arg(s)]")
        opts.add_option("-c", "--config", dest="config", default="",
            type="string",
            nargs=1,
            help=self.concat(["Supply your own configuration file,",
                         "must be an absolute path"])
        )
        opts.add_option("-d", "--dir", dest="todo_dir", default="",
            type="string",
            nargs=1,
            help="Directory you wish {prog} to use.".format(
                prog=self.config["TODO_PY"])
        )
        opts.add_option("-p", "--plain-mode", action="callback",
            callback=self.toggle_opt,
            help="Toggle coloring of items"
        )
        opts.add_option("-P", "--no-priority", action="callback",
            callback=self.toggle_opt,
            help="Toggle display of priority labels"
        )
        opts.add_option("-t", "--prepend-date", action="callback",
            callback=self.toggle_opt,
            help="Toggle whether the date is prepended to new items."
        )
        opts.add_option("-V", "--version", action="callback",
            callback=self.version,
            nargs=0,
            help="Print version, license, and credits"
        )
        opts.add_option("-i", "--invert-colors", action="callback",
            callback=self.toggle_opt,
            help="Toggle coloring the text of items or background of items."
        )
        opts.add_option("-l", "--legacy", action="callback",
            callback=self.toggle_opt,
            help="Toggle organization of items in the old manner."
        )
        opts.add_option("-+", action="callback", callback=self.toggle_opt,
            help="Toggle display of +projects in-line with items."
        )
        opts.add_option("-@", action="callback", callback=self.toggle_opt,
            help="Toggle display of @contexts in-line with items."
        )
        opts.add_option("-#", action="callback", callback=self.toggle_opt,
            help="Toggle display of #{dates} in-line with items."
        )
        return opts


    def execute_commands(self, args):
        commands = self.get_commands()
        commandsl = [intern(key) for key in commands.keys()]

        all_re = re.compile('((app|pre)(?:end)?|p(?:ri)?)')
        all_set = set(["ls", "list", "a", "add", "addm"])
        actions_dir = self.config.get('TODO_ACTIONS_DIR',
            self._pathc([self.config['TODO_DIR'], '/actions']))

        arg = args.pop(0).lower()
        if os.path.exists(actions_dir) and arg in os.listdir(actions_dir):
            arg = self.concat([actions_dir, arg], '/')
            args.insert(0, arg)
            os.system(self.concat(args,  " "))
            args = None
        elif arg in commandsl:
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
            print(self.concat(commandsl, "\n"))
            return 1
        return 0



