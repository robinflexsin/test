from django.shortcuts import render
from django.db.models import Count
from django.db import connection
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from datetime import datetime, timedelta

from api_login.models import (
		User
	)

from strategies.models import (
		SubSectorAssignment,
		MarketSubSector,
		MarketSector,
		Instruments,
		Strategy,
		Contracts,
		Spreads,
		Month,
		Legs
	)

from strategies.serializers import (
		StrategySerializer,
		SpreadsAddSerializer,
		ContactsAddSerializer,
		MarketSectorAddSerializer,
		MarketSubSectorAddSerializer,
		SubSectorAssignmentSerializer,
		InstrumentSerializer
	)

from lib.api import (
		response_message,
		user_dict,
		user_name,
		PaginationSet,
		strategyListing,
		strategy_view,
		filter_name,
		sectorListing,
		subSectorListing,
		sector_view,
		sub_sector_view,
		contract_view,
		contractListing,
		spread_view,
		spreadListing,
		traderContractListing,
		instrument_view,
		instrumentListing
	)

class AddStrategyView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		if 'user_id' not in request.data:
			return Response(response_message("parameter missing"), status=400)
		try:
			userInstance = User.objects.get(id=request.data['user_id'])
		except Exception as e:
			return Response(response_message("User Not Found!"), status=404)
		try:
			request.data._mutable = True
		except Exception as e:
			pass
		request.data['user'] = userInstance.id
		serializer = StrategySerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("success"), status=200)
		else:
			return Response(serializer.errors, status=400)


class StrategyListView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def sortingField(self, number, order):
		if order == 'asc':
			dic = {1: 'user__first_name', 2: 'title', 3: 'product_category', 4: 'product_type',
				5: 'strategy_type', 6: 'status__name', 7: 'created_date'}
		else:
			dic = {1: '-user__first_name', 2: '-title', 3: '-product_category', 4: '-product_type',
				5: '-strategy_type', 6: '-status__name', 7: '-created_date'}
		return dic[number]

	def changeIds(self, ids):
		return '('+','.join(ids)+')'

	def updateStatus(self, isActive, ids):
		if type(eval(ids)) == type(1):
			query = "UPDATE `strategies` SET status_id = %s WHERE id in (%s)"
		else:
			query = "UPDATE `strategies` SET status_id = %s WHERE id in %s"
		try:
			with connection.cursor() as cursor:
				cursor.execute(query, [isActive, eval(ids)])
		except Exception as e:
			pass

	def post(self, request, format=None):
		if 'customActionType' in request.data and 'customActionName' in request.data:
			ids = self.changeIds(dict(request.data)['id[]'])
			if str(request.data['customActionName']).lower() == 'approve':
				self.updateStatus(2, ids)
			if str(request.data['customActionName']).lower() == 'reject':
				self.updateStatus(3, ids)
		strategySet = Strategy.objects.all()

		if 'name' in request.data and request.data['name']:
			strategySet = filter_name(strategySet, str(request.data['name']))
		if 'title' in request.data and request.data['title']:
			strategySet = strategySet.filter(title__icontains=request.data['title'])
		if 'product_category' in request.data and request.data['product_category']:
			strategySet = strategySet.filter(product_category__icontains=request.data['product_category'])
		if 'product_type' in request.data and request.data['product_type']:
			strategySet = strategySet.filter(product_type__icontains=request.data['product_type'])
		if 'strategy_type' in request.data and request.data['strategy_type']:
			strategySet = strategySet.filter(strategy_type__icontains=request.data['strategy_type'])
		if 'status' in request.data and request.data['status']:
			if str(request.data['status']).lower() == 'pending':
				strategySet = strategySet.filter(status=1)
			elif str(request.data['status']).lower() == 'approved':
				strategySet = strategySet.filter(status=2)
			elif str(request.data['status']).lower() == 'rejected':
				strategySet = strategySet.filter(status=3)
		if 'date_joined_from' in request.data and request.data['date_joined_from']:
			dateJoinedFrom = datetime.strptime(request.data['date_joined_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
			dateJoinedTo = (datetime.strptime(request.data['date_joined_to'], '%d/%m/%Y') + timedelta(days=1)).strftime('%Y-%m-%d')
			strategySet = strategySet.filter(created_date__gte=dateJoinedFrom, created_date__lte=dateJoinedTo)

		# ===================== Start Sorting all =================== #
		if int(request.data['order[0][column]']) == 0:
			strategySet = strategySet.order_by('-created_date')
		else:
			fieldValue = self.sortingField(int(request.data['order[0][column]']), str(request.data['order[0][dir]']))
			strategySet = strategySet.order_by(fieldValue)
		# ===================== End Sorting all ====================== #

		totalStrategy = strategySet.count()
		querySet = PaginationSet(strategySet, request.data['length'], request.data['start'])
		strategyList = []
		for strategy in querySet:
			strategyList.append(
				strategyListing(strategy)
			)
		requiredDict = {
				'data': strategyList,
				'draw': request.data['draw'],
				'recordsTotal': totalStrategy,
				'recordsFiltered': totalStrategy
				}
		print (requiredDict)
		return Response(requiredDict, status=200)


class StrategyDetailView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )


	def post(self, request, strategy_id, format=None):
		try:
			strategyInstance = Strategy.objects.get(id=strategy_id)
		except Exception as e:
			return Response(response_message("Strategy Not Found!"), status=404)
		legSet = Legs.objects.filter(strategy=strategyInstance)
		strategyDict = strategy_view(legSet, strategyInstance)
		content = {
			'result': strategyDict
		}
		return Response(content, status=200)


class StrategyListingCustomerView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )


	def post(self, request, format=None):
		strategyInstance = Strategy.objects.filter(status=2)
		strategyDataSet = []
		for strategy in strategyInstance:
			legSet = Legs.objects.filter(strategy__id=strategy.id)
			strategyDict = strategy_view(legSet, strategy)
			strategyDataSet.append(strategyDict)
		content = {
			'result': strategyDataSet
		}
		return Response(content, status=200)


