#!/bin/bash

FILES=('todo.py' 'install.sh' 'README.md' 'LICENSE')

tar czf todo.txt-python.tar.gz ${FILES[@]}
zip -q todo.txt-python.zip ${FILES[@]}
