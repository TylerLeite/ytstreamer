# Known bugs:
"""
1. no youtube results = crash
2. smiley face breaks
3. if you skip while its downloading a song it breaks
"""

import os
import sys
import time
import random
import datetime
import threading

import Queue

from multiprocessing.pool import Pool
from websocket import create_connection

#sys.path.append('..')
from ext.webcrawl import *
from ext.playback import *
from fileio import config

from lib.filelock import FileLock

class Server:
    def __init__(self, settings):
        self.playqueue = Queue.Queue()
        self.autoplaylist = []
        self.cache = []

        self.cmd_queue = Queue.Queue()


        server = settings["serv_url"]
        port = settings["serv_port"]
        route = settings["serv_route"]
        self.ws_host = "ws://%s:%s/%s" % (server, port, route)

        self.alive = threading.Event()
        self.threads = dict()
        self.playback_proc = None

        self.max_queue = settings["max_queue"]
        self.max_cache = settings["max_cache"]

        self.verbose = int(settings["verbose"])

        self.autopl_file = os.path.realpath(settings["autopl_file"])
        self.dl_folder  = os.path.realpath(settings["dl_folder"])
        self.log_folder = os.path.realpath(settings["log_folder"])
        self.err_folder = os.path.realpath(settings["err_folder"])
        self.users_db   = os.path.realpath(settings["users_db"])

        self.current_song = "ainyK6fXku0"

    def init(self):
        if not os.path.exists(self.dl_folder):
            os.makedirs(self.dl_folder)

        #initiate logs
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
        if not os.path.exists(self.err_folder):
            os.makedirs(self.err_folder)

        self.now = lambda: str(datetime.datetime.now())

        # Error log
        fname = self.now().replace(':', '-') + ".log"

        self.log_file = os.path.join(self.log_folder, fname)
        self.err_file = os.path.join(self.err_folder, fname)

        with open(self.log_file, 'w') as f:
            f.write("Activity log for yt-streamer:\n---------------------\n")
        with open(self.err_file, 'w') as f:
            f.write("Error log for yt-streamer:\n---------------------\n")

        # Load users
        self.users = config.read(self.users_db)

        # Load autoplaylist
        with open(self.autopl_file) as f:
            for line in f:
                vid = line.split(" # ")[0]
                self.autoplaylist.append(vid)

        # Create socket
        try:
            #socket.setdefaulttimeout(1)
            self.init_sock()
        except Exception as e:
            self.log_error(e)
            self.alive.clear()

    def init_sock(self):
        for i in range(10):
            try:
                self.ws = create_connection(self.ws_host)
                break
            except Exception as e:
                self.log("Failed to connect #%i" % i)
                print e
                time.sleep(1)

        self.log("Listening on %s" % (self.ws_host), 10)

    def kill_sock(self):
        self.ws.close()
        self.ws = None

    def go(self):
        self.alive.set()

        try:
            # Create looking for connections
            self.threads["#connections"] = threading.Thread(target=self.handle_connections, args=())

            # Create thread for music playback
            self.threads["#playback"] = threading.Thread(target=self.handle_playback, args=())

            # Create thread for handling commands
            self.threads["#commands"] = threading.Thread(target=self.handle_commands, args=())

            # Start all threads
            self.threads["#connections"].start()
            self.threads["#playback"].start()
            self.threads["#commands"].start()

            # Wait on all threads
            #self.cleanup()

        except Exception as e:
            self.log_error(e)
        except:
            self.log("Program terminated by user (Keyboard Interrupt)", 10)
            self.terminate()

    def handle_connections(self):
        while self.alive.isSet():
            try:
                self.log("Awaiting data from %s" % self.ws_host)
                data = self.ws.recv()
                self.log("Recieved %i bytes of data" % len(data), 10)
                out = self.read_get(data)

                #self.ws.send("ACK") #acknowledge (we'll do it later)
                if not None in out:
                    self.cmd_queue.put(out)
            except Exception as e:
                continue

    def handle_commands(self):
        while self.alive.isSet():
            if self.cmd_queue.empty():
                time.sleep(1)
            else:
                uid, cmd, args = self.cmd_queue.get()
                #big bad command controller
                if cmd == "status":
                    self.do_command_status(uid, args[0])
                elif cmd == "play":
                    self.do_command_play(uid, args[0], args[1])
                elif cmd in ["skip", "next"]:
                    self.do_command_skip(uid)
                elif cmd == "clear":
                    self.do_command_clear(uid)
                elif cmd == "add":
                    pass
                elif cmd == "setgroup":
                    pass
                elif cmd == "reboot":
                    pass
                elif cmd == "pause":
                    pass
                elif cmd == "resume":
                    pass
                elif cmd == "volume":
                    pass
                elif cmd == "fuckjon":
                    pass

    def do_command_status(self, uid, of):
        of = of.lstrip("-").lower()

        status = "Improper argument: " + of

        if of in ["queue", "q"]:
            status = "Here is the queue:\n"
            for i, elem in enumerate(list(self.playqueue.queue)):
                info = ytsearch(elem[1])[1]
                status += "%i: %s\n" % (i, info[:len('aaaaaaaaaaaaaaaaaaaaaaa')])
        elif of in ["current", "c"]:
            info = ytsearch(self.current_song)
            status = info[1]
        elif of in ["autoplaylist", "a"]:
            pass

        self.log("Sending status: %s" % status, 10)
        self.ws.send(status)

    def do_command_play(self, uid, placement, query):
        placement = placement.lstrip("-").lower()
        if placement in ["append", "a"]:
            self.log("Adding song to end of queue: %s" % (query))
            self.playqueue.put((uid, query))
        elif placement in ["next", "n"]:
            pass
        elif placement in ["force", "f", "now"]:
            pass
        else:
            print "no bueno"

    def do_command_skip(self, uid):
        self.playback_proc.kill()
        self.log("Skipped a song", 10)

    def do_command_clear(self, uid):
        self.playqueue = Queue.Queue()

    def handle_playback(self):
        self.current_song  = random.choice(self.autoplaylist)

        while self.alive.isSet():
            if not self.playqueue.empty():
                self.current_song = self.playqueue.get()[1]
            else:
                self.current_song  = random.choice(self.autoplaylist)

            self.log("Playing song: " + self.current_song)
            self.playback_proc = ogg123(ytdl(ytsearch(self.current_song)[0]))
            self.playback_proc.wait()

    def read_get(self, data):
        self.log("Parsing command: " + data, 10)
        try:
            command = data.split("GET /")[1].split(" HTTP")[0].split("/")
            uid = command[0][1:]
            cmd = command[1]
            args = command[2:]
            self.log("Command parsed successfully (probably)", 10)
            return (uid, cmd, args)
        except Exception as e:
            self.log_err(e)
            return (None, None, None)

    def terminate(self):
        self.alive.clear()

    def cleanup(self):
        # Clean up threads
        for thread in self.threads:
            self.threads[thread].join(5)
        threads = []
        self.log("Threads successfully closed", 10)

        # Clean up sockets
        for conn in self.connections:
            connections[conn].close()
        self.log("Active connections terminated", 10)

        #self.playback_proc.kill()
        self.log("Subprocesses killed", 10)

    ### LOGGING ###
    def report(self, msg):
        sys.stdout.flush()
        print msg

        # Grab the lock
        with FileLock(self.log_file), open(self.log_file, 'a') as f:
            f.write(self.now() + ':\t')
            f.write(msg + '\n')

        return msg

    def log(self, msg, log_level=0):
        # This function is too complicated to properly comment
        if log_level <= self.verbose:
            return self.report(msg)
        else:
            return msg # This is pythonic

    def log_error(self, e):
        # Grab the lock
        with FileLock(self.err_file), open(self.err_file, 'a') as f:
            f.write(self.now() + ':\t')
            f.write(str(e) + ('\n'))
        self.report("An exception has been raised: %s" % (e,))
        return e
