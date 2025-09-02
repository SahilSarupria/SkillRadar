from django.contrib.auth.tokens import PasswordResetTokenGenerator

class ActivationTokenGenerator(PasswordResetTokenGenerator):
    pass

activation_token = ActivationTokenGenerator()
