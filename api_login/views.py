from django.shortcuts import render

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.conf import settings

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token

from uuid import uuid4
from random import randint

from lib.expresspegion import EmailSendPegion
from api_login.models import (
		CQGOnBoardingDetails,
		OnboardFail,
		User
	)
from api_login.serializers import (
		UserSerializer,
		ForgotPasswordSerializer,
		UserRegistrationUpdateSerializer,
		CqgOnboaringRegistrationSerializer,
		FailedOnBoardingSerializer,
		UserProfileUpdateSerializer,
		ChangePasswordSerializer,
		UpdateProfilePicSerializer
	)

from lib.api import (
		response_message,
		user_dict,
		EmailSend,
		user_name,
		password_generator
	)

# from cqgApi.logon import logon


class LoginView(APIView):

	def responseDict(self, user, token):
		dic = {
				'message': 'success',
				'user' : user_dict(user),
				'token': token[0].key
			}
		return dic

	def post(self, request, format=None):
		if 'email' not in request.data or 'password' not in request.data:
			return Response(response_message("parameter missing"), status=400)
		user = authenticate(email=request.data['email'], password=request.data['password'])
		if user:
			token = Token.objects.get_or_create(user=user)
			return Response(self.responseDict(user, token), status=200)
		else:
			try:
				userSet = User.objects.get(email=request.data['email'])
				if userSet.is_active:
					return Response(response_message("Incorrect Username or password"), status=401)
				else:
					return Response(response_message("User inactive or deleted."), status=401)
			except:
				return Response(response_message("Incorrect Username or password"), status=401)


class RegistrationView(APIView):

	def post(self, request, format=None):
		# tool id=1 for Customer.
		group = Group.objects.get(id=1)
		try:
			request.data._mutable = True
		except Exception as e:
			pass
		# ============= logic for split name with space make first name last name ==========#
		if 'name' in request.data:
			nameList = str(request.data['name']).split(' ', 1)
			if len(nameList) > 1:
				request.data['first_name'] = nameList[0]
				request.data['last_name'] = nameList[-1]
			else:
				request.data['first_name'] = nameList[0]
		# ================ end split name logic =================================#
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			if 'password' in serializer.validated_data:
				serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
			lastInsertId = User.objects.latest('id')
			serializer.validated_data['username'] = str(randint(10000, 99999))+str(lastInsertId.id)
			user = serializer.save()
			user.groups.add(group)
			# ========================== Email Settings ======================== #
			subject = "MIMIC trader Account Verification Email"
			link = settings.MAIN_URL+'api/activation/'+str(user.id)+'/'
			merge_fields = {
				'name': str(request.data['name']),
				'link': link
			}
			template_id = 549316
			try:
				EmailSendPegion(str(request.data['email']), merge_fields, subject, template_id)
			except Exception as e:
				print (e)
			return Response(response_message("success"), status=200)
		else:
			return Response(serializer.errors, status=400)


class ForgotPasswordView(APIView):

	def post(self, request, format=None):
		if 'email' not in request.data:
			return Response(response_message("parameter missing"), status=400)
		emailExist = User.objects.filter(email=request.data['email'])
		if not emailExist:
			return Response(response_message("Email does not exist"), status=401)
		# ========================== Email Settings ======================== #
		subject = "MIMIC trader Reset Password"
		link = settings.WEBSITE_LINK+'#!/reset-password?email='+str(request.data['email'])
		template_id = 549430
		merge_fields = {
			'name': user_name(emailExist[0]),
			'link': link
		}
		try:
			EmailSendPegion(str(request.data['email']), merge_fields, subject, template_id)
		except Exception as e:
			print (e)
		return Response(response_message("success"), status=200)


class ResetPasswordView(APIView):

	def post(self, request, format=None):
		if 'email' not in request.data or 'password' not in request.data:
			return Response(response_message("parameter missing"), status=400)
		emailExist = User.objects.filter(email=request.data['email'])
		if not emailExist:
			return Response(response_message("Email does not exist"), status=401)
		password = make_password(str(request.data['password']))
		emailExist.update(password=password)
		return Response(response_message("success"), status=200)


class ActivationUserView(APIView):

    def get(self, request, user_id, format=None):

        querySetKey = User.objects.filter(id=user_id)

        if querySetKey:
            querySetKey.update(is_verified = True)
            full_address = settings.REDIRECT_LINK+str(user_id)
            return HttpResponseRedirect(full_address)
        else:
            full_address = settings.REDIRECT_LINK+'0'
            return HttpResponseRedirect(full_address)


