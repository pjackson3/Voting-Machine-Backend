"""Implement the blockchain.

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

from hashlib import sha256
import json
import time


class Block:
    """A single block in the chain."""

    def __init__(self, index, transactions, timestamp, previous_hash):
        """Construct the `Block` class.

        :param index: Unique ID of the block.
        :param transactions: List of transactions.
        :param timestamp: Time of generation of the block.
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash

    def compute_hash(self) -> str:
        """Return the hash of the block instance by first converting it into a JSON string.

        :return: The hash of the block
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class BlockChain:
    """The chain of blocks."""

    # The difficulty of the proof of work algorithms.
    difficulty = 2

    def __init__(self):
        """Construct the `BlockChain` class."""
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Generate a genesis block and append it to the chain.

        The block has index 0, previous_hash 0, and a valid hash.
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self) -> Block:
        """Retrieve the most recent block in the chain.

        Note that the chain will always consist of at least one block (the genesis block).
        """
        return self.chain[-1]

    @staticmethod
    def proof_of_work(block: Block) -> str:
        """Try different nonce values to get a hash that satisfies the criteria."""
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * BlockChain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_block(self, block: Block, proof: str) -> bool:
        """Add the block to the chain after verification.

        Verification includes:
         - Checking if the proof is valid
         - The previous_hash is valid.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not BlockChain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def is_valid_proof(block: Block, block_hash: str) -> bool:
        """Check if the block_hash is a valid hash and satisfies the difficulty criteria."""
        return (block_hash.startswith('0' * BlockChain.difficulty)
                and block_hash == block.compute_hash())

    def add_new_transaction(self, transaction: dict) -> None:
        """Add a new transaction."""
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """Add pending transactions to the blockchain by adding them to a block and figuring out proof of work."""
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash
                          )

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index

    @classmethod
    def check_chain_validity(cls, chain) -> bool:
        """A helper method to check if the entire blockchain is valid."""
        result = True
        previous_hash = '0'

        for block in chain:
            block_hash = block.hash
            delattr('block', 'hash')

            if not cls.is_valid_proof(block, block.hash) or previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash
        return result
