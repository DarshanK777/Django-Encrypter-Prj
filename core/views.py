from django.shortcuts import render, redirect
from django.contrib.auth import(
    authenticate,
    get_user_model,
    login,
    logout
)
from .models import Profile
import os
import os.path as path
from .forms import UserLoginForm, UserRegistrationForm, DocumentForm
import pyAesCrypt
import glob
from wsgiref.util import FileWrapper
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
temp_folder = os.path.join(BASE_DIR, 'media\\documents\\')
perm_folder = os.path.join(BASE_DIR, "media\\stored\\" )

def home(request):
    context = {
        'user': request.user
    }
    return render(request, "home.html", context)

def login_view(request):
    next = request.GET.get('next')
    form  = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username = username, password = password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect('/')
    
    context = {
        'form': form
    }
    return render(request, "login.html", context)


def register_view(request):
    next = request.GET.get('next')
    form  = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        s_key = form.cleaned_data.get('secret_key')
        password  = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        profile = Profile.objects.get(user = user)
        profile.secret_key = s_key
        profile.save()
        new_user = authenticate(username = user.username, password = password)
        login(request, new_user)
        if next:
            return redirect(next)
        return redirect('/')
    
    context = {
        'form': form
    }
    return render(request, "signup.html", context)


def logout_view(request):
    logout(request)
    return redirect('/')

def crypt_file(user, filename, sec_key):
    # just read to understand
    global BASE_DIR, perm_folder, temp_folder
    perm_dir = perm_folder + user    

    if not os.path.isdir(perm_dir):
        os.mkdir(perm_dir)

    temp_file = os.path.join(temp_folder, filename)
    filename_mod = filename + ".aes"
    perm_file = os.path.join(perm_dir, filename_mod)
    # till here basic stuff

    bufferSize = 64 * 1024
    password = str(sec_key)

    # encrypt
    pyAesCrypt.encryptFile(temp_file, perm_file, password, bufferSize)
    os.remove(temp_file)

def list_files(user):
    global perm_folder
    perm_dir = perm_folder + user
    x = os.listdir(perm_dir)
    return x

def model_form_upload(request):  
    if request.method == 'POST':
        print("inside this")
        global BASE_DIR, perm_folder, temp_folder
        perm_dir = perm_folder + request.user.username
        form = DocumentForm(request.POST, request.FILES)
        print("inside 2")
        if form.is_valid():
            print("inside 3")
            print(form.cleaned_data.get('document'))
            filename = ((form.cleaned_data.get('document')).name).replace(" ","_")
            form.save()
            user = request.user.username
            user_profile = Profile.objects.get(user = request.user)
            sec_key = user_profile.secret_key
            crypt_file(user, filename, sec_key)
            list_files(user)
            return redirect('download/')
    else:
        form = DocumentForm()
    return render(request, 'home.html', {
        'form': form
    })


def dcrypt(sec_key, user, filename):
    # just read to understand
    global BASE_DIR, perm_folder, temp_folder
    perm_dir = perm_folder + user    
    temp_file = os.path.join(temp_folder, filename[:-4])
    filename_mod = filename 
    perm_file = os.path.join(perm_dir, filename_mod)
    # till here basic stuff

    bufferSize = 64 * 1024
    password = str(sec_key)

    pyAesCrypt.decryptFile(perm_file, temp_file, password, bufferSize)



def try_download(user, filename, sec_key):
    global temp_folder
    dcrypt(sec_key, user, filename)
    filename = filename[:-4]
    file_path = os.path.join(temp_folder, filename)
    file_name = file_path
    wrapper = FileWrapper(open(path.abspath(file_name), 'rb'))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(file_name)
    response['Content-Length'] = os.path.getsize(file_name)
    return response


def download_files(request):
    global temp_folder
    if request.method == "POST":
        toDownload = request.POST.get("toDownload")
        user = request.user.username
        user_profile = Profile.objects.get(user = request.user)
        sec_key = user_profile.secret_key
        res = try_download(user, toDownload, sec_key)
        os.remove(os.path.join(temp_folder, toDownload[:-4]))
        return res
    else:
        user = request.user.username
        files = list_files(user)
        print("this is files", files)
        context = {
            "file_list" : files
        }
        return render(request, "download.html", context)

