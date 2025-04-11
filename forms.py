from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    admin_password = PasswordField('Senha do Administrador', validators=[DataRequired()])
    submit = SubmitField('Registrar')

class ClientForm(FlaskForm):
    full_name = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    japan_address = StringField('Endereço no Japão', validators=[Length(max=200)])
    japan_phone = StringField('Telefone no Japão', validators=[Length(max=15)])
    japan_id = StringField('ID Japonês', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Atualizar Cliente')

class AdminForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Criar Administrador')

class SaleForm(FlaskForm):
    client_id = SelectField('Cliente', validators=[DataRequired(message='Por favor, selecione um cliente')], coerce=int)
    product_id = SelectField('Produto', validators=[DataRequired(message='Por favor, selecione um produto')], coerce=int)
    quantity = IntegerField('Quantidade', validators=[DataRequired(message='Por favor, informe a quantidade'), NumberRange(min=1, message='A quantidade deve ser maior que zero')])
    discount_percentage = FloatField('Desconto (%)', validators=[NumberRange(min=0, max=100, message='O desconto deve estar entre 0% e 100%')], default=0)
    sale_date = DateField('Data da Venda', validators=[DataRequired(message='Por favor, informe a data da venda')])
    notes = StringField('Observações')
    
    # Campos de financiamento
    is_financed = BooleanField('Financiar')
    financing_years = SelectField('Anos de Financiamento',
                                choices=[(str(i), str(i)) for i in range(1, 11)],
                                validators=[],
                                coerce=int)
    interest_rate = FloatField('Taxa de Juros Anual (%)',
                              validators=[NumberRange(min=0, max=100)],
                              default=0)
    
    submit = SubmitField('Salvar')
    
    def validate(self, extra_validators=None):
        if not FlaskForm.validate(self, extra_validators=extra_validators):
            return False
        
        if self.is_financed.data:
            try:
                years = int(self.financing_years.data) if self.financing_years.data else 0
                if not years or years <= 0:
                    self.financing_years.errors = ['Por favor, selecione o período de financiamento']
                    return False
                if not self.interest_rate.data or self.interest_rate.data <= 0:
                    self.interest_rate.errors = ['A taxa de juros deve estar entre 0% e 100%']
                    return False
            except (ValueError, TypeError):
                self.financing_years.errors = ['Valor inválido para o período de financiamento']
                return False
        
        return True


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Redefinição de Senha')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Redefinir Senha')