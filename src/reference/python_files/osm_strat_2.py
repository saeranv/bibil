import geojson
from pprint import pprint

## data definition:
## geojson_obj (listof geojson_obj)

def write_files():
    for i in range(num_bldg):
        output_file = file('bldg\coordinates_%s.txt'%(i),'w')
        loc = data['features'][i]['geometry']['coordinates'][0]
        num_coord = len(loc)
        for j in range(num_coord):
            str_loc = str(loc[j])[1:-1]+'\n'                 
            output_file.write(str_loc)    
        output_file.close()    

gj_data=open('Data/strat_2.geojson')
data = geojson.load(gj_data)
gj_data.close()

num_bldg = len(data['features'])
print num_bldg
pprint(data)

