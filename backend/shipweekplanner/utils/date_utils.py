# backend/shipweekplanner/utils/date_utils.py
import calendar
from django.db.models import Count, Case, When
from datetime import datetime, timedelta
from ..models.models import ShipmentOrder

def get_week_range(year, week_number):
    """
    Belirli bir yıl ve haftaya göre haftanın başlangıç ve bitiş tarihini döner.
    """
    first_day_of_year = datetime(year, 1, 1)
    # Haftanın ilk gününü al (varsayılan olarak Pazartesi)
    if first_day_of_year.weekday() <= 3:
        first_day_of_year = first_day_of_year - timedelta(days=first_day_of_year.weekday())
    else:
        first_day_of_year = first_day_of_year + timedelta(days=(7 - first_day_of_year.weekday()))
    
    start_of_week = first_day_of_year + timedelta(weeks=week_number - 1)
    end_of_week = start_of_week + timedelta(days=6)
    
    return start_of_week, end_of_week

def get_weekly_calendar_data(year):
    """
    Belirli bir yıl için her hafta başlangıç ve bitiş tarihlerini döner.
    """
    weeks_in_year = calendar.Calendar().yeardayscalendar(year, width=1)  # Yılın haftalarını al
    weekly_data = []
    
    for month_data in weeks_in_year:
        for week in month_data[0]:  # Haftalar listesini al
            # Haftada sadece bir gün varsa boş geç (bu, ayın bittiği ve yeni haftaya geçtiği durumlar içindir)
            if week[0] == 0:
                continue
            
            # Haftanın başı ve sonunu hesapla
            week_number = datetime(year, 1, 1).isocalendar()[1]
            start_of_week, end_of_week = get_week_range(year, week_number)
            weekly_data.append({
                "week_number": week_number,
                "start_date": start_of_week,
                "end_date": end_of_week
            })
    
    return weekly_data

def get_current_week():
    """
    Bugünkü tarihe göre bulunduğumuz haftanın başlangıç ve bitiş tarihini döner.
    """
    today = datetime.now()
    return get_week_range(today.year, today.isocalendar()[1])

def copy_to_next_week(shipment_orders, current_week):
    """
    Bu fonksiyon, SevkTarih alanı boş olan siparişleri bir sonraki haftaya kopyalar.
    """
    next_week_start, next_week_end = get_week_range(current_week.year, current_week.week + 1)
    
    copied_orders = []
    for order in shipment_orders:
        if not order.shipment_date:
            # Yeni siparişi kopyala ve bir sonraki haftanın başlangıç tarihini ayarla
            new_order = order
            new_order.shipment_date = next_week_start
            new_order.save()
            copied_orders.append(new_order)
    
    return copied_orders

def generate_weekly_report(year, week_number):
    """
    Verilen yıl ve hafta numarasına göre haftalık sevk raporu oluşturur.
    """
    start_of_week, end_of_week = get_week_range(year, week_number)
    
    # Belirtilen haftadaki sevk siparişlerini al
    orders = ShipmentOrder.objects.filter(order_date__range=(start_of_week, end_of_week))

    # İstatistikleri hesapla
    stats = orders.aggregate(
        total_orders=Count('id'),
        completed_orders=Count(Case(When(order_status='Kapalı', then=1))),
        open_orders=Count(Case(When(order_status='Açık', then=1)))
    )

    report = {
        "week_number": week_number,
        "start_date": start_of_week.strftime('%Y-%m-%d'),
        "end_date": end_of_week.strftime('%Y-%m-%d'),
        "total_orders": stats['total_orders'],
        "completed_orders": stats['completed_orders'],
        "open_orders": stats['open_orders'],
        "completion_rate": (stats['completed_orders'] / stats['total_orders'] * 100) if stats['total_orders'] > 0 else 0
    }

    return report
