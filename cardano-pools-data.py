import requests
import csv
from constant import api_key



def make_pools_list(api_key, url='https://cardano-mainnet.blockfrost.io/api/v0/pools'):
    '''
    This function create full list of cardano pools
    '''

    print('Start making list of all pools.')
    headers = {'project_id': '{key}'.format(key=api_key)}

    params = {
        'count':100,
        'page':1
        }

    data = []

    while params['page'] != 0:
        tmp_data  = requests.get(url, headers=headers, params=params)
        if len(tmp_data.json()) == 100:
            data += tmp_data.json()
            params['page'] += 1
        else:
            data += tmp_data.json()
            params['page'] = 0

    with open('pool_list.txt', 'w') as f:
        f.write('\n'.join(data))
    
    print('End making list of all pools. {0} pools have been found.'.format(str(len(data))))


def check_stake_range(poolData, pool_id, min, max):
    '''
    Will return pool data if active stake
    is between min and max.
    '''
    if poolData:
        if min <= float(poolData['active_stake']) <= max:
            print('Pool active_stake in range. Pool ID: {0},'
                                               ' Active Stake: {1},'
                                               ' Range: {2} - {3}'.format(pool_id,
                                                                            poolData['active_stake'],
                                                                            min,
                                                                            max))
            return True
        else:
            print('Pool active_stake NOT in range. Pool ID: {0},'
                                                    ' Active Stake: {1},'
                                                    ' Range: {2} - {3}'.format(pool_id,
                                                                                poolData['active_stake'],
                                                                                min,
                                                                                max))
            return False
    else:
        print('poolData empty! PoolId: {0}'.format(pool_id))
        return False


def pool_add_id(poolData, pool_id):
    """
    This function will add pool_id into data
    """
    try:
        poolData['pool_id'] = pool_id
        print('PoolId added: {0}'.format(pool_id))
    except:
        print('Failed when adding ID to pool: {0}'.format(pool_id))
    
    return poolData

def get_largest_pool(poolData, topNumber):
    '''
    Will return top number of pools based on active_stake
    '''
    return sorted(poolData, key=lambda k: k['active_stake'], reverse=True)[:(topNumber -1 )]


def save_data_csv(outData, fileName):
    '''
    This function will save data into file
    '''
    csv_columns = outData[0].keys()

    try:
        with open(fileName, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in outData:
                writer.writerow(data)
    except IOError:
        print("I/O error")

#make_pools_list(api_key)

poolList = []
with open('pool_list.txt') as f:
    poolList = f.read().splitlines()

pools_range1 = []
pools_range2 = []

for count, pool_id in enumerate(poolList):
    print ('{0} out of {1}'.format(count+1, len(poolList)))
    url = "https://cardano-mainnet.blockfrost.io/api/v0/pools/" + pool_id + "/history"
    headers = {'project_id': '{key}'.format(key=api_key)}

    params = {
        'count':3,
        'page':1,
        'order':"desc",
        }
    tmp_data = []

    try:
        tmp_data  = requests.get(url, headers=headers, params=params).json()[2]
    except:
        print('Error when pulling history data for pool: ' + pool_id)

    if tmp_data:
        if check_stake_range(tmp_data, pool_id, 50000000000, 100000000000):
            pools_range1.append(pool_add_id(tmp_data, pool_id))
        pools_range2.append(pool_add_id(tmp_data, pool_id))


print("collecting data ..... Done")


# with open('eggs.csv', newline='') as csvfile:
#     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#     for row in spamreader:
#         print(', '.join(row))

save_data_csv(pools_range1, "range1.csv")
save_data_csv(pools_range2, "range2.csv")
save_data_csv(get_largest_pool(pools_range2, 100), "range3.csv")

print("creating csv ..... Done")