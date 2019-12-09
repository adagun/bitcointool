#!/usr/bin/python3
# coding=utf-8

# 

import os, random, binascii, hashlib
from pycoin import encoding, key
from pycoin.encoding.b58 import b2a_hashed_base58
from pycoin.ecdsa.secp256k1 import secp256k1_generator
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


user = "username"
password = "password"
host = "localhost"
port = "8332"
class transactions: pass


def connect():
    """ Connects to the Bitcoin client """
    transactions.connection = AuthServiceProxy("http://%s:%s@%s:%s" % (user, password, host, port))
    

def listSpendables():
    """ Shows a list of spendable outputs in wallet """
    listUnspent = transactions.connection.listunspent()
    for i in range(len(listUnspent)):
        print(str(i)+'.'" address:", listUnspent[i]["address"],"txid:", listUnspent[i]["txid"], "- amount:", listUnspent[i]["amount"],"BTE")


def getSpendable(index):
    """ Returns information about a spendable output  """
    return transactions.connection.listunspent()[int(index)]
    
def transactionFromWallet(keys, transactions):
    """ Creates a raw transaction from outputs in wallet """
    print("Total balance:", transactions.connection.getbalance(), "BTE")
    listSpendables()
    outputID = 0
    nInputs = 0
    outputs = []
    availableAmount = 0
    while (outputID != 's'):
        outputID = input("Choose output to spend (s to stop):")
        if (outputID == 's'):
            break            
        outputs.append(getSpendable(outputID))       
        availableAmount = availableAmount + float(outputs[nInputs]["amount"])
        nInputs = nInputs+1
        print("Output", outputID, " added")  
    print("Available amount: ", availableAmount)    
    transactions.amountToSend = float(input("Enter amount to send:"))
    transactions.changeAddress = input("Enter changeAddress ('self' to use own address):")
    if  transactions.changeAddress == "self":
        transactions.changeAddress = outputs[0]["address"]  
    feeRate = input("Enter fee per kB:")
    transactions.sendTo = input("Enter address to send to ('new' to send to the new generated address):")
    if transactions.sendTo == "new":
        transactions.sendTo = keys.BTCaddressCompressed
    
    data = input("Enter message:")
    nOutputs = 2  
    transactions.recipients = [{"address": transactions.sendTo, "amount": transactions.amountToSend}]
    transactions.fee = calculateFee(feeRate, nInputs, nOutputs)

    inputs = []    
    for i in range(len(outputs)):
        print(i)
        inputs.append({"txid": outputs[i]["txid"], "vout": round(outputs[i]["vout"], 8)})        
    transactions.change = float(availableAmount) - transactions.amountToSend - float(transactions.fee)    

    outputs = {transactions.sendTo: round(transactions.amountToSend, 8), transactions.changeAddress: round(transactions.change, 8),  "data": (data.encode().hex())}    
    connect()
    transactions.rawTransaction = transactions.connection.batch_([["createrawtransaction", inputs, outputs]])
    

def spendOutput(keys, transactions):
    """ Makes a transaction with a spendable output """

    address = input("Enter address to send from:")
    txid = input("Enter transaction id with spendable output:")
    try:
        # Get transaction info and find the spendable outputs of the given address
        connect()
        tx = transactions.connection.getrawtransaction(txid, 1)
        vouts = tx["vout"]   
        for i in range(len(vouts)):
            if "addresses" in vouts[i]["scriptPubKey"]:
                if vouts[i]["scriptPubKey"]["addresses"][0] == address:
                    vout = vouts[i]["n"]        
                    availableAmount = float(vouts[i]["value"])
        if vout is None:
            raise ValueError()
    except:
        print("No spendable output found")
        return -1

    print("Available amount:", availableAmount)
    transactions.amountToSend = float(input("Amount to send:"))

    transactions.changeAddress = input("Enter changeAddress ('self' to use own address):")
    if  transactions.changeAddress == "self":
        transactions.changeAddress = address 
    feeRate = input("Enter fee per kB:")
    transactions.sendTo = input("Enter address to send to:")
    data = input("Enter message:")
    nOutputs = 2
    nInputs = 1
    transactions.sendFrom = address
    transactions.recipients = [{"address": transactions.sendTo, "amount": transactions.amountToSend}]
    transactions.fee = calculateFee(feeRate, nInputs, nOutputs)
    inputs = []
    inputs.append({"txid": txid, "vout": vout})              
    transactions.change = float(availableAmount) - transactions.amountToSend - float(transactions.fee)      
    outputs = {transactions.sendTo: round(transactions.amountToSend, 8), transactions.changeAddress: round(transactions.change, 8),  "data": (data.encode().hex())}  
    connect()
    transactions.rawTransaction = transactions.connection.batch_([["createrawtransaction", inputs, outputs]])



