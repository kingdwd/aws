# from __future__ import print_function
from struct import pack, unpack
from threading import Lock, Thread, Event
from time import sleep
from io import BytesIO

from deepgtav.messages import Start, Stop, Dataset, frame2numpy, Scenario
from deepgtav.client import Client

LIST_TARGETS = 0
FETCH_TARGET = 1
INTERCEPT_KEYS = 2
SEND_KEY = 3
RESET = 4
FETCH_GAME_STATE = 5
GAME_STATE_INFO = 6
CONTROL_REQUEST = 7
TARGET_RECEIVED = 8
START_SCENARIOS = 9
STOP_SCENARIOS = 10

class DataType:
	UINT8 = 0
	UINT16 = 1
	UINT32 = 2
	FLOAT = 3
	HALF = 4
	@staticmethod
	def toNumpy(t):
		import numpy as np
		if t == DataType.UINT8: return np.uint8
		if t == DataType.UINT16: return np.uint16
		if t == DataType.UINT32: return np.uint32
		if t == DataType.FLOAT: return np.float32
		if t == DataType.HALF: return np.float16
		return None

CALLBACK_COMMANDS = set([FETCH_TARGET,INTERCEPT_KEYS,FETCH_GAME_STATE])
POLL_INTERVAL = 0.001

class Object(object): pass

class Message:
	def __init__(self, command = 0, id = None, data = b''):
		self.id = id
		if id is None:
			import random
			self.id = random.randint(0, 2**16-1)
		self.command = command
		self.data = data
	
	def serialize(self):
		return pack('=HB', self.id, self.command)+self.data
	
	@staticmethod
	def parse(buf):
		id, command = unpack('=HB', buf[:3])
		return Message(command, id, buf[3:])

def readString(f):
	B = f.read(2)
	if len(B) < 2: return None
	sz, = unpack('=H', B)
	return f.read(sz).decode()

def readStrings(f):
	r = []
	while True:
		s = readString(f)
		if s is None: break
		r.append(s)
	return r

def packString(s):
	return pack('=H', len(s))+s

def packStrings(s):
	return b''.join([packString(i) for i in s])