class SectorAddView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):

		serializer = MarketSectorAddSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors,  status=200)


class SectorListingView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def sortingField(self, number, order):
		if order == 'asc':
			dic = {1: 'sector_name', 2: 'sector_description', 3: 'sector_exchange_name', 4: 'sector_exchange_abbrev',
				5: 'status', 6: 'created_date'}
		else:
			dic = {1: '-sector_name', 2: '-sector_description', 3: '-sector_exchange_name', 4: '-sector_exchange_abbrev',
				5: 'status', 6: '-created_date'}
		return dic[number]

	def changeIds(self, ids):
		return '('+','.join(ids)+')'

	def updateStatus(self, isActive, ids):
		if type(eval(ids)) == type(1):
			query = "UPDATE `market_sector` SET status = %s WHERE id in (%s)"
		else:
			query = "UPDATE `market_sector` SET status = %s WHERE id in %s"
		try:
			with connection.cursor() as cursor:
				cursor.execute(query, [isActive, eval(ids)])
		except Exception as e:
			pass

	def post(self, request, format=None):

		if 'customActionType' in request.data and 'customActionName' in request.data:
			ids = self.changeIds(dict(request.data)['id[]'])
			if str(request.data['customActionName']).lower() == 'inactive':
				self.updateStatus(0, ids)
			if str(request.data['customActionName']).lower() == 'active':
				self.updateStatus(1, ids)
		sectorSet = MarketSector.objects.all()

		if 'sector_name' in request.data and request.data['sector_name']:
			sectorSet = sectorSet.filter(sector_name__icontains=request.data['sector_name'])
		if 'sector_description' in request.data and request.data['sector_description']:
			sectorSet = sectorSet.filter(sector_description__icontains=request.data['sector_description'])
		if 'sector_exchange_name' in request.data and request.data['sector_exchange_name']:
			sectorSet = sectorSet.filter(sector_exchange_name__icontains=request.data['sector_exchange_name'])
		if 'sector_exchange_abbrev' in request.data and request.data['sector_exchange_abbrev']:
			sectorSet = sectorSet.filter(sector_exchange_abbrev__icontains=request.data['sector_exchange_abbrev'])
		if 'status' in request.data and request.data['status']:
			if str(request.data['status']).lower() == 'active':
				sectorSet = sectorSet.filter(status=1)
			elif str(request.data['status']).lower() == 'inactive':
				sectorSet = sectorSet.filter(status=0)
		if 'date_joined_from' in request.data and request.data['date_joined_from']:
			dateJoinedFrom = datetime.strptime(request.data['date_joined_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
			dateJoinedTo = (datetime.strptime(request.data['date_joined_to'], '%d/%m/%Y') + timedelta(days=1)).strftime('%Y-%m-%d')
			sectorSet = sectorSet.filter(created_date__gte=dateJoinedFrom, created_date__lte=dateJoinedTo)

		# ===================== Start Sorting all =================== #
		if int(request.data['order[0][column]']) == 0:
			sectorSet = sectorSet.order_by('-created_date')
		else:
			fieldValue = self.sortingField(int(request.data['order[0][column]']), str(request.data['order[0][dir]']))
			sectorSet = sectorSet.order_by(fieldValue)
		# ===================== End Sorting all ====================== #
		totalSector = sectorSet.count()
		querySet = PaginationSet(sectorSet, request.data['length'], request.data['start'])
		sectorList = []
		for sector in querySet:
			sectorList.append(
				sectorListing(sector)
			)
		requiredDict = {
				'data': sectorList,
				'draw': request.data['draw'],
				'recordsTotal': totalSector,
				'recordsFiltered': totalSector
				}
		return Response(requiredDict, status=200)


class SectorDetailsView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, sector_id, format=None):
		try:
			sectorInstance = MarketSector.objects.get(id=sector_id)
		except Exception as e:
			return Response(response_message("Market Sector Not Found!"), status=404)

		requiredDict = {
				'result' : sector_view(sectorInstance),
				}
		return Response(requiredDict, status=200)


class SectorEditView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, sector_id, format=None):
		try:
			sectorInstance = MarketSector.objects.get(id=sector_id)
		except Exception as e:
			return Response(response_message("Market Sector Not Found!"), status=404)

		serializer = MarketSectorAddSerializer(sectorInstance, data=request.data)
		if serializer.is_valid():
			serializer.save()
			requiredDict = {
				'result' : serializer.data,
				}
			return Response(requiredDict, status=200)
		else:
			return Response(serializer.errors,  status=200)


