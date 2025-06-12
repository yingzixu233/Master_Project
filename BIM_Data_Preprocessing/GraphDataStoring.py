from GraphStructureManager import GraphStructure
import IfcDataExtractor

def init_neo4j_connection():
    neo4j_scheme ="bolt"  # 默认bolt协议
    neo4j_host = "localhost"
    neo4j_port = "7687"
    neo4j_username = "neo4j"
    neo4j_password = "Xyz0531!!"
    neo4j_url = f"{neo4j_scheme}://{neo4j_host}:{neo4j_port}"
    return GraphStructure(neo4j_url, neo4j_username, neo4j_password)

def ifc_info_getting():
    ifc_info = IfcDataExtractor.DataExtractor('MA-Case Study.ifc',
                                              'module',
                                              'Tube module',
                                              'Corridor module',
                                              'Basic module',
                                              'Conjunctive module',
                                              'Fitted Bathroom',
                                              'none')
    return ifc_info


def graph_data_storing():
    # data preparation
    # extracted ifc data:
    ifc_info = ifc_info_getting()
    # view-related data:
    elevation_1 = ifc_info.getElevation('House Plan1')
    elevation_2 = ifc_info.getElevation('House Plan2')

    # 开始进行数据存储
    graph = init_neo4j_connection()
    print("✅ Neo4j 连接成功")

    # module-related data
    basic_ids = ifc_info.getBasicIds()
    conjunctive_ids = ifc_info.getConjuntiveIds()

    # Add all the modules/nodes and their properties to the Neo4j database
    for tube_module in ifc_info.getTubeModuleData():
        graph.add_tube_module(tube_module['IFC_GUID'])

    for corridor_module in ifc_info.getCorridorModuleData():
        graph.add_corridor_module(corridor_module['IFC_GUID'])

    for basic_module in ifc_info.getBasicModuleData():
        graph.add_basic_module(basic_module['IFC_GUID'],
                               ifc_info.getComponentsOfModule(basic_module,
                                                              elevation_1,
                                                              200))
    for conjunctive_module in ifc_info.getConjunctiveModuleData():
        graph.add_conjunctive_module(conjunctive_module['IFC_GUID'],
                                     ifc_info.getComponentsOfModule(conjunctive_module, elevation_1, 200))

    # Add all the connectivity edges to the Neo4j database: "CONNECTS"
    for i in range(len(ifc_info.getTubeModuleConnectivity())):
        if ifc_info.getTubeModuleConnectivity()[i][2] == 1:
            graph.add_tube_connectivity(ifc_info.getTubeModuleConnectivity()[i][0],
                                        ifc_info.getTubeModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getTubeBasicModuleConnectivity())):
        if ifc_info.getTubeBasicModuleConnectivity()[i][2] == 1:
            graph.add_tube_basic_connectivity(ifc_info.getTubeBasicModuleConnectivity()[i][0],
                                                            ifc_info.getTubeBasicModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getTubeConjunctModuleConnectivity())):
        if ifc_info.getTubeConjunctModuleConnectivity()[i][2] == 1:
            graph.add_tube_conjunct_connectivity(ifc_info.getTubeConjunctModuleConnectivity()[i][0],
                                                               ifc_info.getTubeConjunctModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getTubeCorridorModuleConnectivity())):
        if ifc_info.getTubeCorridorModuleConnectivity()[i][2] == 1:
            graph.add_tube_corridor_connectivity(ifc_info.getTubeCorridorModuleConnectivity()[i][0],
                                                 ifc_info.getTubeCorridorModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getCorridorModuleConnectivity())):
        if ifc_info.getCorridorModuleConnectivity()[i][2] == 1:
            graph.add_corridor_connectivity(ifc_info.getCorridorModuleConnectivity()[i][0],
                                            ifc_info.getCorridorModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getCorridorBasicModuleConnectivity())):
        if ifc_info.getCorridorBasicModuleConnectivity()[i][2] == 1:
            graph.add_corridor_basic_connectivity(ifc_info.getCorridorBasicModuleConnectivity()[i][0],
                                                                ifc_info.getCorridorBasicModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getCorridorConjunctModuleConnectivity())):
        if ifc_info.getCorridorConjunctModuleConnectivity()[i][2] == 1:
            graph.add_corridor_conjunct_connectivity(ifc_info.getCorridorConjunctModuleConnectivity()[i][0],
                                                                   ifc_info.getCorridorConjunctModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getBasicModuleConnectivity())):
        if ifc_info.getBasicModuleConnectivity()[i][2] == 1:
            graph.add_basic_connectivity(ifc_info.getBasicModuleConnectivity()[i][0],
                                         ifc_info.getBasicModuleConnectivity()[i][1],
                                         ifc_info.getBasicModuleConnectivity()[i][6],
                                         ifc_info.getBasicModuleConnectivity()[i][3])

    for i in range(len(ifc_info.getBasicConjunctModuleConnectivity())):
        if ifc_info.getBasicConjunctModuleConnectivity()[i][2] == 1:
            graph.add_basic_conjunct_connectivity(ifc_info.getBasicConjunctModuleConnectivity()[i][0],
                                                  ifc_info.getBasicConjunctModuleConnectivity()[i][1],
                                                  ifc_info.getBasicConjunctModuleConnectivity()[i][6],
                                                  ifc_info.getBasicConjunctModuleConnectivity()[i][3])

    for i in range(len(ifc_info.getConjunctModuleConnectivity())):
        if ifc_info.getConjunctModuleConnectivity()[i][2] == 1:
            graph.add_conjunct_connectivity(ifc_info.getConjunctModuleConnectivity()[i][0],
                                            ifc_info.getConjunctModuleConnectivity()[i][1],
                                            ifc_info.getConjunctModuleConnectivity()[i][6],
                                            ifc_info.getConjunctModuleConnectivity()[i][3])

    # Add all the accessibility for the source floor："ACCESSES_1"
    for i in range(len(ifc_info.getTubeModuleConnectivity())):
        if ifc_info.getTubeModuleConnectivity()[i][2] == 1:
            graph.add_tube_accessibility_1(ifc_info.getTubeModuleConnectivity()[i][0],
                                                         ifc_info.getTubeModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getTubeCorridorModuleAccessibility(elevation_1))):
        graph.add_tube_corridor_accessibility_1(ifc_info.getTubeCorridorModuleAccessibility(elevation_1)[i][0],
                                                ifc_info.getTubeCorridorModuleAccessibility(elevation_1)[i][1])

    for i in range(len(ifc_info.getCorridorModuleConnectivity())):
        if ifc_info.getCorridorModuleConnectivity()[i][2] == 1:
            graph.add_corridor_accessibility_1(ifc_info.getCorridorModuleConnectivity()[i][0],
                                                             ifc_info.getCorridorModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getCorridorHouseAccessibility(elevation_1))):
        if ifc_info.getCorridorHouseAccessibility(elevation_1)[i][1] in basic_ids:
            graph.add_corridor_basic_accessibility_1(ifc_info.getCorridorHouseAccessibility(elevation_1)[i][0],
                                                     ifc_info.getCorridorHouseAccessibility(elevation_1)[i][1],
                                                     ifc_info.getCorridorHouseAccessibility(elevation_1)[i][3])
        elif ifc_info.getCorridorHouseAccessibility(elevation_1)[i][1] in conjunctive_ids:
            graph.add_corridor_conjunct_accessibility_1(ifc_info.getCorridorHouseAccessibility(elevation_1)[i][0],
                                                        ifc_info.getCorridorHouseAccessibility(elevation_1)[i][1],
                                                        ifc_info.getCorridorHouseAccessibility(elevation_1)[i][3])

    for i in range(len(ifc_info.getHouseAccessibility(elevation_1,200, 200))):
        if ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][0] in conjunctive_ids:
            connectivity = list(filter(lambda cc: cc[0] == ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][0] and
                                                  cc[1] == ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][1],
                                       ifc_info.getConjunctModuleConnectivity()))[0]

            graph.add_conjunct_accessibility_1(ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][0],
                                               ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][1],
                                               ifc_info.getWallsOfCoEdge(connectivity, elevation_1, 200))

        elif (ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][0] in basic_ids and
              ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][1] in conjunctive_ids):
            connectivity = list(filter(lambda cc: cc[0] == ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][0] and
                                                  cc[1] == ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][1],
                                       ifc_info.getBasicConjunctModuleConnectivity()))[0]

            graph.add_basic_conjunct_accessibility_1(ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][0],
                                                     ifc_info.getHouseAccessibility(elevation_1,200, 200)[i][1],
                                                     ifc_info.getWallsOfCoEdge(connectivity,elevation_1,200))

    # Add all the accessibility for the objective floor："ACCESSES_2"
    for i in range(len(ifc_info.getTubeModuleConnectivity())):
        if ifc_info.getTubeModuleConnectivity()[i][2] == 1:
            graph.add_tube_accessibility_2(ifc_info.getTubeModuleConnectivity()[i][0],
                                           ifc_info.getTubeModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getTubeCorridorModuleAccessibility(elevation_2))):
        graph.add_tube_corridor_accessibility_2(ifc_info.getTubeCorridorModuleAccessibility(elevation_2)[i][0],
                                                ifc_info.getTubeCorridorModuleAccessibility(elevation_2)[i][1])

    for i in range(len(ifc_info.getCorridorModuleConnectivity())):
        if ifc_info.getCorridorModuleConnectivity()[i][2] == 1:
            graph.add_corridor_accessibility_2(ifc_info.getCorridorModuleConnectivity()[i][0],
                                               ifc_info.getCorridorModuleConnectivity()[i][1])

    for i in range(len(ifc_info.getCorridorHouseAccessibility(elevation_2))):
        if ifc_info.getCorridorHouseAccessibility(elevation_2)[i][1] in basic_ids:
            graph.add_corridor_basic_accessibility_2(ifc_info.getCorridorHouseAccessibility(elevation_2)[i][0],
                                                     ifc_info.getCorridorHouseAccessibility(elevation_2)[i][1],
                                                     ifc_info.getCorridorHouseAccessibility(elevation_2)[i][3])

        elif ifc_info.getCorridorHouseAccessibility(elevation_2)[i][1] in conjunctive_ids:
            graph.add_corridor_conjunct_accessibility_2(ifc_info.getCorridorHouseAccessibility(elevation_2)[i][0],
                                                        ifc_info.getCorridorHouseAccessibility(elevation_2)[i][1],
                                                        ifc_info.getCorridorHouseAccessibility(elevation_2)[i][3])

    for i in range(len(ifc_info.getHouseAccessibility(elevation_2,200,200))):
        if ifc_info.getHouseAccessibility(elevation_2,200,200)[i][0] in conjunctive_ids:
            graph.add_conjunct_accessibility_2(ifc_info.getHouseAccessibility(elevation_2,200,200)[i][0],
                                               ifc_info.getHouseAccessibility(elevation_2,200,200)[i][1])
        elif (ifc_info.getHouseAccessibility(elevation_2,200,200)[i][0] in basic_ids and
              ifc_info.getHouseAccessibility(elevation_2,200,200)[i][1] in conjunctive_ids):
            graph.add_basic_conjunct_accessibility_2(ifc_info.getHouseAccessibility(elevation_2,200,200)[i][0],
                                                     ifc_info.getHouseAccessibility(elevation_2,200,200)[i][1])

    # 关闭连接（确保资源释放）
    graph.close()