class Client:
	__intercept_key = None
	__fetch_target = None
	__fetch_game_state = None
	def __init__(self, addr = None):
		from socket import socket, AF_INET, SOCK_STREAM
		self.__lock = Lock()
		self.__s = socket(AF_INET, SOCK_STREAM)
		self.__poller = Thread(target=self.__poll, daemon=True)
		self.__connected = False

		if addr is not None:
			self.connect( addr )

	def connect(self, addr):
		from socket import SOL_SOCKET, SO_TYPE
		self.__s.connect(addr)
		self.__connected = True
		self.__poller.start()
		print( 'Connecting to ', self.__s.getpeername() )
	
	def disconnect(self):
		from socket import SOL_SOCKET, SO_TYPE
		if self.__connected:
			print( 'Disconnecting' )
			self.__connected = False
			self.__poller.join()
			self.__s.close()
	
	def __del__(self):
		self.disconnect()
	
	def __sendMsg(self, m):
		# print(m.data)
		s_m = m.serialize()
		self.__s.send( pack('I', len(s_m)) + s_m )
	
	__unhandled_msg = [] # Contains all non CALLBACK_COMMANDS messages, that were not yet handled
	def __recvMsg(self):
		m = self.__s.recv(4)
		if len(m) != 4:
			raise ConnectionResetError("Failed to establish a connection to the host!")
		L, = unpack('I', m)
		M = b''
		while len(M) < L:
			M += self.__s.recv(L-len(M))
		return Message.parse( M )
	
	# Handle general callback messages
	def __handleMsg(self, m):
		if m.command == INTERCEPT_KEYS:
			if self.__intercept_key is not None and self.__intercept_key[0] == m.id:
				key, state, ts = unpack('=cBQ', m.data)
				self.__intercept_key[1](key, state)
				return True
		if m.command == FETCH_TARGET:
			if self.__fetch_target is not None and self.__fetch_target[0] == m.id:
				import numpy as np
				f = BytesIO(m.data)
				data_type, W, H, C, frame_id, timestamp = unpack('=BHHHIQ', f.read(19))
				name = readString(f)
				np_data = np.frombuffer(f.read(), dtype=DataType.toNumpy(data_type)).reshape((H,W,C))
				# Let the server know that we read the message
				self.__sendMsg(Message(TARGET_RECEIVED, data=pack('=I', frame_id)+packString(name.encode())))
				# Handle the fetch target
				self.__fetch_target[1](name, frame_id, timestamp, np_data)
				return True
		if m.command == FETCH_GAME_STATE:
			if self.game_state_info is not None and self.__fetch_game_state is not None and self.__fetch_game_state[0] == m.id:
				f = BytesIO(m.data)
				frame_id, timestamp = unpack('=IQ', f.read(12))
				self.__fetch_game_state[1](frame_id, timestamp, unpack(self.game_state_info.fmt_str, f.read()))
				return True
		return False
	
	def __fetchMsg(self, command=None, id=None, blocking=True):
		from select import select
		
		if command is not None:
			if not isinstance(command, list) and not isinstance(command, tuple):
				command = [command]
		
		timeout = None
		if not blocking: timeout = 0
		
		if self.__lock.acquire(blocking):
			try:
				# See if the message is in the unhandled_msg pile
				for m in list(self.__unhandled_msg):
					if (id is None or m.id == id) and (command is None or m.command in command):
						self.__unhandled_msg.remove(m)
						return m
				
				# Otherwise go fetch it
				while True:
					s, _, _ = select([self.__s], [], [], timeout)
					if not len(s) and not blocking:
						return None
					m = self.__recvMsg()
					if m is None: continue
					if (id is None or m.id == id) and (command is None or m.command in command):
						return m
					elif m.command in CALLBACK_COMMANDS:
						self.__handleMsg(m)
					else:
						self.__unhandled_msg.append(m)
			finally:
				self.__lock.release()
	
	def __poll(self):
		while self.__connected:
			m = self.__fetchMsg(command=CALLBACK_COMMANDS, blocking=False)
			if m is None:
				sleep(POLL_INTERVAL)
			else:
				self.__handleMsg(m)
	
	def listTargets(self):
		c = Message(LIST_TARGETS)
		self.__sendMsg(c)
		r = self.__fetchMsg(command = c.command, id = c.id)
		return readStrings(BytesIO(r.data))

	def startScenarios(self):
		_drivingMode=[786603,11.0] # mode (0-4294967296), speed (0-20), only if auto drive
		_vehicle='oracle' # "blista", "voltic", "packer", "oracle"
		_weather='CLEAR' # "CLEAR", "EXTRASUNNY", "CLOUDS", "OVERCAST", "RAIN", "CLEARING", "THUNDER", "SMOG", "FOGGY", "XMAS", "SNOWLIGHT", "BLIZZARD", "NEUTRAL", "SNOW" 
		_time=[10,30] # HH, MM
		_location = [-281.8045, -1396.085]  # [-274.2653, -1122.707]

		dataset = Dataset(throttle=True, brake=True, steering=True, vehicles=True, 
			trafficSigns = True, peds=True, speed=True, yawRate=True, location=True, time=True)
		scenario = Scenario(drivingMode=_drivingMode,vehicle=_vehicle, weather=_weather,time=_time, location=_location)
		start_msg = Start(dataset=dataset,scenario=scenario)
		jsonstr = start_msg.to_json().encode()

		c = Message(START_SCENARIOS, data=jsonstr)
		self.__sendMsg(c)
	
	def sendKey(self, k, duration=0.5):
		c = Message(SEND_KEY, data=pack('=cf', k, duration))
		self.__sendMsg(c)
	
	def interceptKeys(self, callback):
		if callback is not None:
			c = Message(INTERCEPT_KEYS, data=pack('=B', 1))
			self.__intercept_key = (c.id, callback)
			self.__sendMsg(c)
		else:
			c = Message(INTERCEPT_KEYS, data=pack('=B', 0))
			self.__intercept_key = None
			self.__sendMsg(c)
	
	def __convertNames(self, names):
		if isinstance(names, str):
			return [names.encode()]
		elif isinstance(names, bytes):
			return [names]
		return [self.__convertNames(n)[0] for n in names]
	
	# Fetch frames on a regular interval
	#   names is a list of targets to fetch (e.g. ['final'])
	#   callback(name, frame_id, timestamp, np.array) will be called as soon as a frame is fetched
	#   step defines how often we fetch a frame either in milliseconds MS or FRAMES (e.g. 100*MS fetches a frame every 100 milliseconds)
	#   n_frames determines how many frames are fetched (0 means infinite)
	#   W and H define the width and height of the frames to fetch (W=0, H=0 is the native resolution)
	def fetchTarget(self, names, callback=None, step=0, n_frames=0, W=0, H=0):
		names = self.__convertNames(names)
		if not isinstance(step, UNIT):
			step = step * MS
		
		if callback is None or len(names) == 0:
			c = Message(FETCH_TARGET, data=pack('=BHHHH', 0, 0, 0, 0, 0))
			self.__fetch_target = None
			self.__sendMsg(c)
		else:
			c = Message(FETCH_TARGET, data=pack('=BHHHH', step.tpe, step.value, n_frames, W, H)+packStrings(names))
			self.__fetch_target = (c.id, callback)
			self.__sendMsg(c)
	
	# Fetch the game state on a regular interval
	#   callback(frame_id, timestamp, values) will be called as soon as the state is fetched
	#   step defines how often we fetch a frame either in milliseconds MS or FRAMES (e.g. 100*MS fetches a frame every 100 milliseconds)
	#   n_frames determines how many frames are fetched (0 means infinite)
	game_state_info = None
	def fetchGameState(self, callback=None, step=0, n_frames=0):
		if not isinstance(step, UNIT):
			step = step * MS
		
		if callback is None:
			self.__sendMsg(Message(FETCH_GAME_STATE, data=pack('=BHH', 0, 0, 0)))
		else:
			fi = None
			if self.game_state_info is None:
				fi = Message(GAME_STATE_INFO)
				self.__sendMsg(fi)
			c = Message(FETCH_GAME_STATE, data=pack('=BHH', step.tpe, step.value, n_frames))
			self.__fetch_game_state = (c.id, callback)
			self.__sendMsg(c)
			if fi is not None:
				self.game_state_info = Object()
				r = self.__fetchMsg(command = fi.command, id = fi.id)
				if len(r.data) == 0:return None
				f = BytesIO(r.data)
				self.game_state_info.name = readString(f)
				
				# Let's read the variables and types
				n_var, = unpack('=H', f.read(2))
				self.game_state_info.variables = []
				self.game_state_info.fmt_str = "="
				self.game_state_info.np_fmt_str = []
				FMT_TABLE = "BHIf"
				NP_FMT_TABLE = ['u1','u2','u4','f4']
				for i in range(n_var):
					vn = readString(f)
					self.game_state_info.variables.append( vn )
					t, = unpack('B',f.read(1))
					assert t < len(FMT_TABLE)
					self.game_state_info.fmt_str += FMT_TABLE[t]
					self.game_state_info.np_fmt_str.append( (vn, NP_FMT_TABLE[t]) )
			return self.game_state_info.name, self.game_state_info.variables
	
	def control(self, request=True):
		if request:
			c = Message(CONTROL_REQUEST, data=b'\1')
		else:
			c = Message(CONTROL_REQUEST, data=b'\0')
		self.__sendMsg(c)
		return self.__fetchMsg(command = c.command, id = c.id).data == b'\1'
	
	def reset(self):
		c = Message(RESET)
		self.__sendMsg(c)
	