class DropdownSectorListView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):

		sectorSet = MarketSector.objects.filter(status=True)

		sectorSet = sectorSet.order_by('-created_date')

		sectorList = []
		for sector in sectorSet:
			sectorList.append({
				'id': sector.id,
				'name': sector.sector_name
			})
		requiredDict = {
				'result': sectorList,
				}
		return Response(requiredDict, status=200)



class SubSectorAddView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):

		serializer = MarketSubSectorAddSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors, status=200)


class SubSectorEditView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, sub_sector_id, format=None):
		try:
			subSectorInstance = MarketSubSector.objects.get(id=sub_sector_id)
		except Exception as e:
			return Response(response_message("Market Sub Sector Not Found!"), status=404)

		serializer = MarketSubSectorAddSerializer(subSectorInstance, data=request.data)
		if serializer.is_valid():
			serializer.save()
			requiredDict = {
				'result' : serializer.data,
				}
			return Response(requiredDict, status=200)
		else:
			return Response(serializer.errors,  status=200)


class SubSectorDetailsView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, sub_sector_id, format=None):
		try:
			subSectorInstance = MarketSubSector.objects.get(id=sub_sector_id)
		except Exception as e:
			return Response(response_message("Market Sub Sector Not Found!"), status=404)

		requiredDict = {
				'result' : sub_sector_view(subSectorInstance),
				}
		return Response(requiredDict, status=200)


