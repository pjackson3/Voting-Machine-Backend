"""The web interface for the blockchain.

Copyright(C) Peter Jackson Link III.

This file is part of Voting Machine.

    Voting Machine is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Voting Machine is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Voting Machine.  If not, see <https://www.gnu.org/licenses/>.
"""

import json

from flask import Flask, request, jsonify
import requests
import time

from .blockchain import BlockChain, Block


peers = set()

app = Flask(__name__)

blockchain = BlockChain()


@app.route('/new-transaction', methods=['POST'])
def new_transaction():
    """Create a new transaction."""
    tx_data = request.get_json()
    required_fields = ["id", "answer"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 400

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


@app.route('/chain')
def get_chain():
    """Return the chain."""
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    return jsonify({"length": len(chain_data),
                    "chain": chain_data})


@app.route('/mine')
def mine_unconfirmed_transactions():
    """Mine unconfirmed transactions."""
    result = blockchain.mine()
    if not result:
        return "No transactions to mine."

    chain_length = len(blockchain.chain)
    consensus()
    if chain_length == len(blockchain.chain):
        announce_new_block(blockchain.last_block)
    return f"Block #{blockchain.last_block.index} is mined."


@app.route('/pending_tx')
def get_pending_tx():
    """Get pending transactions."""
    return jsonify(blockchain.unconfirmed_transactions)


@app.route('/register_node', methods=['POST'])
def register_new_peers():
    """Register new peers."""
    node_address = request.get_json()['node_address']
    if not node_address:
        return "Invalid data", 400

    peers.add(node_address)

    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """Register self with a node in the chain."""
    node_address = request.get_json()['node_address']
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # Update the chain and peers.
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    """Create a chain from dumped JSON data."""
    new_blockchain = BlockChain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data['index'],
                      block_data['transactions'],
                      block_data['timestamp'],
                      block_data['previous_hash']
                      )
        proof = block_data['hash']
        if idx > 0:
            added = new_blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!")
        else:
            # Genesis block, auto-trusted
            new_blockchain.chain.append(block)
    return new_blockchain


def consensus():
    """A simple consensus algorithm."""
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get(f'{node}/chain')
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    """Add a block mined by someone else to the node's chain.

    Verify before adding.
    """
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


def announce_new_block(block):
    """Announce a new block has been mined."""
    for peer in peers:
        url = "{}add_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))


__all__ = ['app']