def transactionWithGenerated(keys, transactions):    
    """ Spends available outputs from first transaction  """
    # get spendable outputs from last transaction  
    txid = transactions.sentTransaction   
    connect()
    transactions.z
    tx = transactions.connection.getrawtransaction(txid, 1)
    transactions.sendFrom = transactions.sendTo
    vouts = tx["vout"]   
    txOutputs = []
    availableAmount = 0
    for i in range(len(vouts)):
        if "addresses" in vouts[i]["scriptPubKey"]:
            if vouts[i]["scriptPubKey"]["addresses"][0] ==  transactions.sendFrom:
                txOutputs.append({"txid": txid, "vout": vouts[i]["n"]})
                availableAmount = float(availableAmount) + float(vouts[i]["value"])
    availableAmount = abs(availableAmount)
    print("Previous transaction:", txid, availableAmount ,"BTE sent to address:",transactions.sendTo) 
    for i in range(len(txOutputs)):
        print(i, txOutputs[i], " ")
    outputID = 0
    nInputs = 0
    inputs = []

    while (outputID != 's'):
        outputID = input("Choose output to spend (s to stop):")
        if (outputID == 's'):
            break
        else:
            inputs.append(txOutputs[int(outputID)])         
        nInputs = nInputs+1        

    outputs = {}
    transactions.amountToSend = 0
    numOfRecipients = input("Enter number of Recipients:")
    transactions.recipients = []
    for i in range(int(numOfRecipients)):    
        print("\nAvailable amount:", availableAmount-transactions.amountToSend, "BTE")           
        transactions.recipients.append(addRecipient(i))  
        transactions.amountToSend = float(transactions.amountToSend) + transactions.recipients[i]["amount"]
        outputs.update({transactions.recipients[i]["address"]: round(transactions.recipients[i]["amount"], 8)})      
    feeRate = input("Enter fee per kB:")
    transactions.changeAddress = input("Enter changeAddress ('self' to use own address):")
    if  transactions.changeAddress == "self":
        transactions.changeAddress = transactions.sendFrom
     
    data = input("Enter message:")
    nOutputs = int(numOfRecipients)+1
    transactions.fee = calculateFee(feeRate, nInputs, nOutputs)
    transactions.change = availableAmount-transactions.amountToSend-float(transactions.fee)
    outputs.update({transactions.changeAddress: round(transactions.change, 8)})    
    outputs.update({"data": data.encode().hex()})
    connect()
    transactions.rawTransaction = transactions.connection.batch_([["createrawtransaction", inputs, outputs]])
   

def printTransactionDetails(transactions):
    """ Prints details about outgoing transaction """
    for recipient in transactions.recipients:        
        print("Sending", recipient["amount"], "BTE To address:", recipient["address"])
    print("Change", transactions.change, "BTE To address:", transactions.changeAddress)   
    print("Total", transactions.amountToSend,"BTE")
    print("Fee:", transactions.fee,"BTE")
 

def addRecipient(i):
    """ Creates and returns recipient details from user input """    
    print("\n**** Recipient:",i+1,"****" )
    address = input("Enter address:")
    amount = float(input("Enter amount to send:"))
    return {"address": address, "amount": amount}
    


def signTransaction(keys, transactions):
    """ Handles the signing of a transaction """
    privateKey = input("Enter Private Key for " + transactions.sendFrom + ": ")
    privateKeys = [privateKey]           
    try:  
        transactions.signedRawTransaction = transactions.connection.signrawtransaction(transactions.rawTransaction[0], [],  privateKeys)       
    except:
        print("Invalid Private Key")
        return -1
