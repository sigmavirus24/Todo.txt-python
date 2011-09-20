#!/bin/bash
INSTALL_DIR=$HOME/bin
ALIAS_FILE=$HOME/.bashrc

Usage(){
	echo "Usage: $(basename $0) [options]"
	echo
	echo "Options:"
	echo -e " -h, --help\tdisplays this message and exits"
	echo -e " --install-dir=/path/to/dir [Default: $INSTALL_DIR]
		Uses path provided as home directory for todo.py"
	echo -e " --alias-file=/path/to/file [Default: $ALIAS_FILE]
		Uses file to store alias for \$INSTALL_DIR/todo.py"
}

die(){
    Usage
    exit
}

set -- $(getopt -l "help,install-dir:,alias-file:" "h" "$@")

[[ $? -gt 0 ]] && die  # If you fail to give me parameters
                        # I'll fail to install it for you. Simple as that.

while [[ $# -gt 0 ]] ; do 
	case "$1" in
		"-h" | "--help" ) die
			;;
		"--install-dir" ) shift 
            [[ ! -z "$1" ]] && INSTALL_DIR=${1:1:${#1}-2} || die
			;;
		"--alias-file" ) shift
            [[ ! -z "$1" ]] && ALIAS_FILE=${1:1:${#1}-2} || die
            #[1]
			;;
        "--" ) break
            ;;
		* ) shift
	esac
done

prog="[""$(basename $0)""] "

[[ -d $INSTALL_DIR ]] || mkdir -p $INSTALL_DIR
echo $prog"$INSTALL_DIR exists."

[[ -s $ALIAS_FILE ]] || echo "# Bash RC File" >> $ALIAS_FILE
echo $prog"$ALIAS_FILE exists."
## Believe it or not, >> is faster than >.

echo $prog"Copying todo.py to $INSTALL_DIR/todo.py"
if [[ ! -f $INSTALL_DIR/todo.py ]] ; then
    cp ./todo.py $INSTALL_DIR
else
    cp -u ./todo.py $INSTALL_DIR
fi

## Establish alias
pre="\n\n#Alias for todo.py\n"
if grep -q -e "todo.sh" -e "todo.py" "$ALIAS_FILE" ; then
	alias="tpy"
else
	alias="t"
fi

alias_rc=$pre"alias "$alias"='$INSTALL_DIR/todo.py'\n"

echo -e $alias_rc >> $ALIAS_FILE
echo $prog"Alias '$alias' added to $ALIAS_FILE."
echo $prog"To use alias, please run \`source $ALIAS_FILE\`."
echo $prog"You can also add '$INSTALL_DIR' to your PATH variable."
echo $prog"Installation complete."

### Footnote(s)
#[1] the argument is actually passed as "'/path/to/file'" so that instead of
#	- checking /path/to/file or using that, it uses '/path/to/file' (with the
#	- apostrophes). So to remove then you need to start at index 1 take a
#	- substring up until length - 2
