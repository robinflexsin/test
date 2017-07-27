from rest_framework import serializers

from api_login.models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'required': False},
        }

class UserRegistrationAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', 'email', 'phone', 'password',
            'office_phone', 'mobile_phone', 'nfa', 'firm_name', 'firm_nfa',
            'markets_traded', 'biography', 'profile_img', 'is_active',
            'address', 'address1', 'city', 'state', 'zip_code' )
        extra_kwargs = {
            'password': {'required': False},
            'markets_traded': {'required': True}
        }


class UserUpdateAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', 'email', 'phone', 'password',
            'address', 'address1', 'city', 'state', 'zip_code' )


class CustomerAddAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', 'email', 'phone', 'password',
            'address', 'address1', 'city', 'state', 'zip_code', 'profile_img' )
        extra_kwargs = {
            'password': {'required': False},
        }