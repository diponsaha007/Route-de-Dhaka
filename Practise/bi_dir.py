# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 22:09:18 2019

@author: User
"""
import heapq
import math
import networkx as nx
import osmnx as ox
import requests
import matplotlib.cm as cm
import matplotlib.colors as colors
ox.config(use_cache=True, log_console=True)
class Edge:
    def __init__(self, source, dest, length, bidirectional=False):
        self.source = source
        self.dest = dest
        self.length = length
        self.bidirectional = bidirectional


class Graph:

    def __init__(self, nodes, edges, lat_lng_list, street_name_list):
        """
        constructor takes in nodes as list of integars
        and edges as lists of Edge class objects
        and also creates an empty dictionary
        """
        self.nodes = nodes
        self.edges = edges
        self.connections = {}  # for RL
        self.connected_weights = {}  # for RL
        self.adj = {}
        self.inDegree = {}
        self.outDegree = {}
        self.positions = {}
        self.adj_weights = {}
        self.lat_lng ={}
        self.street_names = {}
        for i in nodes:
            self.inDegree[i] = 0
            self.outDegree[i] = 0
            self.adj[i] = []

        for i in edges:
            self.add_edge(i.source, i.dest, i.length, i.bidirectional)
            
#        for i in lat_lng_list:
#            self.lat_lng[i[0]] = (i[1],i[2])
        
        self.lat_lng = lat_lng_list
        for i in street_name_list:
            self.street_names[ (i[0], i[1]) ] = i[2]

    ########################## ADDED BY APURBA ###########################
    def get_vertices(self):
        """ returns the vertices of a graph """
        return list(self.adj.keys())

    def get_edges(self):
        """
        :return: the list of tuples that shows all the edges with weights
        """
        nodes = self.get_vertices()
        ret = []
        for i in nodes:
            for j in self.adj[i]:
                ret.append((i, j[0], j[1]))

        return ret

    def add_edge(self, u, v, w, bidirectional=False):
        """
        :param u: source node
        :param v: destination node
        :param w: weight
        :param bidirectional: If true this will also create an edge from v to u with weight w
        :return: creates an edge from u to v with weight w
        """
        self.adj[u].append((v, w))
        self.adj_weights[(u, v)] = w
        if bidirectional is True:
            self.adj[v].append((u, w))
            self.adj_weights[(v, u)] = w

        self.inDegree[v] += 1
        self.outDegree[u] += 1
        if bidirectional is True:
            self.inDegree[u] += 1
            self.outDegree[v] += 1

    def dijkstra(self, source):
        """
        :param source: takes the source from where dijkstra to be run
        :return: the dictionary of distance from source to all other nodes
                and also the path in a list
        """
        dist = {}
        visited = {}
        parent = {}
        priority_queue = []
        # initializing dist to inf and visited to false and parent to -1
        for i in self.nodes:
            dist[i] = float("inf")
            visited[i] = False
            parent[i] = -1

        dist[source] = 0
        heapq.heappush(priority_queue, (0, source))
        while len(priority_queue) != 0:
            a = priority_queue[0][1]
            heapq.heappop(priority_queue)
            if visited[a] is True:
                continue
            visited[a] = True
            for j in self.adj[a]:
                b = j[0]
                w = j[1]
                if dist[a] + w < dist[b]:  ### this is the main comparison
                    parent[b] = a  # To track the path
                    dist[b] = dist[a] + w
                    heapq.heappush(priority_queue, (dist[b], b))

        return dist, parent

    def get_path(self, parent, cur, path=None):
        """
        Get the path from source to destination grabbed from the parent dictionary of dijkstra
        :param parent: the parent array
        :param cur: current node
        :param path: the returned path list
        :return: a list of the nodes from source to destination
        """
        if path is None:
            path = []
        if parent[cur] == - 1:
            path.append(cur)
            return path
        self.get_path(parent, parent[cur], path)
        path.append(cur)
        return path
    
    def deg2rad(self,deg):
        return deg * (math.pi / 180)


    def getDistanceFromLatLon(self,lat1, lon1, lat2, lon2):
        R = 6371
        dLat = self.deg2rad(lat2 - lat1)
        dLon = self.deg2rad(lon2 - lon1)
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(self.deg2rad(lat1)) * math.cos(self.deg2rad(lat2)) * math.sin(
            dLon / 2) * math.sin(dLon / 2)
    
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return d

    def astar(self, start, end):
        """
        :param start: the start node
        :param end: the end node
        :return: the path from the start to end node
        """

        # first one is f,second one is g , third one is h, fourth one is node number
        start_node = (0, 0, 0, start)
        #end_lat_lng = self.lat_lng[end]
        parent = {}
        open_list = []  # this is the heap to maintain least f
        closed_list = {}
        
        g_list = {}
        f_list = {}
        h_list = {}
        parent[start] = -1
        f_list[start] = 0
        h_list[start] = 0
        g_list[start] = 0
        heapq.heappush(open_list, start_node)

        while len(open_list) != 0:
            current_node = open_list[0]
            current_node_number = current_node[3]
            heapq.heappop(open_list)
            closed_list[current_node_number] = True

            # found the node
            if current_node_number == end:
                print("Path found")
                
                print(g_list[end])
                path = []
                current = current_node[3]
                while current != -1:
                    path.append(current)
                    current = parent[current]
                return path[::-1]  # Return reversed path
            else:
                # Generate children
                children = []
                for i in self.adj[current_node[3]]:  # Adjacent squares

                    # Create new node
                    new_node = (0, 0, 0, i[0])

                    # Append
                    children.append(new_node)

                # Loop through children
                for child in children:
                    child_node_number = child[3]
                    if child_node_number in closed_list.keys():
                        continue

                    # Create the f, g, and h values
                    lat_lngg = self.lat_lng[child_node_number]
                    g_value = current_node[1] + self.adj_weights[(current_node_number, child_node_number)]
                    #h_value = self.getDistanceFromLatLon(lat_lngg[0],lat_lngg[1],end_lat_lng[0],end_lat_lng[1])
                    h_value = 1
                    f_value = g_value + h_value
                    #print(f_value, " ", g_value, " ", child_node_number)
                    if  child_node_number not in f_list or f_list[child_node_number] > f_value:
                        insert_node = (f_value, g_value, h_value, child_node_number)
                        heapq.heappush(open_list, insert_node)
                        parent[child_node_number] = current_node_number
                        f_list[child_node_number] = f_value
                        g_list[child_node_number] = g_value
                        h_list[child_node_number] = h_value

        print("Path not found")
        return None
    
    def get_direction(self,start_lat, start_lng, end_lat, end_lng):
        x1 = end_lat
        y1 = end_lng
        x2 = start_lat
        y2 = start_lng
    
        rad = math.atan2((y1 - y2), (x1 - x2))
        deg = rad * (180/math.pi)
        coordNames = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West", "North"]
        idx = round(deg/45.00)
        if idx<0:
            idx += 8
        return coordNames[idx]
    
    def print_path_info(self,path):
        sz = len(path)
        last = None
        last_dir = None
        for i in range(sz):
            if i==sz-1 :
                print('You have reached your destination')
            else:
                u= path[i]
                v= path[i+1]
                name = self.street_names[(u,v)]
                dir = self.get_direction(self.lat_lng[u][0],self.lat_lng[u][1],self.lat_lng[v][0],self.lat_lng[v][1] )
                
                if last is None or last != name: 
                    print('You are currently in ', name)
                    last = name
                    print('Go to ',dir,' direction following street ', name)
                    last_dir = dir
                
                elif last_dir is None or  last_dir !=dir:
                    print('Now go to ',dir,' direction following street ', name)
                    last_dir = dir
                    
    def print_path_info2(self,path):
        sz = len(path)
        str =[]
        str.append("Source:  ("+str(self.lat_lng[path[0]][0])+ ", "+str(self.lat_lng[path[0]][1])+")")
        str.append("Destination:  ("+str(self.lat_lng[path[sz-1]][0])+ ", "+str(self.lat_lng[path[sz-1]][1])+")")
        for i in range(sz-1):
            if i==0:
                str.append("Ride Car from Source ("+str(self.lat_lng[path[i]][0])+", "+str(self.lat_lng[path[i]][1])+") to ("+str(self.lat_lng[path[i+1]][0])+", "+str(self.lat_lng[path[i+1]][1])+")" )
            elif i== sz-2:
                str.append("Ride Car from ("+str(self.lat_lng[path[i]][0])+", "+str(self.lat_lng[path[i]][1])+") to Destination ("+str(self.lat_lng[path[i+1]][0])+", "+str(self.lat_lng[path[i+1]][1])+")" )
            else:
                str.append("Ride Car from  ("+str(self.lat_lng[path[i]][0])+", "+str(self.lat_lng[path[i]][1])+") to ("+str(self.lat_lng[path[i+1]][0])+", "+str(self.lat_lng[path[i+1]][1])+")" )
    
    def print_path_info_latlong(self,path):
        sz = len(path)
        text =[]
        text.append("Source:  ("+str(path[0][0])+ ", "+str(path[0][1])+")")
        text.append("Source:  ("+str(path[-1][0])+ ", "+str(path[-1][1])+")")
        for i in range(sz-1):
            if i==0:
                text.append("Ride Car from Source ("+str(path[i][0])+", "+str(path[i][1])+") to ("+str(path[i+1][0])+", "+str(path[i+1][1])+")" )
            elif i== sz-2:
                text.append("Ride Car from  ("+str(path[i][0])+", "+str(path[i][1])+") to Destination ("+str(path[i+1][0])+", "+str(path[i+1][1])+")" )
            else:
                text.append("Ride Car from  ("+str(path[i][0])+", "+str(path[i][1])+") to ("+str(path[i+1][0])+", "+str(path[i+1][1])+")" )
             
        return text


    def print_path_info_latlong(self,path):
        sz = len(path)
        text =[]
        text.append("Source:  ("+str(path[0][0])+ ", "+str(path[0][1])+")")
        text.append("Source:  ("+str(path[-1][0])+ ", "+str(path[-1][1])+")")
        for i in range(sz-1):
            if i==0:
                text.append("Ride Car from Source ("+str(path[i][0])+", "+str(path[i][1])+") to ("+str(path[i+1][0])+", "+str(path[i+1][1])+")" )
            elif i== sz-2:
                text.append("Ride Car from  ("+str(path[i][0])+", "+str(path[i][1])+") to Destination ("+str(path[i+1][0])+", "+str(path[i+1][1])+")" )
            else:
                text.append("Ride Car from  ("+str(path[i][0])+", "+str(path[i][1])+") to ("+str(path[i+1][0])+", "+str(path[i+1][1])+")" )
             
        return text
    ############################# RL PART ################################

    # helper function 
    def add_to_dict(self, key, value):
        if key in self.connections.keys():
            if value not in self.connections[key]:
                self.connections[key].append(value)
        else:
            self.connections[key] = [value]

    def get_connections_as_dictionary(self):
        for edge in self.edges:
            self.add_to_dict(edge.source, edge.dest)
            if edge.bidirectional:
                self.add_to_dict(edge.dest, edge.source)
        return self.connections

    # helper function
    def add_to_weights_dict(self, node1, node2, weight):
        if node1 in self.connected_weights.keys():
            if node2 in self.connected_weights[node1]:
                # always choose the least weight for two same nodes
                if self.connected_weights[node1][node2] > weight:
                    self.connected_weights[node1][node2] = weight
            else:
                self.connected_weights[node1][node2] = weight
        else:
            self.connected_weights[node1] = {node2: weight}

    def get_connections_weights_as_dictionary(self):
        for edge in self.edges:
            self.add_to_weights_dict(edge.source, edge.dest, edge.length)
            if edge.bidirectional:
                self.add_to_weights_dict(edge.dest, edge.source, edge.length)
        return self.connected_weights



    def bi_dijkstra(self, source,target):
        """
        :param source: takes the source from where dijkstra to be run
        :return: the dictionary of distance from source to all other nodes
                and also the path in a list
        """
        
        res = 1e10
        
        processed = set()
        
        distS = {}
        distT = {}
        
        #visitedS = {}
        #visitedT = {}
        
        parentS = {}
        parentT = {}
        
        priority_queueS = []
        priority_queueT = []
        # initializing dist to inf and visited to false and parent to -1
        for i in self.nodes:
            distS[i] = 1e9
            distT[i] = 1e9
            #visitedS[i] = False
            #visitedT[i] = False
            parentS[i] = -1
            parentT[i] = -1
    
        distS[source] = 0
        distT[target] = 0
        
        heapq.heappush(priority_queueS, (0, source))
        heapq.heappush(priority_queueT, (0, target))
        while True:
            if(len(priority_queueS)==0 or len(priority_queueT)==0):
                break
            a = priority_queueS[0][1]
            heapq.heappop(priority_queueS)
            for j in self.adj[a]:
                b = j[0]
                w = j[1]
                print(b)
                if distS[a] + w < distS[b]:  ### this is the main comparison
                    parentS[b] = a  # To track the path
                    distS[b] = distS[a] + w
                    heapq.heappush(priority_queueS, (distS[b], b))
                    
            if distS[a]+distT[a]<res:
                res = distS[a]+distT[a]
            
            if(a in processed):
                break
            else:
                processed.add(a)
                
            ra =priority_queueT[0][1]
            heapq.heappop(priority_queueT)
            for j in self.adj[ra]:
                rb = j[0]
                rw = j[1]
                print("->",rb)
                if distT[ra] + rw < distT[rb]:
                    parentT[ra] = rb
                    distT[rb] = distT[ra] + rw
                    heapq.heappush(priority_queueT,(distT[rb],rb))
            
            if distS[ra]+distT[ra]<res:
                res = distS[ra]+distT[ra]
                
            
            if(ra in processed):
                break
            else:
                processed.add(ra)
    
        print("BIDIJKSTRA : ",res)