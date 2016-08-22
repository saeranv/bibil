#******************************************************************************
 # F_RMlab @ Waterloo School of Architecture
 # Code for geojson -> Rhino
 # Saeran Vasanthakumar
#*****************************************************************************

import json as gj
import rhinoscriptsyntax as rs

## for testing only!
## import pprint

## def pp(d):
##    pprint.pprint(d)
    
def open_geojson(fname):
    try:
        fin = open(fname, 'r')
        data = gj.load(fin)
        fin.close()
        return data
    except:
        print 'File %s not opened' % fname
        return False

def geo2pix(p):
    x = p[0]
    y = p[1]
    lat_ratio = (x - minlat) / rangeW
    lon_ratio = (y - minlon) / rangeH
    return [mapW * lat_ratio, mapH * lon_ratio, 0]

fname = raw_input("Enter the geojson filename or filepath ")
D = open_geojson(fname)

geom_test = D['features'][0]['geometry']['coordinates'][0][0] 

# listof lop, where lop is a listofpoints that is a closed polygon
# then polygons 
if type(geom_test) == type([]): 
    lolop = map(lambda x: x['geometry']['coordinates'][0], D['features'])
    lop = map(lambda x: x['geometry']['coordinates'][0][0], D['features'])
# lines
else: 
    lolop = map(lambda x: x['geometry']['coordinates'], D['features'])
    lop = map(lambda x: x['geometry']['coordinates'][0], D['features'])

#set dimensions
minlat = sorted(lop, key = lambda x: x[0])[0][0]
maxlat = sorted(lop, reverse = True, key = lambda x: x[0])[0][0]
minlon = sorted(lop, key = lambda x: x[1])[0][1]
maxlon = sorted(lop, reverse = True,key = lambda x: x[1])[0][1]
dimW = maxlat - minlat
dimH = maxlon - minlon
mapW = dimW / dimH * 100.0
mapH = 100.0
rangeW = maxlat - minlat
rangeH = maxlon - minlon

length = int(len(lop) / 2)

lolop = map(lambda ptlst: \
            map (lambda p: geo2pix(p), ptlst),lolop) 

for geom in lolop:
    rs.AddCurve(geom, 1)
    
print 'done!'

#for i in D['features']:
#    name = i['properties']['name']
#    s = i['properties']['tags'].split(',')
#    for j in s:
#        if 'building:levels' in j:
#            lvl = j
#    if name != '':
#        print name + ': ' + lvl
