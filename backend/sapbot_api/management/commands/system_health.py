# backend/sapbot_api/management/commands/system_health.py
import os
import json
import csv
import time
import psutil
import logging
from django.db import models
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import requests
import redis
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone


from sapbot_api.models import SystemHealth
from sapbot_api.utils.cache_utils import CacheManager
from sapbot_api.utils.helpers import format_file_size

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Health check sonucu"""
    component: str
    status: str  # healthy, warning, critical, down
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = timezone.now()
        if self.details is None:
            self.details = {}


class SystemHealthChecker:
    """Sistem sağlık kontrolcüsü"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.results: List[HealthCheckResult] = []
        
    def check_database(self) -> HealthCheckResult:
        """PostgreSQL veritabanı kontrolü"""
        try:
            start_time = time.time()
            
            with connection.cursor() as cursor:
                # Basit bağlantı testi
                cursor.execute("SELECT 1")
                
                # Performans testi
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_connections,
                        SUM(CASE WHEN state = 'active' THEN 1 ELSE 0 END) as active_connections
                    FROM pg_stat_activity
                    WHERE datname = %s
                """, [settings.DATABASES['default']['NAME']])
                
                conn_stats = cursor.fetchone()
                
                # Disk kullanımı
                cursor.execute("SELECT pg_database_size(%s)", [settings.DATABASES['default']['NAME']])
                db_size = cursor.fetchone()[0]
                
                response_time = time.time() - start_time
                
                # Durum değerlendirmesi
                if response_time > 2.0:
                    status = "warning"
                elif response_time > 5.0:
                    status = "critical"
                else:
                    status = "healthy"
                
                return HealthCheckResult(
                    component="database",
                    status=status,
                    response_time=response_time,
                    details={
                        "total_connections": conn_stats[0],
                        "active_connections": conn_stats[1],
                        "database_size": format_file_size(db_size),
                        "database_size_bytes": db_size
                    }
                )
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return HealthCheckResult(
                component="database",
                status="critical",
                error_message=str(e)
            )
    
    def check_redis(self) -> HealthCheckResult:
        """Redis cache kontrolü"""
        try:
            start_time = time.time()
            
            # Redis bağlantı testi
            redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB_SAPBOT', 3),
                password=getattr(settings, 'REDIS_PASS', None),
                socket_timeout=5
            )
            
            # Ping testi
            redis_client.ping()
            
            # Memory kullanımı
            info = redis_client.info('memory')
            used_memory = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            
            # Test key yazma/okuma
            test_key = "sapbot_health_check"
            redis_client.set(test_key, "test_value", ex=60)
            redis_client.get(test_key)
            redis_client.delete(test_key)
            
            response_time = time.time() - start_time
            
            # Durum değerlendirmesi
            memory_usage = (used_memory / max_memory * 100) if max_memory > 0 else 0
            
            if memory_usage > 90 or response_time > 1.0:
                status = "critical"
            elif memory_usage > 75 or response_time > 0.5:
                status = "warning"
            else:
                status = "healthy"
            
            return HealthCheckResult(
                component="redis",
                status=status,
                response_time=response_time,
                details={
                    "used_memory": format_file_size(used_memory),
                    "used_memory_bytes": used_memory,
                    "max_memory": format_file_size(max_memory) if max_memory else "unlimited",
                    "memory_usage_percent": round(memory_usage, 2),
                    "connected_clients": info.get('connected_clients', 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return HealthCheckResult(
                component="redis",
                status="critical",
                error_message=str(e)
            )
    
    def check_openai_api(self) -> HealthCheckResult:
        """OpenAI API kontrolü"""
        try:
            start_time = time.time()
            
            openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not openai_api_key:
                return HealthCheckResult(
                    component="openai_api",
                    status="warning",
                    error_message="OpenAI API key not configured"
                )
            
            # Models endpoint'ini test et
            headers = {
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                models = response.json().get('data', [])
                gpt_models = [m for m in models if 'gpt' in m.get('id', '').lower()]
                
                status = "healthy"
            elif response.status_code == 401:
                status = "critical"
                error_message = "Invalid API key"
            elif response.status_code == 429:
                status = "warning"
                error_message = "Rate limited"
            else:
                status = "warning"
                error_message = f"HTTP {response.status_code}"
            
            return HealthCheckResult(
                component="openai_api",
                status=status,
                response_time=response_time,
                error_message=locals().get('error_message'),
                details={
                    "available_models": len(gpt_models) if 'gpt_models' in locals() else 0,
                    "status_code": response.status_code
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI API health check failed: {e}")
            return HealthCheckResult(
                component="openai_api",
                status="critical",
                error_message=str(e)
            )
    
    def check_disk_space(self) -> HealthCheckResult:
        """Disk alanı kontrolü"""
        try:
            # Ana disk kullanımı
            disk_usage = psutil.disk_usage('/')
            
            # Media files disk kullanımı
            media_root = getattr(settings, 'MEDIA_ROOT', '/tmp')
            if os.path.exists(media_root):
                media_usage = psutil.disk_usage(media_root)
            else:
                media_usage = disk_usage
            
            # Yüzde hesaplama
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            media_percent = (media_usage.used / media_usage.total) * 100
            
            # Durum değerlendirmesi
            if disk_percent > 95 or media_percent > 95:
                status = "critical"
            elif disk_percent > 85 or media_percent > 85:
                status = "warning"
            else:
                status = "healthy"
            
            return HealthCheckResult(
                component="disk_space",
                status=status,
                details={
                    "root_total": format_file_size(disk_usage.total),
                    "root_used": format_file_size(disk_usage.used),
                    "root_free": format_file_size(disk_usage.free),
                    "root_percent": round(disk_percent, 2),
                    "media_total": format_file_size(media_usage.total),
                    "media_used": format_file_size(media_usage.used),
                    "media_free": format_file_size(media_usage.free),
                    "media_percent": round(media_percent, 2)
                }
            )
            
        except Exception as e:
            logger.error(f"Disk space health check failed: {e}")
            return HealthCheckResult(
                component="disk_space",
                status="critical",
                error_message=str(e)
            )
    
    def check_memory_usage(self) -> HealthCheckResult:
        """Memory kullanımı kontrolü"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Durum değerlendirmesi
            if memory.percent > 95:
                status = "critical"
            elif memory.percent > 85:
                status = "warning"
            else:
                status = "healthy"
            
            return HealthCheckResult(
                component="memory",
                status=status,
                details={
                    "total": format_file_size(memory.total),
                    "available": format_file_size(memory.available),
                    "used": format_file_size(memory.used),
                    "percent": memory.percent,
                    "swap_total": format_file_size(swap.total),
                    "swap_used": format_file_size(swap.used),
                    "swap_percent": swap.percent
                }
            )
            
        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
            return HealthCheckResult(
                component="memory",
                status="critical",
                error_message=str(e)
            )
    
    def check_celery_workers(self) -> HealthCheckResult:
        """Celery worker kontrolü"""
        try:
            from celery import current_app
            
            # Active workers
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            stats = inspect.stats()
            
            if not active_workers:
                return HealthCheckResult(
                    component="celery",
                    status="critical",
                    error_message="No active Celery workers found"
                )
            
            worker_count = len(active_workers)
            total_active_tasks = sum(len(tasks) for tasks in active_workers.values())
            
            # Worker stats
            worker_details = {}
            for worker_name, worker_stats in (stats or {}).items():
                worker_details[worker_name] = {
                    "pool_writes": worker_stats.get("pool", {}).get("writes", 0),
                    "total": worker_stats.get("total", {}),
                }
            
            # Durum değerlendirmesi
            if worker_count == 0:
                status = "critical"
            elif total_active_tasks > 100:
                status = "warning"
            else:
                status = "healthy"
            
            return HealthCheckResult(
                component="celery",
                status=status,
                details={
                    "active_workers": worker_count,
                    "active_tasks": total_active_tasks,
                    "worker_details": worker_details
                }
            )
            
        except Exception as e:
            logger.error(f"Celery health check failed: {e}")
            return HealthCheckResult(
                component="celery",
                status="warning",
                error_message=str(e)
            )
    
    def check_document_processing(self) -> HealthCheckResult:
        """Döküman işleme sistemi kontrolü"""
        try:
            from sapbot_api.models import DocumentSource
            
            # Son 24 saatteki işlemler
            last_24h = timezone.now() - timedelta(hours=24)
            
            recent_docs = DocumentSource.objects.filter(
                created_at__gte=last_24h
            ).values('processing_status').annotate(
                count=models.Count('id')
            )
            
            status_counts = {item['processing_status']: item['count'] for item in recent_docs}
            
            total_docs = sum(status_counts.values())
            failed_docs = status_counts.get('failed', 0)
            processing_docs = status_counts.get('processing', 0)
            
            # Durum değerlendirmesi
            if total_docs > 0:
                failure_rate = (failed_docs / total_docs) * 100
                if failure_rate > 50:
                    status = "critical"
                elif failure_rate > 25 or processing_docs > 10:
                    status = "warning"
                else:
                    status = "healthy"
            else:
                status = "healthy"  # No recent activity
            
            return HealthCheckResult(
                component="document_processing",
                status=status,
                details={
                    "total_last_24h": total_docs,
                    "status_breakdown": status_counts,
                    "failure_rate_percent": round(failure_rate, 2) if total_docs > 0 else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Document processing health check failed: {e}")
            return HealthCheckResult(
                component="document_processing",
                status="warning",
                error_message=str(e)
            )
    
    def check_api_endpoints(self) -> HealthCheckResult:
        """Temel API endpoint'leri kontrolü"""
        try:
            from django.test import Client
            
            client = Client()
            endpoints_to_check = [
                '/api/sapbot/v1/health/',
                '/api/sapbot/v1/system/stats/',
            ]
            
            results = {}
            total_response_time = 0
            failed_endpoints = 0
            
            for endpoint in endpoints_to_check:
                try:
                    start_time = time.time()
                    response = client.get(endpoint)
                    response_time = time.time() - start_time
                    
                    results[endpoint] = {
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "success": response.status_code < 400
                    }
                    
                    total_response_time += response_time
                    if response.status_code >= 400:
                        failed_endpoints += 1
                        
                except Exception as e:
                    results[endpoint] = {
                        "error": str(e),
                        "success": False
                    }
                    failed_endpoints += 1
            
            avg_response_time = total_response_time / len(endpoints_to_check)
            
            # Durum değerlendirmesi
            if failed_endpoints > 0:
                status = "critical"
            elif avg_response_time > 2.0:
                status = "warning"
            else:
                status = "healthy"
            
            return HealthCheckResult(
                component="api_endpoints",
                status=status,
                response_time=avg_response_time,
                details={
                    "endpoints_checked": len(endpoints_to_check),
                    "failed_endpoints": failed_endpoints,
                    "avg_response_time": avg_response_time,
                    "endpoint_results": results
                }
            )
            
        except Exception as e:
            logger.error(f"API endpoints health check failed: {e}")
            return HealthCheckResult(
                component="api_endpoints",
                status="critical",
                error_message=str(e)
            )
    
    def run_all_checks(self) -> List[HealthCheckResult]:
        """Tüm sağlık kontrollerini çalıştır"""
        checks = [
            self.check_database,
            self.check_redis,
            self.check_openai_api,
            self.check_disk_space,
            self.check_memory_usage,
            self.check_celery_workers,
            self.check_document_processing,
            self.check_api_endpoints,
        ]
        
        results = []
        for check in checks:
            try:
                result = check()
                results.append(result)
                logger.info(f"Health check {result.component}: {result.status}")
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                results.append(HealthCheckResult(
                    component="unknown",
                    status="critical",
                    error_message=str(e)
                ))
        
        self.results = results
        return results


class HealthReportGenerator:
    """Sağlık raporu oluşturucu"""
    
    def __init__(self, results: List[HealthCheckResult]):
        self.results = results
        self.timestamp = timezone.now()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Özet rapor oluştur"""
        total_checks = len(self.results)
        healthy = len([r for r in self.results if r.status == "healthy"])
        warning = len([r for r in self.results if r.status == "warning"])
        critical = len([r for r in self.results if r.status == "critical"])
        down = len([r for r in self.results if r.status == "down"])
        
        # Genel durum
        if critical > 0 or down > 0:
            overall_status = "critical"
        elif warning > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "timestamp": self.timestamp,
            "overall_status": overall_status,
            "total_checks": total_checks,
            "healthy": healthy,
            "warning": warning,
            "critical": critical,
            "down": down,
            "success_rate": round((healthy / total_checks) * 100, 2) if total_checks > 0 else 0
        }
    
    def export_json_report(self, file_path: str):
        """JSON formatında rapor"""
        report_data = {
            "summary": self.generate_summary(),
            "checks": [asdict(result) for result in self.results]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
    
    def export_csv_report(self, file_path: str):
        """CSV formatında rapor"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Component', 'Status', 'Response Time', 'Error Message', 'Timestamp'
            ])
            
            for result in self.results:
                writer.writerow([
                    result.component,
                    result.status,
                    result.response_time or '',
                    result.error_message or '',
                    result.timestamp
                ])
    
    def export_html_report(self, file_path: str):
        """HTML formatında rapor"""
        summary = self.generate_summary()
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>SAPBot System Health Report</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status-healthy { color: #28a745; font-weight: bold; }
        .status-warning { color: #ffc107; font-weight: bold; }
        .status-critical { color: #dc3545; font-weight: bold; }
        .status-down { color: #6c757d; font-weight: bold; }
        .component { 
            margin: 15px 0; 
            padding: 20px; 
            border: 1px solid #e9ecef;
            border-radius: 6px;
            background: #f8f9fa;
        }
        .component h3 {
            margin-top: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .issues { 
            background-color: #fff3cd; 
            padding: 15px; 
            margin: 15px 0;
            border-radius: 6px;
            border-left: 4px solid #ffc107;
        }
        .critical-issues {
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            background: #fff;
            padding: 20px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            text-align: center;
        }
        .summary-card h3 {
            margin-top: 0;
            color: #6c757d;
            font-size: 14px;
            text-transform: uppercase;
        }
        .summary-card .value {
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }
        .details-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .details-table th, .details-table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }
        .details-table th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
        }
        .emoji { font-size: 24px; margin-right: 10px; }
        .response-time {
            font-size: 12px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 SAPBot System Health Report</h1>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <p><strong>Overall Status:</strong> 
                <span class="status-{overall_status}">
                    {status_emoji} {overall_status_text}
                </span>
            </p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Checks</h3>
                <div class="value">{total_checks}</div>
            </div>
            <div class="summary-card">
                <h3>Healthy</h3>
                <div class="value status-healthy">{healthy}</div>
            </div>
            <div class="summary-card">
                <h3>Warning</h3>
                <div class="value status-warning">{warning}</div>
            </div>
            <div class="summary-card">
                <h3>Critical</h3>
                <div class="value status-critical">{critical}</div>
            </div>
            <div class="summary-card">
                <h3>Success Rate</h3>
                <div class="value">{success_rate}%</div>
            </div>
        </div>
        
        {issues_section}
        
        <h2>📊 Component Details</h2>
        {components_html}
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e9ecef; color: #6c757d; text-align: center; font-size: 12px;">
            Generated by SAPBot System Health Monitor • {timestamp}
        </div>
    </div>
</body>
</html>"""
        
        # Status emoji ve text
        status_emojis = {
            "healthy": "✅",
            "warning": "⚠️", 
            "critical": "❌",
            "down": "💀"
        }
        
        status_texts = {
            "healthy": "ALL SYSTEMS OPERATIONAL",
            "warning": "SOME ISSUES DETECTED", 
            "critical": "CRITICAL ISSUES FOUND",
            "down": "SYSTEM DOWN"
        }
        
        # Issues section
        issues_html = ""
        critical_components = [r for r in self.results if r.status in ['critical', 'down']]
        warning_components = [r for r in self.results if r.status == 'warning']
        
        if critical_components:
            issues_html += '<div class="issues critical-issues">'
            issues_html += '<h3>🚨 Critical Issues</h3><ul>'
            for comp in critical_components:
                issues_html += f'<li><strong>{comp.component}</strong>: {comp.error_message or "Status: " + comp.status}</li>'
            issues_html += '</ul></div>'
        
        if warning_components:
            issues_html += '<div class="issues">'
            issues_html += '<h3>⚠️ Warnings</h3><ul>'
            for comp in warning_components:
                issues_html += f'<li><strong>{comp.component}</strong>: {comp.error_message or "Status: " + comp.status}</li>'
            issues_html += '</ul></div>'
        
        # Components HTML
        components_html = ""
        for result in self.results:
            response_time_html = ""
            if result.response_time:
                response_time_html = f'<span class="response-time">({result.response_time:.3f}s)</span>'
            
            status_emoji = status_emojis.get(result.status, "❓")
            
            details_html = ""
            if result.details:
                details_html = '<table class="details-table"><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>'
                for key, value in result.details.items():
                    details_html += f'<tr><td>{key.replace("_", " ").title()}</td><td>{value}</td></tr>'
                details_html += '</tbody></table>'
            
            error_html = ""
            if result.error_message:
                error_html = f'<div style="color: #dc3545; margin-top: 10px;"><strong>Error:</strong> {result.error_message}</div>'
            
            components_html += f"""
            <div class="component">
                <h3>
                    <span>{status_emoji} {result.component.replace('_', ' ').title()}</span>
                    <span class="status-{result.status}">{result.status.upper()} {response_time_html}</span>
                </h3>
                {error_html}
                {details_html}
            </div>"""
        
        # Template'i doldur
        html_content = html_template.format(
            timestamp=summary['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC'),
            overall_status=summary['overall_status'],
            status_emoji=status_emojis.get(summary['overall_status'], "❓"),
            overall_status_text=status_texts.get(summary['overall_status'], "UNKNOWN"),
            total_checks=summary['total_checks'],
            healthy=summary['healthy'],
            warning=summary['warning'],
            critical=summary['critical'],
            success_rate=summary['success_rate'],
            issues_section=issues_html,
            components_html=components_html
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)


class Command(BaseCommand):
    help = 'SAPBot sistem sağlığını kontrol eder ve rapor oluşturur'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv', 'html', 'console'],
            default='console',
            help='Rapor formatı'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output dosya yolu'
        )
        parser.add_argument(
            '--save-db',
            action='store_true',
            help='Sonuçları veritabanına kaydet'
        )
        parser.add_argument(
            '--components',
            type=str,
            nargs='+',
            choices=[
                'database', 'redis', 'openai_api', 'disk_space', 
                'memory', 'celery', 'document_processing', 'api_endpoints'
            ],
            help='Sadece belirtilen bileşenleri kontrol et'
        )
        parser.add_argument(
            '--alert',
            action='store_true',
            help='Kritik sorunlar için alert gönder'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🏥 SAPBot sistem sağlık kontrolü başlıyor...")
        
        start_time = time.time()
        checker = SystemHealthChecker()
        
        # Tüm kontrolları çalıştır
        results = checker.run_all_checks()
        
        total_time = time.time() - start_time
        
        # Rapor oluştur
        report_generator = HealthReportGenerator(results)
        summary = report_generator.generate_summary()
        
        # Console output
        self.display_console_report(summary, results)
        
        # Dosya export
        if options['output']:
            output_file = options['output']
            format_type = options['format']
            
            try:
                if format_type == 'json':
                    report_generator.export_json_report(output_file)
                elif format_type == 'csv':
                    report_generator.export_csv_report(output_file)
                elif format_type == 'html':
                    report_generator.export_html_report(output_file)
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Rapor kaydedildi: {output_file}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Rapor kaydetme hatası: {e}")
                )
        
        # Veritabanına kaydet
        if options['save_db']:
            self.save_to_database(results)
        
        # Alert gönder
        if options['alert']:
            self.send_alerts(summary, results)
        
        # Özet bilgi
        self.stdout.write(f"\n⏱️ Toplam süre: {total_time:.2f} saniye")
        self.stdout.write(f"📊 {len(results)} bileşen kontrol edildi")
        
        # Exit code
        if summary['overall_status'] in ['critical', 'down']:
            exit(1)
        elif summary['overall_status'] == 'warning':
            exit(2)
        else:
            exit(0)
    
    def display_console_report(self, summary: Dict[str, Any], results: List[HealthCheckResult]):
        """Console'da rapor göster"""
        
        # Header
        self.stdout.write("\n" + "="*60)
        self.stdout.write("🏥 SAPBOT SİSTEM SAĞLIK RAPORU")
        self.stdout.write("="*60)
        
        # Overall status
        status_colors = {
            'healthy': self.style.SUCCESS,
            'warning': self.style.WARNING,
            'critical': self.style.ERROR,
            'down': self.style.ERROR
        }
        
        status_emojis = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌', 
            'down': '💀'
        }
        
        overall_status = summary['overall_status']
        color_func = status_colors.get(overall_status, self.style.WARNING)
        emoji = status_emojis.get(overall_status, '❓')
        
        self.stdout.write(f"\n🎯 Genel Durum: {color_func(f'{emoji} {overall_status.upper()}')}")
        self.stdout.write(f"📅 Tarih: {summary['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary stats
        self.stdout.write(f"\n📊 ÖZET:")
        self.stdout.write(f"   Toplam Kontrol: {summary['total_checks']}")
        self.stdout.write(f"   Sağlıklı: {self.style.SUCCESS(str(summary['healthy']))} ✅")
        self.stdout.write(f"   Uyarı: {self.style.WARNING(str(summary['warning']))} ⚠️")
        self.stdout.write(f"   Kritik: {self.style.ERROR(str(summary['critical']))} ❌")
        self.stdout.write(f"   Başarı Oranı: {summary['success_rate']}%")
        
        # Critical issues first
        critical_results = [r for r in results if r.status in ['critical', 'down']]
        if critical_results:
            self.stdout.write(f"\n🚨 KRİTİK SORUNLAR:")
            for result in critical_results:
                self.stdout.write(
                    f"   ❌ {result.component}: {result.error_message or result.status}"
                )
        
        # Warning issues
        warning_results = [r for r in results if r.status == 'warning']
        if warning_results:
            self.stdout.write(f"\n⚠️ UYARILAR:")
            for result in warning_results:
                self.stdout.write(
                    f"   ⚠️ {result.component}: {result.error_message or result.status}"
                )
        
        # Detailed results
        self.stdout.write(f"\n📋 DETAYLAR:")
        self.stdout.write("-" * 60)
        
        for result in results:
            # Component header
            status_symbol = status_emojis.get(result.status, '❓')
            color_func = status_colors.get(result.status, self.style.WARNING)
            
            response_time_info = ""
            if result.response_time:
                response_time_info = f" ({result.response_time:.3f}s)"
            
            self.stdout.write(
                f"\n{status_symbol} {result.component.upper().replace('_', ' ')}: "
                f"{color_func(result.status.upper())}{response_time_info}"
            )
            
            # Error message
            if result.error_message:
                self.stdout.write(f"   ❗ Hata: {result.error_message}")
            
            # Details
            if result.details:
                self.stdout.write("   📄 Detaylar:")
                for key, value in result.details.items():
                    key_display = key.replace('_', ' ').title()
                    self.stdout.write(f"      • {key_display}: {value}")
        
        self.stdout.write("\n" + "="*60)
    
    def save_to_database(self, results: List[HealthCheckResult]):
        """Sonuçları veritabanına kaydet"""
        try:
            with transaction.atomic():
                for result in results:
                    SystemHealth.objects.create(
                        component=result.component,
                        status=result.status,
                        response_time=result.response_time,
                        error_message=result.error_message,
                        details=result.details or {}
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ {len(results)} sonuç veritabanına kaydedildi")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Veritabanı kayıt hatası: {e}")
            )
    
    def send_alerts(self, summary: Dict[str, Any], results: List[HealthCheckResult]):
        """Kritik durumlar için alert gönder"""
        try:
            if summary['overall_status'] not in ['critical', 'down']:
                self.stdout.write("📧 Alert gönderilmedi: Kritik sorun yok")
                return
            
            # Critical ve down olan bileşenler
            critical_components = [
                r for r in results 
                if r.status in ['critical', 'down']
            ]
            
            if not critical_components:
                return
            
            # Email alert (örnek)
            subject = f"🚨 SAPBot Sistem Uyarısı - {summary['overall_status'].upper()}"
            
            message_parts = [
                f"SAPBot sisteminde kritik sorunlar tespit edildi!\n",
                f"Tarih: {summary['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                f"Genel Durum: {summary['overall_status'].upper()}",
                f"Kritik Bileşen Sayısı: {len(critical_components)}\n",
                "Kritik Sorunlar:"
            ]
            
            for comp in critical_components:
                message_parts.append(
                    f"- {comp.component}: {comp.error_message or comp.status}"
                )
            
            message_parts.append(f"\nLütfen sistemie acilen müdahale edin!")
            
            email_message = "\n".join(message_parts)
            
            # Django email gönderimi (örnek)
            from django.core.mail import mail_admins
            
            mail_admins(
                subject=subject,
                message=email_message,
                fail_silently=False
            )
            
            self.stdout.write(
                self.style.WARNING(f"📧 Alert gönderildi: {len(critical_components)} kritik sorun")
            )
            
            # Slack webhook (örnek)
            slack_webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
            if slack_webhook_url:
                self.send_slack_alert(slack_webhook_url, summary, critical_components)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Alert gönderme hatası: {e}")
            )
    
    def send_slack_alert(self, webhook_url: str, summary: Dict[str, Any], critical_components: List[HealthCheckResult]):
        """Slack'e alert gönder"""
        try:
            status_emojis = {
                'healthy': ':white_check_mark:',
                'warning': ':warning:',
                'critical': ':x:',
                'down': ':skull:'
            }
            
            emoji = status_emojis.get(summary['overall_status'], ':question:')
            
            slack_payload = {
                "username": "SAPBot Health Monitor",
                "icon_emoji": ":hospital:",
                "attachments": [
                    {
                        "color": "danger" if summary['overall_status'] in ['critical', 'down'] else "warning",
                        "title": f"{emoji} SAPBot System Alert",
                        "title_link": "https://your-domain.com/admin/",
                        "fields": [
                            {
                                "title": "Overall Status",
                                "value": summary['overall_status'].upper(),
                                "short": True
                            },
                            {
                                "title": "Critical Issues",
                                "value": str(len(critical_components)),
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": summary['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC'),
                                "short": True
                            }
                        ],
                        "text": "\n".join([
                            f"• *{comp.component}*: {comp.error_message or comp.status}"
                            for comp in critical_components[:5]  # İlk 5 sorun
                        ]),
                        "footer": "SAPBot Health Monitor",
                        "ts": int(summary['timestamp'].timestamp())
                    }
                ]
            }
            
            response = requests.post(
                webhook_url,
                json=slack_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS("📱 Slack alert gönderildi")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"📱 Slack alert hatası: {response.status_code}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"📱 Slack alert hatası: {e}")
            )
    
    def cleanup_old_health_records(self, days: int = 30):
        """Eski sağlık kayıtlarını temizle"""
        try:
            cutoff_date = timezone.now() - timedelta(days=days)
            deleted_count = SystemHealth.objects.filter(
                created_at__lt=cutoff_date
            ).delete()[0]
            
            if deleted_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"🧹 {deleted_count} eski kayıt temizlendi")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"🧹 Temizleme hatası: {e}")
            )