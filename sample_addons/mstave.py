import re, datetime
from todo import usage, iter_todos, CONFIG, concat, _git_commit
from todo import format_lines, PRIORITIES, prioritize_todo, print_x_of_y

@usage('\tadd | a "Item to do +project @context #{yyyy-mm-dd}"',
       concat(["\t\tAdds 'Item to do +project @context #{yyyy-mm-dd}'",
       "to your todo.txt"], ' '), "\t\tfile.",
       "\t\t+project, @context, #{yyyy-mm-dd} are optional\n")
def add_todo(args):
    """Add a new item to the list of things todo."""
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
            datetime.now().strftime(" %Y-%m-%d ")]), line)
    elif prepend:
        line = concat([datetime.now().strftime("%Y-%m-%d "), line])

    with open(CONFIG["TODO_FILE"], "a") as fd:
        fd.write(concat([line, "\n"]))

    s = "TODO: '{0}' added on line {1}.".format(line, l)
    print(s)
    if CONFIG["USE_GIT"]:
        _git_commit([CONFIG["TODO_FILE"]], s)
    return l


@usage('\tsl', "\t\tList items in your todo.txt in reverse priority\n")
def rev_list():
    """List items in reverse order so for long lists, the most important stuff
    won't scroll off the top of the screen."""

    formatted = format_lines()
    lines = []
    for p in PRIORITIES[::-1]:
        lines.extend(formatted[p])

    if lines:
        print(concat(lines)[:-1])
    print_x_of_y(lines, lines)


@usage('\taddp | ap priority Item to be added', 
        '\t\tAdds "Item to be added" with priority "priority" to your todo list.\n')
def addp(args):
    """Add an item and then prioritize it."""
    pri = args.pop(0)
    prioritize_todo([str(add_todo(args)), pri])
# If someone did ./todo.py addp c Test addp foo bar bogus the output would be
# TODO: 'Test addp foo bar bogus' added on line 9.
# TODO: Item 9 changed from 'Test addp foo bar bogus' to '(C) Test addp foo bar bogus'.

commands = { 'addp' : (True, addp),
             'ap'   : (True, addp),
             'sl'   : (False, rev_list),
             'add'  : (True, add),
             'a'    : (True, add) }