class SubSectorListingView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def sortingField(self, number, order):
		if order == 'asc':
			dic = {1: 'market_sector__sector_name', 2: 'sub_sector_name', 3: 'sub_sector_description', 
				4: 'status', 5: 'created_date'}
		else:
			dic = {1: '-market_sector__sector_name', 2: '-sub_sector_name', 3: '-sub_sector_description',
				4: '-status', 5: '-created_date'}
		return dic[number]

	def changeIds(self, ids):
		return '('+','.join(ids)+')'

	def updateStatus(self, isActive, ids):
		if type(eval(ids)) == type(1):
			query = "UPDATE `market_sub_sector` SET status = %s WHERE id in (%s)"
		else:
			query = "UPDATE `market_sub_sector` SET status = %s WHERE id in %s"
		try:
			with connection.cursor() as cursor:
				cursor.execute(query, [isActive, eval(ids)])
		except Exception as e:
			pass

	def post(self, request, format=None):

		if 'customActionType' in request.data and 'customActionName' in request.data:
			ids = self.changeIds(dict(request.data)['id[]'])
			if str(request.data['customActionName']).lower() == 'inactive':
				self.updateStatus(0, ids)
			if str(request.data['customActionName']).lower() == 'active':
				self.updateStatus(1, ids)
		subSectorSet = MarketSubSector.objects.all()

		if 'sector_name' in request.data and request.data['sector_name']:
			subSectorSet = subSectorSet.filter(market_sector__sector_name__icontains=request.data['sector_name'])
		if 'sub_sector_name' in request.data and request.data['sub_sector_name']:
			subSectorSet = subSectorSet.filter(sub_sector_name__icontains=request.data['sub_sector_name'])
		if 'sub_sector_description' in request.data and request.data['sub_sector_description']:
			subSectorSet = subSectorSet.filter(sub_sector_description__icontains=request.data['sub_sector_description'])
		if 'status' in request.data and request.data['status']:
			if str(request.data['status']).lower() == 'active':
				subSectorSet = subSectorSet.filter(status=1)
			elif str(request.data['status']).lower() == 'inactive':
				subSectorSet = subSectorSet.filter(status=0)
		if 'date_joined_from' in request.data and request.data['date_joined_from']:
			dateJoinedFrom = datetime.strptime(request.data['date_joined_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
			dateJoinedTo = (datetime.strptime(request.data['date_joined_to'], '%d/%m/%Y') + timedelta(days=1)).strftime('%Y-%m-%d')
			subSectorSet = subSectorSet.filter(created_date__gte=dateJoinedFrom, created_date__lte=dateJoinedTo)

		# ===================== Start Sorting all =================== #
		if int(request.data['order[0][column]']) == 0:
			subSectorSet = subSectorSet.order_by('-created_date')
		else:
			fieldValue = self.sortingField(int(request.data['order[0][column]']), str(request.data['order[0][dir]']))
			subSectorSet = subSectorSet.order_by(fieldValue)
		# ===================== End Sorting all ====================== #

		totalSubSector = subSectorSet.count()
		querySet = PaginationSet(subSectorSet, request.data['length'], request.data['start'])
		subSectorList = []
		for subSector in querySet:
			subSectorList.append(
				subSectorListing(subSector)
			)
		requiredDict = {
				'data': subSectorList,
				'draw': request.data['draw'],
				'recordsTotal': totalSubSector,
				'recordsFiltered': totalSubSector
				}
		return Response(requiredDict, status=200)


class ContractAddView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		# import ipdb; ipdb.set_trace()
		serializer = ContactsAddSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors,  status=200)


class ContractEditView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, contract_id, format=None):
		try:
			contractInstance = Contracts.objects.get(id=contract_id)
		except Exception as e:
			return Response(response_message("Contract Not Found!"), status=404)

		serializer = ContactsAddSerializer(contractInstance, data=request.data)
		if serializer.is_valid():
			serializer.save()
			requiredDict = {
				'result' : serializer.data,
				}
			return Response(requiredDict, status=200)
		else:
			return Response(serializer.errors,  status=200)


class ContractDetailsView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, contract_id, format=None):
		try:
			contractInstance = Contracts.objects.get(id=contract_id)
		except Exception as e:
			return Response(response_message("Contract Not Found!"), status=404)

		requiredDict = {
				'result' : contract_view(contractInstance),
				}
		return Response(requiredDict, status=200)


