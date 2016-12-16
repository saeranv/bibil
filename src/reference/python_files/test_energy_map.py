import sys
print (sys.version)

import csv

def open_file(fname):
    try:
        data = []
        with open("C:\\Users\\vasanthakumars\\Documents\\GitHub\\BEnMap\\resources\\Energy_Reporting_Data_Sept2016_CLEAM.csv", 'rb') as csvfile:
            spamreader = csv.reader(csvfile)#, #delimiter=',')
            for row in spamreader:
                data.append(row)#print ', '.join(row)
        return data
    except:
        print 'File %s not opened' % fname
        return False

csvfile = "C:\\Users\\vasanthakumars\\Documents\\GitHub\\BEnMap\\resources\\Energy_Reporting_Data_Sept2016_CLEAM.csv"
lstofbld = open_file(csvfile)


for i,lstofinfo in enumerate(lstofbld):
    if True:
        if i==0:
            for j,bldinfo in enumerate(lstofinfo):
                print j,'-',bldinfo,
            
        type,use,gfa,eui,energy_star_score,energy_star_cert = 'err','err','err','err','err','err'
        if True:
            type = lstofinfo[2]
            use = lstofinfo[10]
            gfa = lstofinfo[5]
            eui = lstofinfo[6]
            energy_star_score = lstofinfo[7]
            energy_star_cert = lstofinfo[8]
            year_built = lstofinfo[10]

        
        # Identify the building type
        chktype = False
        mediansiteeui = 'donotread'
        
        if "K-12 School" in type:
            chktype = True
        elif "College" in type:
            mediansiteeui = 104.
            chktype = True
        elif "Food Sales" in type:
            mediansiteeui = 193.
            chktype = True
        elif "Office" in type:
            chktype = True
        elif "Lodging" in type:
            mediansiteeui = 163. 
            chktype = True
        # 
        
        #print i
        
        if chktype:
            print lstofinfo
            print 'median', mediansiteeui
            print 'escore', energy_star_score #score of "simulated" performance vs mediansiteeui
            print 'energy', eui
            print 'eui', eui, 'm', mediansiteeui
            print 'year', year_built
            
            if year_built < 2010:
                print mediansiteeui * 0.2
            else:
                try:
                    getnum = float(mediansiteeui) * 0.7
                except:
                    getnum = 'notwork'
                    
            print '--'
            
