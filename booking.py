#!/usr/bin/env python26
#print 'Content-type: text/html;charset=utf-8\n'
#print 'Set-Cookie: session=252231467'
import sys
sys.stderr=sys.stdout
import os
import time
import cgi
import Cookie
import datetime
import random
import sqlite3#3
import hashlib
from pyh import *

def Header(notice=''):
    main = div(cl='center')
    main << img(src='img/PiSharpLogo.png') + br()
    if notice:
        main << div(notice['message'], cl=' notice %s' % notice['type']) + br()
    return main

def Footer(userclass=-1):
    main = span('Hosted by ')
    main << a('CERN', href='http://cern.ch/') + ' | '
    main << a('CERN Music Club', href='http://muzipod.free.fr/') + ' | '
    main << a('Contact', href='mailto:turlay@cern.ch') + ' | ' + 'Powered by ' * (userclass < 1)
    if userclass > 0 : main << a('Admin', href='?action=admin') + ' | Powered by '
    main << a('PyH', href='http://pyh.googlecode.com/')
    return br() + main

def Login(notice=''):
    main = Header(notice)
    loginbox =  main << div(id='loginbox', cl='rounded10')
    tablogin = loginbox << form(action='booking.py', method='POST') << table(cl='aligncenter', id='tablogin')
    tablogin << tr() << td("Username") + td(input(type='text', name='username', size=15))
    tablogin << tr() << td("Password") + td(input(type='password', name='password', size=15))
    tablogin << tr() << td() + td(span("Remember me")+ input(type='checkbox', name='remember'))
    loginbox.form << input(type='hidden', name='action', value='login')
    loginbox.form << input(type='submit', value='Login', cl='btn')
    main << br() + Footer()
    return main

def isMember(user, passw):
    passw = hashlib.sha1(passw).hexdigest()
    db = sqlite3.connect('db/CMCmembers.db')
    c = db.cursor()
    isM, userclass = False, -1
    c.execute('select * from CMCmembers where username = "%s" and password = "%s"' % (user, passw))
    rec = c.fetchone()
    if rec != None:
        userclass = int(rec[5])
        return True, userclass
    else: return False, userclass

def openSession(user):
    db = sqlite3.connect('db/CMCmembers.db')
    c = db.cursor()
    if query.getvalue('remember', False): expiration = datetime.datetime.now() + datetime.timedelta(weeks=2)
    else : expiration = datetime.datetime.now() + datetime.timedelta(minutes=20)
    session = random.randint(0, 1e9)
    cookie = Cookie.SimpleCookie()
    cookie['session'] = session
    cookie['username'] = user
    cookie['userclass'] = userclass
    cookie['username']['expires'] = expiration.strftime('%a, %d-%b-%Y %H:%M:%S CEST')
    #cookie['CMCsession']['domain'] = '.'
    #cookie['CMCsession']['path'] = '/'
    cookie['session']['expires'] = expiration.strftime('%a, %d-%b-%Y %H:%M:%S CEST')
    print cookie
    c.execute('update CMCmembers set session = %i where username = "%s"' % (session, user))
    db.commit()
    c.close()

