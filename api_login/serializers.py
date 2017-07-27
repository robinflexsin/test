from rest_framework import serializers

from api_login.models import (
        CQGOnBoardingDetails,
        OnboardFail,
        User
    )

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'required': False},
            'username': {'required': False},
        }


class ForgotPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', )
        extra_kwargs = {
            'email': {'required': True},
        }


class UserRegistrationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', 'email', 'phone', 'password',
            'address', 'address1', 'city', 'state', 'zip_code'
            )
        extra_kwargs = {
            'email': {'required': False},
        }


class CqgOnboaringRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CQGOnBoardingDetails
        fields = (
            'user', 'account_id', 'balance', 'currency',
            'total_value', 'ote', 'upl', 'mvo',
            'cash_excess', 'collateral', 'initial_margin',
            'cqg_web_api_username'
            )


class FailedOnBoardingSerializer(serializers.ModelSerializer):

    class Meta:
        model = OnboardFail
        fields = (
            'email',
        )

class UserProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ( 'username', 'first_name', 'last_name', 'phone', 'office_phone',
            'mobile_phone', 'nfa', 'firm_name', 'firm_nfa', 'markets_traded',
            'biography', 'address', 'address1', 'city', 'state', 'zip_code'
            )
        extra_kwargs = {
            'phone': {'required': False},
            'username': {'required': False},
            'office_phone': {'required': False},
            'mobile_phone': {'required': False},
            'nfa': {'required': False},
            'firm_name': {'required': False},
            'firm_nfa': {'required': False},
            'markets_traded': {'required': False},
            'biography': {'required': False},
            'address': {'required': False},
            'address1': {'required': False},
            'city': {'required': False},
            'state': {'required': False},
            'zip_code': {'required': False},
        }


class ChangePasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('password', )


class UpdateProfilePicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('profile_img',)