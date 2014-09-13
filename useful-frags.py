# set up a py3 virtualenv
virtualenv --python=/usr/local/Cellar/python3/3.4.1/bin/python3 env3

# to clone a git local repo with .git files
git archive master | tar -x -C /somewhere/else
# to export a zipped dump of the repo
git archive --format zip --output /full/path/to/zipfile.zip master


