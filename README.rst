Imagine
=======

Imagine is a small script to download images of the web, by providing a list of url via file.

Installation
------------
Installing imagine can be done easily from this git repository:
    pip install git+ssh://git@github.com:NotANormalNerd/imagine.git

Running the script
------------------
After installing the script can easily be run::
    imagine image-list.txt -d /some/place/big/

Argument and Options
--------------------
Imagine has the following command line options::

    imagine --help
    Usage: imagine [OPTIONS] FILENAME

    Options:
      --ignore-cert                Don't check certificate validity
      --ignore-content-type        Don't check for image/* content-type
      -d, --destination DIRECTORY
      --help                       Show this message and exit.