class ContractListingView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def sortingField(self, number, order):
		if order == 'asc':
			dic = {1: 'market_sub_sector__sub_sector_name', 2: 'contract_name', 3: 'contract_description', 
				4: 'status', 5: 'created_date'}
		else:
			dic = {1: '-market_sub_sector__sub_sector_name', 2: '-contract_name', 3: '-contract_description',
				4: '-status', 5: '-created_date'}
		return dic[number]

	def changeIds(self, ids):
		return '('+','.join(ids)+')'

	def updateStatus(self, isActive, ids):
		if type(eval(ids)) == type(1):
			query = "UPDATE `contracts` SET status = %s WHERE id in (%s)"
		else:
			query = "UPDATE `contracts` SET status = %s WHERE id in %s"
		try:
			with connection.cursor() as cursor:
				cursor.execute(query, [isActive, eval(ids)])
		except Exception as e:
			pass

	def post(self, request, format=None):

		if 'customActionType' in request.data and 'customActionName' in request.data:
			ids = self.changeIds(dict(request.data)['id[]'])
			if str(request.data['customActionName']).lower() == 'inactive':
				self.updateStatus(0, ids)
			if str(request.data['customActionName']).lower() == 'active':
				self.updateStatus(1, ids)
		contractSet = Contracts.objects.all()

		if 'sub_sector_name' in request.data and request.data['sub_sector_name']:
			contractSet = contractSet.filter(market_sub_sector__sub_sector_name__icontains=request.data['sub_sector_name'])
		if 'contract_name' in request.data and request.data['contract_name']:
			contractSet = contractSet.filter(contract_name__icontains=request.data['contract_name'])
		if 'contract_description' in request.data and request.data['contract_description']:
			contractSet = contractSet.filter(contract_description__icontains=request.data['contract_description'])
		if 'status' in request.data and request.data['status']:
			if str(request.data['status']).lower() == 'active':
				contractSet = contractSet.filter(status=1)
			elif str(request.data['status']).lower() == 'inactive':
				contractSet = contractSet.filter(status=0)
		if 'date_joined_from' in request.data and request.data['date_joined_from']:
			dateJoinedFrom = datetime.strptime(request.data['date_joined_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
			dateJoinedTo = (datetime.strptime(request.data['date_joined_to'], '%d/%m/%Y') + timedelta(days=1)).strftime('%Y-%m-%d')
			contractSet = contractSet.filter(created_date__gte=dateJoinedFrom, created_date__lte=dateJoinedTo)

		# ===================== Start Sorting all =================== #
		if int(request.data['order[0][column]']) == 0:
			contractSet = contractSet.order_by('-created_date')
		else:
			fieldValue = self.sortingField(int(request.data['order[0][column]']), str(request.data['order[0][dir]']))
			contractSet = contractSet.order_by(fieldValue)
		# ===================== End Sorting all ====================== #

		totalContract = contractSet.count()
		querySet = PaginationSet(contractSet, request.data['length'], request.data['start'])
		contractList = []
		for contract in querySet:
			contractList.append(
				contractListing(contract)
			)
		requiredDict = {
				'data': contractList,
				'draw': request.data['draw'],
				'recordsTotal': totalContract,
				'recordsFiltered': totalContract
				}
		return Response(requiredDict, status=200)


class DropdownSubSectorListView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):

		subSectorSet = MarketSubSector.objects.filter(status=True)
		subSectorSet = subSectorSet.order_by('-created_date')

		subSectorList = []
		for subSector in subSectorSet:
			subSectorList.append({
				'id': subSector.id,
				'name': subSector.sub_sector_name
			})
		requiredDict = {
				'result': subSectorList,
				}
		return Response(requiredDict, status=200)


class SpreadAddView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		serializer = SpreadsAddSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors,  status=401)


class SpreadEditView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, spread_id, format=None):
		try:
			spreadInstance = Spreads.objects.get(id=spread_id)
		except Exception as e:
			return Response(response_message("Spreads Not Found!"), status=404)

		serializer = SpreadsAddSerializer(spreadInstance, data=request.data)
		if serializer.is_valid():
			serializer.save()
			requiredDict = {
				'result' : serializer.data,
				}
			return Response(requiredDict, status=200)
		else:
			return Response(serializer.errors,  status=401)


class SpreadDetailsView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, spread_id, format=None):
		try:
			spreadInstance = Spreads.objects.get(id=spread_id)
		except Exception as e:
			return Response(response_message("Spreads Not Found!"), status=404)

		requiredDict = {
				'result' : spread_view(spreadInstance),
				}
		return Response(requiredDict, status=200)


