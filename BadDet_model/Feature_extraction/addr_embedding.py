import pandas as pd 
from tqdm import tqdm
from feature import statistics, amount_indicator, addr_degree_indicator, time_indicator
from graph_structrue_feature import structrue_feature


def addr_embedding(marked_address, relation_path, ifstructrue_feature, graph):
    embedding = {}
    print('prepare to get addr_nodes embedding')
    for add, label in tqdm(marked_address.items()):
        file1 = relation_path + add + '_in_addressRelation.csv'
        file2 = relation_path + add + '_out_addressRelation.csv'
        data_in = pd.read_csv(file1, index_col=0)
        data_out = pd.read_csv(file2, index_col=0)
        data_in.columns = ['add', 'val', 'ts', 'block']
        data_out.columns = ['add', 'val', 'ts', 'block']
        data_all = pd.concat([data_in, data_out], axis=0)
        data_all.drop_duplicates(subset='block', inplace=True)

        if not data_all.empty:
            values = list(data_all['val'])
            values = [i / float(100000000) for i in values]

            static_feature = statistics(values)
            values_dict = {}
            values_dict['in'] = list(data_in['val'])
            values_dict['out'] = list(data_out['val'])
            ai = amount_indicator(values_dict)
            di = addr_degree_indicator(data_in, data_out)
            ti = time_indicator(False, data_all)
            if ifstructrue_feature:
                embedding[add] = static_feature + ai + di + ti + structrue_feature(graph, add, False)
            else:
                embedding[add] = static_feature + ai + di + ti

    return embedding