import datetime
from utils import save
from address_preparing import address_preparing
from transaction import transaction
from config import argparser
from preprocess import preprocess
from generate_graph import generate_graph
import pandas as pd
from addr_embedding import addr_embedding
import moduleG
import importlib
importlib.reload(moduleG)
from moduleG import *
import os


def building(txs, tx_path, marked_address, relation_path, sequence_number, ifstructrue_feature):
    preprocess(txs, tx_path)
    if ifstructrue_feature:
        rev_map, graph = generate_graph(txs, sequence_number)
        moduleG.reverse_map = rev_map
        # print("The dict has been loaded!")
        # graph = gt.load_graph("graph_save/"+sequence_number+"_BitcoinGraph.gt")
        # print("The graph has been loaded!")
    
    tx_embedding, edges = transaction(txs, ifstructrue_feature, graph)  # tx节点编码

    address_embedding = addr_embedding(marked_address, relation_path, ifstructrue_feature, graph)
    embedding = {}
    embedding.update(tx_embedding)
    embedding.update(address_embedding)
    # embedding.update(single_embedding)
    # embedding.update(multi_embedding)
    return embedding, edges


def main():
    args = argparser()
    args.label_path = 'label/20220519-20220521/address_label.csv'
    args.size = 1
    args.relation_path = 'relation/20220519-20220521/'
    args.tx_path = 'transaction/20220519-20220521/transaction.pkl'
    args.dataset_path_SI_LI = 'dataset_output_SI_LI/20220519-20220521'
    args.dataset_path_SI = 'dataset_output_SI/20220519-20220521'
    args.sequence_number = '46'
    args.ifstructrue_feature = True
    '''
    return:
    marked_address: {
        address1:label1, address2:label2 ...   the inputs addresses with its label
    }
    '''
    if not os.path.exists(args.dataset_path_SI_LI):
        os.mkdir(args.dataset_path_SI_LI)
    if not os.path.exists(args.dataset_path_SI):
        os.mkdir(args.dataset_path_SI)
    marked_address = address_preparing(args.label_path, args.size, args.relation_path, args.dataset_path_SI_LI) # 读入所有已经标注的addr及其label

    # transactions = pd.read_csv(args.tx_path, index_col=0) 
    transactions = pd.read_pickle(args.tx_path) 
    txs = list(set(str(ts) for ts in transactions['hash']))
    start = datetime.datetime.now()
    embedding, edges = building(txs, args.tx_path, marked_address, args.relation_path, args.sequence_number, args.ifstructrue_feature)  # tx编码+特征压缩+特征增强
    
    if args.ifstructrue_feature:
        save(embedding, edges, marked_address, args.dataset_path_SI_LI)
    else:
        save(embedding, edges, marked_address, args.dataset_path_SI)

    end = datetime.datetime.now()
    print('prcessing time: {}'.format(end-start))

if __name__ == "__main__":
    main()
