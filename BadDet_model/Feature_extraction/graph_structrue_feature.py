# read the graph
import graph_tool.all as gt
import moduleG

# processing structure indicators (serial computing)

'''
    need to set the number of nodes of k-hop subgraph
'''
import importlib
importlib.reload(moduleG)
from moduleG import *


def nhop(g, address, n, istxnode):
    if istxnode:
        source = moduleG.reverse_map["transaction_dict"][address]
    else:
        source = moduleG.reverse_map["account_dict"][address]
    dist = {source:0}
    mp = {source:0}
    num_nhop = 0
    def mp_add(x, num):
        if x not in mp:
            mp[x] = len(mp)
            num += 1
        return num
    edges = []
    gv = gt.GraphView(g, directed=False)
    for f,t in gt.bfs_iterator(gv,source):
        if f not in dist:
            break
        if dist[f] < n:
            if t not in dist:
                dist[t] = dist[f] + 1
                num_nhop = mp_add(t, num_nhop)
            if g.edge(f, t):
                edges.append((mp[f], mp[t]))
            if g.edge(t, f):
                edges.append((mp[t], mp[f]))
        if num_nhop > 3000: # set the number k of k-hop subgraph
            break
    ng = gt.Graph()
    ng.add_edge_list(edges)
    ng.vp["address"] = ng.new_vp("string")
    for i in mp.items():
        ng.vp["address"][i[1]] = g.vp["address"][i[0]]
    return ng


def structrue_feature(graph, node, istx_node):

    s_graph = nhop(graph, node, 4, istx_node)
    S1_1, S1_2, S1_3, S1_4, S1_5, S1_6 = module_221(s_graph)
    S3 = module_223(s_graph)
    S4 = module_224(s_graph)
    S5_1, S5_2 = module_225(s_graph)
    S6 = module_226(s_graph)
    S8 = module_232(s_graph)
    S9 = module_233(s_graph)

    return [S1_1, S1_2, S1_3, S1_4, S1_5, S1_6, S3, S4, S5_1, S5_2, S6, S8, S9]