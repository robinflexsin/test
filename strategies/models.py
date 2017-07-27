from django.db import models

from api_login.models import User, MarketSector


class StrategyStatus(models.Model):
	name = models.CharField(max_length=50)

	class Meta:
		db_table = "strategy_status"

class Strategy(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	description = models.TextField(blank=True, null=True)
	product_category = models.CharField(max_length=50, blank=True, null=True)
	product_type = models.CharField(max_length=50, blank=True, null=True)
	strategy_type = models.CharField(max_length=50, blank=True, null=True)
	trade_info = models.TextField(blank=True, null=True)
	status = models.ForeignKey(StrategyStatus, on_delete=models.CASCADE)
	ratio = models.CharField(max_length=50, blank=True, null=True)
	delta = models.CharField(max_length=50, blank=True, null=True)
	ref = models.CharField(max_length=50, blank=True, null=True)
	loss_target = models.FloatField(default= 0.0, blank=True, null=True)
	profit_target = models.FloatField(default=0.0, blank=True, null=True)
	created_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "strategies"


class Legs(models.Model):
	strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
	type = models.CharField(max_length=50, blank=True, null=True)
	product_type = models.CharField(max_length=50, blank=True, null=True)
	term = models.CharField(max_length=50, blank=True, null=True)
	strike_price = models.CharField(max_length=50, blank=True, null=True)

	class Meta:
		db_table = "strategies_legs"


class MarketSubSector(models.Model):
	market_sector = models.ForeignKey(MarketSector, on_delete=models.CASCADE)
	sub_sector_name = models.CharField(max_length=100)
	sub_sector_description = models.TextField(blank=True, null=True)
	status = models.BooleanField(default=True)
	created_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "market_sub_sector"


class MarketSectorAuthUser(models.Model):
	trader = models.ForeignKey(User, on_delete=models.CASCADE)
	market_sub_sector = models.ForeignKey(MarketSubSector, on_delete=models.CASCADE)
	status = models.BooleanField(default=True)
	created_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "market_sub_sector_auth_user"


class Month(models.Model):
	month_name = models.CharField(max_length=100)
	month_code = models.CharField(max_length=100)

	class Meta:
		db_table = "month"


class Instrument(models.Model):
	market_sub_sector = models.ForeignKey(MarketSubSector, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	type = models.CharField(max_length=50)
	months = models.ManyToManyField(Month)
	cqg_symbol = models.CharField(max_length=100)
	description = models.CharField(max_length=100)
	exchange_symbol = models.CharField(max_length=100)
	enable_for_trading = models.BooleanField(default=False)
	price_tick = models.BooleanField(default=True)
	
	# ratio = models.CharField(max_length=100)
	# construction = models.CharField(max_length=100)
	# max_loss_formula = models.CharField(max_length=100)
	# max_loss_description = models.CharField(max_length=100)
	# max_gain_formula = models.CharField(max_length=100)
	# max_gain_description = models.CharField(max_length=100)
	# break_even_formula = models.CharField(max_length=100)
	# break_even_description = models.CharField(max_length=100)
	status = models.BooleanField(default=True)
	created_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "instruments"


class SpreadDefinitions(models.Model):
	contract = models.ManyToManyField(Contracts)
	spread_name = models.CharField(max_length=100)
	spread_code = models.CharField(max_length=100)
	ratio = models.CharField(max_length=100)
	construction = models.CharField(max_length=100)
	spread_description = models.TextField(blank=True, null=True)
	status = models.BooleanField(default=True)
	created_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "spread_definitions"


# class Contracts(models.Model):
# 	market_sub_sector = models.ForeignKey(MarketSubSector, on_delete=models.CASCADE)
# 	contract_name = models.CharField(max_length=100)
# 	cqg_code = models.CharField(max_length=100)
# 	cme_code = models.CharField(max_length=100)
# 	contract_description = models.TextField(blank=True, null=True)
# 	months = models.ManyToManyField(Month)
# 	status = models.BooleanField(default=True)
# 	created_date = models.DateTimeField(auto_now_add=True)

# 	class Meta:
# 		db_table = "contracts"