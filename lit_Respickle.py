import pickle
import matplotlib.pyplot as plt
from matplotlib import gridspec

signature =True

path1zone = 'C:\\Users\\xav77\\Documents\\FAURE\\prgm_python\\UrbanT\\Eplus4Mubes\\Sim_Results\\1zoneperfloor\\'
#path = 'C:\\Users\\xav77\\Documents\\FAURE\\prgm_python\\UrbanT\\Eplus4Mubes\\Sim_Results\\zone_perim\\'
#path = 'C:\\Users\\xav77\\Documents\\FAURE\\prgm_python\\UrbanT\\Eplus4Mubes\\Sim_Results\\1zone_new\\'
path = 'C:\\Users\\xav77\\Documents\\FAURE\\prgm_python\\UrbanT\\Eplus4Mubes\\Sim_Results\\'
with open(path1zone+'GlobPickle.pickle', 'rb') as handle:
    zone1 = pickle.load(handle)
with open(path+'GlobPickle.pickle', 'rb') as handle:
    zone2 = pickle.load(handle)


for i,key in enumerate(zone1.keys()):
    if i==0:
        print('First key :' + str(zone1[key].keys()))
        for key1 in zone1[key].keys():
            if isinstance(zone1[key][key1],dict):
                keytoprnit = [key for key in zone1[key][key1].keys() if 'Data' in key]
                for nb in keytoprnit:
                    print(nb)
                break


elec1 = []
elec2 = []
heat1 = []
heat2 = []
cool1 = []
cool2 = []
tot1 = []
tot2 = []
nbbuild = []
EPC_elec = []
EPC_Th = []
EPC_Tot = []
TotelPower = {}
EPareas1 =[]
EPareas2 =[]
DBareas = []
EnergieTot = []
for i,key in enumerate(zone2):
    elec1.append(zone1[key]['EnergyConsVal'][1]/3.6) #convert GJ in MWh
    elec2.append(zone2[key]['EnergyConsVal'][1]/3.6)
    cool1.append(zone1[key]['EnergyConsVal'][4]/3.6)
    cool2.append(zone2[key]['EnergyConsVal'][4]/3.6)
    heat1.append(zone1[key]['EnergyConsVal'][5]/3.6)
    heat2.append(zone2[key]['EnergyConsVal'][5]/3.6)
    tot1.append((zone1[key]['EnergyConsVal'][1]+zone1[key]['EnergyConsVal'][4]+zone1[key]['EnergyConsVal'][5])/zone1[key]['EPlusHeatArea']/3.6*1000) #to have GJ into kWh/m2
    tot2.append((zone2[key]['EnergyConsVal'][1]+zone2[key]['EnergyConsVal'][4]+zone2[key]['EnergyConsVal'][5])/zone2[key]['EPlusHeatArea']/3.6*1000)
    EPC_elec.append(zone1[key]['ConsEleTot']/1000)
    EPC_Th.append(zone1[key]['ConsTheTot']/1000)
    EPC_Tot.append((zone1[key]['ConsTheTot']+zone1[key]['ConsEleTot'])/zone2[key]['EPlusHeatArea'])
    EPareas1.append(zone1[key]['EPlusHeatArea'])
    EPareas2.append(zone2[key]['EPlusHeatArea'])
    DBareas.append(zone1[key]['DataBaseArea'])
    TotelPower[key] = [zone2[key]['HeatedArea']['Data_Zone Ideal Loads Supply Air Total Cooling Rate'][i] +
                      zone2[key]['HeatedArea']['Data_Zone Ideal Loads Supply Air Total Heating Rate'][i] +
                      zone2[key]['HeatedArea']['Data_Electric Equipment Total Heating Rate'][i]
                      for i in range(len(zone2[key]['HeatedArea']['Data_Zone Ideal Loads Supply Air Total Heating Rate']))]
    EnergieTot.append(sum(TotelPower[key])/1000/zone2[key]['EPlusHeatArea'])
    nbbuild.append(key)

fig =plt.figure(0)
gs = gridspec.GridSpec(4, 1)
ax0 = plt.subplot(gs[:-1,0])
ax0.plot(nbbuild,elec1,'s')
ax0.plot(nbbuild,elec2,'o')
ax0.plot(nbbuild, EPC_elec,'x')
ax0.grid()
plt.title('Elec_Load (MWh)')
ax1 = plt.subplot(gs[-1,0])

ax1.grid()
#ax1.title('mono-multi')
plt.tight_layout()

