from django.shortcuts import render
from django.shortcuts import render_to_response
from .forms import UserForm
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from tickets.MyException import UserAlreadyRegisteredError
from tickets.models import *
from django.template import RequestContext
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from EmailMultiRelated import *
from django.core.cache import cache
from MyException import UserAlreadyRegisteredError, TicketSoldOutError
import pyqrcode
import random
import os
import re

# Create your views here.

# Register page
def register(requset):
    if requset.method == 'POST':
        form = UserForm(requset.POST)
        if form.is_valid():
            name, email, school, invitelst = parse_input(form)
            try:
                email_to_send = parse_insertdb(name, email, school, invitelst)
            except Exception as e:
                msg = e.message
                requset.session['msg'] = msg
                return HttpResponseRedirect('/tickets/sorry/')
            if email_to_send:
                email, email_qr, email_id, invite_email, error_email = email_to_send
                qrfile_path = generate_qrcode(email_qr)
                insert_checklist(email_id, email_qr)
                send_email(name, email, invite_email, qrfile_path)
                requset.session['errors'] = error_email
            return HttpResponseRedirect('/tickets/thanks/')
    else:
        form = UserForm()
    return render_to_response('register.html', {'form': form}, RequestContext(requset))

# check request from mobile
def checkin(request):
    if request.method == 'GET':
        if 'email' in request.GET and request.GET['email']:
            checkinfo = request.GET['email']
            check_msg = checkdb(checkinfo)
            return HttpResponse(check_msg)

##############################################################
def parse_input(form):
    name = form.cleaned_data['name']
    email = form.cleaned_data['email'].lower()
    school = form.cleaned_data['school']
    invite = form.cleaned_data['invite']
    invitelst = [i.lower() for i in (invite and re.split(r'[ ;\n\t\r]+', invite) or [])]
    return name, email, school, invitelst

def parse_insertdb(name, email, school, invitelst):

    # insert into database
    # check if exist in email list
    email_item = EmailList.objects.filter(email=email)
    if not email_item:
        # insert into email list
        email_id = EmailList.objects.create(email=email).id
    else:
        email_id = email_item[0].id
        # check if exist in user info
        if UserInfo.objects.filter(emailid=email_id):
            raise UserAlreadyRegisteredError('')

    # insert into user info
    UserInfo.objects.create(name=name, emailid=email_id, school=school)

    # generate security email address and insert into check list
    email_qr = email + '_' + str(random.randint(10, 99))

    # insert into relation list

    invite_send_list = []
    error_email_list = []
    for iemail in invitelst:
        # check invite email format
        if iemail.strip():
            try:
                validate_email(iemail)
                email_item = EmailList.objects.filter(email=iemail)
                if not email_item:
                    email_invite = EmailList.objects.create(email=iemail)
                else:
                    email_invite = email_item[0]
                Relation.objects.create(fromid=email_id, toid=email_invite.id)
                invite_send_list.append(iemail)
            except ValidationError:
                error_email_list.append(iemail)
                print iemail, 'format error'
    # check if there has enough tickets
    print 'tickets left', cache.get('tickets')
    if cache.get('tickets') <= 0:
        raise TicketSoldOutError('')
    cache.decr('tickets')
    return email, email_qr, email_id, invite_send_list, error_email_list

def generate_qrcode(url):
    code = pyqrcode.create(url)
    # the temp location of qr code is qrimg/
    file_path = os.path.join('qrimg', url + '.png')
    code.png(file_path, scale=8)
    return file_path

def insert_checklist(email_id, email_qr):
    CheckList.objects.create(emailid=email_id, emailqr=email_qr, checkin='No')

def send_email(name, email, invite_email_list, qrfile_path):
    email_msg = EmailMultiRelated('Jeremy At CUHK', 'Plain text version',
                                  'zengjichuan@outlook.com', [email])
    email_html = '<html><body><p>This is a <strong>ticket</strong> message. ' \
                 'For any problem, <a href="mailto:zengjichuan@outlook.com">Email</a> me back.</p>' \
                 '<img src="%s"></body></html>' % os.path.basename(qrfile_path)
    email_msg.attach_alternative(email_html, 'text/html')
    email_msg.attach_related_file(qrfile_path)
    email_msg.send()

    invite_msg = EmailMultiRelated('Invite: Jeremy At CUHK', 'Plain text version',
                              'zengjichuan@outlook.com', invite_email_list)
    html = '<html><body><p>This is a <strong>invitation</strong> message from your friend %s.' \
           'Please enter this <a href="http://183.62.156.108:8001/tickets/">link</a> to get ticket.</p>' \
           '</body></html>'% name
    invite_msg.attach_alternative(html, 'text/html')
    invite_msg.send()
    print 'Emails have been sent!'

def checkdb(info):
    check = CheckList.objects.filter(emailqr=info)
    if check:
        if check[0].checkin == 'No':
            check.update(checkin='Yes')
            return 'Welcome!'
        else:
            return 'Already checked!'
    else:
        return "No register!"

def thanks(request):
    if request.session.has_key('errors'):
        errors = request.session.get('errors')
        del request.session['errors']
    return render_to_response('thanks.html', locals())

def sorry(request):
    if request.session.has_key('msg'):
        msg = request.session.get('msg')
        del request.session['msg']
    return render_to_response('sorry.html', locals())