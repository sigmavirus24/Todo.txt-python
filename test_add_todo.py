import todo
import sys
import re
from os import unlink

sys.stdout = open("/dev/null", "w")
todo.CONFIG["TODO_FILE"] = "test_add_todo.txt"


def _print(title_string, x, y):
	string = "Test [{function}]: {x} of {y} passed.\n".format(
			function=title_string, x=x, y=y)
	sys.stderr.write(string)


def test_lines(num):
	return ["Test {0}".format(i) for i in range(0, num)]


def create_truncate():
	open(todo.CONFIG["TODO_FILE"], "w+").close()


def add_todo(n, print_count=True):
	lines = test_lines(n)
	for line in lines:
		todo.add_todo(line)

	count = 0
	for line in todo.iter_todos():
		if re.match("Test \d+", line):
			count += 1
	if print_count:
		_print("vanilla add_todo()", count, n)


def add_todo_predate(n):
	_pre = todo.CONFIG["PRE_DATE"]
	todo.CONFIG["PRE_DATE"] = True
	#_print("Test [pre-date]: ")
	add_todo(n, False)

	count = 0
	for line in todo.iter_todos():
		if re.match("\d{4}-\d{2}-\d{2}.*Test \d+", line):
			count += 1
	_print("predate add_todo()", count, n)

if __name__ == "__main__":
	n = 11
	create_truncate()
	add_todo(n)
	create_truncate()
	add_todo_predate(n)
	unlink(todo.CONFIG["TODO_FILE"])
