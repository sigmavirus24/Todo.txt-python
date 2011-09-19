A port of the popular todo.txt-cli project written in bash to python.

This REQUIRES GitPython. Running the script once will give you the URL to
download it. For `todo.py status` to work, it seems git 1.7.x is required. 
At least git 1.6.4 returns an exit status of 1 which causes an error and
prevents GitPython from completing the command. On a different machine, 1.7.4
works with it.

Enjoy, contribute, and feel free to clone. I'm doing this blind[1] as best as
possible for fun.

[1] By blind, I mean without looking at the source of the original todo.txt-cli
project. I'm working solely from my experiences with the script and
experimenting with the functionality while adding things I should probably write
as patches and send upstream... I'll wait to finish my version of the project
first though.
