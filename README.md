STORM
=====

Documentation
-------------

To build documentation at GitHub Pages, at the project root path and
documentation branch, do the following thigs.

```
$ python3 setup.py build_sphinx
$ mkdir .tmp
$ mv docs/build/html/* .tmp
$ git stash
$ git checkout --orphan gh-pages
$ rm -rf *
$ mv .tmp/* .
$ rm -rf .tmp
$ git add --all .
$ git touch .nojekyll
$ git commit -m "Project doumentation"
$ git push <remote> gh-pages
$ git checkout <documentation_branch>
$ git stash pop
```

Documentation will be available [here](http://miquelo.github.io/storm/).

