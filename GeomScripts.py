import re
from geomeppy import geom
from shapely.geometry import Polygon
from shapely.ops import cascaded_union
import Envelope_Param
import DB_Data
Material = DB_Data.BaseMaterial
GeomElement = DB_Data.GeomElement

def createBuilding(idf,building,perim):
    coord_b1 = building.footprint
    #Adding two blocks, one with two storey (the nb of storey defines the nb of Zones)
    if perim:
        idf.add_block(
        name='BuilB1',
        coordinates= coord_b1,
        height=building.height,
        num_stories=building.nbfloor+building.nbBasefloor, #it defines the numbers of zones !
        below_ground_stories = building.nbBasefloor,
        # below_ground_storey_height = 1, the value is by default 2,5m
        zoning = 'core/perim',
        perim_depth = 3,
        )
    else:
        idf.add_block(
        name='BuilB1',
        coordinates= coord_b1,
        height=building.height,
        num_stories=building.nbfloor+building.nbBasefloor, #it defines the numbers of zones !
        below_ground_stories=building.nbBasefloor,
        #below_ground_storey_height = 3,#1, the value is by default 2,5m
        )
    #idf.intersect_match()
    return idf

def createShadings(building,idf):
    for ii,sh in enumerate(building.shades):
            idf.add_shading_block(
                name='Shading'+str(ii),
                coordinates=building.shades[sh]['Vertex'], #[GeomElement['VertexKey']],
                height=building.shades[sh]['height'],
                )
            #Because adding a shading bloc creates two identical surfaces, let remove one to avoid too big input files
            newshade = idf.idfobjects["SHADING:SITE:DETAILED"]
            for i in newshade:
                if i.Name in ('Shading'+str(ii)+'_2'):
                    idf.removeidfobject(i)
    return idf

def createEnvelope(idf,building):
    #settings for the materials and constructions
    idf.set_default_constructions()
    #creating the materials, see Envelope_Param for material specifications
    Envelope_Param.create_Material(idf,Material)
    #for all construction, see if some other material than default exist
    cstr = idf.idfobjects['CONSTRUCTION']
    mat = idf.idfobjects['MATERIAL']
    win = idf.idfobjects['WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM']
    for id_cstr in cstr:
        for id_mat in mat:
            if id_mat.Name in id_cstr.Name:
                id_cstr.Outside_Layer = id_mat.Name
        for id_win in win:
            if id_win.Name in id_cstr.Name:
                id_cstr.Outside_Layer = id_win.Name

    #lets change the construction for some specific zones surfaces, like the the link between none heat zone like
    # basement and the above floors
    # creating the materials, see Envelope_Param for material specifications for seperation with heated and non heated zones
    Envelope_Param.createNewConstruction(idf, 'Project Heated2NonHeated', 'Heated2NonHeated')
    for idx, zone in enumerate(idf.idfobjects["ZONE"]):
        storey = int(zone.Name[zone.Name.find('Storey')+6:]) #the name ends with Storey # so lest get the storey number this way
        for s in zone.zonesurfaces:
            if s.Surface_Type in 'ceiling' and storey==-1:#which mean that we are on the basements juste below ground
                s.Construction_Name = 'Project Heated2NonHeated'
            if s.Surface_Type in 'floor' and storey==0:#which mean that we are on the first floors just above basement
                s.Construction_Name = 'Project Heated2NonHeated'
    #setting windows on all wall with 25% ratio
    idf.set_wwr(building.wwr, construction="Project External Window")
    check4UnusedCSTR(idf)
    return idf

def check4UnusedCSTR(idf):
    cstr = idf.idfobjects["CONSTRUCTION"]
    surf = idf.idfobjects["BUILDINGSURFACE:DETAILED"]
    fen = idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]
    tosupress = []
    for i in cstr:
        Notused = True
        for j in surf:
            if i.Name in j.Construction_Name:
                Notused = False
                break
        for j in fen:
            if i.Name in j.Construction_Name:
                Notused = False
                break
        if Notused:
            tosupress.append(i)
    for i in reversed(tosupress):
        idf.removeidfobject(i)


def createAirwallsCstr(idf):
    #creating the materials, see Envelope_Param for material specifications
    Envelope_Param.CreatAirwallsMat(idf)
    #for all construction, see if some other material than default exist
    cstr = idf.idfobjects['CONSTRUCTION']
    airmat = idf.getobject('MATERIAL','AirWallMaterial')
    for id_cstr in cstr:
        if 'Partition' in id_cstr.Name:
                id_cstr.Outside_Layer = airmat.Name
    return idf


