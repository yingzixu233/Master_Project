import numpy as np
import GraphDataStoring

graph = GraphDataStoring.init_neo4j_connection()
ifc_info = GraphDataStoring.ifc_info_getting()
source_floor = 'House Plan1'
objective_floor = 'House Plan2'

graph.driver.verify_connectivity()

# STEP1.1: 获取原方案与走廊连接的户型内的模块
query_1 = ("MATCH (x:Corridor_Module)-[r:ACCESSES_1]-(y)"
           "WHERE y:Basic_Module|Conjunctive_Module "
           "RETURN y.global_id, r.door_family_type")
records_1, summary_1, keys_1 = graph.driver.execute_query(query_1, routing_="r", database_="neo4j")

start_modules_1 = []
for record in records_1:
    start_modules_1.append([record['y.global_id'], record['r.door_family_type']])

# STEP1.2: 获取新方案与走廊连接的户型内的模块
query_2 = ("MATCH (x:Corridor_Module)-[r:ACCESSES_2]-(y)"
           "WHERE y:Basic_Module|Conjunctive_Module "
           "RETURN y.global_id, r.door_family_type ")
records_2, summary_2, keys_2 = graph.driver.execute_query(query_2, routing_="r", database_="neo4j")

start_modules_2 = []
for record in records_2:
    start_modules_2.append([record['y.global_id'], record['r.door_family_type']])

# STEP2.1.1: 根据与走廊连接的户型内的模块获取原方案所有户型内所有模块及模块内的建筑构件（如果有的话）
houses_1 = []
for start_module in start_modules_1:
    query_3 = ("MATCH p = (x {global_id:$global_id})-[r:ACCESSES_1*0..]-(y) "
               "WHERE y:Basic_Module|Conjunctive_Module and NOT 'corridor_module' IN [a IN nodes(p)|a.type_name] "
               "RETURN [a IN nodes(p)|a.global_id] AS global_id, "
               "[a IN nodes(p)|a.components] AS components_a, "
               "[b IN relationships(p)|b.components] AS components_b")

    records_3, summary_3, keys_3 = graph.driver.execute_query(query_3,
                                                                            global_id=start_module[0],
                                                                            routing_="r",
                                                                            database_="neo4j")
    global_ids = []
    components_all = []
    components_unit = []
    for record in records_3:
        global_ids += record["global_id"]
        for component in record["components_a"]:
            components_all += component
        for component in record["components_b"]:
            components_all += component
    components_all = np.unique(components_all)

    for x in components_all:
        components_unit.append(x)

    basic_module = list(filter(lambda module: module in ifc_info.getBasicIds(), np.unique(global_ids)))[0]
    dictionary = {'house_modules': np.unique(global_ids),
                  'basic_module': basic_module,
                  'house_components': components_unit,
                  'house_door': start_module[1]}
    houses_1.append(dictionary)

# STEP 2.1.2: 将有构件的户型和没有构件的户型分开
houses_1_source = []
houses_1_objective = []

for h in houses_1:
    if len(h['house_components']) == 0:
        dictionary_1 = {'house_modules': h['house_modules'],
                        'basic_module': h['basic_module'],
                        'house_door': h['house_door'],
                        'floor_name': source_floor }
        houses_1_objective.append(dictionary_1)
    else:
        houses_1_source.append(h)

# STEP2.2: 根据与走廊连接的户型内的模块获取新方案所有户型内所有模块
houses_2_objective = []
for start_module in start_modules_2:
    query_4 = ("MATCH p = (x {global_id:$global_id})-[r:ACCESSES_2*0..]-(y) "
               "WHERE y:Basic_Module|Conjunctive_Module and NOT 'corridor_module' IN [a IN nodes(p)|a.type_name] "
               "RETURN [a IN nodes(p)|a.global_id] AS global_id ")

    records_4, summary_4, keys_4 = graph.driver.execute_query(query_4,
                                                                            global_id=start_module[0],
                                                                            routing_="r",
                                                                            database_="neo4j")
    a = []
    for record in records_4:
        a += record["global_id"]
    basic_module = list(filter(lambda module: module in ifc_info.getBasicIds(), np.unique(a)))[0]
    dictionary = {'house_modules': np.unique(a),
                  'basic_module': basic_module,
                  'house_door': start_module[1],
                  'floor_name': objective_floor}
    houses_2_objective.append(dictionary)