def bookingPage(user, room='566', userclass=-1, notice=''):
    today = datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    yesterday = today - datetime.timedelta(days=1)
    db = sqlite3.connect('db/bookings.db',detect_types=sqlite3.PARSE_DECLTYPES)
    c = db.cursor()
    main = Header(notice=notice)
    summary = main << div(id='summary', cl='rounded10')        
    c.execute('select * from bookings where time > ? and username = ?', (yesterday, user,))
    result = c.fetchall()
    if len(result):
        summary << span('Your upcoming sessions', cl='title')
        list = summary << div(style='text-align:left;') << ul()
        for b in result:
            id, uname, broom, band, status, time = b
            if band != uname:
                list << li(cl='sumlist') << span('%s' % time.strftime('%a, %b %d'), cl='bold') + ' at ' + span('%s' % time.strftime('%H:%M'), cl='bold') + ' with ' + span('%s' % band, cl='bold') + ' in room ' + span('%i' % broom, cl='bold')
            else:
                list << li(cl='sumlist') <<  span('%s' % time.strftime('%a, %b %d'), cl='bold') + ' at ' + span('%s' % time.strftime('%H:%M'), cl='bold') + ' in room ' + span('%i' % broom, cl='bold')
    else: summary << span('You have no upcoming sessions', id='sumtitle')
    tabs = summary << div(cl='posrel')
    tabs << a('Change password', href='?action=passwd', id='passwd', cl='sumtab')
    tabs << a('Logout', href='?action=logout', id='logout', cl='sumtab')
    main << br()
    maindiv = main << div(cl='main', id='booking')
    styletab = {'566':(room=='566')*'this'+(room=='52')*'other',
                '52':(room=='52')*'this'+(room=='566')*'other'}
    tabs = maindiv << div(cl='posrel')
    tabs << a('Bdg. 52', href='?room=52', cl='whichroom %sroom' % styletab['52'], id='room52')
    tabs << a('Bdg. 566', href='?room=566', cl='whichroom %sroom' % styletab['566'], id='room566')
    c.execute('select * from bookings where time > ? and room = ?', (yesterday, room,))
    bookings = c.fetchall()
    c.close()
    tabschedule = maindiv << table(id='tabschedule', cl='aligncenter')
    trhead = tabschedule << tr()
    trhead << td() + td()
    month, s, n, nthisweek = '', 0, 0, -1
    slots = [[datetime.time(8), datetime.time(12)], [datetime.time(12), datetime.time(14)],
             [datetime.time(14), datetime.time(18)], [datetime.time(18), datetime.time(20, 30)], [datetime.time(20, 30), datetime.time(0)]]
    for sl in range(len(slots)): trhead << th('%s - %s' % (slots[sl][0].strftime('%Hh%M'), slots[sl][1].strftime('%Hh%M')), cl='t%i' % (s%2))
    #for j in range(8): trhead << th('%ih - %ih' % (j*2 + 8, j*2 + 10), cl='t%i' % (j%2))
    for i in range(30):
        tday = tabschedule << tr()
        if month != today.strftime('%B'):
            month = today.strftime('%B')
            tday << td(month, cl='center t%i' % (i%2))
        else:
            tday << td()
        tday << td(today.strftime('%A %d'), cl='right t%i' % (i%2))
        #tday << span(type(bookings[0][5]))
        if nthisweek == -1: nthisweek = len([b for b in bookings if b[5].strftime('%W') == today.strftime('%W') and b[1] == user])
        for j in range(len(slots)):
            ttime = today + datetime.timedelta(hours=j*2)
            book = [b for b in bookings if b[5] == ttime]
            n += 1
            if len(book):
                id, uname, dum, band, status = book[0][:5]
                if uname == user: style = 'yours%i' % status
                else : style = 'notyours%i' % status
                tdbk = tday << td(cl=style, id='cell%i' % n)
                if uname == user: tdbk.attributes['onclick'] = "showCancel('cell%i', '%i'); return false;" % (n, id)
                tdbk << div(band, cl='band')
                if uname != band: tdbk << div(uname, cl='det_user')
            else:
                if nthisweek < 2 : onclick = "showToolTip('cell%i', '%s'); return false;" % (n, ttime.strftime('%Y%m%d%H%M'))
                else : onclick = "showNoMore('cell%i'); return false;" % n
                tday << td(id='cell%i' % n, cl='center tl%s' % s, onclick=onclick)
        if today.strftime('%w') == '0':
            s = int(not s)
            nthisweek = -1
        today += datetime.timedelta(days=1)
    tooltip = maindiv << div(id='ToolTipDiv', cl='rounded tooltip')
    tooltip << span('Wanna book this slot?', id='bookthisslot') + br()
    bookform = tooltip << form(action='booking.py', method='POST', id='bookform')
    bookform << input(type='text', value=user, size=13, name='band')
    bookform << input(type='hidden', name='time', id='booktime')
    bookform << input(type='hidden', name='username', value=user)
    bookform << input(type='hidden', name='action', value='book')
    bookform << input(type='submit', value='Book!', cl='btn')
    tooltip << a('close', href='#', onclick="closeToolTip('ToolTipDiv'); return false;")
    cancel = maindiv << div(id='CancelDiv', cl='rounded tooltip')
    cancelform = cancel << form(action='booking.py', method='POST', id='cancelform')
    cancelform << input(type='hidden', name='id', id='cancelid')
    cancelform << input(type='hidden', name='username', value=user)
    cancelform << input(type='hidden', name='action', value='cancel')
    bookform << input(type='hidden', name='room', value=room)
    cancelform << input(type='submit', value='Cancel?', cl='btn') + br()
    cancel << a('close', href='#', onclick="closeToolTip('CancelDiv'); return false;")
    nomore = maindiv << div(id='NoMoreDiv', cl='rounded tooltip')
    nomore << span('Not more than 2 bookings per week, sorry!') + br()
    main << Footer(userclass)
    helpTip = main << div(id='helpBox', cl='rounded10')
    helpTip << div('Help', style='text-align:right;font-weight:bold;')
    helpTip << p('You can book a slot by clicking it and entering the name of your band.', id='help')
    helpTip << p('To cancel a booking just click it and cancel.', id='help')
    mailto = a('here', href='mailto:turlay@cern.ch')
    helpTip << p('If you encounter bugs or problems, please report them ', id='help') << mailto + '.'
    return main

