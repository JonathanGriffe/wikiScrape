import psycopg2

conn = psycopg2.connect(host="localhost", database="wikiuser", user="wikiuser", password="myPGPW")
cur = conn.cursor()


cur.execute("SELECT p1.topic as parent, p2.topic as child FROM Links JOIN Pages AS p1 ON parent_id=p1.id AND p1.distance < 3 JOIN Pages AS p2 ON child_id=p2.id AND p2.distance < 3 LIMIT 500")
l = cur.fetchall()

from matplotlib import pylab
import networkx as nx
import matplotlib.pyplot as plt

def save_graph(graph,file_name):
    #initialze Figure
    plt.figure(num=None, figsize=(100, 100), dpi=320)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph,pos)
    nx.draw_networkx_edges(graph,pos)
    nx.draw_networkx_labels(graph,pos)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)
    plt.savefig(file_name,bbox_inches="tight")
    plt.show()
    pylab.close()
    del fig

g = nx.Graph()

for row in l:
    g.add_edge(row[0], row[1])
#Assuming that the graph g has nodes and edges entered
save_graph(g,"my_graph.svg")

#it can also be saved in .svg, .png. or .ps formats
