import logging, urllib2, simplejson, urllib, atexit

_instance = None
  
_axes = {
  'x': ['lng', 'longitude', 'x'],
  'y': ['lat', 'latitude', 'y'],
  #'z': ['elevation', 'altitude', 'z'],
}

_options = {
  'secret.key': '',
  'url.protocol': 'http',
  'url.host': 'cametrics.appspot.com',
  'namespace.separators': r'/[^a-zA-Z0-9]+/',
  'response.format': 'json',
  'request.size': 250
}

_data = []

DATETIME_FORMAT = 'Y-m-d H:i:s'
  
def getOptions():
  return _options

def getSecretKey():
  return _options.get('secret.key')
  
def getURL():
  return '%(url.protocol)s://%(url.host)s/measure/%(secret.key)s/' % _options

def _post_data():
  if not _options.get('secret.key'):
    raise Exception('No Secret Key Specified use Cametrics.initialize')
  
  url = getURL()
  logging.debug('Cametrics posting: %s' % url)

  values = {
    'type': 'bulk',
    'data': simplejson.dumps(_data),
    'format': _options.get('response.format', 'json')
  }

  try:
    response = urllib2.urlopen(urllib2.Request(url, urllib.urlencode(values)))
    logging.debug('Cametrics result: %s' % response)
  except urllib2.HTTPError, e:
    if ((e.code <> 201) and (e.code <> 200)):
      raise Exception('Post did not work: %d' % (e.code))

def initialize(secret_key, options = {}):
  _options.update(options)
  _options.update({'secret.key' : secret_key})

def prepare_bulk(value):
  logging.error('Cametrics script should not use type of "bulk" for value %s' % value)
  return None

def prepare_string(value):
  return str(value).strip()

def prepare_location(value):
  if isinstance(value, dict):
    coord = {'x': None, 'y': None}
    for axis, tests in _axes.iteritems():
      for test in tests:
        if test in value:
          coord[axis] = value[test]
          break

    if ''.join(value.keys()) == '01':
      logging.warning('Cametrics guessing that value, %s, is (%s, %s)' % value, value[0], value[1])
      coord['x'] = value[0]
      coord['y'] = value[1]
    elif None == coord['x'] or None == coord['y']:
      logging.error('Cametrics could not prepare: %s' % value)
      return None
    return '%(x)s,%(y)s' % coord
  
def prepare(value, vtype):
  """
  @see _axes
  
  TODO(ibolmo): Elevation
  """
  if vtype in _prepare_map:
    return globals().get(_prepare_map.get(vtype))(value)
  return value
  
_prepare_map = {
  'bulk': 'prepare_bulk',
  'string': 'prepare_string', 'str': 'prepare_string', 'text': 'prepare_string',
  'location': 'prepare_location', 'coordinate': 'prepare_location', 
  'gps': 'prepare_location'
}
  
def measure(namespace, value = 1, vtype = 'number'):
  try:
    value = prepare(value, vtype)
  except Exception, msg:
    logging.error(msg)
    logging.error('Cametrics could not prepare: %s' % value)
  if value is not None and value:
    post(namespace, value, vtype)

def commit():
  if len(_data):
    _post_data()

def post(namespace, value, vtype):
      _data.append({
        'namespace': namespace,
        'value': value,
        'type': vtype
      })
      
      if len(_data) > _options.get('request.size', 0):
        _post_data()
  
atexit.register(commit)
