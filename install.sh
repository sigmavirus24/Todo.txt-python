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
		"--alias-file" ) shift; BASH_ALIAS_FILE=$1
			;;
		"--" ) break
			;;
		* ) shift
	esac
done

[[ -d $INSTALL_DIR ]] || mkdir -p $INSTALL_DIR
echo "$INSTALL_DIR check passed."

[[ -s $BASH_ALIAS_FILE ]] || echo "# Bash RC File" >> $BASH_ALIAS_FILE
echo "$BASH_ALIAS_FILE check passed."
## Believe it or not, >> is faster than >.

echo "[install.sh] Copying todo.py to $INSTALL_DIR/todo.py"
#cp ./todo.py $INSTALL_DIR

## Establish alias
if grep -q "todo.sh" $BASH_ALIAS_FILE ; then
	ALIAS="\n\nalias tpy='$INSTALL_DIR/todo.py'\n"
else
	ALIAS="\n\nalias t='$INSTALL_DIR/todo.py'\n"
fi

echo $ALIAS
#echo -e $ALIAS >> $BASH_ALIAS_FILE
