from utils import read
import graph_tool.all as gt
from tqdm import tqdm
import pickle
from moduleG import *
import moduleG
import imp
imp.reload(moduleG)
import os
from tqdm_pickle import load_file
# reverse_map = defaultdict(lambda: {})


# def formating_timestamp(timestamp: int) -> str:

#     """Function: Change the timestamp to readable format 
#     param:
#         -timestamp: The timestamp
#     """
    
#     time_array = time.localtime(timestamp)
#     tx_formal_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
#     return tx_formal_time


def add_TxNode_property(directed_graph):
    tx_hash = directed_graph.new_vertex_property("string")
    directed_graph.vp["tx_hash"] = tx_hash
    # tx_inputs_count = directed_graph.new_vertex_property("int")
    # directed_graph.vp["tx_inputs_count"] = tx_inputs_count
    # tx_inputs_value = directed_graph.new_vertex_property("double")
    # directed_graph.vp["tx_inputs_value"] = tx_inputs_value
    # tx_outputs_count = directed_graph.new_vertex_property("int")
    # directed_graph.vp["tx_outputs_count"] = tx_outputs_count
    # tx_outputs_value = directed_graph.new_vertex_property("double")
    # directed_graph.vp["tx_outputs_value"] = tx_outputs_value
    # tx_block_height = directed_graph.new_vertex_property("int")
    # directed_graph.vp["tx_block_height"] = tx_block_height
    # tx_block_time = directed_graph.new_vertex_property("int")
    # directed_graph.vp["tx_block_time"] = tx_block_time
    # tx_fee = directed_graph.new_vertex_property("double")
    # directed_graph.vp["tx_fee"] = tx_fee
    # tx_size = directed_graph.new_vertex_property("int")
    # directed_graph.vp["tx_size"] = tx_size


def add_AdsNode_property(directed_graph):
    ads_address = directed_graph.new_vertex_property("string")
    directed_graph.vp["address"] = ads_address
    # ads_prev_type = directed_graph.new_vertex_property("string")
    # directed_graph.vp["prev_type"] = ads_prev_type
    # ads_next_type = directed_graph.new_vertex_property("string")
    # directed_graph.vp["next_type"] = ads_next_type


def add_edge_property(directed_graph):
    edge_value = directed_graph.new_edge_property("double")
    directed_graph.ep["value"] = edge_value
    # edge_time = directed_graph.new_edge_property("int")
    # directed_graph.ep["time"] = edge_time


def add_TxNode(directed_graph, hash):
    tx_node = directed_graph.add_vertex()
    moduleG.reverse_map["transaction_dict"][hash] = directed_graph.vertex_index[tx_node]
    directed_graph.vp["tx_hash"][tx_node] = hash
    


def add_inputs_AdsNode(directed_graph, prev_address):
    if prev_address not in moduleG.reverse_map["account_dict"]:
        ads_inputs_node = directed_graph.add_vertex()
        moduleG.reverse_map["account_dict"][prev_address] = directed_graph.vertex_index[
            ads_inputs_node]
        directed_graph.vp["address"][ads_inputs_node] = prev_address
    # else:
    #     ads_index = moduleG.reverse_map["account_dict"][prev_address]


def add_outputs_AdsNode(directed_graph, address):
    if address not in moduleG.reverse_map["account_dict"]:
        ads_outputs_node = directed_graph.add_vertex()
        moduleG.reverse_map["account_dict"][address] = directed_graph.vertex_index[
            ads_outputs_node]
        directed_graph.vp["address"][ads_outputs_node] = address
        # directed_graph.vp["next_type"][ads_outputs_node] = next_type
    # else:
    #     ads_index = moduleG.reverse_map["account_dict"][address]
    #     if directed_graph.vp["next_type"][ads_index] == '':
    #         directed_graph.vp["next_type"][ads_index] = next_type


def add_inputs_AdsEdge(directed_graph, AdsNode, TxNode):
    Ads_index = moduleG.reverse_map["account_dict"][AdsNode]
    Tx_index = moduleG.reverse_map["transaction_dict"][TxNode]
    new_edge = directed_graph.add_edge(directed_graph.vertex(Ads_index),
                                       directed_graph.vertex(Tx_index))
    # directed_graph.ep["value"][new_edge] = prev_value
    # directed_graph.ep["time"][new_edge] = block_time


def add_outputs_AdsEdge(directed_graph, TxNode, AdsNode):
    Tx_index = moduleG.reverse_map["transaction_dict"][TxNode]
    Ads_index = moduleG.reverse_map["account_dict"][AdsNode]
    new_edge = directed_graph.add_edge(directed_graph.vertex(Tx_index),
                                       directed_graph.vertex(Ads_index))
    # directed_graph.ep["value"][new_edge] = value
    # directed_graph.ep["time"][new_edge] = block_time




def generate_graph(txs, sequence_number):
    if (os.path.exists("graph_save/"+sequence_number+"_revmap.pkl") 
        and "graph_save/"+sequence_number+"_BitcoinGraph.gt"):
        rev_map = load_file("graph_save/"+sequence_number+"_revmap.pkl")
        moduleG.reverse_map = rev_map
        graph = gt.load_graph("graph_save/"+sequence_number+"_BitcoinGraph.gt")
    else:
        graph = gt.Graph()
        add_TxNode_property(graph)
        add_AdsNode_property(graph)
        add_edge_property(graph)

        print('prepare to generate_graph...\n')
        for tx in tqdm(txs):
            add_TxNode(graph, tx)
            filepath = 'tx_embedding/' + str(tx) + '.json'
            tx_data = read(filepath)
            for p in ['in', 'out']:
                if p == "in":
                    addresses = list(tx_data[p].keys())
                    for address in addresses:
                        add_inputs_AdsNode(graph, address)
                        add_inputs_AdsEdge(graph, address, tx)
                else:
                    addresses = list(tx_data[p].keys())
                    for address in addresses:
                        add_outputs_AdsNode(graph, address)
                        add_outputs_AdsEdge(graph, tx, address)

        with open("graph_save/"+sequence_number+"_revmap.pkl","wb") as f:
            pickle.dump(moduleG.reverse_map,f)
        graph.save("graph_save/"+sequence_number+"_BitcoinGraph.gt")
    
    return moduleG.reverse_map, graph
