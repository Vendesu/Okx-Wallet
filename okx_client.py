import requests
import logging
from typing import Dict, List, Optional
from web3 import Web3
import json
import time
from config import OKX_WALLET_PRIVATE_KEY, OKX_WALLET_ADDRESS, OKX_NETWORK

class OKXWalletClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.private_key = OKX_WALLET_PRIVATE_KEY
        self.wallet_address = OKX_WALLET_ADDRESS
        self.network = OKX_NETWORK
        
        # Setup Web3 connection berdasarkan network
        self.web3 = self._setup_web3()
        
    def _setup_web3(self) -> Web3:
        """Setup Web3 connection berdasarkan network yang dipilih"""
        try:
            if self.network == 'ethereum':
                # Ethereum mainnet
                provider_url = "https://mainnet.infura.io/v3/YOUR_INFURA_KEY"  # Ganti dengan Infura key
                return Web3(Web3.HTTPProvider(provider_url))
            elif self.network == 'polygon':
                # Polygon mainnet
                provider_url = "https://polygon-rpc.com"
                return Web3(Web3.HTTPProvider(provider_url))
            elif self.network == 'bsc':
                # Binance Smart Chain
                provider_url = "https://bsc-dataseed.binance.org"
                return Web3(Web3.HTTPProvider(provider_url))
            elif self.network == 'arbitrum':
                # Arbitrum One
                provider_url = "https://arb1.arbitrum.io/rpc"
                return Web3(Web3.HTTPProvider(provider_url))
            else:
                # Default ke Ethereum
                provider_url = "https://mainnet.infura.io/v3/YOUR_INFURA_KEY"
                return Web3(Web3.HTTPProvider(provider_url))
                
        except Exception as e:
            self.logger.error(f"Gagal setup Web3 untuk network {self.network}: {e}")
            return None
            
    def get_balance(self, token_address: str = None) -> Optional[Dict]:
        """Mendapatkan balance dari OKX Wallet"""
        try:
            if not self.web3 or not self.wallet_address:
                return None
                
            if token_address:
                # Get ERC-20 token balance
                return self._get_token_balance(token_address)
            else:
                # Get native token balance (ETH, MATIC, BNB, dll)
                return self._get_native_balance()
                
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan balance: {e}")
            return None
            
    def _get_native_balance(self) -> Dict:
        """Mendapatkan balance native token"""
        try:
            balance_wei = self.web3.eth.get_balance(self.wallet_address)
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            
            return {
                'token': self._get_native_token_symbol(),
                'address': self.wallet_address,
                'balance': float(balance_eth),
                'balance_wei': balance_wei,
                'decimals': 18
            }
            
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan native balance: {e}")
            return None
            
    def _get_token_balance(self, token_address: str) -> Dict:
        """Mendapatkan balance ERC-20 token"""
        try:
            # ERC-20 ABI untuk balanceOf
            abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "symbol",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function"
                }
            ]
            
            contract = self.web3.eth.contract(address=token_address, abi=abi)
            
            # Get balance
            balance = contract.functions.balanceOf(self.wallet_address).call()
            
            # Get decimals
            decimals = contract.functions.decimals().call()
            
            # Get symbol
            symbol = contract.functions.symbol().call()
            
            # Convert to human readable
            balance_human = balance / (10 ** decimals)
            
            return {
                'token': symbol,
                'address': token_address,
                'balance': float(balance_human),
                'balance_raw': balance,
                'decimals': decimals
            }
            
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan token balance: {e}")
            return None
            
    def _get_native_token_symbol(self) -> str:
        """Mendapatkan symbol native token berdasarkan network"""
        symbols = {
            'ethereum': 'ETH',
            'polygon': 'MATIC',
            'bsc': 'BNB',
            'arbitrum': 'ETH',
            'optimism': 'ETH'
        }
        return symbols.get(self.network, 'ETH')
        
    def send_transaction(self, to_address: str, amount: float, 
                        token_address: str = None, gas_price: int = None) -> Optional[str]:
        """Send transaction dari OKX Wallet"""
        try:
            if not self.web3 or not self.private_key:
                self.logger.error("Web3 atau private key tidak tersedia")
                return None
                
            if token_address:
                # Send ERC-20 token
                return self._send_token_transaction(to_address, amount, token_address, gas_price)
            else:
                # Send native token
                return self._send_native_transaction(to_address, amount, gas_price)
                
        except Exception as e:
            self.logger.error(f"Gagal send transaction: {e}")
            return None
            
    def _send_native_transaction(self, to_address: str, amount: float, gas_price: int = None) -> str:
        """Send native token transaction"""
        try:
            # Convert amount to Wei
            amount_wei = self.web3.to_wei(amount, 'ether')
            
            # Get nonce
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
            
            # Get gas price if not provided
            if not gas_price:
                gas_price = self.web3.eth.gas_price
                
            # Estimate gas
            gas_estimate = self.web3.eth.estimate_gas({
                'to': to_address,
                'value': amount_wei,
                'from': self.wallet_address
            })
            
            # Build transaction
            transaction = {
                'nonce': nonce,
                'to': to_address,
                'value': amount_wei,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'chainId': self.web3.eth.chain_id
            }
            
            # Sign transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            self.logger.info(f"Native transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            self.logger.error(f"Gagal send native transaction: {e}")
            raise
            
    def _send_token_transaction(self, to_address: str, amount: float, 
                               token_address: str, gas_price: int = None) -> str:
        """Send ERC-20 token transaction"""
        try:
            # ERC-20 ABI untuk transfer
            abi = [
                {
                    "constant": False,
                    "inputs": [
                        {"name": "_to", "type": "address"},
                        {"name": "_value", "type": "uint256"}
                    ],
                    "name": "transfer",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }
            ]
            
            contract = self.web3.eth.contract(address=token_address, abi=abi)
            
            # Get token decimals
            token_balance = self._get_token_balance(token_address)
            if not token_balance:
                raise Exception("Gagal mendapatkan token info")
                
            decimals = token_balance['decimals']
            
            # Convert amount to token units
            amount_raw = int(amount * (10 ** decimals))
            
            # Get nonce
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
            
            # Get gas price if not provided
            if not gas_price:
                gas_price = self.web3.eth.gas_price
                
            # Build transaction
            transaction = contract.functions.transfer(to_address, amount_raw).build_transaction({
                'nonce': nonce,
                'gasPrice': gas_price,
                'chainId': self.web3.eth.chain_id
            })
            
            # Estimate gas
            gas_estimate = self.web3.eth.estimate_gas(transaction)
            transaction['gas'] = gas_estimate
            
            # Sign transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            self.logger.info(f"Token transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            self.logger.error(f"Gagal send token transaction: {e}")
            raise
            
    def get_transaction_status(self, tx_hash: str) -> Optional[Dict]:
        """Check status transaction"""
        try:
            if not self.web3:
                return None
                
            # Get transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {
                'tx_hash': tx_hash,
                'status': 'success' if receipt['status'] == 1 else 'failed',
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'effective_gas_price': receipt['effectiveGasPrice']
            }
            
        except Exception as e:
            self.logger.error(f"Gagal check transaction status: {e}")
            return None
            
    def get_transaction_history(self, limit: int = 50) -> Optional[List[Dict]]:
        """Mendapatkan history transaction (basic implementation)"""
        try:
            if not self.web3 or not self.wallet_address:
                return None
                
            # Get latest block
            latest_block = self.web3.eth.block_number
            
            transactions = []
            
            # Scan recent blocks for transactions (basic implementation)
            # Note: Untuk production, gunakan blockchain explorer API yang lebih efisien
            for block_num in range(latest_block - limit, latest_block + 1):
                try:
                    block = self.web3.eth.get_block(block_num, full_transactions=True)
                    
                    for tx in block.transactions:
                        if (tx['from'].lower() == self.wallet_address.lower() or 
                            tx['to'] and tx['to'].lower() == self.wallet_address.lower()):
                            
                            transactions.append({
                                'tx_hash': tx['hash'].hex(),
                                'from': tx['from'],
                                'to': tx['to'],
                                'value': self.web3.from_wei(tx['value'], 'ether'),
                                'block_number': block_num,
                                'timestamp': block.timestamp
                            })
                            
                except Exception as e:
                    continue
                    
            return transactions[:limit]
            
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan transaction history: {e}")
            return None
            
    def test_connection(self) -> bool:
        """Test koneksi ke blockchain network"""
        try:
            if not self.web3:
                return False
                
            # Test basic connection
            latest_block = self.web3.eth.block_number
            if latest_block > 0:
                self.logger.info(f"Koneksi {self.network} berhasil, latest block: {latest_block}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Koneksi {self.network} gagal: {e}")
            return False