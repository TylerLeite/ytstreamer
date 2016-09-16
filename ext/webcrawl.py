import os
import pycurl
import subprocess

from StringIO import StringIO

# Use curl to get the contents of a webpage
def curl(url):
    c = pycurl.Curl()
    c.setopt(c.URL, url)

    buf = StringIO()
    c.setopt(c.WRITEDATA, buf)

    c.perform()
    c.close()

    return buf.getvalue()

def ytdl(vid):
    fname = "./dl/" + vid + ".ogg"

    # check if file exists
    if not os.path.isfile(fname):
        # download the audio of a video based on the
        try:
            p = subprocess.call(["youtube-dl",\
                  "--extract-audio",\
                  "--audio-format", "vorbis",\
                  "-o", "./dl/%(id)s.%(ext)s",\
                  "https://www.youtube.com/watch?v=" + vid],\
                  stdout=subprocess.PIPE)
        except Exception as e:
            return None

    # return the filename
    return fname

def getbetween(search, left, right):
    for line in search.splitlines():
        if not left in line:
            continue
        out = line.split(left)[1].split(right)[0]

        return out

def ytsearch(query):
    #get the first result from the query
    query = query.replace(" ", "+")
    url = "https://www.youtube.com/results?search_query="

    search = curl(url + query)
    left = "<li><div class=\"yt-lockup yt-lockup-tile yt-lockup-video vve-check clearfix\" data-context-item-id=\""
    right = "\""
    video_id = getbetween(search, left, right)

    search = curl("https://www.youtube.com/watch?v=" + video_id)
    left = "<title>"
    right = " - YouTube</title>"
    video_title = getbetween(search, left, right)
    video_title = video_title.replace("&amp;", "&").replace("&quot;", "\"")

    return (video_id, video_title)
