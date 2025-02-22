import networkx as nx
import os
import json
from copy import deepcopy


class Graph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.edgeToIndex = []
        self.edgesNodes = {}
        self.vertices = []
        self.initG()

    def initG(self):
        f = open(f"{os.getcwd()}/src/SimulationConfig/Graph_Data.json")
        self.graphData = json.load(f)
        for vertex in self.graphData["vertices"]:
            self.vertices.append(
                {"name": vertex['name'], "nodes": vertex['nodes']})
        for node in self.graphData["nodes"]:
            self.G.add_node(node["name"], coordinates=node["coordinates"])
        for edge in self.graphData["edges"]:
            self.G.add_edge(edge["nodes"][0], edge["nodes"]
                            [1], name=edge["name"], weight=edge["weight"], nodes=edge["nodes"], priority=edge["priority"])

    def printEdges(self):
        for e in self.G.edges:
            print(
                f"""{self.G.get_edge_data(e[0], e[1])["name"]} -> from {e[0]}:({self.G.nodes.get(e[0])["coordinates"]["x"]},{self.G.nodes.get(e[0])["coordinates"]["y"]}) to {e[1]}:({self.G.nodes.get(e[1])["coordinates"]["x"]},{self.G.nodes.get(e[1])["coordinates"]["y"]})""")

    def getEdgesTuples(self):
        edgesTuples = []
        for e in self.G.edges:
            self.edgeToIndex.append(self.G.get_edge_data(e[0], e[1])["name"])
            self.edgesNodes[self.G.get_edge_data(e[0], e[1])["name"]] = [
                e[0], e[1]]
            edgesTuples.append(((self.G.nodes.get(e[0])["coordinates"]["x"], self.G.nodes.get(e[0])[
                               "coordinates"]["y"]), (self.G.nodes.get(e[1])["coordinates"]["x"], self.G.nodes.get(e[1])["coordinates"]["y"]), self.G.get_edge_data(e[0], e[1])["name"], self.G.get_edge_data(e[0], e[1])['weight'], self.G.get_edge_data(e[0], e[1])['priority'], [e[0], e[1]]))
        return edgesTuples

    def getPath(self, source, target):
        try:
            path = nx.dijkstra_path(self.G, source, target, "weight")
            return self.nodePathToIndexPath(path)
        except Exception as err:
            print(err)

    def reverseEdge(self, edgeName):
        for edge in self.graphData["edges"]:
            if(edge["name"] == edgeName):
                u = edge["nodes"][0]
                v = edge["nodes"][1]
                attrs = self.G.get_edge_data(u, v)
                self.G.remove_edge(u, v)
                self.G.add_edge(v, u, **attrs)

    def getEdgeIndex(self, edgeName):
        return self.edgeToIndex.index(edgeName)

    def nodePathToIndexPath(self, nodePath):
        pathIndex = []
        for index, node in enumerate(nodePath):
            if(index + 1 < len(nodePath)):
                name = self.G.get_edge_data(
                    nodePath[index], nodePath[index+1])["name"]
                pathIndex.append(self.getEdgeIndex(name))
        return pathIndex

    def indexPathToEdgesPath(self, indexPath):
        edgePath = []
        for index in indexPath:
            edgePath.append(self.edgeToIndex[index])
        return edgePath
