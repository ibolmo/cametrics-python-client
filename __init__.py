class Cametrics:
  
  instance = null
    
  axes = {
    'x': ['lng', 'longitude', 'x'],
    'y': ['lat', 'latitude', 'y'],
    #'z': ['elevation', 'altitude', 'z'],
  }
  
  options = {
    'secret.key': '',
    'url.protocol': 'http',
    'url.host': 'cametrics.appspot.com',
    'namespace.separators': r'/[^a-zA-Z0-9]+/',
    'response.format': 'json',
    'request.size': 250
  }
  
  DATETIME_FORMAT = 'Y-m-d H:i:s'
  
  self.baseurl = 'http://'+domain+'/measure/'+key+'/'
  
  def __init__(self, $options):
    self.setOptions($options)
    self.data = []
    
  def __del__(self):
    if len(self.data):
      self._post_data()
    print self.data
    
  @staticmethod
  def getOptions():
    return Cametrics.getInstance().options
    
  @staticmethod
  def getSecretKey():
    options = Cametrics.getOptions()
    return options.get('secret.key')
    
  @staticmethod
  def getURL():
    options = Cametrics.getOptions()
    return '%(url.protocol)s://%(url.host)s/measure/%(secret.key)s' % options
  
  def _post_data(self):
    if not self.options.get('secret.key'):
      raise CametricsException, 
          'No Secret Key Specified use %s.initialize' % __class__
    
    uri = Cametrics.getURL()
    logging.notice('Cametrics posting: %s' % $uri)
    
    result = urllib2.urlopen(url = uri, data = {
      'type': 'bulk',
      'data': simplejson.dumps(self.data),
      'format': self.options.get('response.format', 'json')            
    })
    logging.debug('Cametrics result: %s' % result)
    
  @staticmethod
  def initialize(secret_key, options = {}):
    Cametrics.options.set('secret.key', secret_key)
    return Cametrics.getInstance(options)
    
  def setOptions(self, options = {}):
    self.options.update(options)
    
  @staticmethod
  def getInstance(options):
    if not Cametrics.instance:
      Cametrics.instance = Cametrics(options)
      
    return Cametrics.instance
    
  @staticmethod
  def prepare(value, vtype):
    """
    @see Cametrics.axes
    
    TODO(ibolmo): Elevation
    """
    if vtype in Cametrics._prepare_map:
      return Cametrics._prepare_map.get(vtype)(value)
    
    return value
    
  _prepare_map = {
    'bulk': prepare_bulk,
    'string': prepare_string, 'str': prepare_string, 'text': prepare_string,
    'location': prepare_location, 'coordinate': prepare_location, 
    'gps': prepare_location
  }
    
  @staticmethod
  def prepare_bulk(value):
    logging.error('Cametrics script should not use type of "bulk" for value %s' % value)
    return null
    
  @staticmethod
  def prepare_string(value):
    return str(value).strip()
    
  @staticmethod
  def prepare_location(value):
    if isinstance(value, list):
      coord = {'x': null, 'y': null}
      for axis, tests in Cametrics.axes.iteritems():
        for test in tests:
          if test in value:
            coord[axis] = value[test]
            break
        
      if ''.join(value.keys()) == '01':
        logging.warning('Cametrics guessing that value, %s, is (%s, %s)' % value, value[0], value[1])
        coord['x'] = value[0]
        coord['y'] = value[1]
      elif null == coord['x'] or null == coord['y']:
        logging.error('Cametrics could not prepare: %s' % value)
        return null
      return '%(x)s,%(y)s' % coord
      
  @staticmethod
  def measure(namespace, value = 1, vtype = 'number'):
    try:
      value = Cametrics.prepare(value, vtype)
    except Exception, msg:
      logging.error('Cametrics could not prepare: %s' % value)
    if value is not null and value:
      Cametrics.getInstance().post(namespace, value, vtype)
      
  def post(self, namespace, value, vtype):
        self.data.append({
          'namespace': namespace,
          'value': value,
          'type': vtype
        })
        
        if len(self.data) > self.options.get('request.size', 0):
          self._post_data()
          
class CametricsException(Exception):
  pass