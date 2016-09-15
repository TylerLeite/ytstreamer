import os
import sys
import time
import random
import socket
import datetime
import threading

import Queue

from multiprocessing.pool import Pool

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

        self.sock = None
        self.connections = dict()

        self.address = settings["address"]
        self.port = int(settings["port"])

        self.alive = threading.Event()
        self.threads = dict()
        self.playback_proc = None

        self.max_queue = os.path.realpath(settings["max_queue"])
        self. max_cache = os.path.realpath(settings["max_cache"])

        self.verbose = os.path.realpath(settings["verbose"])

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
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_address = (self.address, self.port)
            self.sock.bind(server_address)
            self.sock.listen(1)
            self.log("Listening on port %i" % (self.port), 10)
        except Exception as e:
            self.log_error(e)
            self.alive.clear()

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
            self.cleanup()

        except Exception as e:
            self.log_error(e)
        except:
            self.log("Program terminated by user (Keyboard Interrupt)", 10)
            self.terminate()

    def handle_connections(self):
        while self.alive.isSet():
            conn, addr = self.sock.accept()
            try:
                self.log("Awaiting data from %s:%i" % (addr[0], addr[1]), 10)
                data = conn.recv(1024)
                self.log("Recieved %i bytes of data" % len(data), 10)
                out = read_get(data)
                cmd_queue.put(out)
            except Exception as e:
                return None

    def handle_commands(self):
        while self.alive.isSet():
            if self.cmd_queue.empty():
                time.sleep(1)
            else:
                print self.cmd_queue.get()
                pass

    def handle_playback(self):
        self.current_song  = random.choice(self.autoplaylist)
        self.playback_proc = ogg123(ytdl(ytsearch(self.current_song)[0]))

        while self.alive.isSet():
            if p.poll():
                print p.poll()
                time.sleep(1)
                continue
            elif not self.playqueue.empty():
                self.current_song = self.playqueue.get()
            else:
                self.current_song  = random.choice(self.autoplaylist)


            self.playback_proc = ogg123(ytdl(ytsearch(self.current_song)[0]))



    def read_get(data):
        self.log("Parsing command: " + command, 10)
        try:
            command = data.split("GET /")[1].split(" HTTP")[0].split("/")
            uid = command[0]
            cmd = command[1]
            args = command[2:-1]
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

        self.playback_proc.kill()
        self.log("Subprocesses killed", 10)

    ### LOGGING ###
    def report(self, msg):
        # This function is too complicated to properly comment
        sys.stdout.flush()
        print msg

        # Grab the lock
        with FileLock(self.log_file), open(self.log_file, 'a') as f:
            f.write(self.now() + ':\t')
            f.write(msg + '\n')

        return msg

    def log(self, msg, log_level=0):
        if log_level <= self.verbose:
            print msg
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
