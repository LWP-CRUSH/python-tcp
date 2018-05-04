# python-tcp
tcp + json for python2x or python3x(reference https://github.com/mdebbar/jsonsocket/blob/master/jsonsocket.py)
This script use 4 fixed bytes to represent the length of the json packet

Examples:
  server = Server(host, port)
  while True:
    server.accept()
    data = server.recv()
    # shortcut: data = server.accept().recv()
    server.send({'status': 'ok'})
    
  data = {
    'name': 'Daisy',
    'age': 24,
  }
  client = Client()
  client.connect(host, port)
  client.send(data)
  response = client.recv()
  client.close()
