import pyarrow as pa
import pyarrow.parquet as pq

import glob
import logging
import math
import os

import dask
import dask.dataframe as dd
import numpy as np
import pandas as pd
from dask.distributed import Client, LocalCluster
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.preprocessing import LabelEncoder

from datetime import datetime
from datetime import timedelta


def get_label_encode(col):
    le = LabelEncoder()
    r = le.fit_transform(col)
    return le, r


def get_connected_components(df, group_prefix=None, fname_without_suffix=None, entity='address', relation_col='hash'):
    # encode into number id
    entity_encoder, entity_numid = get_label_encode(df[entity])
    rel_encoder, rel_numid = get_label_encode(df[relation_col])

    # create tx sparse matrix which holds one tx as one col
    ROW = entity_encoder.classes_.shape[0]
    COL = rel_encoder.classes_.shape[0]
    INT64_COL = np.iinfo(np.int32).max + 1  # which is much larger!
    vals = np.ones(len(df))
    rel_mat = csr_matrix((vals, (entity_numid, rel_numid)),
                         shape=(ROW, INT64_COL))

    # compute adjacency
    adjacency = rel_mat.dot(rel_mat.transpose())

    # connected components
    n_cc, labels = connected_components(
        adjacency, directed=False, return_labels=True)

    # get back address
    addr = pd.Series(entity_encoder.classes_, name=entity)
    addr.index = [f"{group_prefix}_{l}" for l in labels]
    addr = addr.reset_index()

    return addr


day_set = []
start_time = datetime(2020, 4, 18)
for i in range(1200):
    day_set.append(start_time.strftime('%Y%m%d'))
    start_time = start_time + timedelta(days=1)

for date in day_set:
    try:
        df = pq.read_table(u'../../../root_dir/data/bitcoin/transactions.parquet/dt=' + date).to_pandas()
        df = df.drop_duplicates(subset=['hash', 'from'], keep='first', inplace=False)
        tx_dist = df['hash'].value_counts()
        df = df.set_index('hash').join(tx_dist[tx_dist > 1], how='inner')
        df = df.drop('hash', axis=1).reset_index()[['index', 'from']]
        df.rename(columns={"index": "index", "from": "address"}, inplace=True)

        cluster = get_connected_components(df,
                                           group_prefix=f"{date}",
                                           fname_without_suffix=None,
                                           entity='address',
                                           relation_col='index')

        cluster.to_csv(f"DAY_OUT/daily_tx_data_{date}.csv", index=False)

        print(date)
    except:
        continue