from django import forms
from django.contrib.auth.models import User
from . import models


class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = '__all__'
        exclude = ('user',)


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Password',
        help_text=''
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Confirmar password'
    )

    # Permite saber quem está a enviar o formulário
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password',
                  'password2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_error_msgs = {}

        user_data = cleaned.get('username')
        passaword_data = cleaned.get('password')
        passaword2_data = cleaned.get('password2')
        email_data = cleaned.get('email')

        user_db = User.objects.filter(username=user_data).first()
        email_db = User.objects.filter(email=email_data).first()

        # Mensagens de erro
        error_msg_user_exists = 'Utilizador já existe!'
        error_msg_email_exists = 'Email já existe!'
        error_msg_password_required = 'A password é obrigatória!'
        error_msg_password_match = 'As duas passwords não são iguais!'
        error_msg_password_length = 'A password deve ter pelo menos 8 caracteres!'

        # print(data)
        # Utilizadores com sessão iniciada: Com navegação anónima não é impresso no terminal.
        # Utilizadores com sessão iniciada: Actualização
        if self.user:
            # print("Utilizador com sessão iniciada")
            if user_db:
                if user_data != user_db.username:
                    validation_error_msgs['username'] = error_msg_user_exists

            if email_db:
                if email_data != email_db.email:
                    validation_error_msgs['email'] = error_msg_email_exists

            if passaword_data:
                if passaword_data != passaword2_data:
                    validation_error_msgs['password'] = error_msg_password_match
                    validation_error_msgs['password2'] = error_msg_password_match
                if len(passaword_data) < 8:
                    validation_error_msgs['password'] = error_msg_password_length

        # Utilizadores sem sessão iniciada: Registo
        else:
            if user_db:
                validation_error_msgs['username'] = error_msg_user_exists

            if email_db:
                validation_error_msgs['email'] = error_msg_email_exists

            if not passaword_data:
                validation_error_msgs['password'] = error_msg_password_required

            if not passaword2_data:
                validation_error_msgs['password2'] = error_msg_password_required

            if passaword_data != passaword2_data:
                validation_error_msgs['password'] = error_msg_password_match
                validation_error_msgs['password2'] = error_msg_password_match
            if len(passaword_data) < 8:
                validation_error_msgs['password'] = error_msg_password_length

        if validation_error_msgs:
            raise (forms.ValidationError(
                validation_error_msgs,
            )
            )
