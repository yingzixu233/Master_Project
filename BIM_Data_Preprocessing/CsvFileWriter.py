import GraphDataQuery
import GeometryTransformRuling
import pandas as pd

data = []
for hs in GraphDataQuery.houses_1_source:
    basic_source = list(filter(lambda b: b['IFC_GUID'] == hs['basic_module'], GraphDataQuery.ifc_info.getBasicModuleData()))[0]
    house_obj = list(filter(lambda h: h['house_door'] == hs['house_door'],GeometryTransformRuling.objective_houses))
    for ho in house_obj:
        basic_objective = list(filter(lambda b: b['IFC_GUID'] == ho['basic_module'],
                                      GraphDataQuery.ifc_info.getBasicModuleData()))[0]
        dictionary = {'basic_module_source': hs['basic_module'],
                      'source_x': basic_source['Coordinates'][0],
                      'source_y': basic_source['Coordinates'][1],
                      'house_components': hs['house_components'],
                      'basic_module_objective': ho['basic_module'],
                      'objective_x': basic_objective['Coordinates'][0],
                      'objective_y': basic_objective['Coordinates'][1],
                      'floor_name': ho['floor_name'],
                      'transform': ho['transform']}
        data.append(dictionary)
        print(dictionary)

df = pd.DataFrame(data)
df.to_csv('Geometric_Transformation_Schema.csv', index=False, header=True)

