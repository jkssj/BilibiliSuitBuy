package TH2

import "bytes"
import "golang.org/x/net/http2/hpack"

type H2Connection struct {
	_dataToSend []byte
}

func (receiver *H2Connection) InitiateConnection() {
	var preamble = []byte("PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n")
	var data = [][]byte{receiver._dataToSend, preamble}
	receiver._dataToSend = bytes.Join(data, []byte(""))
}

func (receiver *H2Connection) addDataToSend(body []byte) {
	var data = [][]byte{receiver._dataToSend, body}
	receiver._dataToSend = bytes.Join(data, []byte(""))
}

func (receiver *H2Connection) DataToSend() []byte {
	var body = receiver._dataToSend
	receiver._dataToSend = []byte("")
	return body
}

func (receiver *H2Connection) SendData(StreamId int64, data []byte, Flags int64) {
	var frame = NewDataFrame(StreamId)
	frame.Flags = Flags
	var header = frame.EnHeader(data)
	var s = [][]byte{header, data}
	var body = bytes.Join(s, []byte(""))
	receiver.addDataToSend(body)
}

func (receiver *H2Connection) SendHeaders(StreamId int64, headers []hpack.HeaderField, Flags int64) {
	var frame = NewHeadersFrame(StreamId)
	frame.Flags = Flags
	var buf bytes.Buffer
	var ehp = hpack.NewEncoder(&buf)
	for _, header := range headers {
		_ = ehp.WriteField(header)
	}
	var data = buf.Bytes()
	var header = frame.EnHeader(data)
	var s = [][]byte{header, data}
	var body = bytes.Join(s, []byte(""))
	receiver.addDataToSend(body)
}

func (receiver *H2Connection) SendSettings(setting *SettingsFrame) {
	var frame = setting
	if setting == nil {
		frame = NewSettingsFrame(0)
		frame.SettingsHeaderTableSize = 4096
		frame.SettingsEnablePush = 1
		frame.SettingsMaxConcurrentStreams = 100
		frame.SettingsInitialWindowSize = 65535
		frame.SettingsMaxFrameSize = 16384
		frame.SettingsMaxHeaderListSize = 65536
		frame.SettingsMaxClosedStreams = 0
		frame.Flags = 0
	}
	var data = frame.BuildBody()
	var header = frame.EnHeader(data)
	var s = [][]byte{header, data}
	var body = bytes.Join(s, []byte(""))
	receiver.addDataToSend(body)
}
