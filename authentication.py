from uuid import uuid4
import hashlib
import time

try:
    from auth.authorized import authorized_users
except:
    print 'Failed to import authorized_users api. You must implement this yourself'
    print 'Authentication can be disabled in the server command-line interface'
    raise ImportError('Failed to import authorized_users api')

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
    revoke_time = t + timeout #*24*(60**2)
    return token.hex, revoke_time

def revokeSession(token, revoke_time):
    revoke = True
    t =  time.time()
    if t <= revoke_time:
        revoke = False
    return revoke


class Authorized:
    def __init__(self):
        self.authenticated_users = []
        self.tokens = []
        self.timeouts = []

    def new_login(self, username, token, timeout):
        self.authenticated_users.append(username)
        self.tokens.append(token)
        self.timeouts.append(timeout)

    def revoke(self, token):
        try:
            index = self.tokens.index(token)
        except:
            return False
        if time.time() >= self.timeouts[index]:
            del self.authenticated_users[index]
            del self.tokens[index]
            del self.timeouts[index]
            return True
        return False


    def get_password(self, username):
        exists, password = authorized_users(username)
        if not exists:
            return False, 0
        hashed_password = hashlib.sha256(password)
        return True, hashed_password.hexdigest()

    def verify_token(self, username, token):
        try:
            index = self.tokens.index(token) # check token to allow multiple user sessions
        except:
            return False
        if self.authenticated_users[index] == username:
            return True
        return False
