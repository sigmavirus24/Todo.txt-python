todo.py
=======

.. image:: https://secure.travis-ci.org/sigmavirus24/Todo.txt-python.png?branch=development
    :alt: Build Status
    :name: travisci

A port of the `popular todo.txt-cli project
<https://github.com/ginatrapani/todo.txt-cli>`_ from bash to python.

Dependencies
------------

This only requires GitPython_ if you want to have todo.py also manage a git
repository which tracks the related files. Running the script once will give
you the URL to download it. Please note that GitPython is written for ``git
--version`` 1.7.2+.

.. _GitPython: https://github.com/gitpython-developers/GitPython

Hacking
-------

Enjoy, contribute, and feel free to clone. I'm doing this blind[1]_ as best as
possible for fun.

Important Information
---------------------

- License: GPLv3_
- Build Status: TravisCI_

.. _GPLv3: https://raw.github.com/sigmavirus24/Todo.txt-python/master/LICENSE
.. _TravisCI: http://travis-ci.org/sigmavirus24/Todo.txt-python

--------

.. [1] By blind, I mean without looking at the source of the original todo.txt-cli
    project. I'm working solely from my experiences with the script and
    experimenting with the functionality while adding things I should probably write
    as patches and send upstream... I'll wait to finish my version of the project
    first though.
