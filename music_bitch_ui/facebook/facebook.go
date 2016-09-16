package facebook

// The email and password used is taken from the environment variables
// FBEMAIL and FBPASS.

import (
	"io/ioutil"
	"log"
	"os"
	"time"

	"github.com/1lann/messenger"
)

type Facebook struct {
	s           *messenger.Session
	sessionPath string
	loggy       *log.Logger
}

func New(sessionPath string, loggy *log.Logger) *Facebook {
	return &Facebook{
		messenger.NewSession(),
		sessionPath,
		loggy,
	}
}

func (f *Facebook) Login() error {
	//login
	sessionData, err := ioutil.ReadFile(f.sessionPath)
	if os.IsNotExist(err) {
		//from usr and pass
		f.loggy.Println("FB: No session file, logging in with user and passwd")
		err = f.s.Login(os.Getenv("FBEMAIL"), os.Getenv("FBPASS"))
		if err != nil {
			return err
		}
	} else {
		//from file
		err = f.s.RestoreSession(sessionData)
		if err != nil {
			//from usr and pass
			f.loggy.Println("FB: Failed to restore session, logging in with user and passwd")
			err = f.s.Login(os.Getenv("FBEMAIL"), os.Getenv("FBPASS"))
			if err != nil {
				return err
			}
		}
	}
	f.loggy.Println("FB: 1/2 userlogin success")

	//connect
	err = f.s.ConnectToChat()
	if err != nil {
		return err
	}
	f.loggy.Println("FB: 2/2 chat connection success")

	//preserve
	// Save the session file every minute. The use of saved session prevents
	// Facebook from flagging your bot as suspicious for having to re-log so
	// often, and also makes it faster to test your bot as it doesn't need to
	// log in again every time.
	go func() {
		ticker := time.Tick(time.Minute)
		for range ticker {
			f.saveSession()
		}
	}()

	return nil
}

func (f *Facebook) OnMessage(handler func(msg *messenger.Message)) {
	f.s.OnMessage(handler)
}

func (f *Facebook) Listen() {
	f.loggy.Println("FB: listening...")
	f.s.Listen()
}

func (f *Facebook) NewMessageWithThread(thread messenger.Thread) *messenger.Message {
	return f.s.NewMessageWithThread(thread)
}

func (f *Facebook) SendMessage(msg *messenger.Message) (string, error) {
	return f.s.SendMessage(msg)
}

func (f *Facebook) saveSession() {
	data, err := f.s.DumpSession()
	if err != nil {
		f.loggy.Println("FB: Failed to save session:", err)
		return
	}
	//TODO smarter opening files
	err = ioutil.WriteFile(f.sessionPath, data, 0644)
	if err != nil {
		f.loggy.Println("FB: Failed to write session to file:" + err.Error())
	}
}
