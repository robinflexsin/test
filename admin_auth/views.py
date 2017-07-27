from django.shortcuts import render

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.db import connection
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token


from datetime import datetime, timedelta
from api_login.models import (
		User,
		MarketSector
	)

from lib.api import (
		response_message,
		user_dict,
		TraderUserListing,
		PaginationSet,
		user_name
	)

from admin_auth.serializers import (
		UserRegistrationAdminSerializer,
		CustomerAddAdminSerializer,
		
	)

from lib.messages import AllMessages

class LoginView(APIView):

	def responseDict(self, user, token):
		dic = {
				'message': 'success',
				'user' : user_dict(user),
				'token': token[0].key
			}
		return dic

	def post(self, request, format=None):
		if 'username' not in request.data or 'password' not in request.data:
			return Response(response_message("parameter missing"), status=400)
		user = User.objects.filter(username=request.data['username'])
		passwordString = user[0].password if user else None
		checkPassword = check_password(request.data['password'], passwordString)
		if user and checkPassword:
			if not user.filter(is_superuser=1):
				return Response(response_message("You are not authorize"), status=403)		
			token = Token.objects.get_or_create(user=user[0])
			return Response(self.responseDict(user[0], token), status=200)
		return Response(response_message("Incorrect Username or password"), status=401)


class UserListingView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def sortingField(self, number, order):
		if order == 'asc':
			dic = {1: 'first_name', 2: 'last_name', 3: 'email', 4: 'groups__name',
				5: '-is_active', 6: 'date_joined'}
		else:
			dic = {1: '-first_name', 2: '-last_name', 3: '-email', 4: '-groups__name',
				5: 'is_active', 6: '-date_joined'}
		return dic[number]

	def changeIds(self, ids):
		return '('+','.join(ids)+')'

	def updateStatus(self, isActive, ids):
		if type(eval(ids)) == type(1):
			query = "UPDATE `auth_user` SET is_active = %s WHERE id in (%s)"
		else:
			query = "UPDATE `auth_user` SET is_active = %s WHERE id in %s"
		try:
			with connection.cursor() as cursor:
				cursor.execute(query, [isActive, eval(ids)])
		except Exception as e:
			pass

	def post(self, request, user_type, format=None):
		if 'customActionType' in request.data and 'customActionName' in request.data:
			ids = self.changeIds(dict(request.data)['id[]'])
			if str(request.data['customActionName']).lower() == 'active':
				self.updateStatus(1, ids)
			if str(request.data['customActionName']).lower() == 'inactive':
				self.updateStatus(0, ids)
		userSet = User.objects.filter(groups__id=user_type)
		# ======================= all filters ======================= #
		if 'first_name' in request.data and request.data['first_name']:
			userSet = userSet.filter(first_name__icontains=request.data['first_name'])
		if 'last_name' in request.data and request.data['last_name']:
			userSet = userSet.filter(last_name__icontains=request.data['last_name'])
		if 'email' in request.data and request.data['email']:
			userSet = userSet.filter(email__icontains=request.data['email'])
		if 'user_type' in request.data and request.data['user_type']:
			userSet = userSet.filter(groups__name__icontains=request.data['user_type'])
		if 'status' in request.data and request.data['status']:
			if str(request.data['status']).lower() == 'active':
				userSet = userSet.filter(is_active=1)
			elif str(request.data['status']).lower() == 'inactive':
				userSet = userSet.filter(is_active=0)
		if 'date_joined_from' in request.data and request.data['date_joined_from']:
			dateJoinedFrom = datetime.strptime(request.data['date_joined_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
			dateJoinedTo = (datetime.strptime(request.data['date_joined_to'], '%d/%m/%Y') + timedelta(days=1)).strftime('%Y-%m-%d')
			userSet = userSet.filter(date_joined__gte=dateJoinedFrom, date_joined__lte=dateJoinedTo)
		# ===================== end all filters ===================== #
		# ===================== Start Sorting all =================== #
		if int(request.data['order[0][column]']) == 0:
			userSet = userSet.order_by('-date_joined')
		else:
			fieldValue = self.sortingField(int(request.data['order[0][column]']), str(request.data['order[0][dir]']))
			userSet = userSet.order_by(fieldValue)
		# ===================== End Sorting all ====================== #
		totalUsers = userSet.count()
		# Pagination method call from lib/api.py to make pagination in api's.
		querySet = PaginationSet(userSet, request.data['length'], request.data['start'])
		userList = []
		for user in querySet:
			userList.append(
				TraderUserListing(user)
			)
		requiredDict = {
				'data': userList,
				'draw': request.data['draw'],
				'recordsTotal': totalUsers,
				'recordsFiltered': totalUsers
				}
		return Response(requiredDict, status=200)


class AddUserView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, format=None):
		# we use id=2 for trader user group.
		try:
			request.data._mutable = True
		except Exception as e:
			pass
		if 'user_type' not in request.data:
			return Response(response_message("parameter missing"), status=400)
		request.data['password'] = make_password('123456')
		request.data['is_active'] = True
		group = Group.objects.get(id=int(request.data['user_type']))
		serializer = UserRegistrationAdminSerializer(data=request.data)
		if serializer.is_valid():
			# if 'password' in serializer.validated_data:
			# 	serializer.validated_data['password'] = make_password('123456')
			user = serializer.save()
			user.groups.add(group)
			return Response(response_message("success"), status=200)
		else:
			return Response(serializer.errors, status=400)


class EditUserView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, user_id, format=None):
		try:
			userInstance = User.objects.get(id=user_id)
		except Exception as e:
			return Response(response_message("User Not Found!"), status=404)

		serializer = UserRegistrationAdminSerializer(userInstance, data=request.data)
		if serializer.is_valid():
			if 'password' in serializer.validated_data:
				serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
			user = serializer.save()
			# user.groups.add(group)
			return Response(response_message("success"), status=200)
		else:
			return Response(serializer.errors, status=400)


