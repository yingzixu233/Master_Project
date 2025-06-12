import ifcopenshell
import numpy as np
from numpy.linalg import norm
import math

# Get angles between the basic module and its accessed conjunctive modules within each unit, angle ∈ (-180,180].
def getAngle(x1, y1, x2, y2):
    a = np.array([1.0, 0.0])
    b = np.array([(x2 - x1) * 1.0, (y2 - y1) * 1.0])
    cos_ = np.dot(a, b) * 1.0 / ((norm(a) * norm(b)) * 1.0 + 1e-6)
    sin_ = np.cross(a, b) * 1.0 / ((norm(a) * norm(b)) * 1.0 + 1e-6)
    at = np.arctan2(sin_, cos_)
    angle = at / math.pi * 180
    return round(angle, 2)


class DataExtractor:
    def __init__(self, file_name, module_floor_name, tube_module_type_name, corridor_module_type_name,
                 basic_module_type_name, conjunctive_module_type_name,
                 fitted_bathroom_type_name, fitted_kitchen_type_name):

        self.storey = ifcopenshell.open(file_name).by_type("IfcBuildingStorey")
        self.module_level = list(filter(lambda l: l.Name == module_floor_name, self.storey))

        self.element_proxy = ifcopenshell.open(file_name).by_type("IfcBuildingElementProxy")
        self.tube_modules = list(filter(lambda t: tube_module_type_name in t.ObjectType, self.element_proxy))
        self.corridor_modules = list(filter(lambda c: corridor_module_type_name in c.ObjectType, self.element_proxy))
        self.basic_modules = list(filter(lambda b: basic_module_type_name in b.ObjectType, self.element_proxy))
        self.conjunctive_modules = list(filter(lambda c: conjunctive_module_type_name in c.ObjectType,
                                               self.element_proxy))

        self.walls = ifcopenshell.open(file_name).by_type("IfcWallStandardCase")
        self.fitted_rooms = list(filter(lambda b: (fitted_bathroom_type_name in b.ObjectType)
                                                  or (fitted_kitchen_type_name in b.ObjectType),
                                        self.element_proxy))
        self.furniture = ifcopenshell.open(file_name).by_type("IfcFurnishingElement")
        self.slabs = ifcopenshell.open(file_name).by_type("IfcSlab")

    # Get the floor elevation
    def getElevation(self, elevation_name):
        house_level = list(filter(lambda l: l.Name == elevation_name, self.storey))
        return round(house_level[0].Elevation)

        # Get useful information (ifc_guid, center coordinates and dimensions) of modules
    def getTubeModuleData(self):
        tube_modules = []
        for tube in self.tube_modules:
            ifc_guid = tube.GlobalId

            (x, y) = (tube.ObjectPlacement.RelativePlacement.Location.Coordinates[0],
                      tube.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
            coordinates = (round(x), round(y))

            (length, width) = (
                tube.IsDefinedBy[2].RelatingPropertyDefinition.HasProperties[0].NominalValue.wrappedValue,
                tube.IsDefinedBy[2].RelatingPropertyDefinition.HasProperties[1].NominalValue.wrappedValue)
            dimensions = (round(length), round(width))

            dictionary = {'IFC_GUID': ifc_guid, 'Coordinates': coordinates, 'Dimensions': dimensions}
            tube_modules.append(dictionary)
        return tube_modules

    def getCorridorModuleData(self):
        corridor_modules = []
        for corridor in self.corridor_modules:
            ifc_guid = corridor.GlobalId

            (x, y) = (corridor.ObjectPlacement.RelativePlacement.Location.Coordinates[0],
                      corridor.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
            coordinates = (round(x), round(y))

            (length, width) = (
                corridor.IsDefinedBy[2].RelatingPropertyDefinition.HasProperties[0].NominalValue.wrappedValue,
                corridor.IsDefinedBy[2].RelatingPropertyDefinition.HasProperties[1].NominalValue.wrappedValue)
            dimensions = (round(length), round(width))

            dictionary = {'IFC_GUID': ifc_guid, 'Coordinates': coordinates, 'Dimensions': dimensions}
            corridor_modules.append(dictionary)
        return corridor_modules

    def getBasicModuleData(self):
        basic_modules = []
        for basic_module in self.basic_modules:
            ifc_guid = basic_module.GlobalId

            (x, y) = (basic_module.ObjectPlacement.RelativePlacement.Location.Coordinates[0],
                      basic_module.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
            coordinates = (round(x), round(y))

            (length, width) = (
                basic_module.IsDefinedBy[2].RelatingPropertyDefinition.HasProperties[0].NominalValue.wrappedValue,
                basic_module.IsDefinedBy[2].RelatingPropertyDefinition.HasProperties[1].NominalValue.wrappedValue)
            dimensions = (round(length), round(width))

            dictionary = {'IFC_GUID': ifc_guid, 'Coordinates': coordinates, 'Dimensions': dimensions}
            basic_modules.append(dictionary)
        return basic_modules

    def getBasicIds(self):
        basic_ids =[]
        for b in self.getBasicModuleData():
            basic_ids.append(b['IFC_GUID'])
        return basic_ids

    def getConjunctiveModuleData(self):
        conjunctive_modules = []
        for conjunct_module in self.conjunctive_modules:
            ifc_guid = conjunct_module.GlobalId

            (x, y) = (conjunct_module.ObjectPlacement.RelativePlacement.Location.Coordinates[0],
                      conjunct_module.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
            coordinates = (round(x), round(y))

            (length, width) = (
                conjunct_module.IsDefinedBy[2].RelatingPropertyDefinition.HasProperties[0].NominalValue.wrappedValue,
                conjunct_module.IsDefinedBy[2].RelatingPropertyDefinition.HasProperties[1].NominalValue.wrappedValue)
            dimensions = (round(length), round(width))

            dictionary = {'IFC_GUID': ifc_guid, 'Coordinates': coordinates, 'Dimensions': dimensions}
            conjunctive_modules.append(dictionary)
        return conjunctive_modules

    def getConjuntiveIds(self):
        conjunctive_ids = []
        for c in self.getConjunctiveModuleData():
            conjunctive_ids.append(c['IFC_GUID'])
        return conjunctive_ids

    # get the connectivity between two modules (IFC_GUIDS, CONNECTS_OR_NOT, Relative Location, Co_edge)
    def getTubeModuleConnectivity(self):
        connectivity = []
        tube_modules = self.getTubeModuleData()
        n = len(tube_modules)
        eps = 1e-4
        for i in range(0, n - 1):
            for j in range(1, n - i):
                x_diff = tube_modules[i]['Coordinates'][0] - tube_modules[i + j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (tube_modules[i]['Dimensions'][0]
                                         + tube_modules[i + j]['Dimensions'][0])
                y_diff = tube_modules[i]['Coordinates'][1] - tube_modules[i + j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (tube_modules[i]['Dimensions'][1]
                                         + tube_modules[i + j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([tube_modules[i]['Coordinates'][1]
                                        + 0.5 * tube_modules[i]['Dimensions'][1],
                                        tube_modules[i]['Coordinates'][1]
                                        - 0.5 * tube_modules[i]['Dimensions'][1],
                                        tube_modules[i + j]['Coordinates'][1]
                                        + 0.5 * tube_modules[i + j]['Dimensions'][1],
                                        tube_modules[i + j]['Coordinates'][1]
                                        - 0.5 * tube_modules[i + j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = tube_modules[i]['Coordinates'][0] - 0.5 * tube_modules[i]['Dimensions'][0]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             tube_modules[i + j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                    if x_diff < 0:
                        co_edge_x = tube_modules[i]['Coordinates'][0] + 0.5 * tube_modules[i]['Dimensions'][0]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             tube_modules[i + j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([tube_modules[i]['Coordinates'][0]
                                        - 0.5 * tube_modules[i]['Dimensions'][0],
                                        tube_modules[i]['Coordinates'][0]
                                        + 0.5 * tube_modules[i]['Dimensions'][0],
                                        tube_modules[i + j]['Coordinates'][0]
                                        + 0.5 * tube_modules[i + j]['Dimensions'][0],
                                        tube_modules[i + j]['Coordinates'][0]
                                        - 0.5 * tube_modules[i + j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = tube_modules[i]['Coordinates'][1] - 0.5 * tube_modules[i]['Dimensions'][1]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             tube_modules[i + j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                    if y_diff < 0:
                        co_edge_y = tube_modules[i]['Coordinates'][1] + 0.5 * tube_modules[i]['Dimensions'][1]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             tube_modules[i + j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                else:
                    connectivity.append([tube_modules[i]['IFC_GUID'],
                                         tube_modules[i + j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0)])
        return connectivity

    def getTubeCorridorModuleConnectivity(self):
        connectivity = []
        tube_modules = self.getTubeModuleData()
        corridor_modules = self.getCorridorModuleData()
        n = len(tube_modules)
        m = len(corridor_modules)

        eps = 1e-4
        for i in range(0, n):
            for j in range(0, m):
                x_diff = tube_modules[i]['Coordinates'][0] - corridor_modules[j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (tube_modules[i]['Dimensions'][0] + corridor_modules[j]['Dimensions'][0])
                y_diff = tube_modules[i]['Coordinates'][1] - corridor_modules[j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (tube_modules[i]['Dimensions'][1] + corridor_modules[j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([tube_modules[i]['Coordinates'][1]
                                        - 0.5 * tube_modules[i]['Dimensions'][1],
                                        tube_modules[i]['Coordinates'][1]
                                        + 0.5 * tube_modules[i]['Dimensions'][1],
                                        corridor_modules[j]['Coordinates'][1]
                                        + 0.5 * corridor_modules[j]['Dimensions'][1],
                                        corridor_modules[j]['Coordinates'][1]
                                        - 0.5 * corridor_modules[j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = tube_modules[i]['Coordinates'][0] - 0.5 * tube_modules[i]['Dimensions'][0]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             corridor_modules[j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                    if x_diff < 0:
                        co_edge_x = tube_modules[i]['Coordinates'][0] + 0.5 * tube_modules[i]['Dimensions'][0]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             corridor_modules[j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([tube_modules[i]['Coordinates'][0]
                                        - 0.5 * tube_modules[i]['Dimensions'][0],
                                        tube_modules[i]['Coordinates'][0]
                                        + 0.5 * tube_modules[i]['Dimensions'][0],
                                        corridor_modules[j]['Coordinates'][0]
                                        + 0.5 * corridor_modules[j]['Dimensions'][0],
                                        corridor_modules[j]['Coordinates'][0]
                                        - 0.5 * corridor_modules[j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = tube_modules[i]['Coordinates'][1] - 0.5 * tube_modules[i]['Dimensions'][1]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             corridor_modules[j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                    if y_diff < 0:
                        co_edge_y = tube_modules[i]['Coordinates'][1] + 0.5 * tube_modules[i]['Dimensions'][1]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             corridor_modules[j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                else:
                    connectivity.append([self.tube_modules[i]['IFC_GUID'],
                                         self.corridor_modules[j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0)])
        return connectivity

    def getTubeBasicModuleConnectivity(self):
        connectivity = []
        tube_modules = self.getTubeModuleData()
        basic_modules = self.getBasicModuleData()
        n = len(tube_modules)
        m = len(basic_modules)

        eps = 1e-4
        for i in range(0, n):
            for j in range(0, m):
                x_diff = tube_modules[i]['Coordinates'][0] - basic_modules[j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (tube_modules[i]['Dimensions'][0] + basic_modules[j]['Dimensions'][0])
                y_diff = tube_modules[i]['Coordinates'][1] - basic_modules[j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (tube_modules[i]['Dimensions'][1] + basic_modules[j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([tube_modules[i]['Coordinates'][1] - 0.5 * tube_modules[i]['Dimensions'][1],
                                        tube_modules[i]['Coordinates'][1] + 0.5 * tube_modules[i]['Dimensions'][1],
                                        basic_modules[j]['Coordinates'][1] + 0.5 * basic_modules[j]['Dimensions'][1],
                                        basic_modules[j]['Coordinates'][1] - 0.5 * basic_modules[j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = tube_modules[i]['Coordinates'][0] - 0.5 * tube_modules[i]['Dimensions'][0]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             basic_modules[j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                    if x_diff < 0:
                        co_edge_x = tube_modules[i]['Coordinates'][0] + 0.5 * tube_modules[i]['Dimensions'][0]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             basic_modules[j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([tube_modules[i]['Coordinates'][0] - 0.5 * tube_modules[i]['Dimensions'][0],
                                        tube_modules[i]['Coordinates'][0] + 0.5 * tube_modules[i]['Dimensions'][0],
                                        basic_modules[j]['Coordinates'][0] + 0.5 * basic_modules[j]['Dimensions'][0],
                                        basic_modules[j]['Coordinates'][0] - 0.5 * basic_modules[j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = tube_modules[i]['Coordinates'][1] - 0.5 * tube_modules[i]['Dimensions'][1]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             basic_modules[j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                    if y_diff < 0:
                        co_edge_y = tube_modules[i]['Coordinates'][1] + 0.5 * tube_modules[i]['Dimensions'][1]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             basic_modules[j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                else:
                    connectivity.append([tube_modules[i]['IFC_GUID'],
                                         basic_modules[j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0)])
        return connectivity

    def getTubeConjunctModuleConnectivity(self):
        connectivity = []
        tube_modules = self.getTubeModuleData()
        conjunctive_modules = self.getConjunctiveModuleData()
        n = len(tube_modules)
        m = len(conjunctive_modules)
        eps = 1e-4
        for i in range(0, n):
            for j in range(0, m):
                x_diff = tube_modules[i]['Coordinates'][0] - conjunctive_modules[j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (tube_modules[i]['Dimensions'][0] + conjunctive_modules[j]['Dimensions'][0])
                y_diff = tube_modules[i]['Coordinates'][1] - conjunctive_modules[j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (tube_modules[i]['Dimensions'][1] + conjunctive_modules[j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([tube_modules[i]['Coordinates'][1]
                                        - 0.5 * tube_modules[i]['Dimensions'][1],
                                        tube_modules[i]['Coordinates'][1]
                                        + 0.5 * tube_modules[i]['Dimensions'][1],
                                        conjunctive_modules[j]['Coordinates'][1]
                                        + 0.5 * conjunctive_modules[j]['Dimensions'][1],
                                        conjunctive_modules[j]['Coordinates'][1]
                                        - 0.5 * conjunctive_modules[j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = tube_modules[i]['Coordinates'][0] - 0.5 * tube_modules[i]['Dimensions'][0]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                    if x_diff < 0:
                        co_edge_x = tube_modules[i]['Coordinates'][0] + 0.5 * tube_modules[i]['Dimensions'][0]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([tube_modules[i]['Coordinates'][0]
                                        - 0.5 * tube_modules[i]['Dimensions'][0],
                                        tube_modules[i]['Coordinates'][0]
                                        + 0.5 * tube_modules[i]['Dimensions'][0],
                                        conjunctive_modules[j]['Coordinates'][0]
                                        + 0.5 * conjunctive_modules[j]['Dimensions'][0],
                                        conjunctive_modules[j]['Coordinates'][0]
                                        - 0.5 * conjunctive_modules[j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = tube_modules[i]['Coordinates'][1] - 0.5 * tube_modules[i]['Dimensions'][1]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                    if y_diff < 0:
                        co_edge_y = tube_modules[i]['Coordinates'][1] + 0.5 * tube_modules[i]['Dimensions'][1]
                        connectivity.append([tube_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                else:
                    connectivity.append([tube_modules[i]['IFC_GUID'],
                                         conjunctive_modules[j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0)])
        return connectivity

    def getCorridorModuleConnectivity(self):
        connectivity = []
        corridor_modules = self.getCorridorModuleData()
        n = len(corridor_modules)

        eps = 1e-4
        for i in range(0, n - 1):
            for j in range(1, n - i):
                x_diff = corridor_modules[i]['Coordinates'][0] - corridor_modules[i + j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (corridor_modules[i]['Dimensions'][0]
                                         + corridor_modules[i + j]['Dimensions'][0])
                y_diff = corridor_modules[i]['Coordinates'][1] - corridor_modules[i + j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (corridor_modules[i]['Dimensions'][1]
                                         + corridor_modules[i + j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([corridor_modules[i]['Coordinates'][1]
                                        + 0.5 * corridor_modules[i]['Dimensions'][1],
                                        corridor_modules[i]['Coordinates'][1]
                                        - 0.5 * corridor_modules[i]['Dimensions'][1],
                                        corridor_modules[i + j]['Coordinates'][1]
                                        + 0.5 * corridor_modules[i + j]['Dimensions'][1],
                                        corridor_modules[i + j]['Coordinates'][1]
                                        - 0.5 * corridor_modules[i + j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = corridor_modules[i]['Coordinates'][0] - 0.5 * corridor_modules[i]['Dimensions'][0]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             corridor_modules[i + j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                    if x_diff < 0:
                        co_edge_x = corridor_modules[i]['Coordinates'][0] + 0.5 * corridor_modules[i]['Dimensions'][0]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             corridor_modules[i + j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([corridor_modules[i]['Coordinates'][0]
                                        - 0.5 * corridor_modules[i]['Dimensions'][0],
                                        corridor_modules[i]['Coordinates'][0]
                                        + 0.5 * corridor_modules[i]['Dimensions'][0],
                                        corridor_modules[i + j]['Coordinates'][0]
                                        + 0.5 * corridor_modules[i + j]['Dimensions'][0],
                                        corridor_modules[i + j]['Coordinates'][0]
                                        - 0.5 * corridor_modules[i + j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = corridor_modules[i]['Coordinates'][1] - 0.5 * corridor_modules[i]['Dimensions'][1]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             corridor_modules[i + j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                    if y_diff < 0:
                        co_edge_y = corridor_modules[i]['Coordinates'][1] + 0.5 * corridor_modules[i]['Dimensions'][1]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             corridor_modules[i + j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                else:
                    connectivity.append([corridor_modules[i]['IFC_GUID'],
                                         corridor_modules[i + j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0)])
        return connectivity

    def getCorridorBasicModuleConnectivity(self):
        connectivity = []
        corridor_modules = self.getCorridorModuleData()
        basic_modules = self.getBasicModuleData()
        n = len(corridor_modules)
        m = len(basic_modules)

        eps = 1e-4
        for i in range(0, n):
            for j in range(0, m):
                x_diff = corridor_modules[i]['Coordinates'][0] - basic_modules[j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (corridor_modules[i]['Dimensions'][0] + basic_modules[j]['Dimensions'][0])
                y_diff = corridor_modules[i]['Coordinates'][1] - basic_modules[j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (corridor_modules[i]['Dimensions'][1] + basic_modules[j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([corridor_modules[i]['Coordinates'][1]
                                        + 0.5 * corridor_modules[i]['Dimensions'][1],
                                        corridor_modules[i]['Coordinates'][1]
                                        - 0.5 * corridor_modules[i]['Dimensions'][1],
                                        basic_modules[j]['Coordinates'][1]
                                        + 0.5 * basic_modules[j]['Dimensions'][1],
                                        basic_modules[j]['Coordinates'][1]
                                        - 0.5 * basic_modules[j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = corridor_modules[i]['Coordinates'][0] - 0.5 * corridor_modules[i]['Dimensions'][0]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             basic_modules[j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                    if x_diff < 0:
                        co_edge_x = corridor_modules[i]['Coordinates'][0] + 0.5 * corridor_modules[i]['Dimensions'][0]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             basic_modules[j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([corridor_modules[i]['Coordinates'][0]
                                        - 0.5 * corridor_modules[i]['Dimensions'][0],
                                        corridor_modules[i]['Coordinates'][0]
                                        + 0.5 * corridor_modules[i]['Dimensions'][0],
                                        basic_modules[j]['Coordinates'][0] + 0.5 * basic_modules[j]['Dimensions'][0],
                                        basic_modules[j]['Coordinates'][0] - 0.5 * basic_modules[j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = corridor_modules[i]['Coordinates'][1] - 0.5 * corridor_modules[i]['Dimensions'][1]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             basic_modules[j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                    if y_diff < 0:
                        co_edge_y = corridor_modules[i]['Coordinates'][1] + 0.5 * corridor_modules[i]['Dimensions'][1]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             basic_modules[j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                else:
                    connectivity.append([corridor_modules[i]['IFC_GUID'],
                                         basic_modules[j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0)])
        return connectivity

    def getCorridorConjunctModuleConnectivity(self):
        connectivity = []
        corridor_modules = self.getCorridorModuleData()
        conjunctive_modules = self.getConjunctiveModuleData()
        n = len(corridor_modules)
        m = len(conjunctive_modules)

        eps = 1e-4
        for i in range(0, n):
            for j in range(0, m):
                x_diff = corridor_modules[i]['Coordinates'][0] - conjunctive_modules[j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (corridor_modules[i]['Dimensions'][0] + conjunctive_modules[j]['Dimensions'][0])
                y_diff = corridor_modules[i]['Coordinates'][1] - conjunctive_modules[j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (corridor_modules[i]['Dimensions'][1] + conjunctive_modules[j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([corridor_modules[i]['Coordinates'][1]
                                        + 0.5 * corridor_modules[i]['Dimensions'][1],
                                        corridor_modules[i]['Coordinates'][1]
                                        - 0.5 * corridor_modules[i]['Dimensions'][1],
                                        conjunctive_modules[j]['Coordinates'][1]
                                        + 0.5 * conjunctive_modules[j]['Dimensions'][1],
                                        conjunctive_modules[j]['Coordinates'][1]
                                        - 0.5 * conjunctive_modules[j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = corridor_modules[i]['Coordinates'][0] - 0.5 * corridor_modules[i]['Dimensions'][0]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                    if x_diff < 0:
                        co_edge_x = corridor_modules[i]['Coordinates'][0] - 0.5 * corridor_modules[i]['Dimensions'][0]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2]))])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([corridor_modules[i]['Coordinates'][0]
                                        - 0.5 * corridor_modules[i]['Dimensions'][0],
                                        corridor_modules[i]['Coordinates'][0]
                                        + 0.5 * corridor_modules[i]['Dimensions'][0],
                                        conjunctive_modules[j]['Coordinates'][0]
                                        + 0.5 * conjunctive_modules[j]['Dimensions'][0],
                                        conjunctive_modules[j]['Coordinates'][0]
                                        - 0.5 * conjunctive_modules[j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = corridor_modules[i]['Coordinates'][1] - 0.5 * corridor_modules[i]['Dimensions'][1]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                    if y_diff < 0:
                        co_edge_y = corridor_modules[i]['Coordinates'][1] + 0.5 * corridor_modules[i]['Dimensions'][1]
                        connectivity.append([corridor_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y))])
                else:
                    connectivity.append([corridor_modules[i]['IFC_GUID'],
                                         conjunctive_modules[j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0)])
        return connectivity

    def getBasicModuleConnectivity(self):
        connectivity = []
        basic_modules = self.getBasicModuleData()
        n = len(basic_modules)
        eps = 1e-4
        for i in range(0, n - 1):
            for j in range(1, n - i):
                angle = getAngle(basic_modules[i]['Coordinates'][0], basic_modules[i]['Coordinates'][1],
                                 basic_modules[i + j]['Coordinates'][0], basic_modules[i + j]['Coordinates'][1])
                x_diff = basic_modules[i]['Coordinates'][0] - basic_modules[i + j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (basic_modules[i]['Dimensions'][0] + basic_modules[i + j]['Dimensions'][0])
                y_diff = basic_modules[i]['Coordinates'][1] - basic_modules[i + j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (basic_modules[i]['Dimensions'][1] + basic_modules[i + j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([basic_modules[i]['Coordinates'][1]
                                        + 0.5 * basic_modules[i]['Dimensions'][1],
                                        basic_modules[i]['Coordinates'][1]
                                        - 0.5 * basic_modules[i]['Dimensions'][1],
                                        basic_modules[i + j]['Coordinates'][1]
                                        + 0.5 * basic_modules[i + j]['Dimensions'][1],
                                        basic_modules[i + j]['Coordinates'][1]
                                        - 0.5 * basic_modules[i + j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = basic_modules[i]['Coordinates'][0] - 0.5 * basic_modules[i]['Dimensions'][0]
                        connectivity.append([basic_modules[i]['IFC_GUID'],
                                             basic_modules[i + j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2])),
                                             angle])
                    if x_diff < 0:
                        co_edge_x = basic_modules[i]['Coordinates'][0] + 0.5 * basic_modules[i]['Dimensions'][0]
                        connectivity.append([basic_modules[i]['IFC_GUID'],
                                             basic_modules[i + j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2])),
                                             angle])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([basic_modules[i]['Coordinates'][0] - 0.5 * basic_modules[i]['Dimensions'][0],
                                        basic_modules[i]['Coordinates'][0] + 0.5 * basic_modules[i]['Dimensions'][0],
                                        basic_modules[i + j]['Coordinates'][0]
                                        + 0.5 * basic_modules[i + j]['Dimensions'][0],
                                        basic_modules[i + j]['Coordinates'][0]
                                        - 0.5 * basic_modules[i + j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = basic_modules[i]['Coordinates'][1] - 0.5 * basic_modules[i]['Dimensions'][1]
                        connectivity.append([basic_modules[i]['IFC_GUID'],
                                             basic_modules[i + j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y)),
                                             angle])
                    if y_diff < 0:
                        co_edge_y = basic_modules[i]['Coordinates'][1] + 0.5 * basic_modules[i]['Dimensions'][1]
                        connectivity.append([basic_modules[i]['IFC_GUID'],
                                             basic_modules[i + j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y)),
                                             angle])
                else:
                    connectivity.append([basic_modules[i]['IFC_GUID'],
                                         basic_modules[i + j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0),
                                         angle])
        return connectivity

    def getBasicConjunctModuleConnectivity(self):
        connectivity = []

        basic_modules = self.getBasicModuleData()
        conjunctive_modules = self.getConjunctiveModuleData()

        n = len(basic_modules)
        m = len(conjunctive_modules)

        eps = 1e-4
        for i in range(0, n):
            for j in range(0, m):
                angle = getAngle(basic_modules[i]['Coordinates'][0], basic_modules[i]['Coordinates'][1],
                                 conjunctive_modules[j]['Coordinates'][0], conjunctive_modules[j]['Coordinates'][1])
                x_diff = basic_modules[i]['Coordinates'][0] - conjunctive_modules[j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (basic_modules[i]['Dimensions'][0] + conjunctive_modules[j]['Dimensions'][0])
                y_diff = basic_modules[i]['Coordinates'][1] - conjunctive_modules[j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (basic_modules[i]['Dimensions'][1] + conjunctive_modules[j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([basic_modules[i]['Coordinates'][1]
                                        + 0.5 * basic_modules[i]['Dimensions'][1],
                                        basic_modules[i]['Coordinates'][1]
                                        - 0.5 * basic_modules[i]['Dimensions'][1],
                                        conjunctive_modules[j]['Coordinates'][1]
                                        + 0.5 * conjunctive_modules[j]['Dimensions'][1],
                                        conjunctive_modules[j]['Coordinates'][1]
                                        - 0.5 * conjunctive_modules[j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = basic_modules[i]['Coordinates'][0] - 0.5 * basic_modules[i]['Dimensions'][0]
                        connectivity.append([basic_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2])),
                                             angle])
                    if x_diff < 0:
                        co_edge_x = basic_modules[i]['Coordinates'][0] + 0.5 * basic_modules[i]['Dimensions'][0]
                        connectivity.append([basic_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2])),
                                             angle])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([basic_modules[i]['Coordinates'][0]
                                        - 0.5 * basic_modules[i]['Dimensions'][0],
                                        basic_modules[i]['Coordinates'][0]
                                        + 0.5 * basic_modules[i]['Dimensions'][0],
                                        conjunctive_modules[j]['Coordinates'][0]
                                        + 0.5 * conjunctive_modules[j]['Dimensions'][0],
                                        conjunctive_modules[j]['Coordinates'][0]
                                        - 0.5 * conjunctive_modules[j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = basic_modules[i]['Coordinates'][1] - 0.5 * basic_modules[i]['Dimensions'][1]
                        connectivity.append([basic_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y)),
                                             angle])
                    if y_diff < 0:
                        co_edge_y = basic_modules[i]['Coordinates'][1] + 0.5 * basic_modules[i]['Dimensions'][1]
                        connectivity.append([basic_modules[i]['IFC_GUID'],
                                             conjunctive_modules[j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y)),
                                             angle])
                else:
                    connectivity.append([basic_modules[i]['IFC_GUID'],
                                         conjunctive_modules[j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0),
                                         angle])
        return connectivity

    def getConjunctModuleConnectivity(self):
        connectivity = []
        conjunctive_modules = self.getConjunctiveModuleData()
        n = len(conjunctive_modules)
        eps = 1e-4
        for i in range(0, n - 1):
            for j in range(1, n - i):
                angle = getAngle(conjunctive_modules[i]['Coordinates'][0],
                                 conjunctive_modules[i]['Coordinates'][1],
                                 conjunctive_modules[i + j]['Coordinates'][0],
                                 conjunctive_modules[i + j]['Coordinates'][1])
                x_diff = conjunctive_modules[i]['Coordinates'][0] - conjunctive_modules[i + j]['Coordinates'][0]
                a = abs(x_diff) - 0.5 * (conjunctive_modules[i]['Dimensions'][0]
                                         + conjunctive_modules[i + j]['Dimensions'][0])
                y_diff = conjunctive_modules[i]['Coordinates'][1] - conjunctive_modules[i + j]['Coordinates'][1]
                b = abs(y_diff) - 0.5 * (conjunctive_modules[i]['Dimensions'][1]
                                         + conjunctive_modules[i + j]['Dimensions'][1])
                if abs(a) <= eps and b < 0:
                    co_edge_y = sorted([conjunctive_modules[i]['Coordinates'][1]
                                        + 0.5 * conjunctive_modules[i]['Dimensions'][1],
                                        conjunctive_modules[i]['Coordinates'][1]
                                        - 0.5 * conjunctive_modules[i]['Dimensions'][1],
                                        conjunctive_modules[i + j]['Coordinates'][1]
                                        + 0.5 * conjunctive_modules[i + j]['Dimensions'][1],
                                        conjunctive_modules[i + j]['Coordinates'][1]
                                        - 0.5 * conjunctive_modules[i + j]['Dimensions'][1]])
                    if x_diff > 0:
                        co_edge_x = conjunctive_modules[i]['Coordinates'][0] \
                                    - 0.5 * conjunctive_modules[i]['Dimensions'][0]
                        connectivity.append([conjunctive_modules[i]['IFC_GUID'],
                                             conjunctive_modules[i + j]['IFC_GUID'],
                                             1,
                                             "right&left",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2])),
                                             angle])
                    if x_diff < 0:
                        co_edge_x = conjunctive_modules[i]['Coordinates'][0] \
                                    + 0.5 * conjunctive_modules[i]['Dimensions'][0]
                        connectivity.append([conjunctive_modules[i]['IFC_GUID'],
                                             conjunctive_modules[i + j]['IFC_GUID'],
                                             1,
                                             "left&right",
                                             (round(co_edge_x), round(co_edge_y[1])),
                                             (round(co_edge_x), round(co_edge_y[2])),
                                             angle])
                elif abs(b) <= eps and a < 0:
                    co_edge_x = sorted([conjunctive_modules[i]['Coordinates'][0]
                                        - 0.5 * conjunctive_modules[i]['Dimensions'][0],
                                        conjunctive_modules[i]['Coordinates'][0]
                                        + 0.5 * conjunctive_modules[i]['Dimensions'][0],
                                        conjunctive_modules[i + j]['Coordinates'][0]
                                        + 0.5 * conjunctive_modules[i + j]['Dimensions'][0],
                                        conjunctive_modules[i + j]['Coordinates'][0]
                                        - 0.5 * conjunctive_modules[i + j]['Dimensions'][0]])
                    if y_diff > 0:
                        co_edge_y = conjunctive_modules[i]['Coordinates'][1] \
                                    - 0.5 * conjunctive_modules[i]['Dimensions'][1]
                        connectivity.append([conjunctive_modules[i]['IFC_GUID'],
                                             conjunctive_modules[i + j]['IFC_GUID'],
                                             1,
                                             "up&down",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y)),
                                             angle])
                    if y_diff < 0:
                        co_edge_y = conjunctive_modules[i]['Coordinates'][1] \
                                    + 0.5 * conjunctive_modules[i]['Dimensions'][1]
                        connectivity.append([conjunctive_modules[i]['IFC_GUID'],
                                             conjunctive_modules[i + j]['IFC_GUID'],
                                             1,
                                             "down&up",
                                             (round(co_edge_x[1]), round(co_edge_y)),
                                             (round(co_edge_x[2]), round(co_edge_y)),
                                             angle])
                else:
                    connectivity.append([conjunctive_modules[i]['IFC_GUID'],
                                         conjunctive_modules[i + j]['IFC_GUID'],
                                         0,
                                         "no_connectivity",
                                         (0, 0),
                                         (0, 0),
                                         angle])
        return connectivity

    # get the walls in different drawn ways used for later functions
    def getDownDrawnWalls(self, elevation):
        down_drawn_walls = list(filter(lambda wall:
                                       wall.ObjectPlacement.PlacementRelTo.RelativePlacement.Location.Coordinates[2] ==
                                       elevation and
                                       wall.ObjectPlacement.RelativePlacement.RefDirection is not None and
                                       wall.ObjectPlacement.RelativePlacement.RefDirection.DirectionRatios ==
                                       (0.0, -1.0, 0.0),
                                       self.walls))
        return down_drawn_walls

    def getUpDrawnWalls(self, elevation):
        up_drawn_walls = list(filter(lambda wall:
                                     wall.ObjectPlacement.PlacementRelTo.RelativePlacement.Location.Coordinates[2]
                                     == elevation and
                                     wall.ObjectPlacement.RelativePlacement.RefDirection is not None and
                                     wall.ObjectPlacement.RelativePlacement.RefDirection.DirectionRatios ==
                                     (0.0, 1.0, 0.0),
                                     self.walls))
        return up_drawn_walls

    def getLeftDrawnWalls(self, elevation):
        left_drawn_walls = list(filter(lambda wall:
                                       wall.ObjectPlacement.PlacementRelTo.RelativePlacement.Location.Coordinates[2]
                                       == elevation and
                                       wall.ObjectPlacement.RelativePlacement.RefDirection is not None and
                                       wall.ObjectPlacement.RelativePlacement.RefDirection.DirectionRatios ==
                                       (-1.0, 0.0, 0.0),
                                       self.walls))
        return left_drawn_walls

    def getRightDrawnWalls(self, elevation):
        right_drawn_walls = list(filter(lambda w:
                                        w.ObjectPlacement.PlacementRelTo.RelativePlacement.Location.Coordinates[2]
                                        == elevation and
                                        w.ObjectPlacement.RelativePlacement.RefDirection is None,
                                        self.walls))  # (1.0, 0.0, 0.0)
        return right_drawn_walls

    # Get components for each module

    def getSlabsOfModule(self, module, elevation):
        slabs = list(filter(lambda m:
                            m.ObjectPlacement.PlacementRelTo.RelativePlacement.Location.Coordinates[2] == elevation
                            and
                            module['Coordinates'][0] - module['Dimensions'][0] / 2 <=
                            m.Representation.Representations[0].Items[0].Position.Location.Coordinates[0] <=
                            module['Coordinates'][0] + module['Dimensions'][0] / 2
                            and
                            module['Coordinates'][1] - module['Dimensions'][1] / 2 <=
                            m.Representation.Representations[0].Items[0].Position.Location.Coordinates[1] <=
                            module['Coordinates'][1] + module['Dimensions'][1] / 2,
                            self.slabs))
        return slabs

    def getInteriorWallsOfModule(self, module, elevation, wall_width_min):
        w2 = wall_width_min / 2
        walls_down = list(filter(lambda w:
                                 module['Coordinates'][0] - module['Dimensions'][0] / 2 + w2
                                 < round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                                 < module['Coordinates'][0] + module['Dimensions'][0] / 2 - w2
                                 and
                                 module['Coordinates'][1] - module['Dimensions'][1] / 2 - w2
                                 <= round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) -
                                 w.Representation.Representations[1].Items[0].SweptArea.XDim
                                 < round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
                                 <= module['Coordinates'][1] + module['Dimensions'][1] / 2 + w2,
                                 self.getDownDrawnWalls(elevation)))

        walls_up = list(filter(lambda w:
                               module['Coordinates'][0] - module['Dimensions'][0] / 2 + w2
                               < round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                               < module['Coordinates'][0] + module['Dimensions'][0] / 2 - w2
                               and
                               module['Coordinates'][1] - module['Dimensions'][1] / 2 - w2
                               <= round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
                               < round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) +
                               round(w.Representation.Representations[1].Items[0].SweptArea.XDim)
                               <= module['Coordinates'][1] + module['Dimensions'][1] / 2 + w2,
                               self.getUpDrawnWalls(elevation)))

        walls_left = list(filter(lambda w:
                                 module['Coordinates'][0] - module['Dimensions'][0] / 2 - w2
                                 <= round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) -
                                 round(w.Representation.Representations[1].Items[0].SweptArea.XDim)
                                 < round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                                 <= module['Coordinates'][0] + module['Dimensions'][0] / 2 + w2
                                 and
                                 module['Coordinates'][1] - module['Dimensions'][1] / 2 + w2
                                 < round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
                                 < module['Coordinates'][1] + module['Dimensions'][1] / 2 - w2,
                                 self.getLeftDrawnWalls(elevation)))

        walls_right = list(filter(lambda w:
                                  round(w.ObjectPlacement.PlacementRelTo.RelativePlacement.Location.Coordinates[2])
                                  == round(elevation) and
                                  w.ObjectPlacement.RelativePlacement.RefDirection is None and
                                  module['Coordinates'][0] - module['Dimensions'][0] / 2 - w2
                                  <= round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                                  < round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) +
                                  round(w.Representation.Representations[1].Items[0].SweptArea.XDim)
                                  <= module['Coordinates'][0] + module['Dimensions'][0] / 2 + w2
                                  and
                                  module['Coordinates'][1] - module['Dimensions'][1] / 2 + w2
                                  < round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
                                  < module['Coordinates'][1] + module['Dimensions'][1] / 2 - w2,
                                  self.getRightDrawnWalls(elevation)))

        return walls_down + walls_up + walls_right + walls_left

    def getFurnitureOfModule(self, module, elevation):
        furniture = list(filter(lambda m:
                                m.ObjectPlacement.PlacementRelTo.RelativePlacement.Location.Coordinates[2] == elevation
                                and
                                module['Coordinates'][0] - module['Dimensions'][0] / 2 <=
                                m.ObjectPlacement.RelativePlacement.Location.Coordinates[0] <=
                                module['Coordinates'][0] + module['Dimensions'][0] / 2
                                and
                                module['Coordinates'][1] - module['Dimensions'][1] / 2 <=
                                m.ObjectPlacement.RelativePlacement.Location.Coordinates[1] <=
                                module['Coordinates'][1] + module['Dimensions'][1] / 2,
                                self.furniture))
        return furniture

    def getFittedBathroomsOfModule(self, module, elevation):
        bathroom = list(filter(lambda m:
                               m.ObjectPlacement.PlacementRelTo.RelativePlacement.Location.Coordinates[2] == elevation
                               and
                               module['Coordinates'][0] - module['Dimensions'][0] / 2 <=
                               m.ObjectPlacement.RelativePlacement.Location.Coordinates[0] <=
                               module['Coordinates'][0] + module['Dimensions'][0] / 2
                               and
                               module['Coordinates'][1] - module['Dimensions'][1] / 2 <=
                               m.ObjectPlacement.RelativePlacement.Location.Coordinates[1] <=
                               module['Coordinates'][1] + module['Dimensions'][1] / 2,
                               self.fitted_rooms))
        return bathroom

    def getComponentsOfModule(self, module, elevation, wall_width_min):
        ifc_guids = []
        # slab:
        # print("Slabs:")
        slabs = self.getSlabsOfModule(module, elevation)
        for slab in slabs:
            ifc_guids.append(slab.GlobalId)
            # print(slab.GlobalId)
        # interior wall
        # print("Walls:")
        walls = self.getInteriorWallsOfModule(module, elevation, wall_width_min)
        for wall in walls:
            ifc_guids.append(wall.GlobalId)
            # print(wall.GlobalId)
        # furniture
        # print("Furniture: ")
        furniture = self.getFurnitureOfModule(module, elevation)
        for f in furniture:
            ifc_guids.append(f.GlobalId)
            # print(f.GlobalId)
        # fitted bathroom
        # print("Bathrooms:")
        fitted_bathrooms = self.getFittedBathroomsOfModule(module, elevation)
        for fitted_bathroom in fitted_bathrooms:
            ifc_guids.append(fitted_bathroom.GlobalId)
            # print(fitted_bathroom.GlobalId)
        # print()
        return ifc_guids

    def getWallsOfCoEdge(self, connectivity, elevation, wall_with_min):
        ifc_guids = []
        w = wall_with_min / 2
        walls_down = []
        walls_up = []
        walls_left = []
        walls_right = []

        module1 = list(filter(lambda m: m['IFC_GUID'] == connectivity[0],
                              self.getBasicModuleData() + self.getConjunctiveModuleData()))[0]

        module2 = list(filter(lambda m: m['IFC_GUID'] == connectivity[1],
                              self.getBasicModuleData() + self.getConjunctiveModuleData()))[0]

        if connectivity[3] == "up&down" or connectivity[3] == "down&up":
            a = connectivity[4][0]
            b = connectivity[5][0]

            walls_left += list(filter(lambda wall:
                                      (a - w <= round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) -
                                       round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) < b - w or
                                       a + w < round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                                       <= b + w)
                                      and
                                      round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) ==
                                      connectivity[4][1],
                                      self.getLeftDrawnWalls(elevation)))

            walls_right += list(filter(lambda wall:
                                       (a + w < round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) +
                                        round(wall.Representation.Representations[1].Items[0].SweptArea.XDim)
                                        <= b + w or
                                        a - w <= round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                                        < b - w)
                                       and
                                       round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) ==
                                       connectivity[4][1],
                                       self.getRightDrawnWalls(elevation)))

            walls_up += list(filter(lambda wall:
                                    ((module1['Coordinates'][1] - module1['Dimensions'][1] / 2 - w <=
                                      round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) <
                                      module1['Coordinates'][1] + module1['Dimensions'][1] / 2 - w
                                      and
                                      module2['Coordinates'][1] - module2['Dimensions'][1] / 2 + w <
                                      round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) +
                                      round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) <=
                                      module2['Coordinates'][1] + module2['Dimensions'][1] / 2 + w)
                                     or
                                     (module2['Coordinates'][1] - module2['Dimensions'][1] / 2 - w <=
                                      round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) <
                                      module2['Coordinates'][1] + module2['Dimensions'][1] / 2 - w
                                      and
                                      module1['Coordinates'][1] - module1['Dimensions'][1] / 2 + w <
                                      round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) +
                                      round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) <=
                                      module1['Coordinates'][1] + module1['Dimensions'][1] / 2 + w))
                                    and
                                    a + w <
                                    round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                                    < b - w,
                                    self.getUpDrawnWalls(elevation)))

            walls_down += list(filter(lambda wall:
                                      ((module1['Coordinates'][1] - module1['Dimensions'][1] / 2 + w <
                                        round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) <=
                                        module1['Coordinates'][1] + module1['Dimensions'][1] / 2 + w
                                        and
                                        module2['Coordinates'][1] - module2['Dimensions'][1] / 2 - w <=
                                        round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) -
                                        round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) <
                                        module2['Coordinates'][1] + module2['Dimensions'][1] / 2 - w)
                                       or
                                       (module2['Coordinates'][1] - module2['Dimensions'][1] / 2 + w <
                                        round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) <=
                                        module2['Coordinates'][1] + module2['Dimensions'][1] / 2 + w
                                        and
                                        module1['Coordinates'][1] - module1['Dimensions'][1] / 2 - w <=
                                        round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) -
                                        round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) <
                                        module1['Coordinates'][1] + module1['Dimensions'][1] / 2 - w))
                                      and
                                      a + w <
                                      round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                                      < b - w,
                                      self.getDownDrawnWalls(elevation)))

        if connectivity[3] == "left&right" or connectivity[3] == "right&left":
            c = connectivity[4][1]
            d = connectivity[5][1]
            walls_up += list(filter(lambda wall:
                                    (c + w < round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) +
                                     round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) <= d + w or
                                     c - w <= round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
                                     < d - w)
                                    and
                                    round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) ==
                                    connectivity[4][0],
                                    self.getUpDrawnWalls(elevation)))

            walls_down += list(filter(lambda wall:
                                      (c - w <= round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) -
                                       round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) < d - w or
                                       c + w < round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) <=
                                       d + w)
                                      and
                                      round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) ==
                                      connectivity[4][0],
                                      self.getDownDrawnWalls(elevation)))

            walls_left += list(filter(lambda wall:
                                      ((module1['Coordinates'][0] - module1['Dimensions'][0] / 2 + w <
                                        round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) <=
                                        module1['Coordinates'][0] + module1['Dimensions'][0] / 2 + w
                                        and
                                        module2['Coordinates'][0] - module2['Dimensions'][0] / 2 - w <=
                                        round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) -
                                        round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) <
                                        module2['Coordinates'][0] + module2['Dimensions'][0] / 2 - w)
                                       or
                                       (module2['Coordinates'][0] - module2['Dimensions'][0] / 2 + w <
                                        round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) <=
                                        module2['Coordinates'][0] + module2['Dimensions'][0] / 2 + w
                                        and
                                        module1['Coordinates'][0] - module1['Dimensions'][0] / 2 - w <=
                                        round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) -
                                        round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) <
                                        module1['Coordinates'][0] + module1['Dimensions'][0] / 2 - w))
                                      and
                                      c + w <
                                      round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
                                      < d - w,
                                      self.getLeftDrawnWalls(elevation)))

            walls_right += list(filter(lambda wall:
                                       ((module1['Coordinates'][0] - module1['Dimensions'][0] / 2 - w <=
                                         round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) <
                                         module1['Coordinates'][0] + module1['Dimensions'][0] / 2 - w
                                         and
                                         module2['Coordinates'][0] - module2['Dimensions'][0] / 2 + w <
                                         round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) +
                                         round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) <=
                                         module2['Coordinates'][0] + module2['Dimensions'][0] / 2 + w)
                                        or
                                        (module2['Coordinates'][0] - module2['Dimensions'][0] / 2 - w <=
                                         round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) <
                                         module2['Coordinates'][0] + module2['Dimensions'][0] / 2 - w
                                         and
                                         module1['Coordinates'][0] - module1['Dimensions'][0] / 2 + w <
                                         round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) +
                                         round(wall.Representation.Representations[1].Items[0].SweptArea.XDim) <=
                                         module1['Coordinates'][0] + module1['Dimensions'][0] / 2 + w))
                                       and
                                       c + w <
                                       round(wall.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
                                       < d - w,
                                       self.getRightDrawnWalls(elevation)))

        for w in (walls_down + walls_up + walls_left + walls_right):
            ifc_guids.append(w.GlobalId)

        return ifc_guids

    # Get the accessibility between moduls depending on different floor plans
    def getTubeCorridorModuleAccessibility(self, elevation):
        tube_modules = self.getTubeModuleData()
        tube_corridor_connectivity = self.getTubeCorridorModuleConnectivity()
        accessibility = []
        h_connectivity = []
        v_connectivity = []
        for t in tube_modules:
            h_connectivity += list(filter(lambda element: element[0] == t['IFC_GUID'] and
                                                          (element[3] == 'right&left' or element[3] == 'left&right'),
                                          tube_corridor_connectivity))
            v_connectivity += list(filter(lambda element: element[0] == t['IFC_GUID'] and
                                                          (element[3] == 'up&down' or element[3] == 'down&up'),
                                          tube_corridor_connectivity))
        for h in h_connectivity:
            walls_to_down = list(filter(lambda m:
                                        round(m.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) == h[4][0],
                                        self.getDownDrawnWalls(elevation)))
            for w in walls_to_down:
                opening = list(filter(lambda op:
                                      h[4][1] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[1] -
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= h[5][1],
                                      w.HasOpenings))
                if opening:
                    accessibility.append([h[0], h[1], 1])

            walls_to_up = list(filter(lambda m:
                                      round(m.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) == h[4][0],
                                      self.getUpDrawnWalls(elevation)))
            for w in walls_to_up:
                opening = list(filter(lambda op:
                                      h[4][1] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[1] +
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= h[5][1],
                                      w.HasOpenings))
                if opening:
                    accessibility.append([h[0], h[1], 1])
        for v in v_connectivity:
            walls_to_left = list(filter(lambda m:
                                        round(m.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) == v[4][1],
                                        self.getLeftDrawnWalls(elevation)))
            for w in walls_to_left:
                opening = list(filter(lambda op:
                                      v[4][0] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] -
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= v[5][0],
                                      w.HasOpenings))
                if opening:
                    accessibility.append([v[0], v[1], 1])
                # for o in w.HasOpenings:
                #     o_x = w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] - \
                #           o.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                #     if v[4][0] <= o_x <= v[5][0]:
                #         connectivity.append([v[0], v[1], 1])

            walls_to_right = list(filter(lambda m:
                                         round(m.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) == v[4][1],
                                         self.getRightDrawnWalls(elevation)))
            for w in walls_to_right:
                opening = list(filter(lambda op:
                                      v[4][0] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] +
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= v[5][0],
                                      w.HasOpenings))
                if opening:
                    accessibility.append([v[0], v[1], 1])

        return accessibility

    def getCorridorHouseAccessibility(self, elevation):
        corridor_modules = self.getCorridorModuleData()
        corridor_basic_connectivity = self.getCorridorBasicModuleConnectivity()
        corridor_conjunct_connectivity = self.getCorridorConjunctModuleConnectivity()
        accessibility = []
        h_connectivity = []
        v_connectivity = []
        for c in corridor_modules:
            h_connectivity += list(filter(lambda element: element[0] == c['IFC_GUID'] and
                                                          (element[3] == 'right&left' or element[3] == 'left&right'),
                                          corridor_basic_connectivity + corridor_conjunct_connectivity))

            v_connectivity += list(filter(lambda element: element[0] == c['IFC_GUID'] and
                                                          (element[3] == 'up&down' or element[3] == 'down&up'),
                                          corridor_basic_connectivity + corridor_conjunct_connectivity))

        for h in h_connectivity:
            walls_to_down = list(filter(lambda m:
                                        round(m.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) == h[4][0],
                                        self.getDownDrawnWalls(elevation)))
            for w in walls_to_down:
                opening = list(filter(lambda op:
                                      h[4][1] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[1] -
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= h[5][1],
                                      w.HasOpenings))
                if opening:
                    name = opening[0].RelatedOpeningElement.Name
                    door_family_type = name.split(":")[1]
                    accessibility.append([h[0], h[1], 1, door_family_type])

            walls_to_up = list(filter(lambda m:
                                      round(m.ObjectPlacement.RelativePlacement.Location.Coordinates[0]) == h[4][0],
                                      self.getUpDrawnWalls(elevation)))
            for w in walls_to_up:
                opening = list(filter(lambda op:
                                      h[4][1] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[1] +
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= h[5][1],
                                      w.HasOpenings))
                if opening:
                    name = opening[0].RelatedOpeningElement.Name
                    door_family_type = name.split(":")[1]
                    accessibility.append([h[0], h[1], 1, door_family_type])

        for v in v_connectivity:
            walls_to_left = list(filter(lambda m:
                                        round(m.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) == v[4][1],
                                        self.getLeftDrawnWalls(elevation)))
            for w in walls_to_left:
                opening = list(filter(lambda op:
                                      v[4][0] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] -
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= v[5][0],
                                      w.HasOpenings))
                if opening:
                    name = opening[0].RelatedOpeningElement.Name
                    door_family_type = name.split(":")[1]
                    accessibility.append([v[0], v[1], 1, door_family_type])
                # for o in w.HasOpenings:
                #     o_x = w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] - \
                #           o.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                #     if v[4][0] <= o_x <= v[5][0]:
                #         connectivity.append([v[0], v[1], 1])

            walls_to_right = list(filter(lambda m:
                                         round(m.ObjectPlacement.RelativePlacement.Location.Coordinates[1]) == v[4][1],
                                         self.getRightDrawnWalls(elevation)))
            for w in walls_to_right:
                opening = list(filter(lambda op:
                                      v[4][0] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] +
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= v[5][0],
                                      w.HasOpenings))
                if opening:
                    name = opening[0].RelatedOpeningElement.Name
                    door_family_type = name.split(":")[1]
                    accessibility.append([v[0], v[1], 1, door_family_type])

        for i in range(len(accessibility)):
            accessibility[i].append(f"house_{i + 1}")

        return accessibility

    def getHouseAccessibility(self, elevation, wall_width_min, wall_width_max):
        accessibility = []
        h_connectivity = []
        v_connectivity = []
        basic_module = self.getBasicModuleData()
        conjunctive_module = self.getConjunctiveModuleData()
        basic_connectivity = self.getBasicModuleConnectivity()
        conjunct_connectivity = self.getConjunctModuleConnectivity()
        basic_conjunct_connectivity = self.getBasicConjunctModuleConnectivity()
        w1 = wall_width_min / 2
        w2 = wall_width_max / 2

        for house in basic_module + conjunctive_module:
            h_connectivity += list(filter(lambda element: element[0] == house['IFC_GUID'] and
                                                          (element[3] == 'right&left' or element[3] == 'left&right'),
                                          basic_connectivity + conjunct_connectivity + basic_conjunct_connectivity))
            v_connectivity += list(filter(lambda element: element[0] == house['IFC_GUID'] and
                                                          (element[3] == 'up&down' or element[3] == 'down&up'),
                                          basic_connectivity + conjunct_connectivity + basic_conjunct_connectivity))
        for h in h_connectivity:
            down_drawn_walls = list(filter(lambda mm:
                                           round(mm.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                                           == h[4][0],
                                           self.getDownDrawnWalls(elevation)))
            up_drawn_walls = list(filter(lambda mm:
                                         round(mm.ObjectPlacement.RelativePlacement.Location.Coordinates[0])
                                         == h[4][0],
                                         self.getUpDrawnWalls(elevation)))
            a_list = []
            for w in down_drawn_walls + up_drawn_walls:
                if w in down_drawn_walls:
                    a_list.append((round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1] -
                                         w.Representation.Representations[1].Items[0].SweptArea.XDim),
                                   round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1])))
                elif w in up_drawn_walls:
                    a_list.append((round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1]),
                                   round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[1] +
                                         w.Representation.Representations[1].Items[0].SweptArea.XDim)))
            sorted_list = sorted(a_list)
            m = 0
            for w in down_drawn_walls:
                opening = list(filter(lambda op:
                                      h[4][1] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[1] -
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= h[5][1],
                                      w.HasOpenings))
                if opening:
                    m = 1
                    accessibility.append([h[0], h[1], 1])
                    break
            for w in up_drawn_walls:
                opening = list(filter(lambda op:
                                      h[4][1] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[1] +
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= h[5][1],
                                      w.HasOpenings))
                if opening:
                    m = 1
                    accessibility.append([h[0], h[1], 1])
                    break
            if m == 1:
                continue

            n = []
            x = []

            # If there is only one wall and the co-edge is covered
            if len(sorted_list) == 1 and sorted_list[0][0] <= h[4][1] + w1 and sorted_list[0][1] >= h[5][1] - w1:
                accessibility.append([h[0], h[1], 0])
                continue
            elif len(sorted_list) > 1:
                # If there are multiple walls and any of them covers the co-edge
                for i in range(len(sorted_list)):
                    if sorted_list[i][0] <= h[4][1] + w1 and sorted_list[i][1] >= h[5][1] - w1:
                        x.append(1)
                # If there are multiple walls, they are connected to cover the co-edge
                # (partition walls perpendicular to the co-edge is allowed.)
                for i in range(len(sorted_list) - 1):
                    # Prevents both sides from being equal
                    if ((h[4][1] + w2 < sorted_list[i][1] < sorted_list[i + 1][0] < h[5][1] - w2 or
                         h[4][1] + w2 <= sorted_list[i][1] < sorted_list[i + 1][0] < h[5][1] - w2 or
                         h[4][1] + w2 < sorted_list[i][1] < sorted_list[i + 1][0] <= h[5][1] - w2)
                            and (sorted_list[0][0] <= h[4][1] + w1 and sorted_list[-1][1] >= h[5][1] - w1)):
                        if 0 < sorted_list[i + 1][0] - sorted_list[i][1] <= 2 * w2:
                            n.append(0)
                        else:
                            n.append(1)
            if x:
                accessibility.append([h[0], h[1], 0])
                continue
            if n != [] and 1 not in n:
                # If n is null it means that each of the multiple walls does not pass through the co-edge
                accessibility.append([h[0], h[1], 0])
                continue
            # the rest connectivity are all accessibility
            accessibility.append([h[0], h[1], 1])

        for v in v_connectivity:
            left_drawn_walls = list(filter(lambda mm:
                                           round(mm.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
                                           == v[4][1],
                                           self.getLeftDrawnWalls(elevation)))
            right_drawn_walls = list(filter(lambda mm:
                                            round(mm.ObjectPlacement.RelativePlacement.Location.Coordinates[1])
                                            == v[4][1],
                                            self.getRightDrawnWalls(elevation)))
            a_list = []
            for w in left_drawn_walls + right_drawn_walls:
                if w in left_drawn_walls:
                    a_list.append((round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] -
                                         w.Representation.Representations[1].Items[0].SweptArea.XDim),
                                   round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0])))
                elif w in right_drawn_walls:
                    a_list.append((round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0]),
                                   round(w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] +
                                         w.Representation.Representations[1].Items[0].SweptArea.XDim)))

            sorted_list = sorted(a_list)
            m = 0
            for w in left_drawn_walls:
                opening = list(filter(lambda op:
                                      v[4][0] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] -
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= v[5][0],
                                      w.HasOpenings))
                if opening:
                    m = 1
                    accessibility.append([v[0], v[1], 1])
                    break
            for w in right_drawn_walls:
                opening = list(filter(lambda op:
                                      v[4][0] <=
                                      w.ObjectPlacement.RelativePlacement.Location.Coordinates[0] +
                                      op.RelatedOpeningElement.ObjectPlacement.RelativePlacement.Location.Coordinates[0]
                                      <= v[5][0],
                                      w.HasOpenings))
                if opening:
                    m = 1
                    accessibility.append([v[0], v[1], 1])
                    break
            if m == 1:
                continue
            n = []
            x = []
            # If there is only one wall and the co-edge is covered
            if len(sorted_list) == 1 and sorted_list[0][0] <= v[4][0] + w1 and sorted_list[0][1] >= v[5][0] - w1:
                accessibility.append([v[0], v[1], 0])
                continue
            elif len(sorted_list) > 1:
                # If there are multiple walls and any of them covers the co-edge
                for i in range(len(sorted_list)):
                    if sorted_list[i][0] <= v[4][0] + w1 and sorted_list[i][1] >= v[5][0] - w1:
                        x.append(1)
                # If there are multiple walls, they are connected to cover the co-edge
                # (partition walls perpendicular to the co-edge is allowed.)
                for i in range(len(sorted_list) - 1):
                    if ((v[4][0] + w2 < sorted_list[i][1] < sorted_list[i + 1][0] < v[5][0] - w2 or
                         v[4][0] + w2 <= sorted_list[i][1] < sorted_list[i + 1][0] < v[5][0] - w2 or
                         v[4][0] + w2 < sorted_list[i][1] < sorted_list[i + 1][0] <= v[5][0] - w2) and
                            (sorted_list[0][0] <= v[4][0] + w1 and sorted_list[-1][1] >= v[5][0] - w1)):
                        if 0 < sorted_list[i + 1][0] - sorted_list[i][1] <= 2 * w2:
                            n.append(0)
                        else:
                            n.append(1)
            if x:
                accessibility.append([v[0], v[1], 0])
                continue

            if n != [] and 1 not in n:
                # If n is null it means that each of the multiple walls does not pass through the co-edge
                accessibility.append([v[0], v[1], 0])
                continue
            # the rest connectivity are all accessibility
            accessibility.append([v[0], v[1], 1])

        return list(filter(lambda a: a[2] == 1, accessibility))
