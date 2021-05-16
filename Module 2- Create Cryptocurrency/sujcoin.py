# Module1 - Create Blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# Part 1 : Building Blockchain
class Blockchain:
    
    def __init__(self): 
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.node = Set()

    def create_block(self, proof, previous_hash):
        block = {
                "index": len(self.chain) + 1,
                "timestamp": str(datetime.datetime.now()),
                "proof": proof,
                "previous_hash":previous_hash,
                "transactions": self.transactions
            }
        self.chain.append(block)
        self.transactions = []
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        is_proof_found = False
        while is_proof_found is False:
            hash_operation_value = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation_value[:4] == '0000':
                is_proof_found = True
            else:
                new_proof += 1
                
        return new_proof
    
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys= True).encode()
        return hashlib.sha256(encoded_block).hexdigest() 
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain): 
            current_block = chain[block_index]
            if current_block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            current_proof = current_block['proof']
            hash_operation_value = hashlib.sha256(str(current_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation_value[:4] == '0000':
                return False
            previous_block = current_block
            block_index += 1
            
        return True
               
    def add_transaction(self, sender, receiver, amount):
        transaction = {'sender': sender, 'receiver':receiver, 'amount': amount}
        self.transactions.append(transaction)
        return self.get_previous_block()['index'] + 1
    
    def add_node(self, address): 
        parsed_address = urlparse(address)
        self.nodes.add(parsed_address)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                response_json = response.json()
                length = response_json['length']
                chain = response_json['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
            
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

# Part 2 : Mining our Blockchain
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


@app.route('/')
def hello_world():
    return 'Hello, World!'

blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    return jsonify(blockchain.create_block(proof, previous_hash)), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'length': len(blockchain.chain), 'chain':blockchain.chain}
    return jsonify(response), 200    

@app.route('/is_valid', methods=['GET'])
def is_valid():
    return jsonify(blockchain.is_chain_valid(blockchain.chain)), 200
 
# Part 3 : Decentralizing out Blockchain
# Running app   
app.run(host='0.0.0.0', port = 5000)    