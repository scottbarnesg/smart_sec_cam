from uuid import uuid4
import time

# Server Side Auth Functions
def serverAuth(username, supplied_hashed_password, correct_hashed_password):
    authenticated = False
    token = False
    revoke_time = 0
    if supplied_hashed_password == correct_hashed_password:
        authenticated = True
    if authenciated is True:
        (token, revoke_time) = createSession(username)
    return token, revoke_time

def createSession(username, timeout=7): # Timeout in days
    token = uuid4()
    t = time.time()
    revoke_time = t + timeout*24*(60**2)
    return token, revoke_time

def revokeSession(token, revoke_time):
    revoke = True
    t =  time.time()
    if t <= revoke_time:
        revoke = False
    return revoke

# Client Side Auth Functions
def clientAuth(username, password):
    return 0
