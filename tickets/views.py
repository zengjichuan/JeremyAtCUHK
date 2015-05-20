from django.shortcuts import render
from django.shortcuts import render_to_response
from .forms import UserForm
from django.http import HttpRequest, HttpResponseRedirect
from tickets.MyException import UserAlreadyRegisteredError
from tickets.models import *
from django.template import RequestContext
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from EmailMultiRelated import *
import pyqrcode
import random
import os

# Create your views here.

def name(request):
    return render_to_response('thanks.html')

def register(requset):
    if requset.method == 'POST':
        form = UserForm(requset.POST)
        if form.is_valid():
            try:
                email_to_send = parse_insertdb(form)
            except Exception as e:
                print e.message
                return HttpResponseRedirect('/tickets/sorry/')
            if email_to_send:
                email, email_en, invite_email, error_email = email_to_send
                # the temp location of qr code is qrimg/
                qrfile_path = generate_qrcode(email_en)
                send_email(email, invite_email, qrfile_path)
                requset.session['errors'] = error_email
            return HttpResponseRedirect('/tickets/thanks/')
    else:
        form = UserForm()
    return render_to_response('register.html', {'form': form}, RequestContext(requset))

def parse_insertdb(form):
    # parse input data
    name = form.cleaned_data['name']
    email = form.cleaned_data['email']
    school = form.cleaned_data['school']
    chris = True and form.cleaned_data['chris'] or 'None'
    invite = form.cleaned_data['invite']
    invitelst = invite and invite.split(';') or []

    # insert into dataset
    # check if exist in email list
    email_item = EmailList.objects.filter(email=email)
    if not email_item:
        # insert into email list
        email_id = EmailList.objects.create(email=email).id
    else:
        email_id = email_item[0].id
        # check if exist in user info
        if UserInfo.objects.filter(emailid=email_id):
            raise UserAlreadyRegisteredError('User already been registered!')

    # insert into user info
    UserInfo.objects.create(name=name, emailid=email_id, school=school, chris=chris)

    # generate security email address and insert into check list
    email_en = email + '_' + str(random.randint(10, 99))

    # insert into relation list

    invite_send_list = []
    error_email_list = []
    for iemail in invitelst:
        # check invite email format
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
    return email, email_en, invite_send_list, error_email_list

def generate_qrcode(url):
    code = pyqrcode.create(url)
    file_path = os.path.join('qrimg', url + '.png')
    code.png(file_path, scale=8)
    return file_path

def send_email(email, invite_email_list, qrfile_path):
    email_msg = EmailMultiRelated('Jeremy At CUHK', 'Plain text version',
                                  'zengjichuan@outlook.com', [email])
    email_html = '<html><body><p>This is a <strong>ticket</strong> message. ' \
                 '<a href="mailto:zengjichuan@outlook.com">Email</a> me back.</p>' \
                 '<img src="%s"></body></html>' % os.path.basename(qrfile_path)
    email_msg.attach_alternative(email_html, 'text/html')
    email_msg.attach_related_file(qrfile_path)
    email_msg.send()

    invite_msg  = EmailMultiRelated('Invite: Jeremy At CUHK', 'Plain text version',
                              'zengjichuan@outlook.com', invite_email_list)
    html = '<html><body><p>This is a <strong>invitation</strong> message.</p></body></html>'
    invite_msg.attach_alternative(html, 'text/html')
    invite_msg.send()
    print 'Emails have been sent!'

def thanks(request):
    if request.session.has_key('errors'):
        errors = request.session.get('errors')
        del request.session['errors']
    return render_to_response('thanks.html', locals())

def sorry(request):
    return render_to_response('sorry.html')