fig1 =plt.figure()
gs = gridspec.GridSpec(4, 1)
ax0 = plt.subplot(gs[:-1,0])
ax0.plot(nbbuild,heat1,'s')
ax0.plot(nbbuild,heat2,'o')
ax0.plot(nbbuild, EPC_Th,'x')
ax0.grid()
plt.title('Heat (MWh)')
ax1 = plt.subplot(gs[-1,0])
ax1.plot(nbbuild, [(heat1[i]-heat2[i])/heat1[i]*100 for i in range(len(heat1))],'s')
ax1.grid()
#ax1.title('mono-multi')
plt.tight_layout()


fig2 =plt.figure()
gs = gridspec.GridSpec(4, 1)
ax0 = plt.subplot(gs[:-1,0])
ax0.plot(nbbuild,cool1,'s')
ax0.plot(nbbuild,cool2,'o')
ax0.grid()
plt.title('Cool (MWh)')
ax1 = plt.subplot(gs[-1,0])
ax1.plot(nbbuild, [(cool1[i]-cool2[i])/cool1[i]*100 for i in range(len(cool1))],'s')
ax1.grid()
#ax1.title('mono-multi')
plt.tight_layout()


fig3 =plt.figure()
gs = gridspec.GridSpec(4, 1)
ax0 = plt.subplot(gs[:-1,0])
ax0.plot(nbbuild,EPareas1,'s')
ax0.plot(nbbuild,EPareas2,'o')
ax0.plot(nbbuild,DBareas,'x')
ax0.grid()
plt.title('Areas (m2)')
ax1 = plt.subplot(gs[-1,0])
ax1.plot(nbbuild, [(EPareas1[i]-DBareas[i])/EPareas1[i]*100 for i in range(len(EPareas1))],'s')
ax1.plot(nbbuild, [(EPareas2[i]-DBareas[i])/EPareas2[i]*100 for i in range(len(EPareas1))],'x')
ax1.grid()
#ax1.title('mono-multi')
plt.tight_layout()

fig4 = plt.figure()
gs = gridspec.GridSpec(4, 1)
ax0 = plt.subplot(gs[:-1,0])
ax0.plot(nbbuild,tot1,'s')
ax0.plot(nbbuild,tot2,'o')
ax0.plot(nbbuild,EPC_Tot,'x')
ax0.plot(nbbuild,EnergieTot,'>')
ax0.grid()
plt.title('Tot (kWh/m2)')
ax1 = plt.subplot(gs[-1,0])
ax1.plot(nbbuild, [(tot1[i]-tot2[i])/tot1[i]*100 for i in range(len(cool1))],'s')
ax1.plot(nbbuild, [(EPC_Tot[i]-tot2[i])/EPC_Tot[i]*100 for i in range(len(cool1))],'x')
ax1.grid()
#ax1.title('mono-multi')
plt.tight_layout()

if signature:
    fig = plt.figure()
    posy = -1
    gs = gridspec.GridSpec(int(len(zone1)**0.5)+1, round(len(zone1)**0.5))
    for i,key in enumerate(zone2):
        posx = i%(int(len(zone1)**0.5)+1) # if i<=int(len(zone1)/2) else int(len(zone1)/2)
        if posx==0:
            posy += 1# i%(round(len(zone1)/2)) #0 if posx<int(len(zone1)/2) else i-posx
        ax0 = plt.subplot(gs[posx, posy])
        ax0.plot(zone2[key]['OutdoorSite']['Data_Site Outdoor Air Drybulb Temperature'],zone2[key]['HeatedArea']['Data_Zone Ideal Loads Supply Air Total Heating Rate'],'.')
        ax0.plot(zone2[key]['OutdoorSite']['Data_Site Outdoor Air Drybulb Temperature'],
                 zone2[key]['HeatedArea']['Data_Zone Ideal Loads Supply Air Total Cooling Rate'],'.')
        ax0.plot(zone2[key]['OutdoorSite']['Data_Site Outdoor Air Drybulb Temperature'],
                 zone2[key]['HeatedArea']['Data_Zone Ideal Loads Heat Recovery Total Heating Rate'],'.')
        ax0.plot(zone2[key]['OutdoorSite']['Data_Site Outdoor Air Drybulb Temperature'],
                 zone2[key]['HeatedArea']['Data_Zone Ideal Loads Heat Recovery Total Cooling Rate'],'.')
        plt.title('Building_'+str(key))

plt.show()