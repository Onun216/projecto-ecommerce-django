from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError


import re

from utils.validacpf import valida_cpf


class Profile(models.Model):
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField()
    cpf = models.CharField(max_length=11, help_text='')
    address = models.CharField(max_length=50)
    number = models.CharField(max_length=5)
    complement = models.CharField(max_length=30)
    ng_hood = models.CharField(max_length=30)
    cep = models.CharField(max_length=8)
    city = models.CharField(max_length=30)
    state = models.CharField(
        max_length=2,
        default='SP',
        choices=(
                ('AC', 'Acre'),
                ('AL', 'Alagoas'),
                ('AP', 'Amapá'),
                ('AM', 'Amazonas'),
                ('BA', 'Bahia'),
                ('CE', 'Ceará'),
                ('DF', 'Distrito Federal'),
                ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'),
                ('MA', 'Maranhão'),
                ('MT', 'Mato Grosso'),
                ('MS', 'Mato Grosso do Sul'),
                ('MG', 'Minas Gerais'),
                ('PA', 'Pará'),
                ('PB', 'Paraíba'),
                ('PR', 'Paraná'),
                ('PE', 'Pernambuco'),
                ('PI', 'Piauí'),
                ('RJ', 'Rio de Janeiro'),
                ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'),
                ('RO', 'Rondônia'),
                ('RR', 'Roraima'),
                ('SC', 'Santa Catarina'),
                ('SP', 'São Paulo'),
                ('SE', 'Sergipe'),
                ('TO', 'Tocantins'),
        )
    )

    def __str__(self):
        return f'{self.user}'

    def clean(self):
        error_messages = {}

        cpf_sent = self.cpf or None
        cpf_saved = None
        profile = Profile.objects.filter(cpf=cpf_sent).first()

        # Verificação do cpf. 
        # Não podemos ter dois cpfs iguais.
        if profile:
            cpf_saved = profile.cpf

            if cpf_saved is not None and self.pk != profile.pk:
                error_messages['cpf'] = 'CPF já existe.'


        if not valida_cpf(self.cpf):
            error_messages['cpf'] = 'Type in a valid CPF'

        # Verifica se há algum valor que não seja um número dentro do CEP
        if re.search(r'[^0-9]', self.cep) or len(self.cep) < 8:
            error_messages['cep'] = 'Invalid CEP'

        if error_messages:
            raise ValidationError(error_messages)
