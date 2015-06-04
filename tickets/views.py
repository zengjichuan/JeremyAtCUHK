# coding: utf-8
from email.mime.image import MIMEImage
from django.shortcuts import render
from django.shortcuts import render_to_response
from .forms import UserForm, InviteForm
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from tickets.models import *
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from EmailMultiRelated import *
from django.core.cache import cache
from MyException import UserAlreadyRegisteredError, TicketSoldOutError
from JeremyAtCUHK.settings import ROOT_SITE, BASE_DIR
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
            name, email, school = parse_input(form)
            try:
                email_to_send = insertdb(name, email, school)
            except Exception as e:
                msg = e.message
                requset.session['msg'] = msg
                return HttpResponseRedirect(reverse('sorry'))
            if email_to_send:
                email, email_qr, email_id = email_to_send
                qrfile_path = generate_qrcode(email_qr)
                insert_checklist(email_id, email_qr)
                send_email(name, email, qrfile_path)
                requset.session['email_id'] = email_id
                requset.session['name'] = name
            return HttpResponseRedirect(reverse('invite'))
    else:
        form = UserForm()
    return render_to_response('register.html', {'form': form}, RequestContext(requset))

# invite page
def invite(request):
    if request.method == 'POST':
        if request.session.has_key('email_id') and request.session.has_key('name'):
            email_id = request.session.get('email_id')
            name = request.session.get('name')
            del request.session['email_id']
            del request.session['name']
            form = InviteForm(request.POST)
            if form.is_valid():
                invitelst = parse_invite(form)
                if not invitelst:
                    return HttpResponseRedirect(ROOT_SITE)
                invite_send_list, error_email_list = insertdb_invite(email_id, invitelst)
                send_invite(name, invite_send_list)
                request.session['errors'] = error_email_list
                return HttpResponseRedirect(reverse('thanks'))
        else:
            return HttpResponseRedirect('/tickets/')
    elif request.session.has_key('email_id') and request.session.has_key('name'):
        form = InviteForm()
        return render_to_response('invite.html', {'form': form}, RequestContext(request))
    else:
        # in order to prevent visit directly
        return HttpResponseRedirect(reverse('register'))

# check request from mobile
def checkin(request):
    if request.method == 'GET':
        if 'email' in request.GET and request.GET['email']:
            checkinfo = request.GET['email']
            check_msg = checkdb(checkinfo)
            return HttpResponse(check_msg)

########################## Register Page ##############################
def parse_input(form):
    name = form.cleaned_data['name']
    email = form.cleaned_data['email'].lower()
    school = form.cleaned_data['school']
    return name, email, school

def insertdb(name, email, school):

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

    # check if there has enough tickets
    print 'tickets left', cache.get('tickets')
    if cache.get('tickets') <= 0:
        raise TicketSoldOutError('')
    cache.decr('tickets')
    return email, email_qr, email_id

########################## Invite Page ##############################
def parse_invite(form):
    invite = form.cleaned_data['invite']
    return [i.lower() for i in (invite and re.split(r'[ ;\n\t\r]+', invite) or [])]

def insertdb_invite(email_id, invitelst):
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
    return invite_send_list, error_email_list

def send_invite(name, invite_email_list):
    html = render_to_string('invitation.html', {'name': name})
    invite_msg = EmailMultiAlternatives('Invite: Jeremy At CUHK', 'Plain text version',
                              'zengjichuan@outlook.com', invite_email_list)
    invite_msg.attach_alternative(html, 'text/html')
    invite_msg.send()
    print 'Invite Emails have been sent!'

def generate_qrcode(url):
    code = pyqrcode.create(url)
    # the temp location of qr code is qrimg/
    file_path = os.path.join('qrimg', url + '.png')
    code.png(file_path, scale=8)
    return file_path

def insert_checklist(email_id, email_qr):
    CheckList.objects.create(emailid=email_id, emailqr=email_qr, checkin='No')

def send_email(name, email, qrfile_path):
    qrfile_base = os.path.basename(qrfile_path)
    email_msg = EmailMultiAlternatives('林書豪旋風2.0 – 成功的再思 Linsanity 2.0 – Redefining Success', 'Plain text version',
                                  'zengjichuan@outlook.com', [email])
    email_html = render_to_string('congratulation.html', {'qrpath': qrfile_base})
    email_msg.attach_alternative(email_html, 'text/html')
    email_msg.mixed_subtype = 'related'
    # add image
    fp = open(os.path.join(BASE_DIR, qrfile_path), 'rb')
    msg_image = MIMEImage(fp.read())
    fp.close()
    msg_image.add_header('Content-ID', '<{}>'.format(qrfile_base))
    email_msg.attach(msg_image)
    email_msg.send()
    print 'Confirm Email has been sent!'

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