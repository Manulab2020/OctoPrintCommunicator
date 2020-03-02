import socket

'''
This module is currently only for testing purposes.
It does what it says on the tin: handles transfer of data over TCP
'''

def createServerSocket(hostname='127.0.0.1', port=80):
    '''
    Create a server socket from hostname/IP address & port number.
    If no arguments are passed, a local server socket will be established.
    '''
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((hostname, port))
    # Start listening
    serversocket.listen()
