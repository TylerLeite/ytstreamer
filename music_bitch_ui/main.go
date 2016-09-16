// The email and password used is taken from the environment variables
// FBEMAIL and FBPASS.

//TODO MAKE THIS CODE NOT BAD

package main

import (
	"log"
	"os"
	"strings"
	"time"

	"github.com/austindoeswork/music_bitch_ui/facebook"
	"github.com/austindoeswork/music_bitch_ui/logger"
	"github.com/austindoeswork/music_bitch_ui/server"

	"github.com/1lann/messenger"
)

var (
	sessionPath = os.Getenv("HOME") + "/.music_bitch_ui/session_data"
)

func main() {

	wsIn := make(chan string)
	wsOut := make(chan string)

	//server
	s := server.New(wsIn, wsOut)
	go s.Start()

	//logger
	logW, err := logger.New()
	if err != nil {
		log.Println("failed to start logger: ", err.Error())
	}
	loggy := log.New(logW, "", log.Ldate|log.Ltime|log.Lshortfile)

	//facebook
	f := facebook.New(sessionPath, loggy)
	h := FBHandler{f, loggy, wsIn, wsOut}
	f.Login()
	f.OnMessage(h.HandleFBMessage)
	f.Listen()

	println("listening...")

}

func route(msg, userID, threadID string, wsChan chan<- string, wsOut <-chan string) string {
	if len(msg) == 0 {
		return ""
	}

	msg = strings.ToLower(msg)
	wsMsg := "GET /?" + userID
	words := strings.Split(msg, " ")

	//check for fucks
	for i := 0; i < len(words)-1; i++ {
		if words[i] == "fuck" {
			return "yo fuck " + words[i+1] + " tho"
		}
	}

	if msg[0] != '/' {
		return ""
	}

	switch words[0] {

	case "/help":
		return commandList

	case "/play":
		if len(words) <= 1 {
			return playHelp
		}
		switch words[1] {
		case "-h":
			return playHelp
		case "-n":
			if len(words) <= 2 {
				return playHelp
			}
			wsChan <- wsMsg + "/play/-n/" + strings.Join(words[2:], "+")
			return "adding to queue (next)"
		case "-f":
			if len(words) <= 2 {
				return playHelp
			}
			wsChan <- wsMsg + "/play/-f/" + strings.Join(words[2:], "+")
			return "playing next (force)"
		default:
			wsChan <- wsMsg + "/play/-a/" + strings.Join(words[1:], "+")
			return "adding to queue"
		}

	case "/status":
		if len(words) <= 1 {
			wsChan <- wsMsg + "/status/-c"
			select {
			case statusText := <-wsOut:
				return statusText
			case <-time.After(time.Second * 5):
				return "failed to retrieve status, sorry"
			}
			return ""
		}
		switch words[1] {
		case "-h":
			return statusHelp
		case "-p":
			wsChan <- wsMsg + "/status/-a"
			select {
			case statusText := <-wsOut:
				return statusText
			case <-time.After(time.Second * 5):
				return "failed to retrieve status, sorry"
			}
		case "-q":
			wsChan <- wsMsg + "/status/-q"
			select {
			case statusText := <-wsOut:
				return statusText
			case <-time.After(time.Second * 15):
				return "failed to retrieve status, sorry"
			}
		default:
			return statusHelp
		}

	case "/pause":
		if len(words) > 1 {
			switch words[1] {
			case "-h":
				return "are you fucking retarded"
			}
		}
		wsChan <- wsMsg + "/pause"
		return "pausing"

	case "/resume":
		wsChan <- wsMsg + "/pause"
		return "resuming"

	case "/clear":
		wsChan <- wsMsg + "/clear"
		return "fuck you spammy bitches"

	case "/skip":
		wsChan <- wsMsg + "/skip"
		return "skippin dat shit"

	case "/fuckjon":
		wsChan <- wsMsg + "/fuckjon"
		return "fucking jon up the asshole"

	case "/whoami":
		return userID

	case "/5enly":
		return fivenly

	default:
		return commandList
	}

	return ""
}

type FBHandler struct {
	fb     *facebook.Facebook
	loggy  *log.Logger
	wsChan chan<- string
	wsOut  <-chan string
}

func (h *FBHandler) HandleFBMessage(msg *messenger.Message) {
	h.loggy.Println("FB: \"" + msg.Body + "\" from " + msg.FromUserID)

	if responseStr := route(msg.Body, msg.FromUserID, msg.Thread.ThreadID, h.wsChan, h.wsOut); responseStr != "" {
		resp := h.fb.NewMessageWithThread(msg.Thread)
		resp.Body = responseStr
		_, err := h.fb.SendMessage(resp)
		if err != nil {
			h.loggy.Println("FB: Failed to send message: " + err.Error())
		}
	}

}

const (
	commandList = `/help:	- display this list
/play:	- add a song to queue
/clear:	- fuck people in the ass
/pause:	- pause music
/resume:	- resume paused music
/skip:	- fuck this song
/whoami:	- who the fuck am I
`
	playHelp = `/play |-flag| <Name of Song or Youtube ID>
-h: display this 
-n: add to top of queue
-f: play right now
default: add to bottom of queue
`
	statusHelp = `/status |-flag|
-h: display this 
-q: show songs in queue
-p: show songs in playlist
default: show current playing song
`
	fivenly = `Three times five is johnny five alive
Five mighty thighs drive my flintstones ride
Snide motherfuckers don't glide by my side
Get yourself checked at the Clock of Flying Time
Cheap cheese grows on the trees
With the butterfly leaves
Please do your duty and squeeze
The cheezy juice right out of my sleeves
Sir this is not a goof nor is it a goose-chase
Get your filthy toothpaste
The hell out of my suitcase
I travel alone with five bootleg mixtapes
Five pickled pig legs
And five hard-boiled easter eggs
Feast your eyes, affix your gaze
As i prepare my famous glaze
(like they make at Famous Dave's)
I fly to London and Versailles
By this point i bet you wonder what it pays
Five million dollars
And five golden commodes
In five tiny mansions
All in a row
In the state of Nebraska
In a city unknown
With five ugly wives
And six chickens
`
)

// func getResBody(res *http.Response) string {
// 	b, err := ioutil.ReadAll(res.Body)
// 	if err != nil {
// 		return ""
// 	}
// 	return string(b)
// }
