from django.conf.urls import url, include

from strategies.views import (
		StrategyListingCustomerView,
		SubSectorAddView,
		AddStrategyView,
		SectorAddView
	)

urlpatterns = [
	url(r'^create/$', AddStrategyView.as_view(), name="create_strategy"),
	url(r'^listing/$', StrategyListingCustomerView.as_view(), name="strategy_listing"),
]