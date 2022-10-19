package TH2

import (
	"bytes"
	"golang.org/x/net/http2/hpack"
)

type DataFrames struct {
	StreamId  int
	EndStream bool
}

func (receiver *DataFrames) buildDataFrames(body []byte) []byte {
	var bodyLength = len(body)
	var flag = 0
	if receiver.EndStream {
		flag += 1
	}
	var header = StructPack("HBBBL", []int{
		(bodyLength >> 8) & 0xFFFF,
		bodyLength & 0xFF, 0, flag,
		receiver.StreamId & 0x7FFFFFFF,
	})
	return bytes.Join([][]byte{header, body}, []byte(""))
}

func NewDataFrames(StreamId int, EndStream bool) *DataFrames {
	var data = new(DataFrames)
	data.StreamId = StreamId
	data.EndStream = EndStream
	return data
}

func BuildDataFrames(dataFrames *DataFrames, data []byte) []byte {
	return dataFrames.buildDataFrames(data)
}

// ------------------------------------------------------------------------------------------------

type HeadersFrames struct {
	StreamId  int
	EndStream bool
}

func (receiver *HeadersFrames) buildHeaders(headers []hpack.HeaderField) []byte {
	var buf bytes.Buffer
	var EnHp = hpack.NewEncoder(&buf)
	for _, value := range headers {
		_ = EnHp.WriteField(value)
	}
	return buf.Bytes()
}

func (receiver *HeadersFrames) buildHeadersFrames(headers []hpack.HeaderField) []byte {
	var body = receiver.buildHeaders(headers)
	var bodyLength = len(body)
	var flag = 5
	if !receiver.EndStream {
		flag = 4
	}
	var header = StructPack("HBBBL", []int{
		(bodyLength >> 8) & 0xFFFF,
		bodyLength & 0xFF, 1, flag,
		receiver.StreamId & 0x7FFFFFFF,
	})
	return bytes.Join([][]byte{header, body}, []byte(""))
}

func NewHeadersFrames(StreamId int, EndStream bool) *HeadersFrames {
	var headers = new(HeadersFrames)
	headers.StreamId = StreamId
	headers.EndStream = EndStream
	return headers
}

func BuildHeadersFrames(headersFrames *HeadersFrames, headers []hpack.HeaderField) []byte {
	return headersFrames.buildHeadersFrames(headers)
}

// ------------------------------------------------------------------------------------------------

type SettingsFrames struct {
	SettingsHeaderTableSize      int
	SettingsEnablePush           int
	SettingsMaxConcurrentStreams int
	SettingsInitialWindowSize    int
	SettingsMaxFrameSize         int
	SettingsMaxHeaderListSize    int
	SettingsMaxClosedStreams     int
	StreamId                     int
}

func (receiver *SettingsFrames) buildSettings() []byte {
	var settings = make([][]int, 7)
	var body = make([][]byte, 7)
	settings[0] = []int{1, receiver.SettingsHeaderTableSize}
	settings[1] = []int{2, receiver.SettingsEnablePush}
	settings[2] = []int{4, receiver.SettingsInitialWindowSize}
	settings[3] = []int{5, receiver.SettingsMaxFrameSize}
	settings[4] = []int{8, receiver.SettingsMaxClosedStreams}
	settings[5] = []int{3, receiver.SettingsMaxConcurrentStreams}
	settings[6] = []int{6, receiver.SettingsMaxHeaderListSize}
	for i, setting := range settings {
		body[i] = StructPack("HL", setting)
	}
	return bytes.Join(body, []byte(""))
}

func (receiver *SettingsFrames) buildSettingsFrames() []byte {
	var body = receiver.buildSettings()
	var bodyLength = len(body)
	var header = StructPack("HBBBL", []int{
		(bodyLength >> 8) & 0xFFFF,
		bodyLength & 0xFF, 4, 0,
		receiver.StreamId & 0x7FFFFFFF,
	})
	return bytes.Join([][]byte{header, body}, []byte(""))
}

func NewSettingsFrames() *SettingsFrames {
	var settings = new(SettingsFrames)
	settings.SettingsHeaderTableSize = 4096
	settings.SettingsEnablePush = 1
	settings.SettingsMaxConcurrentStreams = 100
	settings.SettingsInitialWindowSize = 65535
	settings.SettingsMaxFrameSize = 16384
	settings.SettingsMaxHeaderListSize = 65536
	settings.SettingsMaxClosedStreams = 0
	settings.StreamId = 0
	return settings
}

func BuildSettingsFrames(settingsFrames *SettingsFrames) []byte {
	return settingsFrames.buildSettingsFrames()
}

// ------------------------------------------------------------------------------------------------

type UnFrames struct {
	StreamId   int64
	FrameType  int64
	bodyLength int64
	body       []byte
}

func (receiver *UnFrames) Unpack(body []byte) []byte {
	var header = StructUnPack("HBBBL", body[:9])
	receiver.bodyLength = header[1]
	receiver.FrameType = header[2]
	receiver.StreamId = header[4]
	//fmt.Printf("%v\n", receiver.bodyLength)
	//return receiver.bodyLength
	receiver.body = body[9 : receiver.bodyLength+9]
	return body[receiver.bodyLength+9:]
}