class UserDetailsView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, user_id, format=None):
		try:
			userInstance = User.objects.get(id=user_id)
		except Exception as e:
			return Response(response_message("User Not Found!"), status=404)

		requiredDict = {
				'user' : user_dict(userInstance),
				}
		return Response(requiredDict, status=200)


class MarketsTradedDataView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, format=None):
		
		querySet = MarketSector.objects.all()

		dataLi = []
		for data in querySet:
			dataLi.append({
				'id': data.id,
				'text': data.sector_name
			})
		content = {
			'result': dataLi
		}
		return Response(content, status=200)


class AddCustomerView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, format=None):
		try:
			request.data._mutable = True
		except Exception as e:
			pass
		if 'user_type' not in request.data:
			return Response(response_message("parameter missing"), status=400)
		request.data['password'] = make_password('123456')
		request.data['is_active'] = True
		group = Group.objects.get(id=int(request.data['user_type']))
		serializer = CustomerAddAdminSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()
			user.groups.add(group)
			return Response(response_message("success"), status=200)
		else:
			return Response(serializer.errors, status=400)


class EditCustomerView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, user_id, format=None):
		try:
			userInstance = User.objects.get(id=user_id)
		except Exception as e:
			return Response(response_message("User Not Found!"), status=404)

		serializer = CustomerAddAdminSerializer(userInstance, data=request.data)
		if serializer.is_valid():
			if 'password' in serializer.validated_data:
				serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
			user = serializer.save()
			return Response(response_message("success"), status=200)
		else:
			return Response(serializer.errors, status=400)


class ActiveTraderListing(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, format=None):
		traderSet = User.objects.filter(groups__id=2, is_active=True)

		traderList = []
		for trader in traderSet:
			traderList.append({
				'id': trader.id,
				'name': user_name(trader)
				})
		context = {
			'result': traderList
		}
		return Response(context, status=200)