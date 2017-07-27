
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import get_template
from django.contrib.auth.models import Group
from django.template import Context
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Q

from datetime import datetime
import string
import random

from strategies.models import Spreads


# send message in response
def response_message(message):
	return {'message': message}

# send data in response
# def response_data(dictionary):
# 	return dictionary

def user_name(user):
	return user.first_name+" "+user.last_name

# make dic for user
def user_dict(user):
	try:
		userGroup = Group.objects.get(user=user)
	except Exception as e:
		userGroup = None
	if userGroup and userGroup.id == 2:
		dic = {
			'id': user.id,
			'email': user.email,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'office_phone': user.office_phone,
			'mobile_phone': user.mobile_phone,
			'is_verified': user.is_verified,
			'is_active': user.is_active,
			'nfa': user.nfa,
			'firm_name': user.firm_name,
			'firm_nfa': user.firm_nfa,
			'markets_traded': user.markets_traded.id if user.markets_traded else None,
			'markets_traded_name': user.markets_traded.text if user.markets_traded else None,
			'biography': user.biography,
			'profile_img': settings.MAIN_URL+user.profile_img.url if user.profile_img else None,
			'date_joined': user.date_joined,
			'user_type': userGroup.name if userGroup else 'Admin',
		}
	elif userGroup and userGroup.id == 1:
		dic = {
			'id': user.id,
			'email': user.email,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'phone': user.phone,
			'office_phone': user.office_phone,
			'mobile_phone': user.mobile_phone,
			'is_verified': user.is_verified,
			'is_active': user.is_active,
			'firm_name': user.firm_name,
			'firm_nfa': user.firm_nfa,
			'markets_traded': user.markets_traded.id if user.markets_traded else None,
			'markets_traded_name': user.markets_traded.text if user.markets_traded else None,
			'biography': user.biography,
			'address': user.address,
			'address1': user.address1,
			'city': user.city,
			'state': user.state,
			'zip_code': user.zip_code,
			'profile_img': settings.MAIN_URL+user.profile_img.url if user.profile_img else None,
			'date_joined': user.date_joined,
			'user_type': userGroup.name if userGroup else 'Admin',
		}
	else:
		dic = {
				'id': user.id,
				'email': user.email,
				'first_name': user.first_name,
				'last_name': user.last_name,
				'phone': user.phone,
				'is_verified': user.is_verified,
				'is_active': user.is_active,
				'address': user.address,
				'address1': user.address1,
				'city': user.city,
				'state': user.state,
				'zip_code': user.zip_code,
				'date_joined': user.date_joined,
				'user_type': userGroup.name if userGroup else 'Admin',
			}
	return dic

def user_dict_details(user):
	try:
		userGroup = Group.objects.get(user=user)
	except Exception as e:
		userGroup = None
	if userGroup and userGroup.id == 2:
		dic = {
			'id': user.id,
			'email': user.email,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'office_phone': user.office_phone,
			'mobile_phone': user.mobile_phone,
			'is_verified': user.is_verified,
			'is_active': user.is_active,
			'nfa': user.nfa,
			'firm_name': user.firm_name,
			'firm_nfa': user.firm_nfa,
			'markets_traded': user.markets_traded.text if user.markets_traded else None,
			'biography': user.biography,
			'profile_img': settings.MAIN_URL+user.profile_img.url,
			'date_joined': user.date_joined,
			'user_type': userGroup.name if userGroup else 'Admin',
		}
	elif userGroup and userGroup.id == 1:
		dic = {
			'id': user.id,
			'email': user.email,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'phone': user.phone,
			'office_phone': user.office_phone,
			'mobile_phone': user.mobile_phone,
			'is_verified': user.is_verified,
			'is_active': user.is_active,
			'firm_name': user.firm_name,
			'firm_nfa': user.firm_nfa,
			'markets_traded': user.markets_traded.text if user.markets_traded else None,
			'biography': user.biography,
			'address': user.address,
			'address1': user.address1,
			'city': user.city,
			'state': user.state,
			'zip_code': user.zip_code,
			'profile_img': settings.MAIN_URL+user.profile_img.url,
			'date_joined': user.date_joined,
			'user_type': userGroup.name if userGroup else 'Admin',
		}
	else:
		dic = {
				'id': user.id,
				'email': user.email,
				'first_name': user.first_name,
				'last_name': user.last_name,
				'phone': user.phone,
				'is_verified': user.is_verified,
				'is_active': user.is_active,
				'address': user.address,
				'address1': user.address1,
				'city': user.city,
				'state': user.state,
				'zip_code': user.zip_code,
				'date_joined': user.date_joined,
				'user_type': userGroup.name if userGroup else 'Admin',
			}
	return dic


