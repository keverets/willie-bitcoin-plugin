import sys
import time
import locale

from operator import itemgetter
from decimal import Decimal

from bitcoinrpc.authproxy import AuthServiceProxy

USERNAME=""
PASSWORD=""

STARTING_PEER_HEIGHT=0

BYTE_MAGNITUDE = (
    'B',
    'KB',
    'MB',
    'GB'
)
def get_transaction(btcd, txnid):
    raw = btcd.getrawtransaction(txnid)
    return btcd.decoderawtransaction(raw)

def estimate_spent_transaction(btcd, txnid):

    transaction = get_transaction(btcd, txnid)
    inputs = []
    outputs = []
    spent = Decimal(0)

    # get the sum of the inputs
    for vin in transaction['vin']:
        txnin = get_transaction(btcd, vin['txid'])
        inputs.append(txnin['vout'][vin['vout']]['value'])

    for vout in transaction['vout']:
        outputs.append(vout['value'])

    fee = sum(inputs) - sum(outputs)

    if len(outputs) == 1:
        spent = outputs[0]
    elif len(inputs) == 1:
        spent = min(outputs)

    return (spent, fee)

def format_bytes(number):
    iterations = 0

    while number > 1024:
        number /= Decimal(1024.0)
        iterations += 1

    return "{0:.2f}{1}".format(number, BYTE_MAGNITUDE[iterations])

def block_details(btcd, blockindex):
    blockhash = btcd.getblockhash(blockindex)
    block = btcd.getblock(blockhash)
    amount = Decimal(0);

    for txid in block['tx']:
        tx = btcd.gettxout(txid , 0)

        if tx:
            amount += tx['value']
        else:
            print "no txout for txn ", txid

    return {
        "index": blockindex,
        "txncount": len(block['tx']),
        "spent": amount,
        "size": format_bytes(block['size'])
    }

def new_difficulty(btcd, difficulty):
    return "new difficulty reached {0}".format(difficulty)

CHECKPOINT = {
    'getdifficulty': (new_difficulty, None),
    'getblockcount': (block_details, None),
}

def monitor(verbose=False):
    url = "http://{0}:{1}@127.0.0.1:8332".format(
        USERNAME,
        PASSWORD
    )
    btcd = AuthServiceProxy(url)

    peerheight = max_peer_height(btcd)
    blockheight = btcd.getblockcount()

    # wait until the our local copy of the chain has caught up before notifying
    # of changes to the blockchain
    while blockheight < peerheight:
        if verbose:
            print "waiting for rpc bitcoind at height {0} to reach height {1}" \
                    .format(blockheight, peerheight)

        blockheight = btcd.getblockcount()
        time.sleep(10)

    while True:
        for name in CHECKPOINT:
            current = getattr(btcd, name)()
            action, last = CHECKPOINT[name]

            if verbose:
                print name, " last: ", last, " current: ", current

            if last is not None and last != current:
                print action(btcd, current)

            CHECKPOINT[name] = (action, current)

        if verbose:
            print "sleeping for ten seconds"

        time.sleep(10)

def max_peer_height(btcd):
    peerheights = {}
    peers = btcd.getpeerinfo()

    for peer in peers:
        height = peer['startingheight']

        if height not in peerheights:
            peerheights[height] = 0

        peerheights[height] += 1


    maxheight = sorted(peerheights.items(), key=itemgetter(1), reverse=True)

    return maxheight[0][0]


if __name__ == "__main__":
    #monitor(verbose=False)
    url = "http://{0}:{1}@127.0.0.1:8332".format(
        USERNAME,
        PASSWORD
    )
    btcd = AuthServiceProxy(url)

    btcd.getblockcount()
    txnid = sys.argv[1]

    print estimate_spent_transaction(btcd, txnid)
