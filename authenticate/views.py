from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib import messages 
from .forms import SignUpForm, EditProfileForm, CustomPasswordChangeForm
import logging
from django.http import HttpRequest

logger = logging.getLogger('custom_logger')

def home(request):
	return render(request, 'authenticate/home.html', {})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Логирование успешного входа
            ip_address = get_client_ip(request)
            logger.info(f"User {username} login in system. IP: {ip_address}")
            messages.success(request, ('Вы вошли!'))
            return redirect('home')
        else:
            # Логирование неудачной попытки входа
            ip_address = get_client_ip(request)
            logger.warning(f"Неудачная попытка входа для пользователя {username}. IP: {ip_address}")
            messages.error(request, ('Ошибка при входе в Систему - Пожалуйста, повторите попытку...'))
            return redirect('login')
    else:
        return render(request, 'authenticate/login.html', {})

# Функция для получения IP-адреса пользователя
def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def logout_user(request):
    ip_address = get_client_ip(request)
    logger.info(f"User {request.user.username} logout from system. IP: {ip_address}")
    logout(request)
    messages.success(request, ('Вы Вышли Из Системы...'))
    return redirect('home')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            ip_address = get_client_ip(request)
            logger.info(f"New user {username} register. IP: {ip_address}")
            messages.success(request, ('Ваша учётная запись создана.'))
            return redirect('home')
    else:
        form = SignUpForm()
    
    context = {'form': form}
    return render(request, 'authenticate/register.html', context)



def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            ip_address = get_client_ip(request)
            logger.info(f"User {request.user.username} change profile. IP: {ip_address}")
            messages.success(request, ('Вы Отредактировали Свой Профиль...'))
            return redirect('home')
    else:
        form = EditProfileForm(instance=request.user)
    
    context = {'form': form}
    return render(request, 'authenticate/edit_profile.html', context)



def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            ip_address = get_client_ip(request)
            logger.info(f"User {request.user.username} change password. IP: {ip_address}")
            messages.success(request, ('Вы Отредактировали Свой Пароль...'))
            return redirect('home')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'authenticate/change_password.html', context)
