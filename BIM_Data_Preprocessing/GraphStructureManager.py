from neo4j import GraphDatabase

class GraphStructure:

    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    # Don't forget to close the driver connection when you are finished with it
    def close(self):
        self.driver.close()

    # all the nodes
    def add_tube_module(self, global_id, type_name='tube_module'):
        with self.driver.session() as session:
            session.execute_write(self.create_tube_node, global_id, type_name)

    @staticmethod
    # all the static methods are transaction functions
    def create_tube_node(tx, global_id, type_name):
        tx.run("CREATE (m:Tube_Module {global_id: $global_id, type_name: $type_name})",
               global_id=global_id, type_name=type_name)

    def add_corridor_module(self, global_id, type_name='corridor_module'):
        with self.driver.session() as session:
            session.execute_write(self.create_corridor_node, global_id, type_name)

    @staticmethod
    # all the static methods are transaction functions
    def create_corridor_node(tx, global_id, type_name):
        tx.run("CREATE (m:Corridor_Module {global_id: $global_id, type_name: $type_name})",
               global_id=global_id, type_name=type_name)

    def add_basic_module(self, global_id, components, type_name='basic_module'):
        with self.driver.session() as session:
            session.execute_write(self.create_basic_node, global_id, components, type_name)

    @staticmethod
    # all the static methods are transaction functions
    def create_basic_node(tx, global_id, components, type_name):
        tx.run("CREATE (m:Basic_Module "
               "{global_id: $global_id, components: $components, type_name: $type_name})",
               global_id=global_id, components=components, type_name=type_name)

    def add_conjunctive_module(self, global_id, components, type_name='conjunctive_module'):
        with self.driver.session() as session:
            session.execute_write(self.create_conjunctive_node, global_id, components, type_name)

    @staticmethod
    # all the static methods are transaction functions
    def create_conjunctive_node(tx, global_id, components, type_name):
        tx.run("CREATE (m:Conjunctive_Module "
               "{global_id: $global_id, components: $components, type_name: $type_name})",
               global_id=global_id, components=components, type_name=type_name)