class SpreadListingView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def sortingField(self, number, order):
		if order == 'asc':
			dic = {1: 'spread_name', 2: 'spread_code', 3: 'spread_description', 
				4: 'status', 5: 'created_date'}
		else:
			dic = {1: '-spread_name', 2: '-spread_code', 3: '-spread_description',
				4: '-status', 5: '-created_date'}
		return dic[number]

	def changeIds(self, ids):
		return '('+','.join(ids)+')'

	def updateStatus(self, isActive, ids):
		if type(eval(ids)) == type(1):
			query = "UPDATE `spreads` SET status = %s WHERE id in (%s)"
		else:
			query = "UPDATE `spreads` SET status = %s WHERE id in %s"
		try:
			with connection.cursor() as cursor:
				cursor.execute(query, [isActive, eval(ids)])
		except Exception as e:
			pass

	def post(self, request, format=None):

		if 'customActionType' in request.data and 'customActionName' in request.data:
			ids = self.changeIds(dict(request.data)['id[]'])
			if str(request.data['customActionName']).lower() == 'inactive':
				self.updateStatus(0, ids)
			if str(request.data['customActionName']).lower() == 'active':
				self.updateStatus(1, ids)
		spreadSet = Spreads.objects.all()

		if 'spread_name' in request.data and request.data['spread_name']:
			spreadSet = spreadSet.filter(spread_name__icontains=request.data['spread_name'])
		if 'spread_code' in request.data and request.data['spread_code']:
			spreadSet = spreadSet.filter(spread_code__icontains=request.data['spread_code'])
		if 'spread_description' in request.data and request.data['spread_description']:
			spreadSet = spreadSet.filter(spread_description__icontains=request.data['spread_description'])
		if 'status' in request.data and request.data['status']:
			if str(request.data['status']).lower() == 'active':
				spreadSet = spreadSet.filter(status=1)
			elif str(request.data['status']).lower() == 'inactive':
				spreadSet = spreadSet.filter(status=0)
		if 'date_joined_from' in request.data and request.data['date_joined_from']:
			dateJoinedFrom = datetime.strptime(request.data['date_joined_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
			dateJoinedTo = (datetime.strptime(request.data['date_joined_to'], '%d/%m/%Y') + timedelta(days=1)).strftime('%Y-%m-%d')
			spreadSet = spreadSet.filter(created_date__gte=dateJoinedFrom, created_date__lte=dateJoinedTo)

		# ===================== Start Sorting all =================== #
		if int(request.data['order[0][column]']) == 0:
			spreadSet = spreadSet.order_by('-created_date')
		else:
			fieldValue = self.sortingField(int(request.data['order[0][column]']), str(request.data['order[0][dir]']))
			spreadSet = spreadSet.order_by(fieldValue)
		# ===================== End Sorting all ====================== #

		totalSpread = spreadSet.count()
		querySet = PaginationSet(spreadSet, request.data['length'], request.data['start'])
		spreadList = []
		for spread in querySet:
			spreadList.append(
				spreadListing(spread)
			)
		requiredDict = {
				'data': spreadList,
				'draw': request.data['draw'],
				'recordsTotal': totalSpread,
				'recordsFiltered': totalSpread
				}
		return Response(requiredDict, status=200)


class DropdownContractListView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):

		contractSet = Contracts.objects.filter(status=True)
		contractSet = contractSet.order_by('-created_date')

		contactList = []
		for contract in contractSet:
			contactList.append({
				'id': contract.id,
				'name': contract.contract_name
			})
		requiredDict = {
				'result': contactList,
				}
		return Response(requiredDict, status=200)


class MonthListing(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):

		monthSet = Month.objects.all()

		monthList = []
		for month in monthSet:
			monthList.append({
				'id': month.id,
				'month_name': month.month_name + ' - ' + month.month_code
			})
		requiredDict = {
				'result': monthList,
				}
		return Response(requiredDict, status=200)



class TraderAssignContractView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		print ("request data =", request.data)
		serializer = SubSectorAssignmentSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors,  status=401)


class ContractAssignmentEditView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, trader_id, format=None):
		assignmentInstance = SubSectorAssignment.objects.filter(trader__id=trader_id)
		if not assignmentInstance:
			return Response(response_message("Contracts Not Found!"), status=404)

		serializer = SubSectorAssignmentSerializer(assignmentInstance[0], data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors,  status=401)


class ContractAssignmentDetailView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, trader_id, format=None):
		try:
			traderInstance = User.objects.get(id=trader_id)
		except:
			return Response(response_message("Trader Not Found!"), status=404)
		assignmentSet = SubSectorAssignment.objects.filter(trader=traderInstance)
		assignmentList = []
		for assignment in assignmentSet:
			assignmentList.append({
				'id': assignment.market_sub_sector.id,
				'name': assignment.market_sub_sector.sub_sector_name,
				'status': assignment.status
			})

		requiredDict = {
				'result' : {
						'trader': traderInstance.id,
						'trader_name': user_name(traderInstance),
						'trader_status': traderInstance.is_active,
						'sub_sector': assignmentList
					},
				}
		return Response(requiredDict, status=200)