def TraderUserListing(user):
	try:
		userGroup = Group.objects.get(user=user)
	except Exception as e:
		userGroup = None
		pass
	status = 'Active' if user.is_active else 'Inactive'
	className = 'label-info' if user.is_active else 'label-danger'
	if userGroup.name == 'Customer':
		action = '<div class="btn-group btn-group-solid"><a href="#!/view-customer/'+str(user.id)+'" class="btn view btn-sm btn-outline blue tooltips" title="View"><i class="fa fa-search"></i></a><a href="#!/edit-customer/'+str(user.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'
	else:
		action = '<div class="btn-group btn-group-solid"><a href="#!/view/'+str(user.id)+'" class="btn view btn-sm btn-outline blue tooltips" title="View"><i class="fa fa-search"></i></a><a href="#!/edit/'+str(user.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'

	dic = {
			'id': '<label class="mt-checkbox mt-checkbox-single mt-checkbox-outline"><input name="id[]" type="checkbox" class="checkboxes" value="'+str(user.id)+'"/><span></span></label>',
			'first_name': user.first_name,
			'last_name': user.last_name,
			'email': user.email,
			'user_type': userGroup.name if userGroup else 'Admin',
			'date_joined': user.date_joined.strftime('%d/%m/%Y'),
			'status': '<span class="label label-sm '+className+'">'+status+'</span>',
			'action': action,
		}
	return dic


# def CustomerUserListing(user):
# 	try:
# 		userGroup = Group.objects.get(user=user)
# 	except Exception as e:
# 		userGroup = None
# 		pass
# 	status = 'Active' if user.is_active else 'Inactive'
# 	className = 'label-info' if user.is_active else 'label-danger'
# 	dic = {
# 			'id': '<label class="mt-checkbox mt-checkbox-single mt-checkbox-outline"><input name="id[]" type="checkbox" class="checkboxes" value="'+str(user.id)+'"/><span></span></label>',
# 			'first_name': user.first_name,
# 			'last_name': user.last_name,
# 			'email': user.email,
# 			'user_type': userGroup.name if userGroup else 'Admin',
# 			'date_joined': user.date_joined.strftime('%d/%m/%Y'),
# 			'status': '<span class="label label-sm '+className+'">'+status+'</span>',
# 			'action': '<div class="btn-group btn-group-solid"><a href="#!/view-customer/'+str(user.id)+'" class="btn view btn-sm btn-outline blue tooltips" title="View"><i class="fa fa-search"></i></a><a href="#!/edit-customer/'+str(user.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'
# 		}
# 	return dic


def strategyListing(strategy):
	try:
		userGroup = Group.objects.get(user=strategy.user)
		name = userGroup.name
	except Exception as e:
		name = "Admin"
	user = {
		'id': strategy.user.id,
		'name': '<a href="#!/view/'+str(strategy.user.id)+'?back=strategies">'+str(strategy.user.first_name+" "+strategy.user.last_name)+'</a>',
		'user_type': name
	}

	if strategy.status.id == 1:
		status = 'Pending'
		className = 'label-info'
	elif strategy.status.id == 2:
		status = 'Approved'
		className = "label-success"
	elif strategy.status.id == 3:
		status = 'Rejected'
		className = "label-danger"

	# className = 'label-info' if strategy.status else 'label-danger'
	dic = {
		'user': user,
		'id': '<label class="mt-checkbox mt-checkbox-single mt-checkbox-outline"><input name="id[]" type="checkbox" class="checkboxes" value="'+str(strategy.id)+'"/><span></span></label>',
		'title': strategy.title,
		'description': strategy.description,
		'product_category': strategy.product_category,
		'product_type': strategy.product_type,
		'strategy_type': strategy.strategy_type,
		'trader_info': strategy.trade_info,
		'status': '<span class="label label-sm '+className+'">'+status+'</span>',
		'ratio': strategy.ratio,
		'delta': strategy.delta,
		'ref': strategy.ref,
		'loss_target': strategy.loss_target,
		'profit_target': strategy.profit_target,
		'created_date': strategy.created_date.strftime('%d/%m/%Y'),
		'action': '<div class="btn-group btn-group-solid"><a href="#!/view-strategy/'+str(strategy.id)+'" class="btn view btn-sm btn-outline blue tooltips" title="View"><i class="fa fa-search"></i></a></div>'
	}
	return dic

# password generator in forgot password
def password_generator(size=8, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


# email send method
def EmailSend(subject, email, context, template):
	print (context)
	from_email = settings.EMAIL_HOST_USER
	message = get_template(template).render(context)
	msg = EmailMessage(subject, message, to=email, from_email=from_email)
	msg.content_subtype = "html"
	msg.send()


def PaginationSet(querySet, length, start):
	# =================== start pagination ====================== #
	paginator = Paginator(querySet, length)
	if int(start) == 0:
		page = 1
	else:
		pageFormula = (int(length)/int(start))+1
		page = pageFormula
	try:
		contacts = paginator.page(page)
	except PageNotAnInteger:
		contacts = paginator.page(1)
	except EmptyPage:
		contacts = paginator.page(paginator.num_pages)
	# =================== Pagination End ======================== #
	return contacts



def strategy_view(legSet, strategy):
	legLi = []
	for legs in legSet:
		legLi.append({
			'id': legs.id,
			'type': legs.type,
			'product_type': legs.product_type,
			'term': legs.term,
			'strike_price': legs.strike_price
		})
	strategyDict = {
		'id': strategy.id,
		'user_id': strategy.user.id,
		'name': user_name(strategy.user),
		'title': strategy.title,
		'description': strategy.description,
		'product_category': strategy.product_category,
		'product_type': strategy.product_type,
		'trade_info': strategy.trade_info,
		'strategy_type': strategy.strategy_type,
		'status': strategy.status.name,
		'ratio': strategy.ratio,
		'delta': strategy.delta,
		'ref': strategy.ref,
		'loss_target': strategy.loss_target,
		'profit_target': strategy.profit_target,
		'created_date': strategy.created_date,
		'legs': legLi
	}
	return strategyDict


def filter_name(strategySet, name):
		nameList = name.split(" ")
		if len(nameList) > 1:
			strategySet = strategySet.filter(Q(user__first_name__icontains=nameList[0]) | 
				Q(user__first_name__icontains=nameList[1]))
		else:
			strategySet = strategySet.filter(Q(user__first_name__icontains=name) |
				Q(user__last_name__icontains=name))
		return strategySet


def sectorListing(sector):

	className = 'label-info' if sector.status else 'label-danger'
	status = "Active" if sector.status else "Inactive"

	dic = {
		'sector_name': sector.sector_name,
		'id': '<label class="mt-checkbox mt-checkbox-single mt-checkbox-outline"><input name="id[]" type="checkbox" class="checkboxes" value="'+str(sector.id)+'"/><span></span></label>',
		'sector_description': sector.sector_description,
		'sector_exchange_name': sector.sector_exchange_name,
		'sector_exchange_abbrev': sector.sector_exchange_abbrev,
		'status': '<span class="label label-sm '+className+'">'+status+'</span>',
		'created_date': sector.created_date.strftime('%d/%m/%Y'),
		'action': '<div class="btn-group btn-group-solid"><a href="#!/edit-sector/'+str(sector.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'
	}
	return dic


def sector_view(sector):

	status = "Active" if sector.status else "Inactive"
	sectorDict = {
		'id': sector.id,
		'sector_name': sector.sector_name,
		'sector_exchange_abbrev': sector.sector_exchange_abbrev,
		'sector_exchange_name': sector.sector_exchange_name,
		'sector_description': sector.sector_description,
		'status': status,
		'created_date': sector.created_date.strftime('%d/%m/%Y'),
	}
	return sectorDict


def subSectorListing(subSector):

	className = 'label-info' if subSector.status else 'label-danger'
	status = "Active" if subSector.status else "Inactive"

	dic = {
		'id': '<label class="mt-checkbox mt-checkbox-single mt-checkbox-outline"><input name="id[]" type="checkbox" class="checkboxes" value="'+str(subSector.id)+'"/><span></span></label>',
		'sector_name': subSector.market_sector.sector_name,
		'sub_sector_name': subSector.sub_sector_name,
		'sub_sector_description': subSector.sub_sector_description,
		'status': '<span class="label label-sm '+className+'">'+status+'</span>',
		'created_date': subSector.created_date.strftime('%d/%m/%Y'),
		'action': '<div class="btn-group btn-group-solid"><a href="#!/edit-sub-sector/'+str(subSector.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'
	}
	return dic


def sub_sector_view(subsector):

	status = "Active" if subsector.status else "Inactive"
	subSectorDict = {
		'id': subsector.id,
		'sub_sector_name': subsector.sub_sector_name,
		'market_sector': subsector.market_sector.id,
		'sub_sector_description': subsector.sub_sector_description,
		'status': status,
		'created_date': subsector.created_date.strftime('%d/%m/%Y'),
	}
	return subSectorDict


def contract_view(contract):

	status = 1 if contract.status else 0
	monthSet = contract.months.all()
	monthList = []
	for data in monthSet:
		monthList.append({
				'id': data.id,
				'month_name': data.month_name,
				'month_code': data.month_code,
			})
	contractDict = {
		'id': contract.id,
		'market_sub_sector': contract.market_sub_sector.id,
		'contract_name': contract.contract_name,
		'cqg_code': contract.cqg_code,
		'cme_code': contract.cme_code,
		'contract_description': contract.contract_description,
		'months': monthList,
		'status': status,
		'created_date': contract.created_date.strftime('%d/%m/%Y'),
	}
	return contractDict

def contractListing(contract):

	className = 'label-info' if contract.status else 'label-danger'
	status = "Active" if contract.status else "Inactive"

	dic = {
		'id': '<label class="mt-checkbox mt-checkbox-single mt-checkbox-outline"><input name="id[]" type="checkbox" class="checkboxes" value="'+str(contract.id)+'"/><span></span></label>',
		'sub_sector_name': contract.market_sub_sector.sub_sector_name,
		'contract_name': contract.contract_name,
		'cqg_code': contract.cqg_code,
		'contract_description': contract.contract_description,
		'status': '<span class="label label-sm '+className+'">'+status+'</span>',
		'created_date': contract.created_date.strftime('%d/%m/%Y'),
		# 'action': '<div class="btn-group btn-group-solid"><a href="#!/view-contract/'+str(contract.id)+'" class="btn view btn-sm btn-outline blue tooltips" title="View"><i class="fa fa-search"></i></a><a href="#!/edit-contract/'+str(contract.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'
		'action': '<div class="btn-group btn-group-solid"><a href="#!/edit-contract/'+str(contract.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'
	}
	return dic


def spread_view(spread):

	status = 1 if spread.status else 0
	contractSet = spread.contract.all()
	contractList = []
	for data in contractSet:
		contractList.append({
				'id': data.id,
				'contract_name': data.contract_name,
				'cqg_code': data.cqg_code,
				'cme_code': data.cme_code,
				'contract_description': data.contract_description
			})

	spreadDict = {
		'id': spread.id,
		'spread_name': spread.spread_name,
		'spread_code': spread.spread_code,
		'spread_description': spread.spread_description,
		'status': status,
		'contract': contractList,
		'created_date': spread.created_date.strftime('%d/%m/%Y'),
	}
	return spreadDict

def spreadListing(spread):

	className = 'label-info' if spread.status else 'label-danger'
	status = "Active" if spread.status else "Inactive"

	dic = {
		'id': '<label class="mt-checkbox mt-checkbox-single mt-checkbox-outline"><input name="id[]" type="checkbox" class="checkboxes" value="'+str(spread.id)+'"/><span></span></label>',
		'spread_name': spread.spread_name,
		'spread_code': spread.spread_code,
		'spread_description': spread.spread_description,
		'status': '<span class="label label-sm '+className+'">'+status+'</span>',
		'created_date': spread.created_date.strftime('%d/%m/%Y'),
		'action': '<div class="btn-group btn-group-solid"><a href="#!/view-spread/'+str(spread.id)+'" class="btn view btn-sm btn-outline blue tooltips" title="View"><i class="fa fa-search"></i></a><a href="#!/edit-spread/'+str(spread.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'
	}
	return dic


def traderContractListing(traderContract):

	className = 'label-info' if traderContract.status else 'label-danger'
	status = "Active" if traderContract.status else "Inactive"

	dic = {
		'id': '<label class="mt-checkbox mt-checkbox-single mt-checkbox-outline"><input name="id[]" type="checkbox" class="checkboxes" value="'+str(traderContract.id)+'"/><span></span></label>',
		'trader_name': user_name(traderContract.trader),
		'status': '<span class="label label-sm '+className+'">'+status+'</span>',
		'created_date': traderContract.created_date.strftime('%d/%m/%Y'),
		'action': '<div class="btn-group btn-group-solid"><a href="#!/view-assignment/'+str(traderContract.trader.id)+'" class="btn view btn-sm btn-outline blue tooltips" title="View"><i class="fa fa-search"></i></a><a href="#!/edit-assignment/'+str(traderContract.trader.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'
	}
	return dic


def instrumentListing(traderInstrument):

	className = 'label-info' if traderInstrument.status else 'label-danger'
	status = "Active" if traderInstrument.status else "Inactive"

	dic = {
		'id': '<label class="mt-checkbox mt-checkbox-single mt-checkbox-outline"><input name="id[]" type="checkbox" class="checkboxes" value="'+str(traderInstrument.id)+'"/><span></span></label>',
		'contract': traderInstrument.contract.contract_name,
		'name': traderInstrument.name,
		'type': traderInstrument.type,
		'description': traderInstrument.description,
		'status': '<span class="label label-sm '+className+'">'+status+'</span>',
		'created_date': traderInstrument.created_date.strftime('%d/%m/%Y'),
		'action': '<div class="btn-group btn-group-solid"><a href="#!/view-instrument/'+str(traderInstrument.id)+'" class="btn view btn-sm btn-outline blue tooltips" title="View"><i class="fa fa-search"></i></a><a href="#!/edit-instrument/'+str(traderInstrument.id)+'" class="btn edit btn-sm btn-outline grey-salsa tooltips" title="Edit"><i class="fa fa-pencil"></i></a></div>'
	}
	return dic


def instrument_view(instrument):

	status = 1 if instrument.status else 0
	instrumentDict = {
		'id': instrument.id,
		'contract': instrument.contract.id,
		'contract_name': instrument.contract.contract_name,
		'name': instrument.name,
		'type': instrument.type,
		'description': instrument.description,
		'ratio': instrument.ratio,
		'construction': instrument.construction,
		'max_loss_formula': instrument.max_loss_formula,
		'max_loss_description': instrument.max_loss_description,
		'max_gain_formula': instrument.max_gain_formula,
		'max_gain_description': instrument.max_gain_description,
		'break_even_formula': instrument.break_even_formula,
		'break_even_description': instrument.break_even_description,
		'exchange_symbol': instrument.exchange_symbol,
		'cqg_symbol': instrument.cqg_symbol,
		'status': status,
		'created_date': instrument.created_date.strftime('%d/%m/%Y'),
	}
	return instrumentDict