def split2convex(idf):
    surlist = idf.idfobjects['BUILDINGSURFACE:DETAILED']
    idxi = []
    for i, j in enumerate(surlist):
        if j.Outside_Boundary_Condition.lower() == "outdoors" and not('Wall' in j.Construction_Name):
        #if 'roof' in j.Surface_Type or 'ceiling' in j.Surface_Type or 'floor' in j.Surface_Type:
            roofcoord = j.coords
            coord2split = []
            for nbpt in roofcoord:
                coord2split.append(nbpt[0:2])
            isconv = geom.polygons.is_convex_polygon(coord2split)
            if not (isconv):
                idxi.append(j.Name)
    import tripy
    #print(idxi)
    for surfi in idxi:
        coord2split = []
        surf2treat = idf.getobject('BUILDINGSURFACE:DETAILED',surfi)
        for nbpt in surf2treat.coords:
            coord2split.append(nbpt[0:2])
        height = nbpt[2]
        trigle = tripy.earclip(coord2split)
        stillleft = True
        while stillleft:
            mergeTrigle, stillleft = MergeTri(trigle)
            trigle = mergeTrigle

            # import matplotlib.pyplot as plt
            # plt.figure()
            # xs, ys = zip(*list(coord2split))
            # for i in trigle:
            #     xs, ys = zip(*list(i))  # create lists of x and y values
            #     plt.plot(xs, ys)
            # plt.show()

        for nbi, subsurfi in enumerate(trigle):
            new_coord = []
            for nbpt in subsurfi:
                x = nbpt[0]
                y = nbpt[1]
                z = height
                new_coord.append((x, y, z))
            surftri = idf.newidfobject(
                "BUILDINGSURFACE:DETAILED",
                Name=surf2treat.Name + str(nbi),
                Surface_Type=surf2treat.Surface_Type,
                Construction_Name=surf2treat.Construction_Name,
                Outside_Boundary_Condition=surf2treat.Outside_Boundary_Condition,
                Sun_Exposure=surf2treat.Sun_Exposure,
                Zone_Name=surf2treat.Zone_Name,
                Wind_Exposure=surf2treat.Wind_Exposure,
            )
            #if not 'Core' in surf2treat.Name:
            #    if surf2treat.tilt == 180:
            #        new_coord.reverse()
            #surftri.setcoords(new_coord)
            surftri.setcoords(new_coord)
            if 'Roof' in surf2treat.Construction_Name and surftri.tilt == 180:
                    surftri.setcoords(reversed(new_coord))
        #print(surf2treat.Name)
        idf.removeidfobject(surf2treat)
    return idf

def MergeTri(trigle):
    stillleft = True
    newtrigle = {}
    for nbi, subsurfi in enumerate(trigle):
        PossibleMerge = {}
        PossibleMerge['Edge'] = []
        PossibleMerge['EdLg'] = []
        PossibleMerge['surf1'] = []
        PossibleMerge['surf2'] = []
        PossibleMerge['Vertexidx'] = []
        for nbj, subsurfj in enumerate(trigle):
            if nbj>nbi:
                edge, idx = isCommunNode(subsurfi, subsurfj)
                if len(edge)  == 2:
                    PossibleMerge['Edge'].append(edge)
                    PossibleMerge['Vertexidx'].append(idx)
                    PossibleMerge['EdLg'].append(edgeLength(edge[0],edge[1]))
                    PossibleMerge['surf1']=[i for i in subsurfi]
                    PossibleMerge['surf2']=[i for i in subsurfj]
        newtrigle[nbi]= PossibleMerge
    #now let find the longests edge that could lead to merging surfaces
    #try to merge and if not, lets take the edge just befor and so on
    finished =0
    nb_tries = 0
    while finished==0:
        lg = 0
        for key in newtrigle:
            if newtrigle[key]['EdLg']:
                if newtrigle[key]['EdLg'][0] > lg:
                    lg = newtrigle[key]['EdLg'][0]
                    idx = key  # dict(sorted(PossibleMerge.items(), key=lambda item: item[1]))
        isconv, newsurf = merge2surf(newtrigle[idx])
        if isconv:
            newTrigle = composenewtrigle(trigle,newtrigle[idx],newsurf)
            finished = 1
        else:
            nb_tries+=1
            newtrigle[idx]['EdLg'][0]=0 #we just forced the edge length to be 0 in order to be avoid of the baove selection
            if nb_tries>len(newtrigle):
                newTrigle = trigle
                stillleft = False
                finished = 1

    return newTrigle,stillleft

def composenewtrigle(trigle,data,newsurf):
    newTrigle = []
    surf1 = data['surf1']
    surf2 = data['surf2']
    for i in trigle:
        current = list(i)
        if not str(current) in str(surf1) and not str(current) in str(surf2):
            newTrigle.append(i)
    newTrigle.append(newsurf)
    return newTrigle




def merge2surf(data):
    polygon1 = Polygon(data['surf1'])
    polygon2 = Polygon(data['surf2'])
    polygons = [polygon1, polygon2]
    u = cascaded_union(polygons)
    newsurfcoord = list(u.exterior.coords)[:-1]
    isconv = geom.polygons.is_convex_polygon(newsurfcoord)
    return isconv, newsurfcoord


def edgeLength(node1,node2):
    return ((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2) ** 0.5

def isCommunNode(surf1,surf2):
    egde = []
    idx = []
    for i,nodei in enumerate(surf1):
        for j,nodej in enumerate(surf2):
            if str(nodei) in str(nodej):
                egde.append(nodei)
                idx.append((i,j))
    return egde, idx