class UNIT:
	def __init__(self, tpe, v=1):
		self.tpe = tpe
		self.value = v
	
	def __call__(self, v):
		return UNIT(self.tpe, v)
	
	def __rmul__(self, o):
		from numbers import Number
		assert isinstance(o, Number), "Can only specify numeric unit types"
		return UNIT(self.tpe, o*self.value)

MS = UNIT(0) # Milliseconds
FRAMES = UNIT(1) # Frames

if __name__ == "__main__":
	from time import time, sleep
	
	c = Client(('localhost', 8766))
	print(c)
	if not c.control():
		print( "Failed to gain control over game, just watching then ...")
	c.reset()
	t0 = time()
	#for i in range(100):
	target_list = c.listTargets()
	print( target_list )

	c.startScenarios()

	#c.interceptKeys(print)
	c.fetchGameState(print, 1*FRAMES)
	
	import matplotlib
	matplotlib.use('tkagg')
	from pylab import *
	f = figure()
	im, id = None, None
	cols = np.random.random((10000,3))
	cols[0] = 0
	def to_img(d):
		# print(d.shape)
		if d.size == 0: 
			return None
		if d.dtype == np.uint8:
			return d[:,:,:3]
		elif d.dtype == np.float64:
			return d[:,:,0]
		elif d.dtype == np.float32:
			return d[:,:,0]
		elif d.dtype == np.uint32:
			# print (unique(d))
			return d[:,:,0]
		else:
			return None
		
	NY = int(np.sqrt(len(target_list)))
	NX = (len(target_list)-1) // NY + 1
	target_imgs = {}
	# from matplotlib.animation import FFMpegWriter
	# anim = FFMpegWriter(fps=5)
	# anim.setup(f, "test.mp4", 500)
	# count = 0
	def vis(n, d):
		global target_imgs
		global count
		dI = to_img(d)
		if dI is not None:
			if n in target_imgs:
				target_imgs[n].set_data(dI)
			else:
				subplot(NY, NX, len(target_imgs)+1)
				target_imgs[n] = imshow(dI)
				title(n)
				axis('off')
			# if n == 'depth':
			# 	anim.grab_frame()
			# 	count += 1
			# 	if count == 200:
			# 		anim.finish()
			# 		print("FINISHED")
			f.canvas.draw()
	
	def keyUp(e):
		if e.key == 'r':
			c.sendKey(b'\x26', 0) # VK_UP
		elif e.key == 'e':
			c.sendKey(b'\x28', 0) # VK_DOWN
	
	def keyDown(e):
		if e.key == 'r':
			c.sendKey(b'\x26', 1) # VK_UP
		elif e.key == 'e':
			c.sendKey(b'\x28', 1) # VK_DOWN
	
	cid = f.canvas.mpl_connect('key_press_event', keyDown)
	cid = f.canvas.mpl_connect('key_release_event', keyUp)
	c.fetchTarget(['final', 'depth', 'object_id'], lambda n, i, t, d: vis(n,d), W=0, H=0, step=10*MS)
	# c.fetchTarget(['depth', 'object_id'], lambda n, i, t, d: vis(n,d), W=0, H=0, step=1*MS)
	show()
	#c.sendKey(b'\x26', 2) # VK_UP
	#sleep(2)
	#c.sendKey(b'\x26', 2) # VK_UP
	#sleep(2)
	#c.sendKey(b'\x26', 2) # VK_UP
	#sleep(2)
	#c.sendKey(b'\x28', 1) # VK_DOWN
	#sleep(2)
	print( 'done' )

