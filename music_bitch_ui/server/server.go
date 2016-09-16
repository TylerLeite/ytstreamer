package server

import (
	"fmt"
	"net/http"
	"time"

	"golang.org/x/net/websocket"
)

type Server struct {
	input  <-chan string
	output chan<- string
}

func New(input <-chan string, output chan<- string) *Server {
	return &Server{
		input,
		output,
	}
}

func (s *Server) handler(h *Hub, ws *websocket.Conn) {

	fmt.Println("opening a ws")

	read := make(chan string)
	defer func() {
		h.Unregister <- read
		close(read)
		ws.Close()
	}()

	h.Register <- read

	go func() {
		fmt.Println("listening for output")
		for {
			var m string
			err := websocket.Message.Receive(ws, &m)
			if err != nil {
				fmt.Println("err recieving ws")
				ws.Close()
				return
			}
			if m != "" {
				select {
				case s.output <- m:
				case <-time.After(time.Second * 1):
				}
			}

		}
	}()

	for msg := range read {
		err := websocket.Message.Send(ws, msg)
		if err != nil {
			fmt.Println("closing a ws...")
			return
		}
	}

}

func (s *Server) Start() {

	h := NewHub(s.input)
	go h.Run()

	http.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		s.handler(h, ws)
	}))
	http.Handle("/", http.FileServer(http.Dir("/home/austin/.music_bitch_ui/static")))

	fmt.Println("starting ws server...")
	err := http.ListenAndServe(":42069", nil)

	if err != nil {
		panic("ListenAndServe: " + err.Error())
	}

}

type Hub struct {
	input      <-chan string
	listeners  map[chan<- string]bool
	Register   chan chan string
	Unregister chan chan string
}

func NewHub(input <-chan string) *Hub {
	return &Hub{
		input,
		make(map[chan<- string]bool),
		make(chan chan string),
		make(chan chan string),
	}
}

func (h *Hub) Run() {
	for {
		select {
		case client := <-h.Register:
			fmt.Println("registered client")
			h.listeners[client] = true
		case message := <-h.input:
			for client := range h.listeners {
				select {
				case client <- message:
					fmt.Println("sent message: ", message)
				case <-time.After(time.Second * 3):
					fmt.Println("closing chan")
					close(client)
					delete(h.listeners, client)
				}
			}
		}
	}
}
