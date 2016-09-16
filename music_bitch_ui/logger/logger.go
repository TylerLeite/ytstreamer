package logger

import (
	"os"
	"strconv"
	"time"
)

var (
	logDir = "/var/log/music_bitch/"
)

// FileWriter is a type which adheres to the io.Writer interface but outputs
// log messages to a given file
type FileWriter struct {
	filePath   string
	fileHandle *os.File
}

// New returns a pointer to a FileWriter. It creates the logfile if said
// file does not exist
func New() (*FileWriter, error) {

	logFilePath := logDir + genLogName()

	// Attempt to open the log file
	logFileHandle, err := openLogFile(logFilePath, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0666)
	if err != nil {
		return nil, err
	}

	// Create a file writer and return it
	return &FileWriter{
		filePath:   logFilePath,
		fileHandle: logFileHandle,
	}, nil
}

// Write defines a generic byte writer to adhere to the io.Writer interface
func (f *FileWriter) Write(p []byte) (n int, err error) {
	return f.fileHandle.Write(p)
}

// openLogFile opens a log file for writing, and creates said file if the file
// does not exist
func openLogFile(filePath string, mode int, perms os.FileMode) (*os.File, error) {
	f, err := os.OpenFile(filePath, mode, perms)
	if err == os.ErrNotExist {
		// TODO(shaba): Do we care about the mode and perms when creating a filePath?
		return os.Create(filePath)
	}
	return f, err
}

func genLogName() string {
	now := time.Now()
	year, month, day := now.Date()
	yearString := strconv.Itoa(year)
	dayString := strconv.Itoa(day)

	logName := "log_" + yearString + "_" + month.String() + "_" + dayString
	return logName
}
