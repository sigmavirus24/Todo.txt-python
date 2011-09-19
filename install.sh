#!/bin/bash
$INSTALL_DIR=$HOME/bin
$BASH_ALIAS_FILE=$HOME/.bashrc

[[ -d $INSTALL_DIR ]] || mkdir -p $INSTALL_DIR

[[ -s $BASH_ALIAS_FILE ]] || echo "# Bash RC File" >> $BASH_ALIAS_FILE
## Believe it or not, >> is faster than >.

echo "[install.sh] Copying todo.py to $INSTALL_DIR/todo.py"
cp ./todo.py $INSTALL_DIR

## Establish alias
if grep -q "todo.sh" $BASH_ALIAS_FILE ; then
	$ALIAS="\n\nalias tpy='$INSTALL_DIR/todo.py'\n"
else
	$ALIAS="\n\nalias t='$INSTALL_DIR/todo.py'\n"
fi

echo -e $ALIAS >> $BASH_ALIAS_FILE
