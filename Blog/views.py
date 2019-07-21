from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.contrib.sites.shortcuts import get_current_site

from django.shortcuts import render, redirect

from django.core.files.storage import FileSystemStorage

from django.utils import timezone
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.template.loader import render_to_string

from django.core.paginator import Paginator
from django.core.mail import EmailMessage

from .forms import UploadForm

from .token import account_activation_token
from .forms import SignUpForm
from .models import Post


# Create your views here.


def index(request):
    post_list = Post.objects.order_by("createdAt").reverse()
    paginator = Paginator(post_list, 3)

    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    return render(request, 'index.html', {'posts' : paginator.page(page), 'form' : UploadForm()})


'''
    Profile related views
'''


@login_required
def profile(request):
    uri_id = request.build_absolute_uri().split('/')[5]

    try:
        count_posts = Post.objects.filter(createdBy=uri_id).count()
    except Post.DoesNotExist:
        count_posts = 0

    if int(request.user.id) == int(uri_id):
        return render(request, 'profile.html', {'count' : count_posts})
    else:
        return render(request, 'profile.html', {'count' : count_posts})


'''
    Search related views
'''


def search(request):
    value = request.GET.get('value').split(":")

    if value[0] == 'from':
        try:
            uid = User.objects.get(username = value[1]).id
        except User.DoesNotExist:
            return redirect('/')

        try:
            post_list = Post.objects.filter(createdBy=uid).order_by("createdAt").reverse()
        except Post.DoesNotExist:
            return redirect('/')
    elif value[0] == 'tag':
        print()


    paginator = Paginator(post_list, 3)

    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    return render(request, 'index.html', {'posts' : paginator.page(page)})


'''
    Post related views
'''


def post(request):
    post_id = request.build_absolute_uri().split('/')[5]

    filelist = []
    for s in FileSystemStorage().listdir('Blog/static/photos/')[1]:
        if s.split("_")[0] == post_id:
            filelist.append(s)

    return render(request, 'readmore.html', {'post' : Post.objects.get(id=post_id), 'files' : filelist})


def publish(request):
    post = Post(title=request.POST.get('title'), text = request.POST.get('text'), createdAt = timezone.now(), createdBy = User.objects.get(id = int(request.user.id)))
    post.save()

    i = 0
    print(request.FILES['myfiles'])
    for f in request.FILES.getlist('myfiles'):
        fs = FileSystemStorage()
        splitted = f.name.split(".")
        filename = fs.save('Blog/static/photos/' + str(post.id) + '_' + str(i) + '.' + splitted[len(splitted) - 1], f)
        i = i + 1

    return redirect('/')


'''
    Authentication related views
'''


def authentication(request):
    return render(request, 'login.html')


def login(request):
    auth_login(request, User.objects.get(username=request.POST.get('username')))
    return redirect('/')


def logout(request):
    auth_logout(request)
    return redirect('/')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Erasmus Experiences - Activate Your Account'
            message = render_to_string('email/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                subject, message, to=[to_email]
            )
            email.send()

            return redirect('/')
    else:
        form = SignUpForm()
    return redirect('/')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        auth_login(request, user)

        return redirect('/')
    else:
        return render(request, 'email/account_activation_invalid.html')


def account_activation_sent(request):
    return render(request, 'email/account_activation_sent.html')

