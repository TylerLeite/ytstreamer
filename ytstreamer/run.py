import sys

sys.path.append('..')
from fileio.config import *
from app.server import *

if __name__ == "__main__":
    print
    # Get what config file we're using from command line
    cfg_file = "dat/mb.conf"
    if len(sys.argv) > 2:
        print "Usage: python -m server.run (/path/to/config.file)"
    elif len(sys.argv) == 2:
        # Improper usage, terminate
        cfg_file = sys.argv[0]

    # Get the proper config file based on input
    settings = read(cfg_file)

    # Could not load config file, probably it doesn't exist
    if not settings:
        print "Could not open configuration file. Terminating."
        sys.exit(1)

    # Attempt to initiate the server with the dynamically imported game
    server = Server(settings)
    server.init()
    server.go()
