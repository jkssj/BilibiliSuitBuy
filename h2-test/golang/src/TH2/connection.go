package TH2

import (
	"bytes"
	"golang.org/x/net/http2/hpack"
	"golang/src/TypeBinary"
)

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
	var header = frame.buildHeader(data)
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
	var header = frame.buildHeader(data)
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
	var header = frame.buildHeader(data)
	var s = [][]byte{header, data}
	var body = bytes.Join(s, []byte(""))
	receiver.addDataToSend(body)
}

func (receiver *H2Connection) ReceiveData(body []byte) []interface{} {
	var events []interface{}
	for len(body) > 0 {
		var header = TypeBinary.UnPack("BHBBL", body[:9])
		var bodyLength = header[1]
		var FrameType = header[2]
		var Flags = header[3]
		var StreamId = header[4]
		//fmt.Printf("%v\n", header)
		switch FrameType {
		case 0:
			// data帧
			var data = body[9 : bodyLength+9]
			var dataFrame = new(DataFrame)
			dataFrame.FrameType = FrameType
			dataFrame.Flags = Flags
			dataFrame.StreamId = StreamId
			dataFrame.BodyLength = bodyLength
			dataFrame.Body = data
			events = append(events, dataFrame)
			body = body[bodyLength+9:]
		case 1:
			// headers帧
			var headers = body[9 : bodyLength+9]
			var headersFrame = new(HeadersFrame)
			var Length = uint32(bodyLength)
			var Dhp = hpack.NewDecoder(Length, nil)
			var DeHeaders, _ = Dhp.DecodeFull(headers)
			headersFrame.FrameType = FrameType
			headersFrame.Flags = Flags
			headersFrame.StreamId = StreamId
			headersFrame.BodyLength = bodyLength
			headersFrame.Headers = DeHeaders
			events = append(events, headersFrame)
			body = body[bodyLength+9:]
		case 2:
			// PRIORITY帧
			var priorityFrame = new(PriorityFrame)
			events = append(events, priorityFrame)
			body = body[bodyLength+9:]
		case 3:
			// RstStream帧
			var rstStreamFrame = new(RstStreamFrame)
			events = append(events, rstStreamFrame)
			body = body[bodyLength+9:]
		case 4:
			// SETTINGS帧
			var settings = body[9 : bodyLength+9]
			var settingsList [][]int64
			for len(settings) > 0 {
				var s = TypeBinary.UnPack("HL", settings[:6])
				settingsList = append(settingsList, s)
				settings = settings[6:]
			}
			var settingsFrame = new(SettingsFrame)
			settingsFrame.Settings = settingsList
			settingsFrame.FrameType = FrameType
			settingsFrame.Flags = Flags
			settingsFrame.StreamId = StreamId
			settingsFrame.BodyLength = bodyLength
			events = append(events, settingsFrame)
			body = body[bodyLength+9:]
		case 8:
			// WINDOW_UPDATE帧
			var DeltaB = body[9 : bodyLength+9]
			var Deltas = TypeBinary.UnPack("L", DeltaB)
			var windowUpdateFrame = new(WindowUpdateFrame)
			windowUpdateFrame.FrameType = FrameType
			windowUpdateFrame.Flags = Flags
			windowUpdateFrame.StreamId = StreamId
			windowUpdateFrame.BodyLength = bodyLength
			windowUpdateFrame.Delta = Deltas[0]
			events = append(events, windowUpdateFrame)
			body = body[bodyLength+9:]
		default:

			body = []byte("")
			break
		}
	}
	return events
}
