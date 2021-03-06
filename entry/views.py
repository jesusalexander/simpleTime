from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django import forms
from django.contrib import auth  
from django.contrib import messages 
from django.contrib.auth.models import User
from models import Article
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import Article,UploadFile
from django import forms
from django.core.context_processors import csrf
import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from uploadToQiniu import uploadToQiniu
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def entry(request):
    articleList = Article.objects.order_by('-id')
    localURL = request.get_host()
    return render_to_response('index.html',{'articleList':articleList,'localURL':localURL},context_instance = RequestContext(request))

def article(request,articleID):
    article = Article.objects.get(id=articleID)

    return render_to_response('article.html',{'article':article},context_instance = RequestContext(request))

def person(request):
    if request.method == 'GET':
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/entry/login')
        else :
            articleForm = forms.ArticleFormPerson()

            return render_to_response('person.html',{'state':"GET",'articleForm':articleForm},context_instance = RequestContext(request))
            
    else :
        form = forms.ArticleFormPerson(request.POST)
        if form.is_valid:
            title = request.POST.get('title')
            content_markdown = request.POST.get('content_markdown')
            if title == '' :
                title = content_markdown[:10]
            
            content_markup = content_markdown
            
            articleModel = Article(title=title,content_markdown=content_markdown,content_markup=content_markup)
            articleModel.save()
        return HttpResponseRedirect('/entry/')

def articleList(request):
    if request.method == 'GET':
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/entry/login')
        else :
            articleList = Article.objects.order_by('-id')
            return render_to_response('articleList.html',{'articleList':articleList},context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect('/entry/')




def login(request):
    if request.method == 'GET':
        form = forms.LoginForm()
        return render_to_response('login.html',{'form':form},context_instance=RequestContext(request))
    else :
        form = forms.LoginForm(request.POST)
        if form.is_valid :
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(username=username,password=password)
            if user is not None and user.is_active :
                auth.login(request,user)
                request.session['username'] =  username 
                return HttpResponseRedirect('/entry/write') 
            else :
                return render_to_response('person.html',{'login_state':'0'},context_instance=RequestContext(request))
        return HttpResponseRedirect('/')


def logoutView(request):
    if request.user.is_authenticated():
        logout(request)
        return HttpResponseRedirect('/entry/')
    else :
        return HttpResponseRedirect('/entry/')
    
    # Redirect to a success page.

@csrf_exempt
def upload(request):
    uploadState = ''
    if request.method == 'POST':
        fileForm = forms.UploadFileForm(request.POST,request.FILES)
        if fileForm.is_valid():
            #u = UploadFile()
            #u.filename = 'title'
            #u.fileContent = request.FILES['fileContent']
            #u.filename = request.POST['filename']
            fileContent = request.FILES['fileContent']
            filename = request.POST['filename']
            ret = uploadToQiniu(fileContent,filename)
            
            #u.save()
            # handle_uploaded_file(request.FILES['fileContent'])
            uploadState = 'ok'
            return HttpResponse(ret['key'])
        else :
            uploadState = 'error'
            return render_to_response('upload.html',{'uploadState':uploadState,'fileForm':fileForm},context_instance=RequestContext(request))

    else :
        fileForm = forms.UploadFileForm()

    return render_to_response('upload.html',{'uploadState':uploadState,'fileForm':fileForm},context_instance=RequestContext(request))

def handle_uploaded_file(f):
    upload_path = 'upload/files/' + f.name

    with open(upload_path,'wb+') as info :
        print f.filename
        for chunk in f.chunks():
            info.write(chunk)
    return f


