from datetime import date
import random
import hashlib

import requests

import app

SECRET = "42"

def produce_hexdigest():
    today = str(date.today())
    m = hashlib.sha512(today + SECRET)
    return m.hexdigest()[:15]

def mail_winner(winner):
    message = """
    You have been randomly selected to win a free car!
    reply to this email address with what you want to say to the listserv 
    """ 
    name, dest = app.LISTADDR.split('@')
    addr = "%s+%s@%s" % (name, produce_hexdigest(), dest)
    print produce_hexdigest()
    resp = requests.post(app.URL + '/messages',
            auth=("api", app.KEY),
            data={"from": addr,
                "to": [winner],
                'subject': 'Its your turn',
                'text': message,
                'o:tag':'daily-winner',
                })
    return True

if __name__ == "__main__":
    mems = app.get_members()
    winner = random.choice(mems)
    print "mailing the winner: ", winner
    mail_winner(winner)
    
