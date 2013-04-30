from wtforms import Form, TextField, validators, BooleanField
from flask import Flask, request, redirect, flash, render_template
import json
import requests
from jinja2 import Template
from IPython import embed

ADDR = 'uvalistserv.mailgun.org'
LISTADDR = 'sage@%s' % ADDR
KEY = 'key-3d1gtj048oxhghiwh4v2h9tvx-l3hew7'
URL = "https://api.mailgun.net/v2/%s" % ADDR
SECRET = "42"

import chooser
from models import session, EmailMessage

__HEXDIGEST__ = chooser.produce_hexdigest()
__HD_USED__ = False

class EditForm(Form):
    subject = TextField('subject', [validators.Length(2,)])
    text = TextField('body', [validators.Length(2,)])
    approved = BooleanField('approved',)

class SubForm(Form):
    email = TextField('Email Address', [validators.Email('must provide a valid email dingus')])

app = Flask(__name__, static_folder="./static", static_url_path="/static")
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
    global __HEXDIGEST__
    _json = json.dumps(form.to_dict())
    mess = EmailMessage(_json)
    mess.hexdigest = __HEXDIGEST__
    session.add(mess)
    session.commit()

@app.route("/mod-real-ones", methods=["GET", "POST"])
def mod():
    global __HEXDIGEST__
    if request.method == "GET":
        mess = session.query(EmailMessage).get(__HEXDIGEST__)
        if mess is None or mess.approved == True:
            flash('No new messages to edit')
            return render_template('edit.html')
        dct = json.loads(mess.everything)
        form = EditForm()
        form.subject.data = dct.get('subject')
        form.text.data = dct.get('body-plain')
        form.approved.data = mess.approved
        return render_template('edit.html', form=form) 
    else:
        form = EditForm(request.form)
        mess = session.query(EmailMessage).get(__HEXDIGEST__)
        if form.approved.data == True:
            send_message(form.data)
            mess.approved = True
            session.add(mess)
            session.commit()
            flash('message sent')
            return render_template('edit.html')
        flash("bad form")
        return "bad form"

def send_message(dct):
    hit_list = requests.post(URL + "/messages",
                auth=('api', KEY),
                data={
                 "to": LISTADDR,
                 "from": 'originalsen@uvalistserv.mailgun.org',
                 "text": dct.get('text'),
                 "subject": "[UVALIST] %s" % dct.get('subject'),
                 })
    print hit_list.json()
    
def hash_unused(_hash):
    global __HEXDIGEST__
    global __HD_USED__
    print _hash, __HD_USED__
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

def already_sent(form):
    resp = request.post(URL + "/messages",
                        auth=('api', KEY),
                        data={
                          "to": form.get('From'),
                          "from": our_email,
                          "subject": "Failed to deliver",
                          "text":"You already sent us an email for the day",
                          })

@app.route('/message', methods=["POST"])
def message():
    our_email = request.form.get('To') 
    _hash = chooser.produce_hexdigest()
    if our_email.find(_hash) > -1:
        if hash_unused(_hash):
            print "message_good"
            message_good(request.form)    
            return "good"
        else:
            print "hash was used"
            alread_sent()
            return "bad"
    else:
        print "the hashes did not match"
        return "message bad"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
