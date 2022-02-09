from random import random
import sys
import re



class graph:
    def __init__(self, data):
        self.graph = {data:[]}
    
    def insertEdge(self, start, end, distance):
        self.graph[end].append(start, distance)


class packetDetails:
    def __init__(self):
        self.mark = ""
        self.start = ""
        self.distance = None
        self.end = ""

    def __str__(self):
        return f"Mark: {self.mark}\nStart: {self.start}\nDistance: {self.distance}\nEnd: {self.end}"


def RIP(source, destination, graph, path = []):
        path = path + [source]
        if source == destination:  # returns the source node if source and destination nodes are the same
            return path
        shortest = None
        for node in graph[source]:
            if node not in path:
                newpath = RIP(node, destination,  graph, path)  # Recursively calls RIP to create every possible path in the network
                if newpath:
                    if not shortest or len(newpath) < len(shortest):  # Checks to see if the latest path is shorter than the previously shortest path
                        shortest = newpath  
        return shortest

def getGraph(branches):
    graph = {}
    with open (f"Graph{branches}.txt", "r") as graphFile:  # Opens CustomGraph.txt file
        currentNode = ""
        fileInput = graphFile.readlines()  # Reads every line of the file
        for line in fileInput:
            line = line.strip('\n')  # Removes any newline characters
            line = line.split(",")  # Converts the line into a list with each node as an entry
            currentNode = line[0]
            graph[currentNode] = {}
            for node in line:
                if node == currentNode:  # Skips the root node
                    continue
                node = re.split(r'\((?P<cost>\d+)\)', node)  # Seperates the node from the link cost value
                if len(node) == 3:
                    del node[2]  # Removes extra comma if one exists
                if len(node) == 2:
                    graph[currentNode][node[0]] = int(node[1])  # Adds a new dictionary to the graph dictionary with node as a key and the cost as the value
                else:
                    graph[currentNode][node[0]] = 1  # If no cost value exists then it defaults to 1
    return graph

def sendPacket(topology, source = "A1", destination = "V1"):
    path = RIP(source, destination, topology)
    return path

def nodeSample(packet, probability):
    
    node = packetDetails()
    for hop in packet:
        if "R" not in hop:
            continue 

        if random() < probability:
            node.mark = hop 
    
    return node

def nodeSampleReconstruction(marked_packets):
    count_of_marks = {}
    constructed_path = []
    for packet in marked_packets:
        if packet.mark == "":
            continue
        elif packet.mark not in count_of_marks:
            count_of_marks[packet.mark] = 1
        else:
            count_of_marks[packet.mark] += 1

    constructed_path = {k: v for k, v in sorted(count_of_marks.items(), key=lambda item: item[1])}


    return list(constructed_path)


def edgeSample(packet, probability):
    node = packetDetails()
    for hop in packet:
        if "R" not in hop:
            continue

        if random() < probability:
            node.start = hop
            node.distance = 0
        else:
            if not node.distance:
                continue 
            elif node.distance == 0:
                node.end = hop 
            node.distance += 1
    print(node)
    return node


def edgeSampleReconstruction(marked_packets):
    count_of_marks = {}
    constructed_path = []
    reconstruction_tree = tree("V1")
    for packet in marked_packets:
        if packet.distance == 0:
            insertEdge(packet.start,"v",0)

    return constructed_path

def main():
    p = [0.2, 0.4, 0.5, 0.6, 0.8]
    x = [10, 100, 1000]
    algorithm = int(input("Select the algorithm you would like to test:\n1. Node Sampling\n2. Edge Sampling\n"))
    branches = input("Input the number of branches you would like to test with: 3, 4, or 5: ")
    no_attackers = int(input("Input the number of attackers from 1 - 2: "))
    x_value = int(input("Input the multiplier for the attackers packet sending: "))
    prob = float(input("Input the probability of marking: "))
    no_packets = int(input("How many packets shall the attacker(s) send: "))

    topology = getGraph(branches)  # Gets the graph from the input file.
    marked_packets = []

    attacker_packets_sent = 0
    while attacker_packets_sent < no_packets:
        if algorithm == 1:
            for i in range(0, x_value):
                marked_packets.append(nodeSample(sendPacket(topology),prob)) # Attacker Packets
                attacker_packets_sent += 1
            marked_packets.append(nodeSample(sendPacket(topology, source = "", destination = ""),prob)) # Normal User packet
            print(f"Node Sample Reconstructed Path with multiplier:= {x_value}, marking probability:= {prob}")
            print(nodeSampleReconstruction(marked_packets))

        
        elif algorithm == 2:
            marked_packets = []
            for i in range(0, x_value):
                marked_packets.append(edgeSample(sendPacket(topology),prob)) # Attacker Packets
                attacker_packets_sent += 1
            print(marked_packets)
            marked_packets.append(edgeSample(sendPacket(topology, source = "", destination = ""),prob)) # Normal User packet
            print(f"Edge Sample Reconstructed Path with multiplier:= {x[i]}, marking probability:= {prob}")
            print(edgeSampleReconstruction(marked_packets))
        else: 
            print("Inavlid algorithm selection")
            break

if __name__ == '__main__':
    main()

        
    