# all the connectivity: "CONNECTS"
    def add_tube_connectivity(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.tube_relationship, global_id_a, global_id_b)

    @staticmethod
    def tube_relationship(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Tube_Module {global_id: $global_id_a})"
               "MATCH (b:Tube_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    # add relationship between tube and corridor modules
    def add_tube_corridor_connectivity(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.tube_corridor_relationship, global_id_a, global_id_b)

    @staticmethod
    def tube_corridor_relationship(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Tube_Module {global_id: $global_id_a})"
               "MATCH (b:Corridor_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_tube_basic_connectivity(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.tube_basic_relationship, global_id_a, global_id_b)

    @staticmethod
    def tube_basic_relationship(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Tube_Module {global_id: $global_id_a})"
               "MATCH (b:Basic_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_tube_conjunct_connectivity(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.tube_conjunct_relationship, global_id_a, global_id_b)

    @staticmethod
    def tube_conjunct_relationship(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Tube_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_corridor_connectivity(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.corridor_relationship, global_id_a, global_id_b)

    @staticmethod
    def corridor_relationship(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Corridor_Module {global_id: $global_id_a})"
               "MATCH (b:Corridor_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_corridor_basic_connectivity(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.corridor_basic_relationship, global_id_a, global_id_b)

    @staticmethod
    def corridor_basic_relationship(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Corridor_Module {global_id: $global_id_a})"
               "MATCH (b:Basic_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_corridor_conjunct_connectivity(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.corridor_conjunct_relationship, global_id_a, global_id_b)

    @staticmethod
    def corridor_conjunct_relationship(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Corridor_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_basic_connectivity(self, global_id_a, global_id_b, angle, relative_position):
        with self.driver.session() as session:
            session.execute_write(self.basic_relationship, global_id_a, global_id_b, angle, relative_position)

    @staticmethod
    def basic_relationship(tx, global_id_a, global_id_b, angle, relative_position):
        tx.run("MATCH (a:Basic_Module {global_id: $global_id_a})"
               "MATCH (b:Basic_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS {angle: $angle, relative_position: $relative_position}]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b, angle=angle, relative_position=relative_position)

    def add_basic_conjunct_connectivity(self, global_id_a, global_id_b, angle, relative_position):
        with self.driver.session() as session:
            session.execute_write(self.basic_conjunct_relationship, global_id_a, global_id_b, angle, relative_position)

    @staticmethod
    def basic_conjunct_relationship(tx, global_id_a, global_id_b, angle, relative_position):
        tx.run("MATCH (a:Basic_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS {angle: $angle, relative_position: $relative_position}]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b, angle=angle, relative_position=relative_position)

    def add_conjunct_connectivity(self, global_id_a, global_id_b, angle, relative_position):
        with self.driver.session() as session:
            session.execute_write(self.conjunct_relationship, global_id_a, global_id_b, angle, relative_position)

    @staticmethod
    def conjunct_relationship(tx, global_id_a, global_id_b, angle, relative_position):
        tx.run("MATCH (a:Conjunctive_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:CONNECTS {angle: $angle, relative_position: $relative_position}]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b, angle=angle, relative_position=relative_position)

# all the accessibility for the source floor: "ACCESSES_1"
    def add_tube_accessibility_1(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.tube_accessibility_1, global_id_a, global_id_b)

    @staticmethod
    def tube_accessibility_1(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Tube_Module {global_id: $global_id_a})"
               "MATCH (b:Tube_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_1]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_tube_corridor_accessibility_1(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.tube_corridor_accessibility_1, global_id_a, global_id_b)

    @staticmethod
    def tube_corridor_accessibility_1(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Tube_Module {global_id: $global_id_a})"
               "MATCH (b:Corridor_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_1]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_corridor_accessibility_1(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.corridor_accessibility_1, global_id_a, global_id_b)

    @staticmethod
    def corridor_accessibility_1(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Corridor_Module {global_id: $global_id_a})"
               "MATCH (b:Corridor_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_1]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_corridor_basic_accessibility_1(self, global_id_a, global_id_b, door_family_type):
        with self.driver.session() as session:
            session.execute_write(self.corridor_basic_accessibility_1, global_id_a, global_id_b, door_family_type)

    @staticmethod
    def corridor_basic_accessibility_1(tx, global_id_a, global_id_b, door_family_type):
        tx.run("MATCH (a:Corridor_Module {global_id: $global_id_a})"
               "MATCH (b:Basic_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_1 {door_family_type: $door_family_type}]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b, door_family_type=door_family_type)

    def add_corridor_conjunct_accessibility_1(self, global_id_a, global_id_b, door_family_type):
        with self.driver.session() as session:
            session.execute_write(self.corridor_conjunct_accessibility_1, global_id_a, global_id_b, door_family_type)

    @staticmethod
    def corridor_conjunct_accessibility_1(tx, global_id_a, global_id_b, door_family_type):
        tx.run("MATCH (a:Corridor_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_1 {door_family_type: $door_family_type}]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b, door_family_type=door_family_type)

    def add_basic_conjunct_accessibility_1(self, global_id_a, global_id_b, components):
        with self.driver.session() as session:
            session.execute_write(self.basic_conjunct_accessibility_1, global_id_a, global_id_b, components)

    @staticmethod
    def basic_conjunct_accessibility_1(tx, global_id_a, global_id_b, components):
        tx.run("MATCH (a:Basic_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_1 {components: $components}]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b, components=components)

    def add_conjunct_accessibility_1(self, global_id_a, global_id_b, components):
        with self.driver.session() as session:
            session.execute_write(self.conjunct_accessibility_1, global_id_a, global_id_b, components)

    @staticmethod
    def conjunct_accessibility_1(tx, global_id_a, global_id_b, components):
        tx.run("MATCH (a:Conjunctive_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_1 {components: $components}]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b, components=components)

# all the accessibility for the objective floor: "ACCESSES_2"
    def add_tube_accessibility_2(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.tube_accessibility_2, global_id_a, global_id_b)

    @staticmethod
    def tube_accessibility_2(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Tube_Module {global_id: $global_id_a})"
               "MATCH (b:Tube_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_2]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_tube_corridor_accessibility_2(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.tube_corridor_accessibility_2, global_id_a, global_id_b)

    @staticmethod
    def tube_corridor_accessibility_2(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Tube_Module {global_id: $global_id_a})"
               "MATCH (b:Corridor_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_2]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_corridor_accessibility_2(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.corridor_accessibility_2, global_id_a, global_id_b)

    @staticmethod
    def corridor_accessibility_2(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Corridor_Module {global_id: $global_id_a})"
               "MATCH (b:Corridor_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_2]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_corridor_basic_accessibility_2(self, global_id_a, global_id_b, door_family_type):
        with self.driver.session() as session:
            session.execute_write(self.corridor_basic_accessibility_2, global_id_a, global_id_b, door_family_type)

    @staticmethod
    def corridor_basic_accessibility_2(tx, global_id_a, global_id_b, door_family_type):
        tx.run("MATCH (a:Corridor_Module {global_id: $global_id_a})"
               "MATCH (b:Basic_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_2 {door_family_type: $door_family_type}]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b, door_family_type=door_family_type)

    def add_corridor_conjunct_accessibility_2(self, global_id_a, global_id_b, door_family_type):
        with self.driver.session() as session:
            session.execute_write(self.corridor_conjunct_accessibility_2,
                                  global_id_a,
                                  global_id_b,
                                  door_family_type)

    @staticmethod
    def corridor_conjunct_accessibility_2(tx, global_id_a, global_id_b, door_family_type):
        tx.run("MATCH (a:Corridor_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_2 {door_family_type: $door_family_type}]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b, door_family_type=door_family_type)

    def add_basic_conjunct_accessibility_2(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.basic_conjunct_accessibility_2, global_id_a, global_id_b)

    @staticmethod
    def basic_conjunct_accessibility_2(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Basic_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_2]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)

    def add_conjunct_accessibility_2(self, global_id_a, global_id_b):
        with self.driver.session() as session:
            session.execute_write(self.conjunct_accessibility_2, global_id_a, global_id_b)

    @staticmethod
    def conjunct_accessibility_2(tx, global_id_a, global_id_b):
        tx.run("MATCH (a:Conjunctive_Module {global_id: $global_id_a})"
               "MATCH (b:Conjunctive_Module {global_id: $global_id_b})"
               "MERGE (a)-[:ACCESSES_2]-(b)",
               global_id_a=global_id_a, global_id_b=global_id_b)
