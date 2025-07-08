# backend/shipweekplanner/serializers.py
from rest_framework import serializers
from .models.models import ShipmentOrder
from datetime import datetime, date

class ShipmentOrderSerializer(serializers.ModelSerializer):
    planned_dates = serializers.ListField(child=serializers.DateField(), required=False)

    class Meta:
        model = ShipmentOrder
        fields = [
            'id', 'order_number', 'customer_name', 'order_date',
            'planned_dates', 'planned_date_mirror', 'planned_date_real',
            'planned_date_week', 'shipment_date', 'sales_person',
            'shipment_details', 'shipment_notes', 'order_status',
            'created_at', 'updated_at', 'selected_color'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        date_fields = ['order_date', 'shipment_date', 'planned_date_real', 'planned_date_mirror', 'created_at', 'updated_at']

        for field in date_fields:
            value = representation.get(field)
            if value and isinstance(value, (date, datetime)):
                representation[field] = value.isoformat()

        if instance.planned_dates:
            representation['planned_dates'] = [
                d.isoformat() if isinstance(d, (date, datetime)) else str(d)
                for d in instance.planned_dates if d is not None
            ]

        return representation

    def to_internal_value(self, data):
        if 'planned_dates' in data and isinstance(data['planned_dates'], list):
            data['planned_dates'] = [
                datetime.strptime(d, "%Y-%m-%d").date() if isinstance(d, str) else d
                for d in data['planned_dates'] if d is not None
            ]
        return super().to_internal_value(data)