def menu():
    """ The programs main loop. Presents and handles menu choices """
    quit = False
    keys = None
    connect()
    while (quit == False):
        print ("\n**********Meny**********\nOptions:\n1 - Generate Keys\n2 - " 
               "Show Generated Keys\n3 - Make Transaction from an output in wallet\n"
               "4 - Spend an output with generated keys\n5 - Spend outputs from last transaction\n0 - Exit")
        choice = input("Your choice:")
        if (choice == '0'): 
            quit = True 
        elif (choice == '1'):  
            keys = generateKeys()   
                     
        elif (choice == '2'):
            if(keys is None):
                print("You haven't generated any keys yet\n")      
            else:
                printGeneratedKeys(keys)
        elif(choice == '3'):
            print ("\n**********Make Transaction From Wallet**********")
            transactionFromWallet(keys, transactions)    
            transactions.signedRawTransaction = transactions.connection.signrawtransaction(transactions.rawTransaction[0])       
            printTransactionDetails(transactions)     
            input("Press any key to confirm transaction...")
            transactions.sentTransaction = transactions.connection.sendrawtransaction(transactions.signedRawTransaction["hex"])
            print("Transaction sent. txid:", transactions.sentTransaction)
        elif(choice == '4'):
                print ("\n**********Make a transaction with a spendable output **********")
                if spendOutput(keys, transactions) == -1:
                   break
                else:
                    if signTransaction(keys, transactions) == -1:
                        break          
                    printTransactionDetails(transactions)
                    input("Press any key to confirm transaction...")
                    transactions.sentTransaction = transactions.connection.sendrawtransaction(transactions.signedRawTransaction["hex"])
                    print("Transaction sent. txid:", transactions.sentTransaction)
        
        elif(choice == '5'):
            if not(hasattr(transactions, "sentTransaction")):
                print("\nYou need to make a first transaction\n")    
            else:                
                print ("\n**********Spend outputs from last transaction **********")
                transactionWithGenerated(keys, transactions)
                if signTransaction(keys, transactions) == -1:
                        break       
                printTransactionDetails(transactions)
                input("Press any key to confirm transaction...")
                transactions.sentTransaction = transactions.connection.sendrawtransaction(transactions.signedRawTransaction["hex"])
                print("Transaction sent. txid:", transactions.sentTransaction)
        else:    
            print("Invalid choice \n")    
        
 
def calculateFee(feeRate, nInputs, nOutputs):
    """ Calculates pay to address fee size  """
    transactionSize = (nInputs*180)+(nOutputs*34)+10   
    return float(feeRate)*transactionSize/1000

def generateKeys():
    """ Generates bitcoin keys from an integer """
    k = input("Enter Number to generate keys from (leave empty for randomized):")
    if(k == ""):
        #random 255-bit integer
        k = random.SystemRandom().getrandbits(255) 
    print("\nGENERATING KEYS FROM K =", k, "\n")
    keys = key.Key(int(k), secp256k1_generator) 
    keys.privateKeyHex = "%064x" % keys._secret_exponent
    keys.P = keys._secret_exponent*secp256k1_generator
    # Px and Py as hex
    keys.Px = "%064x" % keys.P[0]
    keys.Py = "%064x" % keys.P[1]
    # add prefixes
    keys.publicKeyUncompressed  = "04" + str(keys.Px) + str(keys.Py)
    keys.publicKeyCompressed= ("02" if keys.P[1] % 2 == 0 else "03") + keys.Px
    keys.wifUncompressed = hashedBase58("80"+str(keys.privateKeyHex))
    keys.wifCompressed = hashedBase58("80"+str(keys.privateKeyHex)+"01")
    # get hash160 keys
    keys.hash160Compressed = hash160(keys.publicKeyCompressed)
    keys.hash160Uncompressed = hash160(keys.publicKeyUncompressed)
    # get double sha256-hashed base58 keys
    keys.BTCaddressCompressed = hashedBase58("00"+keys.hash160Compressed)   
    keys.BTCaddressUncompressed = hashedBase58("00"+keys.hash160Uncompressed)   
    return keys

def hash160(x):
    """ Returns the ripemd160 hash of a sha256hashed hex number """
    return hashlib.new("ripemd160", hashlib.sha256(binascii.unhexlify(x)).digest()).hexdigest()
   
def hashedBase58(x):
    """ Returns a base58check encoded hexstring  """
    return b2a_hashed_base58(binascii.unhexlify(x.encode()))     

def printGeneratedKeys(keys): 
    """ Prints out the generated keys  """     
    print("\nPrivate Key (dec) = {}".format(keys._secret_exponent))   
    print("Private key (hex) = ", "{}".format(keys.privateKeyHex))    
    print("wif (compressed) = {}".format(keys.wifCompressed))
    print("wif (uncompressed) = {}".format(keys.wifUncompressed))
    print("Public Key (compressed) = {}".format(keys.publicKeyCompressed))
    print("Public Key (uncompressed) = {}".format(keys.publicKeyUncompressed))
    print("Hash 160 (compressed) = {}".format(keys.hash160Compressed))
    print("Hash 160 (uncompressed) = {}".format(keys.hash160Uncompressed))
    print("Bitcoin Address Compressed = {}".format(keys.BTCaddressCompressed) )
    print("Bitcoin Address Uncompressed  = {}".format(keys.BTCaddressUncompressed))

menu()
