import os
import pickle
import csv
import pandas as pd
from tqdm import tqdm
def integrity_checking(address, size, relation_path):
    file1 = relation_path + address + '_in_addressRelation.csv'
    file2 = relation_path + address + '_out_addressRelation.csv'

    # check the addressRelation file is vaild or not
    if (os.path.getsize(file1) == 0) or (os.path.getsize(file2) == 0):
        print(file1)
        print('\n')
        print(file2)
        return False
    else:
        data_in = pd.read_csv(file1, index_col=0)
        data_out = pd.read_csv(file2, index_col=0)
        data_in.columns = ['add', 'val', 'tx', 'block']
        data_out.columns = ['add', 'val', 'tx', 'block']
        data_all = pd.concat([data_in, data_out], axis=0)
        txs = list(set(data_all['tx']))
        """ check num of tx file larger than the size of tx_group """
        if len(txs) < size:
            return False

        """ check tx file whether exist """
        # for tx in txs:
        #     if (not os.path.exists(tx_path + tx + '_tx.json')):
        #         return False

        return True


def marking(label_path):
    # data = pd.read_csv(label_path, header=None, index_col=0)
    data = pd.read_csv(label_path, index_col=0)
    data = data.iloc[:,0:2]
    print(data)
    marked_address = {}
    for i in set(data['address']):
        label = list(data[data['address'] == i]['label'])[0]
        label = str(label)
        if label == 'Exchange':
            marked_address[i] = 0
        elif label == 'Scam':
            marked_address[i] = 1
        elif label == 'Ransom':
            marked_address[i] = 2
        elif label == 'Mixer':
            marked_address[i] = 3
        elif label == 'Darknet':
            marked_address[i] = 4
        # if label in ['Gambling','DEX', 'Mining', 'Sanctioned', 'Wallet', 'Services', 'Theft', 'Child Abuse Material', 'High risk', 'Terrorism', 'Merchant', 'null']:
        #     marked_address[i] = 5
        else:
            marked_address[i] = 5

        # if label == 'EXCHANGE':
        #     marked_address[i] = 0
        # if label == 'GAMBLING_WEBSITE':
        #     marked_address[i] = 1
        # if label == 'MINING_POOL':
        #     marked_address[i] = 2
        # if label in ['RANSOMWARE', 'MARKETPLACE', 'FAUCET',
        #              'MIXER', 'WALLET', 'OLDHISTORY', 'SERVICE']:
        #     marked_address[i] = 3
    return marked_address


def address_checking(marked_address, size, relation_path):
    print('addresses checking ...')
    for address in tqdm(list(marked_address.keys())):
        if not integrity_checking(address, size, relation_path):
            del marked_address[address]  # delete the invaild addresses
    print('checking finish !')
    print('The number of valid addresses : ', len(marked_address))
    return marked_address


def address_preparing(label_path, size, relation_path, dateset_path):
    if (os.path.exists(dateset_path + '/marked_address.pkl')):
        print('marked_address are already prepared')
        f = open(dateset_path + '/marked_address.pkl', 'rb')
        marked_address = pickle.load(f)
        f.close()
        return marked_address
    else:
        print('marked_address start to prepare')
        marked_address = marking(label_path)
        
        marked_address = address_checking(marked_address, size, relation_path)
        f = open(dateset_path + '/marked_address.pkl', 'wb')
        pickle.dump(marked_address, f)
        f.close()
        print('marked_address are already prepared')
        return marked_address
