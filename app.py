from wtforms import Form, TextField, validators
from flask import Flask, request, redirect, flash, render_template
import requests
from jinja2 import Template

import chooser

ADDR = 'uvalistserv.mailgun.org'
LISTADDR = 'sage@%s' % ADDR
KEY = 'key-3d1gtj048oxhghiwh4v2h9tvx-l3hew7'
URL = "https://api.mailgun.net/v2/%s" % ADDR

__HEXDIGEST__ = chooser.produce_hexdigest()
__HD_USED__

class SubForm(Form):
    email = TextField('Email Address', [validators.Email('must provide a valid email dingus')])

app = Flask(__name__)
app.secret_key = "asdasdhakshd232812389188!@#$%^&*("

def email_subbed(email_addr):
    resp = requests.get('https://api.mailgun.net/v2/lists/%s/members/%s' % (LISTADDR, email_addr),
                auth=('api', KEY),
                )
    dct = resp.json()
    if resp.status_code == 200:
        try:
            return dct['member']['subscribed']
        except KeyError:
            flash(str(dct))
            return False
    return False

def get_members():
    mem_json = requests.get('https://api.mailgun.net/v2/lists/%s/members' % LISTADDR,
                        auth=('api',KEY)).json()
    mem_lst = mem_json.get('items') 
    return map(lambda x: x['address'], mem_lst) 

@app.route('/')
def home():
    sub_form = SubForm()
    mem_json = requests.get('https://api.mailgun.net/v2/lists/%s/members' % LISTADDR,
                            auth=('api',KEY)).json()
    mem_lst = mem_json.get('items') 
    mem_lst = map(lambda x: (x['address'], x['subscribed']), mem_lst)
    return render_template('home.html', form=sub_form, lst=mem_lst)

@app.route('/subscribe', methods=['POST'])
def sub():
    sub_req = SubForm(request.form)
    if not sub_req.validate():
        flash('This is not a valid email address')
        return redirect('/')
    post = requests.post("https://api.mailgun.net/v2/lists/%s/members" % LISTADDR,
                auth=('api', KEY),
                data={'subscribed': True,
                      'address': sub_req.email.data}
                )
    if post.status_code == 200:
        flash('You were sucessfully subscribed')
    else:
        flash('You were not subcribed!, our mailserver sent us this error %s' % post.status_code)
    return redirect('/')
    
@app.route('/unsub', methods=['GET', 'POST'])
def unsub():
    unsub = SubForm(request.form or None)
    if request.method == "GET":
        return render_template('unsub.html', form=unsub)
    else:
        if unsub.validate():
            if email_subbed(unsub.email.data):
                post = requests.delete("https://api.mailgun.net/v2/lists/%s/members/%s" % (LISTADDR, unsub.email.data),
                        auth=('api', KEY),
                        )
                if post.status_code == 200:
                    flash('You sucessfully unsubscribed!')
                else:
                   ost
                   flash('List serv is broken!')
            else:
                flash('That email is already unsubscribed') 
        else:
            flash('The email you entered is bad')
        return redirect('/')

def message_good(form):
    hit_list = requests.post(URL + "/messages",
                auth=('api', KEY),
                data={
                 "to": LISTADDR,
                 "from": 'originalsen@uvalistserv.mailgun.org',
                 "text": "The problem" + form.get('body-plain'),
                 "subject": "[UVALIST] %s" % form.get('subject'),
                 })
    print hit_list.json()
    
def hash_unused(_hash):
    if _hash != __HEXDIGEST__:
        __HEXDIGEST__ = _hash
        __HD_USED__ = True
        return True
    else:
        if __HD_USED__:
            return False
        else:
            __HD_USED__ = True
            return True

@app.route('/message', methods=["POST"])
def message():
    our_email = request.form.get('To') 
    _hash = chooser.produce_hexdigest()
    if our_email.find(_hash) > -1 and hash_unused(_hash):
        print "message_good"
        message_good(request.form)    
        return "good"
    else:
        print "the hash did not match"
        return "message bad"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
