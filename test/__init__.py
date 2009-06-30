import sys, os; sys.path.append(os.pardir)
import Cametrics 

# Simple Unit Test for Cametrics
Cametrics.initialize('ahBjYW1ldHJpY3Mtc3RyZXNzchALEghDYW1wYWlnbhjCgAIM', {
    'url.host': 'cametrics-stress.appspot.com'
})

print Cametrics.getURL()
print Cametrics.getOptions()
print Cametrics.getSecretKey()
Cametrics.measure('contributions.names', 'joe', 'string')
Cametrics.measure('contributions.locations', {'lng': -118.01, 'lat':34.22},'location')
Cametrics.measure('contributions.score', 4, 'number')
Cametrics.measure('contributions.time', '2009-08-17 13:12:01', 'datetime')