# STEP 3.1.1 增加源户型的基本模块的周边关系（包括连通模块的名称，角度，和相对位置）
for house in houses_1_source:
    surrounding = []
    query_5 = ("MATCH p = (x:Basic_Module {global_id:$global_id})-[r:ACCESSES_1]-(y:Conjunctive_Module) "
               "RETURN y.global_id")
    records_5, summary_5, keys_5 = graph.driver.execute_query(query_5,
                                                                            global_id=house['basic_module'],
                                                                            routing_="r",
                                                                            database_="neo4j")
    for r in records_5:
        query_6 = ("MATCH p = (x:Basic_Module {global_id:$global_id_1})-[r:CONNECTS]-(y {global_id:$global_id_2}) "
                   "RETURN r.angle, r.relative_position")
        records_6, summary_6, keys_6 = graph.driver.execute_query(query_6,
                                                                                global_id_1=house['basic_module'],
                                                                                global_id_2=r['y.global_id'],
                                                                                routing_="r",
                                                                                database_="neo4j")

        dictionary = {'accessed_module': r['y.global_id'],
                      'angle': records_6[0]['r.angle'],
                      'relative_position': records_6[0]['r.relative_position']}
        surrounding.append(dictionary)
    house['surrounding'] = surrounding

# STEP 3.1.2 增加同楼层目标户型的基本模块的周边关系（包括连通模块的名称，角度，和相对位置）
for house in houses_1_objective:
    surrounding = []
    query_5 = ("MATCH p = (x:Basic_Module {global_id:$global_id})-[r:ACCESSES_1]-(y:Conjunctive_Module) "
               "RETURN y.global_id")
    records_5, summary_5, keys_5 = graph.driver.execute_query(query_5,
                                                                            global_id=house['basic_module'],
                                                                            routing_="r",
                                                                            database_="neo4j")
    for r in records_5:
        query_6 = ("MATCH p = (x:Basic_Module {global_id:$global_id_1})-[r:CONNECTS]-(y {global_id:$global_id_2}) "
                   "RETURN r.angle, r.relative_position")
        records_6, summary_6, keys_6 = graph.driver.execute_query(query_6,
                                                                                global_id_1=house['basic_module'],
                                                                                global_id_2=r['y.global_id'],
                                                                                routing_="r",
                                                                                database_="neo4j")

        dictionary = {'accessed_Module': r['y.global_id'],
                      'angle': records_6[0]['r.angle'],
                      'relative_position': records_6[0]['r.relative_position']}
        surrounding.append(dictionary)
    house['surrounding'] = surrounding

# STEP 3.1.3 增加其他楼层目标户型的基本模块的周边关系（包括连通模块的名称，角度，和相对位置）
for house in houses_2_objective:
    surrounding = []
    query_5 = ("MATCH p = (x:Basic_Module {global_id:$global_id})-[r:ACCESSES_2]-(y:Conjunctive_Module) "
               "RETURN y.global_id")
    records_5, summary_5, keys_5 = graph.driver.execute_query(query_5,
                                                                            global_id=house['basic_module'],
                                                                            routing_="r",
                                                                            database_="neo4j")
    for r in records_5:
        query_6 = ("MATCH p = (x:Basic_Module {global_id:$global_id_1})-[r:CONNECTS]-(y {global_id:$global_id_2}) "
                   "RETURN r.angle, r.relative_position")
        records_6, summary_6, keys_6 = graph.driver.execute_query(query_6,
                                                                                global_id_1=house['basic_module'],
                                                                                global_id_2=r['y.global_id'],
                                                                                routing_="r",
                                                                                database_="neo4j")

        dictionary = {'accessed_Module': r['y.global_id'],
                      'angle': records_6[0]['r.angle'],
                      'relative_position': records_6[0]['r.relative_position']}
        surrounding.append(dictionary)
    house['surrounding'] = surrounding

house_objective = houses_1_objective + houses_2_objective