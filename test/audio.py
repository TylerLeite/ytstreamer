import pyglet
import pyglet.media as media
def main():
    fname='test.ogg'
    src=media.load(fname)
    player=media.Player()
    player.queue(src)
    player.volume=1.0
    player.play()
    try:
        pyglet.app.run()
    except KeyboardInterrupt:
        player.next()

if __name__=="__main__":
    main()
