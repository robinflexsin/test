from django.conf.urls import url
from admin_auth.views import (
		LoginView,
		UserListingView,
		AddUserView,
		EditUserView,
		UserDetailsView,
		MarketsTradedDataView,
		AddCustomerView,
		EditCustomerView,
		ActiveTraderListing
	)

from strategies.views import (
		StrategyListView,
		StrategyDetailView,
		SectorAddView,
		SubSectorAddView,
		SectorListingView,
		SubSectorListingView,
		DropdownSectorListView,
		SectorDetailsView,
		SectorEditView,
		SubSectorEditView,
		SubSectorDetailsView,
		ContractAddView,
		ContractEditView,
		ContractDetailsView,
		DropdownSubSectorListView,
		ContractListingView,
		SpreadAddView,
		SpreadEditView,
		SpreadDetailsView,
		SpreadListingView,
		DropdownContractListView,
		MonthListing,
		TraderAssignContractView,
		TraderListingContractView,
		ContractAssignmentDetailView,
		ContractAssignmentEditView,
		InstrumentListingView,
		InstrumentAddView,
		InstrumentEditView,
		InstrumentDetailView
	)
# import django.views.static

urlpatterns = [
	url(r'^login/?', LoginView.as_view()),
	url(r'^user/listing/(?P<user_type>[0-9]+)$', UserListingView.as_view()),
	url(r'^trader/listing/$', ActiveTraderListing.as_view()),
	url(r'^user/add/$', AddUserView.as_view()),
	url(r'^user/edit/(?P<user_id>[0-9]+)$', EditUserView.as_view()),
	url(r'^customer/add/$', AddCustomerView.as_view()),
	url(r'^customer/edit/(?P<user_id>[0-9]+)$', EditCustomerView.as_view()),
	url(r'^user/view/(?P<user_id>[0-9]+)$', UserDetailsView.as_view()),
	url(r'^market/traded/$', MarketsTradedDataView.as_view()),
	url(r'^strategies/list/$', StrategyListView.as_view(), name="list_strategy"),
	url(r'^strategies/view/(?P<strategy_id>[0-9]+)$', StrategyDetailView.as_view(), name="list_strategy"),
	url(r'^strategies/add/sector/$', SectorAddView.as_view(), name="add_sector"),
	url(r'^strategies/view/sector/(?P<sector_id>[0-9]+)$', SectorDetailsView.as_view(), name="sector_details_view"),
	url(r'^strategies/edit/sector/(?P<sector_id>[0-9]+)$', SectorEditView.as_view(), name="sector_edit_view"),
	url(r'^strategies/list/sector/$', SectorListingView.as_view(), name="list_strategy"),
	url(r'^strategies/list/sector/dropdown/$', DropdownSectorListView.as_view(), name="list_sector_dropdown"),
	url(r'^strategies/add/subsector/$', SubSectorAddView.as_view(), name="add_sub_sector"),
	url(r'^strategies/edit/subsector/(?P<sub_sector_id>[0-9]+)$', SubSectorEditView.as_view(), name="sub_sector_edit_view"),
	url(r'^strategies/view/subsector/(?P<sub_sector_id>[0-9]+)$', SubSectorDetailsView.as_view(), name="sub_sector_edit_view"),
	url(r'^strategies/list/subsector/$', SubSectorListingView.as_view(), name="list_strategy"),
	url(r'^strategies/list/subsector/dropdown/$', DropdownSubSectorListView.as_view(), name="list_sub_sector_dropdown"),
	url(r'^strategies/add/contract/$', ContractAddView.as_view(), name="add_contract"),
	url(r'^strategies/edit/contract/(?P<contract_id>[0-9]+)$', ContractEditView.as_view(), name="contract_edit_view"),
	url(r'^strategies/view/contract/(?P<contract_id>[0-9]+)$', ContractDetailsView.as_view(), name="contract_details_view"),
	url(r'^strategies/list/contract/$', ContractListingView.as_view(), name="list_contract"),
	url(r'^strategies/list/contract/dropdown/$', DropdownContractListView.as_view(), name="list_contract_dropdown"),
	url(r'^strategies/add/spread/$', SpreadAddView.as_view(), name="add_spread"),
	url(r'^strategies/edit/spread/(?P<spread_id>[0-9]+)$', SpreadEditView.as_view(), name="spread_edit_view"),
	url(r'^strategies/view/spread/(?P<spread_id>[0-9]+)$', SpreadDetailsView.as_view(), name="spread_details_view"),
	url(r'^strategies/list/spread/$', SpreadListingView.as_view(), name="list_spread"),
	url(r'^strategies/list/month/dropdown/$', MonthListing.as_view(), name="list_month_dropdown"),
	url(r'^trader/assign/contract/$', TraderAssignContractView.as_view(), name="trader_assign_contract"),
	url(r'^trader/list/contract/$', TraderListingContractView.as_view(), name="trader_assign_contract"),
	url(r'^trader/view/contract/(?P<trader_id>[0-9]+)$', ContractAssignmentDetailView.as_view(), name="trader_details_view"),
	url(r'^trader/edit/contract/(?P<trader_id>[0-9]+)$', ContractAssignmentEditView.as_view(), name="trader_details_view"),
	url(r'^strategies/list/instrument/$', InstrumentListingView.as_view(), name="list_instrument"),
	url(r'^strategies/add/instrument/$', InstrumentAddView.as_view(), name="add_instrument"),
	url(r'^strategies/edit/instrument/(?P<instrument_id>[0-9]+)$', InstrumentEditView.as_view(), name="add_instrument"),
	url(r'^strategies/view/instrument/(?P<instrument_id>[0-9]+)$', InstrumentDetailView.as_view(), name="add_instrument"),
]