class TraderListingContractView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def sortingField(self, number, order):
		if order == 'asc':
			dic = {1: 'trader__first_name', 2: 'status', 3: 'created_date'}
		else:
			dic = {1: '-trader__first_name', 2: '-status', 3: '-created_date'}
		return dic[number]

	def changeIds(self, ids):
		return '('+','.join(ids)+')'

	def updateStatus(self, isActive, ids):
		if type(eval(ids)) == type(1):
			query = "UPDATE `sub_sector_assignment` SET status = %s WHERE id in (%s)"
		else:
			query = "UPDATE `sub_sector_assignment` SET status = %s WHERE id in %s"
		try:
			with connection.cursor() as cursor:
				cursor.execute(query, [isActive, eval(ids)])
		except Exception as e:
			pass

	def post(self, request, format=None):

		print ("Request Data =", request.data)

		if 'customActionType' in request.data and 'customActionName' in request.data:
			ids = self.changeIds(dict(request.data)['id[]'])
			if str(request.data['customActionName']).lower() == 'inactive':
				self.updateStatus(0, ids)
			if str(request.data['customActionName']).lower() == 'active':
				self.updateStatus(1, ids)

		traderSectorSet = SubSectorAssignment.objects.values('trader').annotate(dcount=Count('trader'))

		if 'trader_name' in request.data and request.data['trader_name']:
			traderSectorSet = traderSectorSet.filter(Q(trader__first_name__icontains=request.data['trader_name']) | Q(trader__last_name__icontains=request.data['trader_name']))
		if 'status' in request.data and request.data['status']:
			if str(request.data['status']).lower() == 'active':
				traderSectorSet = traderSectorSet.filter(status=1)
			elif str(request.data['status']).lower() == 'inactive':
				traderSectorSet = traderSectorSet.filter(status=0)
		if 'date_joined_from' in request.data and request.data['date_joined_from']:
			dateJoinedFrom = datetime.strptime(request.data['date_joined_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
			dateJoinedTo = (datetime.strptime(request.data['date_joined_to'], '%d/%m/%Y') + timedelta(days=1)).strftime('%Y-%m-%d')
			traderSectorSet = traderSectorSet.filter(created_date__gte=dateJoinedFrom, created_date__lte=dateJoinedTo) 

		# ===================== Start Sorting all =================== #
		if int(request.data['order[0][column]']) == 0:
			traderSectorSet = traderSectorSet.order_by('-created_date')
		else:
			fieldValue = self.sortingField(int(request.data['order[0][column]']), str(request.data['order[0][dir]']))
			traderSectorSet = traderSectorSet.order_by(fieldValue)
		# ===================== End Sorting all ====================== #

		totalAssignment = traderSectorSet.count()
		querySet = PaginationSet(traderSectorSet, request.data['length'], request.data['start'])
		traderContractList = []
		for traderContract in querySet:
			instance = SubSectorAssignment.objects.filter(trader__id=traderContract['trader'])[0]
			traderContractList.append(
				traderContractListing(instance)
			)
		requiredDict = {
				'data': traderContractList,
				'draw': request.data['draw'],
				'recordsTotal': totalAssignment,
				'recordsFiltered': totalAssignment
				}
		return Response(requiredDict, status=200)


class TradersSubSectorView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		if 'trader_id' not in request.data:
			return Response(response_message("parameter missing"), status=400)

		tradersSubSectorSet = SubSectorAssignment.objects.filter(trader__id=int(request.data['trader_id']), status=True)

		tradersSubSectorList = []
		for traderSubSector in tradersSubSectorSet:
			tradersSubSectorList.append({
					'id': traderSubSector.id,
					'sub_sector_id' : traderSubSector.market_sub_sector.id,
					'sub_sector_name' : traderSubSector.market_sub_sector.sub_sector_name
				})

		requiredDict = {
				'result': tradersSubSectorList,
				}
		return Response(requiredDict, status=200)


class TradersContractsView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		if 'sub_sector_id' not in request.data:
			return Response(response_message("parameter missing"), status=400)

		contractSet = Contracts.objects.filter(market_sub_sector=int(request.data['sub_sector_id']), status=True)

		contractList = []
		for contract in contractSet:
			contractList.append({
					'id': contract.id,
					'contract_name' : contract.contract_name,
					'cqg_code' : contract.cqg_code,
					'cme_code' : contract.cme_code,
					'contract_description' : contract.contract_description
				})

		requiredDict = {
				'result': contractList,
				}
		return Response(requiredDict, status=200)


class TradersSpreadsView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		if 'contract_id' not in request.data:
			return Response(response_message("parameter missing"), status=400)

		spreadSet = Spreads.objects.filter(contract=int(request.data['contract_id']), status=True)

		spreadList = []
		for spread in spreadSet:
			spreadList.append({
					'id': spread.id,
					'spread_name' : spread.spread_name,
					'spread_code' : spread.spread_name,
					'spread_description' : spread.spread_description
				})

		requiredDict = {
				'result': spreadList,
				}
		return Response(requiredDict, status=200)


class InstrumentListingView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def sortingField(self, number, order):
		if order == 'asc':
			dic = {1: 'contract__contract_name', 2: 'name', 3:'type', 4: 'status', 5: 'created_date'}
		else:
			dic = {1: '-contract__contract_name', 2: '-name', 3: '-type', 4: '-status', 5: '-created_date'}
		return dic[number]

	def changeIds(self, ids):
		return '('+','.join(ids)+')'

	def updateStatus(self, isActive, ids):
		if type(eval(ids)) == type(1):
			query = "UPDATE `instruments` SET status = %s WHERE id in (%s)"
		else:
			query = "UPDATE `instruments` SET status = %s WHERE id in %s"
		try:
			with connection.cursor() as cursor:
				cursor.execute(query, [isActive, eval(ids)])
		except Exception as e:
			pass

	def post(self, request, format=None):

		print ("Request Data =", request.data)

		if 'customActionType' in request.data and 'customActionName' in request.data:
			ids = self.changeIds(dict(request.data)['id[]'])
			if str(request.data['customActionName']).lower() == 'inactive':
				self.updateStatus(0, ids)
			if str(request.data['customActionName']).lower() == 'active':
				self.updateStatus(1, ids)

		instrumentSet = Instruments.objects.all()

		if 'contract_name' in request.data and request.data['contract_name']:
			instrumentSet = instrumentSet.filter(contract__contract_name__icontains=request.data['contract_name'])
		if 'instrument_name' in request.data and request.data['instrument_name']:
			instrumentSet = instrumentSet.filter(name__icontains=request.data['instrument_name'])
		if 'instrument_type' in request.data and request.data['instrument_type']:
			instrumentSet = instrumentSet.filter(type__icontains=request.data['instrument_type'])
		if 'status' in request.data and request.data['status']:
			if str(request.data['status']).lower() == 'active':
				instrumentSet = instrumentSet.filter(status=1)
			elif str(request.data['status']).lower() == 'inactive':
				instrumentSet = instrumentSet.filter(status=0)
		if 'date_joined_from' in request.data and request.data['date_joined_from']:
			dateJoinedFrom = datetime.strptime(request.data['date_joined_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
			dateJoinedTo = (datetime.strptime(request.data['date_joined_to'], '%d/%m/%Y') + timedelta(days=1)).strftime('%Y-%m-%d')
			instrumentSet = instrumentSet.filter(created_date__gte=dateJoinedFrom, created_date__lte=dateJoinedTo) 

		# ===================== Start Sorting all =================== #
		if int(request.data['order[0][column]']) == 0:
			instrumentSet = instrumentSet.order_by('-created_date')
		else:
			fieldValue = self.sortingField(int(request.data['order[0][column]']), str(request.data['order[0][dir]']))
			instrumentSet = instrumentSet.order_by(fieldValue)
		# ===================== End Sorting all ====================== #

		totalInstrument = instrumentSet.count()
		querySet = PaginationSet(instrumentSet, request.data['length'], request.data['start'])
		traderInstrumentList = []
		for traderInstrument in querySet:
			traderInstrumentList.append(
				instrumentListing(traderInstrument)
			)
		requiredDict = {
				'data': traderInstrumentList,
				'draw': request.data['draw'],
				'recordsTotal': totalInstrument,
				'recordsFiltered': totalInstrument
				}
		return Response(requiredDict, status=200)


class InstrumentAddView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		serializer = InstrumentSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors,  status=401)


class InstrumentEditView(APIView):

	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def post(self, request, instrument_id, format=None):
		try:
			instrumentInstance = Instruments.objects.get(id=instrument_id)
		except:
			return Response(response_message("Instrument Not Found!"), status=404)

		serializer = InstrumentSerializer(instrumentInstance, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(response_message("Success!"), status=200)
		else:
			return Response(serializer.errors,  status=401)


class InstrumentDetailView(APIView):

	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, instrument_id, format=None):
		try:
			instrumentInstance = Instruments.objects.get(id=instrument_id)
		except:
			return Response(response_message("Instrument Not Found!"), status=404)

		requiredDict = {
				'result' : instrument_view(instrumentInstance),
				}
		return Response(requiredDict, status=200)