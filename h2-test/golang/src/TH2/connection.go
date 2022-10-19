package TH2

import (
	"bytes"
)
import "golang.org/x/net/http2/hpack"

type H2Connection struct {
	_dataToSend []byte
}

func (receiver *H2Connection) InitiateConnection(setting *SettingsFrames) {
	var preamble = []byte("PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n")
	var settings = setting
	if setting == nil {
		settings = NewSettingsFrames()
	}
	var body = BuildSettingsFrames(settings)
	var data = [][]byte{receiver._dataToSend, preamble, body}
	receiver._dataToSend = bytes.Join(data, []byte(""))
}

func (receiver *H2Connection) SendHeaders(StreamId int, headers []hpack.HeaderField, EndStream bool) {
	var header = NewHeadersFrames(StreamId, EndStream)
	var body = BuildHeadersFrames(header, headers)
	var data = [][]byte{receiver._dataToSend, body}
	receiver._dataToSend = bytes.Join(data, []byte(""))
}

func (receiver *H2Connection) SendData(StreamId int, body []byte, EndStream bool) {
	var dataF = NewDataFrames(StreamId, EndStream)
	var bodyF = BuildDataFrames(dataF, body)
	var data = [][]byte{receiver._dataToSend, bodyF}
	receiver._dataToSend = bytes.Join(data, []byte(""))
}

func (receiver *H2Connection) DataToSend() []byte {
	var body = receiver._dataToSend
	receiver._dataToSend = []byte("")
	return body
}

func (receiver *H2Connection) ReceiveData(body []byte) []*UnFrames {
	var events []*UnFrames

	for len(body) > 0 {
		var UnF = new(UnFrames)
		body = UnF.Unpack(body)
		if UnF.FrameType == 8 {
			receiver._dataToSend = []byte{0, 0, 0, 4, 1, 0, 0, 0, 0}
		}
		events = append(events, UnF)
	}
	return events
}
