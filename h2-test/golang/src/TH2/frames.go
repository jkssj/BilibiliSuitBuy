package TH2

import (
	"bytes"
	"golang.org/x/net/http2/hpack"
	"golang/src/TypeBinary"
)

type Frame struct {
	FrameType  int64
	StreamId   int64
	BodyLength int64
	Flags      int64
	Delta      int64
	EndStream  bool
	Body       []byte
	Headers    []hpack.HeaderField
	Settings   [][]int64
}

//func (receiver *Frame) DeHeader(body []byte) *Frame {
//	var data = TypeBinary.UnPack("HBBBL", body)
//	receiver.BodyLength = data[1]
//	receiver.FrameType = data[2]
//	receiver.Flags = data[3]
//	receiver.StreamId = data[4]
//	return receiver
//}

func (receiver *Frame) buildHeader(body []byte) []byte {
	receiver.BodyLength = int64(len(body))
	var H1 = int((receiver.BodyLength >> 8) & 0xFFFF)
	var B1 = int(receiver.BodyLength & 0xFF)
	var B2 = int(receiver.FrameType)
	var B3 = int(receiver.Flags)
	var L1 = int(receiver.StreamId & 0x7FFFFFFF)
	var values = []int{H1, B1, B2, B3, L1}
	return TypeBinary.Pack("HBBBL", values)
}

type DataFrame struct{ Frame }

type HeadersFrame struct{ Frame }

type PriorityFrame struct{ Frame }

type RstStreamFrame struct{ Frame }

type SettingsFrame struct {
	Frame
	SettingsHeaderTableSize      int
	SettingsEnablePush           int
	SettingsMaxConcurrentStreams int
	SettingsInitialWindowSize    int
	SettingsMaxFrameSize         int
	SettingsMaxHeaderListSize    int
	SettingsMaxClosedStreams     int
}

// ---------------------------------------------------------------------------------------------

func (receiver *SettingsFrame) BuildBody() []byte {
	var settings = make([][]int, 7)
	settings[0] = []int{1, receiver.SettingsHeaderTableSize}
	settings[1] = []int{2, receiver.SettingsEnablePush}
	settings[2] = []int{4, receiver.SettingsInitialWindowSize}
	settings[3] = []int{5, receiver.SettingsMaxFrameSize}
	settings[4] = []int{8, receiver.SettingsMaxClosedStreams}
	settings[5] = []int{3, receiver.SettingsMaxConcurrentStreams}
	settings[6] = []int{6, receiver.SettingsMaxHeaderListSize}
	var bodyList = make([][]byte, 7)
	for i, setting := range settings {
		bodyList[i] = TypeBinary.Pack("HL", setting)
	}
	return bytes.Join(bodyList, []byte(""))
}

// ---------------------------------------------------------------------------------------------

type PushPromiseFrame struct{ Frame }

type PingFrame struct{ Frame }

type GoawayFrame struct{ Frame }

type WindowUpdateFrame struct{ Frame }

type ContinuationFrame struct{ Frame }

// ---------------------------------------------------------------------------------------------

func NewDataFrame(StreamId int64) *DataFrame {
	var NewFrame = new(DataFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 0
	return NewFrame
}

func NewHeadersFrame(StreamId int64) *HeadersFrame {
	var NewFrame = new(HeadersFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 1
	return NewFrame
}

func NewPriorityFrame(StreamId int64) *PriorityFrame {
	var NewFrame = new(PriorityFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 2
	return NewFrame
}

func NewRstStreamFrame(StreamId int64) *RstStreamFrame {
	var NewFrame = new(RstStreamFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 3
	return NewFrame
}

func NewSettingsFrame(StreamId int64) *SettingsFrame {
	var NewFrame = new(SettingsFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 4
	return NewFrame
}

func NewPushPromiseFrame(StreamId int64) *PushPromiseFrame {
	var NewFrame = new(PushPromiseFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 5
	return NewFrame
}

func NewPingFrame(StreamId int64) *PingFrame {
	var NewFrame = new(PingFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 6
	return NewFrame
}

func NewGoawayFrame(StreamId int64) *GoawayFrame {
	var NewFrame = new(GoawayFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 7
	return NewFrame
}

func NewWindowUpdateFrame(StreamId int64) *WindowUpdateFrame {
	var NewFrame = new(WindowUpdateFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 8
	return NewFrame
}

func NewContinuationFrame(StreamId int64) *ContinuationFrame {
	var NewFrame = new(ContinuationFrame)
	NewFrame.StreamId = StreamId
	NewFrame.FrameType = 9
	return NewFrame
}
