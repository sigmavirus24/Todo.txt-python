Why not use map() in _list_()?
==============================

In ``_list_()``, we use a list comprehension to remove priority, context, and
project tags from the todos. You might wonder why we don't just use the
following:

.. sourcecode:: python

    from functools import partial

    for b in by_list:
        todo[b] = map(partial(hide_proj_re.sub, ""), todo[b])
        todo[b] = map(partial(hide_cont_re.sub, ""), todo[b])
        todo[b] = map(partial(hide_date_re.sub, ""), todo[b])

``map()`` is no faster than a list comprehension and the latter are something
everyone learns early on so even the newest python hacker can read it easily.

Why are format_lines() and _list_() functions so ugly?
======================================================

That's a good question (or isn't, depending on whether you think there are good
questions). I am slowly picking away at their complexity to try to make them
easier to read and understand. If you'd like to help, fork the project, make
your changes, prove that they don't change the result of the function and make a
pull request. I'd be happy to accept changes like this. **Seriously, get
cracking.**
