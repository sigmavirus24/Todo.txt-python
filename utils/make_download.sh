#!/bin/bash

FILES=('todo.py' 'install.sh' 'README.rst' 'LICENSE' 'HISTORY.rst' 'setup.py')

base_name="todo.txt-python"
if [[ -n $1 ]] ; then
    base_name=${base_name}"-"${1}
else 
    branch="$(git status | sed -rn '/On branch/ s/.*branch (.*)/\1/p')"
    if [[ ${branch} != "master" ]] ; then
        commit="$(git log --oneline | sed -nr '1 s/(.*) [A-Z].*/\1/p')"
        base_name=${base_name}"-"${branch}"-"${commit}
    fi
fi


tar czf ${base_name}.tar.gz ${FILES[@]}
zip -q ${base_name}.zip ${FILES[@]}
