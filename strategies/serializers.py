from rest_framework import serializers
from django.db import connection

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

class LegsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legs
        fields = ('type', 'product_type', 'term', 'strike_price')


class StrategySerializer(serializers.ModelSerializer):
    legs = LegsSerializer(many=True)

    class Meta:
        model = Strategy
        fields = (
            'user', 'title', 'description',
            'product_category', 'product_type',
            'trade_info', 'strategy_type',
            'ratio', 'delta', 'ref',
            'loss_target', 'profit_target', 'legs'
        )

    def create(self, validated_data):
        legs_data = validated_data.pop('legs')
        strategy = Strategy.objects.create(**validated_data)
        for legs in legs_data:
            Legs.objects.create(strategy=strategy, **legs)
        return strategy


class MarketSectorAddSerializer(serializers.ModelSerializer):

    class Meta:
        model = MarketSector
        fields = (
            'sector_name',
            'sector_exchange_abbrev',
            'sector_exchange_name',
            'sector_description'
        )


class MarketSubSectorAddSerializer(serializers.ModelSerializer):

    class Meta:
        model = MarketSubSector
        fields = (
            'market_sector',
            'sub_sector_name',
            'sub_sector_description'
        )


class monthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = ('id', 'month_name', 'month_code')
        extra_kwargs = {
            'id': {'read_only': False},
            'month_code': {'required': False}
        }


class ContactsAddSerializer(serializers.ModelSerializer):
    months = monthSerializer(many=True)

    class Meta:
        model = Contracts
        fields = (
            'market_sub_sector',
            'contract_name',
            'cqg_code',
            'cme_code',
            'contract_description',
            'status',
            'months'
        )

    def create(self, validated_data):
        months_data = validated_data.pop('months')
        contract = Contracts.objects.create(**validated_data)
        for month in months_data:
            monthInstance = Month.objects.get(id=month['id'])
            contract.months.add(monthInstance)
        return contract

    def update(self, instance, validated_data):
        months_data = validated_data.pop('months')
        Contracts.objects.filter(id=instance.id).update(**validated_data)
        instance.months.clear()
        for month in months_data:
            monthInstance = Month.objects.get(id=month['id'])
            instance.months.add(monthInstance)
        return instance


class ContractSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contracts
        fields = ( 'id', )
        extra_kwargs = {
            'id': {'read_only': False},
        }


class SpreadsAddSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(many=True)

    class Meta:
        model = Spreads
        fields = (
            'spread_name',
            'spread_code',
            'spread_description', 
            'contract'
        )

    def create(self, validated_data):
        contracts_data = validated_data.pop('contract')
        spred = Spreads.objects.create(**validated_data)
        for contrt in contracts_data:
            contractInstance = Contracts.objects.get(id=contrt['id'])
            spred.contract.add(contractInstance)
        return spred

    def update(self, instance, validated_data):
        contracts_data = validated_data.pop('contract')
        Spreads.objects.filter(id=instance.id).update(**validated_data)
        instance.contract.clear()
        for contrt in contracts_data:
            contractInstance = Contracts.objects.get(id=contrt['id'])
            instance.contract.add(contractInstance)
        return instance


class MarketSubSectorSerialzer(serializers.ModelSerializer):
    class Meta:
        model = MarketSubSector
        fields = (
            'id',
        )
        extra_kwargs = {
            'id': {'read_only': False},
        }


class SubSectorAssignmentSerializer(serializers.ModelSerializer):
    sub_sector = MarketSubSectorSerialzer(many=True)

    class Meta:
        model = SubSectorAssignment
        fields = (
            'trader',
            'sub_sector'
        )

    def create(self, validated_data):
        sub_sector_data = validated_data.pop('sub_sector')
        for sub_sector in sub_sector_data:
            subSectorInstance = MarketSubSector.objects.get(id=sub_sector['id'])
            SubSectorAssignment.objects.create(trader=validated_data['trader'], market_sub_sector=subSectorInstance)
        return True

    def update(self, instance, validated_data):
        sub_sector_data = validated_data.pop('sub_sector')
        traderInstance = validated_data.pop('trader')
        SubSectorAssignment.objects.filter(trader=traderInstance).delete()
        for sub_sector in sub_sector_data:
            subSectorInstance = MarketSubSector.objects.get(id=sub_sector['id'])
            assignmentInstance = SubSectorAssignment.objects.create(trader=traderInstance, market_sub_sector=subSectorInstance)
        return True



class InstrumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Instruments
        fields = (
            'contract', 'name', 'type',
            'description', 'ratio', 'construction', 'max_loss_formula',
            'max_loss_description', 'max_gain_formula', 'max_gain_description',
            'break_even_formula', 'break_even_description', 'exchange_symbol',
            'cqg_symbol', 'status'
        )