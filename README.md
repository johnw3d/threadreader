ThreadReader
=============

A web-based feed-aggregator and reader using ThreadStore.

Prerequisites
-------------

Requires node.js with bower, grunt, and lessc.

For the node.js tools, after [installing node itself](http://nodejs.org), you can use npm as follows:

    npm install -g bower
    npm install -g grunt-cli
    npm install grunt --save-dev
    npm install grunt-contrib-watch --save-dev
    npm install grunt-contrib-less --save-dev
    npm install grunt-contrib-copy --save-dev
    npm install grunt-contrib-clean --save-dev
    npm install -g less

Getting started
---------------

Recommended env vars:

	THREADREADER_ROOT=/Users/john/Projects/threadreader
	THREADREADER_LOCAL=1

Create log and cached asset dirs and make them writeable:

    mkdir /var/log/threadreader
    chgrp staff /var/log/threadreader
    chmod 775 /var/log/threadreader

Create the virtualenv and install python dependencies:

    # install python 3, at least 3.4.1, eg brew install python3

    cd $THREADREADER_ROOT
	virtualenv --python=<path_to_python3_install>/bin/python3 env
	source env/bin/activate
	pip install -r requirements.txt

Install front-end dependencies with bower:

    bower install

Build CSS and Javascript assets with grunt:

    grunt build

Start the Tornado development server:

    python app.py

Visit the local sites:

    http://localhost:9001

Working with CSS and Javascript
-------------------------------

We use bower and grunt to manage CSS and Javascript (and fonts and a few other bits and pieces).

If you want to add new components, install using bower, e.g.:

    bower install d3

And if you decide to use the new component permanently remember to add it to bower.json.

While you're editing/adding new assets, use grunt to recompile, copy, uglify, etc. You can do a one-off build:

    grunt build

... or leave grunt open and watching for changes with:

    grunt watch

Note that built assets are not added to the git repository. 