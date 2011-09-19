#!/bin/bash
INSTALL_DIR=$HOME/bin
BASH_ALIAS_FILE=$HOME/.bashrc

set -- $(getopt -l "help,install-dir::,alias-file::" "h" "$@")

while [[ $# -gt 0 ]] ; do 
	case "$1" in
		"-h" | "--help" ) echo -e \
			"Usage: $(basename $0) -h[--help] [--install-dir] [--alias-file]\n"
			exit
			;;
		"--install-dir" ) shift; INSTALL_DIR=$1
			;;
		"--alias-file" ) shift; BASH_ALIAS_FILE=${1:1:${#1}-2} #[1]
			;;
		"--" ) break
			;;
		* ) shift
	esac
done

prog="[""$(basename $0)""] "

[[ -d $INSTALL_DIR ]] || mkdir -p $INSTALL_DIR
echo $prog"$INSTALL_DIR check passed."

[[ -s $BASH_ALIAS_FILE ]] || echo "# Bash RC File" #>> $BASH_ALIAS_FILE
echo $prog"$BASH_ALIAS_FILE check passed."
## Believe it or not, >> is faster than >.

echo $prog"Copying todo.py to $INSTALL_DIR/todo.py"
cp ./todo.py $INSTALL_DIR

## Establish alias
pre="\n\nAlias for todo.py\n"
if grep -q "todo.sh" "$BASH_ALIAS_FILE" ; then
	ALIAS=$pre"alias tpy='$INSTALL_DIR/todo.py'\n"
else
	ALIAS=$pre"alias t='$INSTALL_DIR/todo.py'\n"
fi

echo -e $ALIAS >> $BASH_ALIAS_FILE

### Footnote(s)
#[1] the argument is actually passed as "'/path/to/file'" so that instead of
#	- checking /path/to/file or using that, it uses '/path/to/file' (with the
#	- apostrophes). So to remove then you need to start at index 1 take a
#	- substring up until length - 2
