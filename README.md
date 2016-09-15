# Music Bitch

<p>A server / RESTful api for "streaming" audio from youtube</p>

<p>Requires</p>
<ul>
  <li>ogg123</li>
  <li>libav-tools</li>
  <li>youtube-dl</li>
</ul>

<p>How to install these things</p>
<ol>
  <li>sudo apt-get install vorbis-tools</li>
  <li>sudo apt-get install libav-tools</li>
  <li>pip install youtube-dl</li>
</ol>

## Running the server

### Configuration files

## Issuing the commands through the RESTful api (back end)

## Issuing the commands through facebook messenger (front end)

setgroup
  [role]
  [id]

reboot

pause

resume

volume
  -u, --up
  -d, --down
fuckjon

add [id]

status
  -q, --queue
  -c, --current
  -a, --autoplaylist

play
  -a, --append
  -n, --next
  -f, --force, --now
  [id], [songname]

skip, next

clear

## User roles

users also have all permissions below them
owner - edit roles
admin - edit autoplaylist, reboot bot, pause / play, volume, fuckjon
         playnow,
normy - add to queue, skip songs, playnext
guest - status

## Project Structure
ext - calls to external programs (curl, cvlc, youtube-dl)
config - reading and writing config / log files
server - actual server code
