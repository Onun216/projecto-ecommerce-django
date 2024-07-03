from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import copy

from . import models
from . import forms


class BaseProfile(View):
    template_name = 'user_profile/create.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.cart = copy.deepcopy(self.request.session.get('cart', {}))

        self.profile = None
        
        if self.request.user.is_authenticated:
            self.profile = models.Profile.objects.filter(
                user=self.request.user).first()

            self.context = {
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    user=self.request.user,
                    instance=self.request.user,),
                'profileform': forms.ProfileForm(
                    data=self.request.POST or None,
                    instance=self.profile)
            }
        else:
            self.context = {
                'userform': forms.UserForm(
                    data=self.request.POST or None),
                'profileform': forms.ProfileForm(
                    data=self.request.POST or None)
            }

        self.userform = self.context['userform']
        self.profileform = self.context['profileform']

        #
        if self.request.user.is_authenticated:
            self.template_name = 'user_profile/update.html'

        # Atributo de instância
        self.rendering = render(self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):
        return self.rendering


class Create(BaseProfile):
    def post(self, *args, **kwargs):
        # print(self.profile)
        if not self.userform.is_valid() or not self.profileform.is_valid():
            # print('FORMULÁRIO INVÁLIDO')
            messages.error(
                self.request, 
                'Existem erros no registo! Tente novamente.'
            )
            return self.rendering

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')

        # Utilizador com sessão iniciada
        if self.request.user.is_authenticated:
            user = get_object_or_404(User, username=self.request.user.username)

            # Se não quisermos que o utilizador altera o nome de utilizador basta comentar
            user.username = username

            if password:
                user.set_password(password)

            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Cria perfil para um utilizador com sessão já iniciada.
            if not self.profile:
                self.profileform.cleaned_data['user'] = user
                # print(**self.profileform.cleaned_data)
                profile = models.Profile(**self.profileform.cleaned_data)
                profile.save()
            else:
                profile = self.profileform.save(commit=False)
                profile.user = user
                profile.save()

        # Utilizador sem sessão iniciada (novo utilizador)
        else:
            user = self.userform.save(commit=False)
            user.set_password(password)
            user.save()

            profile = self.profileform.save(commit=False)
            profile.user = user
            profile.save()

        # Sessão do utilizador é iniciada novamente depois de alterar a password
        if password:
            auth_user = authenticate(self.request, username=user,
                                     password=password)
            if auth_user:
                login(self.request, user=user)

        # print('FORMULÁRIO VÁLIDO')
        self.request.session['cart'] = self.cart
        self.request.session.save()

        messages.success(
            self.request,
            'O registe foi efectuado com sucesso!'
        )
        #return redirect('user_profile:create')
        return redirect('product:cart')

        # return self.rendering


class Update(View):
    pass


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if not username or not password:
            messages.error(
                self.request,
                'O nome de utilizador ou a password estão incorretos!'
            )
            return redirect('user_profile:create')

        user = authenticate(self.request, username=username, password=password)

        if not user:
            messages.error(
                self.request,
                'O nome de utilizador ou a password estão incorretos!'
            )
            return redirect('user_profile:create')

        login(self.request, user=user)

        messages.success(
            self.request,
            'Bem-vindo!'
        )
        return redirect('product:cart')


class Logout(View):
    def get(self, *args, **kwargs):
        # Verificação da existência de uma carrinho serviria para economizar uma consulta na base de dados.
        cart = copy.deepcopy(self.request.session.get('cart'))

        logout(self.request)
        self.request.session['cart'] = cart
        self.request.session.save()
        return redirect('product:list')