class UserDetailsView(APIView):

	def post(self, request, format=None):
		if 'id' not in request.data:
			return Response(response_message("parameter missing"), status=400)
		userSet = User.objects.filter(id=request.data['id'])
		if userSet:
			return Response({ "data": user_dict(userSet[0])}, status=200)
		return Response(response_message("User does't exist!"), status=404)


class UpdateUserDetailsView(APIView):

	def post(self, request, format=None):
		if 'id' not in request.data['user']:
			return Response(response_message("parameter missing"), status=400)
		try:
			CQGOnBoardingDetails.objects.get(cqg_web_api_username=str(request.data['user']['cqg_id']
				))
			return Response(response_message("That username is already exist!"), status=404)
		except:
			pass
		userInstance = User.objects.get(id=request.data['user']['id'])
		serializer = UserRegistrationUpdateSerializer(userInstance, data=request.data['user'])
		if serializer.is_valid():
			serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
			serializer.save()
			User.objects.filter(id=userInstance.id).update(is_active=True)
			for dataSet in request.data['brokerageMetadataData']:
				dataSet['user'] = userInstance.id
				dataSet['cqg_web_api_username'] = request.data['user']['cqg_id']
				serializerCqg = CqgOnboaringRegistrationSerializer(data=dataSet)
				if serializerCqg.is_valid():
					serializerCqg.save()
				else:
					return Response(serializerCqg.errors, status=400)
			# ========================== Email Settings ======================== #
			subject = "OnBoarding Welcome Email"
			link = settings.WEBSITE_LINK+'#!/login'
			template_id = 531018
			merge_fields = {
				'name': user_name(userInstance),
				'username': userInstance.username,
				'link': link
			}
			try:
				EmailSendPegion(userInstance.email, merge_fields, subject, template_id)
			except Exception as e:
				print (e)
			return Response(response_message("success"), status=200)
		else:
			return Response(serializer.errors, status=400)


class CQGRegistrationView(APIView):

	def post(self, request, format=None):
		try:
			CQGOnBoardingDetails.objects.get(cqg_web_api_username=str(request.data['cqg_web_api_username']))
			return Response(response_message("That username is already exist!"), status=404)
		except:
			pass
		serializer = CqgOnboaringRegistrationSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success"), status=200)
		else:
			return Response(serializer.errors, status=400)


class FailedOnBoardingView(APIView):

	def post(self, request,  format=None):
		try:
			userSet = User.objects.get(email=str(request.data['email']))
		except Exception as e:
			return Response(response_message("User does not exist!"), status=404)

		serializer = FailedOnBoardingSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			userSet.delete()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors, status=400)



class UserProfileView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, format=None):
		try:
			userInstance = User.objects.get(id=request.data['id'])
		except:
			return Response(response_message("User Not Found!"), status=404)

		requiredDict = { 
				"result": user_dict(userInstance)
			}
		return Response(requiredDict, status=200)


class UserUpdateView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, user_id, format=None):
		try:
			userInstance = User.objects.get(id=user_id)
		except:
			return Response(response_message("User Not Found!"), status=404)

		serializer = UserProfileUpdateSerializer(userInstance, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors, status=400)


class ChangePasswordView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, user_id, format=None):
		try:
			userInstance = User.objects.get(id=user_id)
		except:
			return Response(response_message("User Not Found!"), status=404)

		request.data._mutable = True
		correctPassword = check_password(request.data.pop('old_password')[0], userInstance.password)
		if not correctPassword:
			return Response(response_message("Invalid current password!"), status=404)

		serializer = ChangePasswordSerializer(userInstance, data=request.data)
		if serializer.is_valid():
			serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors, status=400)


class UpdateProfilePicView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, user_id, format=None):
		try:
			userInstance = User.objects.get(id=user_id)
		except:
			return Response(response_message("User Not Found!"), status=404)

		serializer = UpdateProfilePicSerializer(userInstance, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors, status=400)


class RemoveProfilePicView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, user_id, format=None):
		try:
			userInstance = User.objects.get(id=user_id)
		except:
			return Response(response_message("User Not Found!"), status=404)

		User.objects.filter(id=userInstance.id).update(profile_img='default/default.jpeg')

		result = {
			'profile_img' : settings.MAIN_URL+'images/default/default.jpeg'
		}
		return Response(result, status=200)