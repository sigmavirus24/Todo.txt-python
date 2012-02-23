#!/bin/bash

FILES=('todo.py' 'install.sh' 'README.md' 'LICENSE')

base_name="todo.txt-python"
if [[ -n $1 ]] ; then
    base_name=${base_name}"-"${1}
fi

tar czf ${base_name}.tar.gz ${FILES[@]}
zip -q ${base_name}.zip ${FILES[@]}
