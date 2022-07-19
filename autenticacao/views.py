from django.http import HttpResponse
from django.shortcuts import render
from .utils import password_is_valid, email_html
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import auth, messages
import os
from django.conf import settings
from .models import Ativacao
from hashlib import sha256
# Create your views here.
from django.contrib.messages import constants


def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/pacientes')
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro')
        try:
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=senha,
                                            is_active=False)
            user.save()
            
            token = sha256(f"{username}{email}".encode()).hexdigest()
            ativacao = Ativacao(token=token, user=user)
            ativacao.save()
            
            
            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/email/cadastro_confirmado.html')
            email_html(path_template, 'Cadastro confirmado', [email], username=username, link_ativacao=f"127.0.0.1:8000/auth/ativar_conta/{token}")
            messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado com sucesso')
            return redirect('/auth/login')
        except:
            return redirect('/auth/cadastro')
    
def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/pacientes')
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')
        
        usuario = auth.authenticate(username=username, password=senha)

        if not usuario:
            messages.add_message(request, constants.ERROR, 'Nome ou senha inválidos')
            return redirect('/auth/login')
        else:
            auth.login(request, usuario)
            return redirect('/pacientes/')
        
        
        
def sair(request):
    auth.logout(request)
    return redirect('/auth/login')


def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Esse token já foi usado')
        return redirect('/auth/login')
    
    user = User.objects.get(username=token.user.username)
    user.is_active = True 
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'A conta foi ativada')
    return redirect('/auth/login')
    
    
    