def adminPage(user):
    db = sqlite3.connect('db/CMCmembers.db')
    c = db.cursor()
    c.execute('select class from CMCmembers where username = ?', (user,))
    userclass = c.fetchone()[0]
    c.close()
    main = Header()
    maindiv = main << div(cl='main', id='admin')
    tabs = maindiv << div(cl='posrel')
    tabs << a('Back to booking', href='?', cl='backtab')
    maindiv << div('Administration', cl='title', id='admintitle')
    if userclass < 1:
        maindiv << span('You are not authorized to see this page!', id='failedlogin')
        return main
    c = db.cursor()
    c.execute('select id, username, firstname, lastname, email, class from CMCmembers order by username')
    list = c.fetchall()
    c.close()
    tab = maindiv << table(id='tabschedule')
    thead = tab << tr()
    thead << th('Username', cl='t0') + th('First', cl='t1') + th('Last', cl='t0')
    thead << th('Email', cl='t1') + th('Class', cl='t0') + th('Actions', cl='t1', colspan=2)
    className = ['Ringo', 'George', 'Paul']
    addForm = tab << tr() << form(method='POST', action='booking.py')
    addForm << input(type='hidden', name='action', value='adduser')
    addForm << td() << input(type='text', name='addusername', size=10)
    addForm << td() << input(type='text', name='addfirst', size=10)
    addForm << td() << input(type='text', name='addlast', size=10)
    addForm << td() << input(type='text', name='addemail', size=10)
    selcl = addForm << td() << select(name='addclass')
    selcl << option('Ringo', value='0', selected='selected')
    selcl << option('George', value='1')
    addForm << td(colspan=2) << input(type='submit', value='Add user')
    i = 1
    for u in list:
        id, username, first, last, email, clas = u
        ttr = tab << tr()
        ttr << td(username, cl='t%i' % (i%2)) + td(first, cl='t0') + td(last, cl='t0')
        ttr << td(email, cl='t0') + td(className[clas], cl='t0')
        #ttr << td(username, cl='action') + td(email, cl='action') + td(className[clas], cl='action')
        #ttr << td(cl='action') << img(src='img/edit.gif', alt='Edit this user')
        delform = ttr << td(cl='action') << form(method='POST', action='booking.py')
        delform << input(type='hidden', name='action', value='edituser')
        if userclass >= clas:
            delform << input(type='image', src='img/edit.gif', alt='Edit this user', cl='img')
        delform = ttr << td(cl='action') << form(method='POST', action='booking.py')
        delform << input(type='hidden', name='action', value='remuser')
        delform << input(type='hidden', name='id', value='%i' % id)
        if userclass > clas:
            delform << input(type='image', src='img/delete.jpg', alt='Remove this user', cl='img')
        i += 1
    maindiv << br() + b('User classes')
    legend = maindiv << table(cl='aligncenter')
    legend << tr() << td(b('Ringo'), cl='right') + td('Basic users. They can only book and cancel slots.', cl='left')
    legend << tr() << td(b('George'), cl='right') + td('Admins. They can also add or remove users.', cl='left')
    legend << tr() << td(b('Paul'), cl='right') + td('Master of the universe. Well, of PiSharp at least.', cl='left')
    legend << tr() << td(b('John'), cl='right') + td('Who the hell is John?', cl='left')
    main << Footer(userclass)
    return main

def addBooking(user='', band='', room='', time=None):
    db = sqlite3.connect('db/bookings.db',detect_types=sqlite3.PARSE_DECLTYPES)
    c = db.cursor()
    c.execute('insert into bookings values (NULL, ?, ?, ?, ?, ?)', (user, int(room), band, 0, time))
    db.commit()
    c.close()

def cancelBooking(id):
    db = sqlite3.connect('db/bookings.db',detect_types=sqlite3.PARSE_DECLTYPES)
    c = db.cursor()
    c.execute('delete from bookings where id = ?', (id,))
    db.commit()
    c.close()

def addUser(q):
    adduser = q.getvalue('addusername')
    db = sqlite3.connect('db/CMCmembers.db')
    c = db.cursor()
    c.execute('select id from CMCmembers where username = ?', (adduser,))
    if len(c.fetchall()) == 0:
        addfirst = q.getvalue('addfirst')
        addlast = q.getvalue('addlast')
        addemail = q.getvalue('addemail')
        addclass = int(q.getvalue('addclass'))
        password = hashlib.sha1('IAmTheWalrus').hexdigest()
        if addfirst and addlast and addemail:
            c.execute('insert into CMCmembers (username, firstname, lastname, email, class, password, session) values (?, ?, ?, ?, ?, ?, ?)',
                      (adduser, addfirst, addlast, addemail, addclass, password, 0))
            db.commit()
    c.close()

