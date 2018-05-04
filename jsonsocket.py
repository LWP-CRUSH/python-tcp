import json, socket, struct

# Run on py2 or py3
class Server(object):
  """
  A JSON socket server used to communicate with a JSON socket client. All the
  data is serialized in JSON. How to use it:

  server = Server(host, port)
  while True:
    server.accept()
    data = server.recv()
    # shortcut: data = server.accept().recv()
    server.send({'status': 'ok'})
  """

  client = None

  def __init__(self, host, port,backlog=1):
    self.socket = socket.socket()
    self.backlog = 1
    self.socket.bind((host, port))
    self.socket.listen(self.backlog)

  def __del__(self):
    self.close()

  def accept(self):
    # if a client is already connected, disconnect it
    if self.client:
      self.client.close()
    self.client, self.client_addr = self.socket.accept()
    return self

  def send(self, data, big_endian=True):
    if not self.client:
      raise Exception('Cannot send data, no client is connected')
    _send(self.client, data,big_endian)
    return self

  def recv(self, big_endian=True):
    if not self.client:
      raise Exception('Cannot receive data, no client is connected')
    return _recv(self.client, big_endian)

  def close(self):
    if self.client:
      self.client.close()
      self.client = None
    if self.socket:
      self.socket.close()
      self.socket = None


class Client(object):
  """
  A JSON socket client used to communicate with a JSON socket server. All the
  data is serialized in JSON. How to use it:

  data = {
    'name': 'Daisy',
    'age': 24,
  }
  client = Client()
  client.connect(host, port)
  client.send(data)
  response = client.recv()
  client.close()
  """

  socket = None

  def __del__(self):
    self.close()

  def connect(self, host, port):
    self.socket = socket.socket()
    self.socket.connect((host, port))
    return self

  def send(self, data, big_endian=True):
    if not self.socket:
      raise Exception('You have to connect first before sending data')
    _send(self.socket, data, big_endian)
    return self

  def recv(self, big_endian=True):
    if not self.socket:
      raise Exception('You have to connect first before receiving data')
    return _recv(self.socket, big_endian)

  def close(self):
    if self.socket:
      self.socket.close()
      self.socket = None


## helper functions ##

def _send(socket, data, big_endian):
  try:
    serialized = json.dumps(data)
    byt = serialized.encode()
  except (TypeError, ValueError) as e:
    raise Exception('You can only send JSON-serializable data')
  # send the length of the serialized data first(4 bytes)
  if big_endian == True:
    format_s = '>I'
  else:
    format_s = '<I'
  socket.send(struct.pack(format_s,len(byt)))
  # send the serialized data
  socket.sendall(byt)

  
# little-endian <I
# big-endian >I
def _recv(socket, big_endian):
  # read the length of the data, letter by letter until we reach EOL
  head = socket.recv(4)
  if big_endian == True:
    format_s = '>I'
  else:
    format_s = '<I'
  total, = struct.unpack(format_s,head)
  # use a memoryview to receive the data chunk by chunk efficiently
  view = memoryview(bytearray(total))
  next_offset = 0
  while total - next_offset > 0:
    recv_size = socket.recv_into(view[next_offset:], total - next_offset)
    next_offset += recv_size
  try:
    deserialized = json.loads(view.tobytes().decode())
  except (TypeError, ValueError) as e:
    raise Exception('Data received was not in JSON format')
  return deserialized
