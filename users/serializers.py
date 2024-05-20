from shered.utility import check_email_or_phone
from .models import User, UserConfirmation,VIA_PHONE, VIA_EMAIL,CODE_VERIFIED, NEW, PHONE_STEP, DONE
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework import exceptions


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)


    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status'
        )
        extra_kwargs = {
            'auth_type':{'read_only':True, 'required':True},
            'auth_status':{'read_only':True, 'required':True}
        }

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data


    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get("email_phone_number")).lower()
        input_type = check_email_or_phone(user_input)
        print("user_input", user_input)
        print("input_type", input_type)

        return data