def remUser(q):
    id = q.getvalue('id')
    if id:
        id = int(id)
        db = sqlite3.connect('db/CMCmembers.db')
        c = db.cursor()
        c.execute('delete from CMCmembers where id = ?', (id,))
        db.commit()
        c.close()

def changePasswdPage(user, userclass=-1, notice=''):
    main = Header(notice=notice)
    maindiv = main << div(cl='main', id='admin')
    tabs = maindiv << div(cl='posrel')
    tabs << a('Back to booking', href='?', cl='backtab')
    maindiv << div('Change password', cl='title', id='admintitle')
    chgform = maindiv << form(action='booking.py', method='POST')
    formtab = chgform << table()
    formtab << tr() << th('Old password') + th('New password')
    inputLine = formtab << tr()
    inputLine << td() << input(type='password', name='oldPass', size=10)
    inputLine << td() << input(type='password', name='newPass', size=10)
    submitLine = formtab << tr()
    submitLine << td() << input(type='hidden', name='action', value='change') + input(type='hidden', name='username', value=user)
    submitLine << td(input(type='submit', value='Change', cl='btn'), style='text-align:right;')
    main << Footer(userclass)
    return main

def changePasswd(user, old, new):
    isM, userclass = isMember(user, old)
    if not isM : return False, {'type':'fail', 'message':'Error : Wrong password!'}
    if len(new) < 4 : return False, {'type':'fail', 'message':'Error : New password is too short!'}
    newHash = hashlib.sha1(new).hexdigest()
    db = sqlite3.connect('db/CMCmembers.db')
    c = db.cursor()
    c.execute('update CMCmembers set password = "%s" where username = "%s"' % (newHash, user))
    db.commit()
    c.close()
    return True, {'type':'success','message':'Password successfully changed'}

query = cgi.FieldStorage()
page = PyH('PiSharp : CERN Music Club booking system')
page.addCSS('CMCstyle.css')
page.addJS('js/tooltip.js')
#page << h1('PiSharp', cl='center')
hasValidCookie = False
user, userclass = '', -1
action = query.getvalue('action', '')
if action == 'logout':
    cookie = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    cookie['session']['expires'] = yesterday.strftime('%a, %d-%b-%Y %H:%M:%S CEST')
    print cookie
    hasValidCookie = False
else:
    try:
        cookie = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
        if 'username' in cookie and 'session' in cookie:
            userclass = int(cookie['userclass'].value)
            conn = sqlite3.connect('db/CMCmembers.db')
            c = conn.cursor()
            c.execute('select * from CMCmembers where username = "%s" and session = %i' \
                      % (cookie['username'].value, int(cookie['session'].value)))
            if c.fetchone() != None:
                user = cookie['username'].value
                hasValidCookie = True
                conn.close()
    except (Cookie.CookieError, KeyError): hasValidCookie = False

if hasValidCookie:
    room = query.getvalue('room', '566')
    if not user: user = query.getvalue('username','')
    if action == 'book':
        time = datetime.datetime.strptime(query.getvalue('time', ''), '%Y%m%d%H%M')
        addBooking(user=user, band=query.getvalue('band', ''), room=room, time=time)
        page << bookingPage(user, room, userclass, notice={'type':'success', 'message':"Thanks for booking, let's rock!"})
    elif action == 'cancel':
        cancelBooking(id=int(query.getvalue('id','')))
        page << bookingPage(user, room, userclass, notice={'type':'success', 'message':"Thanks for canceling"})
    elif action in ['admin', 'adduser', 'remuser']:
        if action == 'adduser': addUser(query)
        if action == 'remuser': remUser(query)
        page << adminPage(user)
    elif action == 'passwd' :
        page << changePasswdPage(user, userclass)
    elif action == 'change' :
        oldPass = query.getvalue('oldPass', '')
        newPass = query.getvalue('newPass', '')
        ok, notice = changePasswd(user, oldPass, newPass)
        if ok:
            page << bookingPage(user, room, userclass, notice=notice)
        else: page << changePasswdPage(user, userclass, notice=notice)
    else: page << bookingPage(user, room, userclass)
else:
    if action == 'login' :
        username = query.getvalue('username', '')
        password = query.getvalue('password', '')
        isM, userclass = isMember(username, password)
        if isM:
            openSession(username)
            page << bookingPage(username, userclass=userclass, notice={'type':'success', 'message':'Welcome %s!' % username})
        else:
            page << Login(notice={'type':'fail', 'message':'Error : Wrong credentials!'})
    else:
        page << Login()

print 'Content-type: text/html\n\n'
page.printOut()

#DATABASE PLAYIN ROUND
#db = sqlite3.connect('db/CMCmembers.db')
#c = db.cursor()
#c.execute('update CMCmembers set lastname = "Turlay" where username = "turlay"')
#c.execute('alter table CMCmembers add column lastname')
#db.commit()
#c.close()
