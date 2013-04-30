from datetime import date
import random
import hashlib

import requests

def produce_hexdigest():
    today = str(date.today())
    m = hashlib.sha512(today + "42")
    m = m.hexdigest()[:15].replace('@', '')
    return m

import app

def mail_winner(winner):
    name, dest = app.LISTADDR.split('@')
    addr = "%s+%s@%s" % (name, produce_hexdigest(), dest)
    message = u"""
    You have been randomly selected to send something to this listserv
    click <a href="mailto:{0}?subject=Read%20the%20rules!">here</a> to say what you want to the listserv!
    Make sure you change the subject!
    """.format(addr)
    print produce_hexdigest()
    resp = requests.post(app.URL + '/messages',
            auth=("api", app.KEY),
            data={"from": app.LISTADDR,
                "to": [winner],
                'subject': 'Its your turn',
                'html': message,
                'o:tag':'daily-winner',
                })
    return True


if __name__ == "__main__":
    mems = app.get_members()
    winner = random.choice(mems)
    print "mailing the winner: ", winner
    mail_winner(winner)
    
