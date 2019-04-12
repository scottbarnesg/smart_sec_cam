from uuid import uuid4
import hashlib
import time

# Server Side Auth Functions
def serverAuth(username, supplied_password, correct_hashed_password):
    authenticated = False
    token = False
    revoke_time = 0
    supplied_hashed_password = hashlib.sha256(supplied_password)
    if supplied_hashed_password.hexdigest() == correct_hashed_password:
        print('Authenticating user')
        authenticated = True
    if authenticated:
        print('Creating session')
        (token, revoke_time) = createSession(username)
    return token, revoke_time, authenticated

def createSession(username, timeout=7): # Timeout in days
    token = uuid4()
    t = time.time()
    revoke_time = t + timeout*24*(60**2)
    return token.hex, revoke_time

def revokeSession(token, revoke_time):
    revoke = True
    t =  time.time()
    if t <= revoke_time:
        revoke = False
    return revoke
