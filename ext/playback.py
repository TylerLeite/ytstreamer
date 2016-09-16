import subprocess

def cvlc(filen):
    #play a file with vlc (no video output)
    p = subprocess.call(["cvlc",\
         "-q",\
         "--vout", "none",\
         "./" + filen],
         stdout=subprocess.PIPE)
    return p

def ogg123(filen):
    #play a file with ogg123 (quits when finished)
    p = subprocess.Popen(["ogg123", "-q", "./" + filen], stdout=None)
    return p
