from librespot.core import Session

username = ..
password = ..
try:
    SESSION = Session.Builder().user_pass("wrong", "creds").create();
except Exception as e:
    print(e)
try:
    SESSION = Session.Builder().user_pass(username, password).create();
except Exception as e:
    #Never throws exception
    print(e)
#Never reaches here
print('login complete.')
