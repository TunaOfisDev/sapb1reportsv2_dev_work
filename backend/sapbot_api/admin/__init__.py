# backend/sapbot_api/admin/__init__.py
"""
SAPBot API Admin Configuration

Django admin interface için tüm admin sınıfları ve
custom view'ları bu modülde organize edilir.
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import render

# Model admin'lerini import et
from .document_admin import (
    DocumentSourceAdmin,
    KnowledgeChunkAdmin,
    DocumentAnalyticsView,
    BulkDocumentProcessView,
    admin_site  # Custom admin site
)

from .chat_admin import (
    ChatConversationAdmin,
    ChatMessageAdmin,
    MessageFeedbackAdmin
)

from .user_admin import (
    UserProfileAdmin,
    UserPreferencesAdmin,
    UserSessionAdmin,
    UserActivityAdmin
)

from .analytics_admin import (
    QueryAnalyticsAdmin,
    UserFeedbackAdmin,
    UsageStatisticsAdmin,
    PerformanceMetricsAdmin,
    ErrorLogAdmin
)

from .system_admin import (
    SystemConfigurationAdmin,
    SystemMetricsAdmin,
    SystemLogAdmin,
    SystemHealthAdmin
)

# Model'leri import et
from ..models import (
    # Document models
    DocumentSource,
    KnowledgeChunk,
    
    # Chat models
    ChatConversation,
    ChatMessage,
    MessageFeedback,
    
    # User models
    UserProfile,
    UserPreferences,
    UserSession,
    UserActivity,
    
    # Analytics models
    QueryAnalytics,
    UserFeedback,
    UsageStatistics,
    PerformanceMetrics,
    ErrorLog,
    
    # System models
    SystemConfiguration,
    SystemMetrics,
    SystemLog,
    SystemHealth
)

# Admin site customization
admin.site.site_header = 'SAPBot API Yönetimi'
admin.site.site_title = 'SAPBot Admin'
admin.site.index_title = 'SAPBot API Administration Panel'

# Chat models
admin.site.register(ChatConversation, ChatConversationAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(MessageFeedback, MessageFeedbackAdmin)

# User models
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)
admin.site.register(UserSession, UserSessionAdmin)
admin.site.register(UserActivity, UserActivityAdmin)

# Analytics models
admin.site.register(QueryAnalytics, QueryAnalyticsAdmin)
admin.site.register(UserFeedback, UserFeedbackAdmin)
admin.site.register(UsageStatistics, UsageStatisticsAdmin)
admin.site.register(PerformanceMetrics, PerformanceMetricsAdmin)
admin.site.register(ErrorLog, ErrorLogAdmin)

# System models
admin.site.register(SystemConfiguration, SystemConfigurationAdmin)
admin.site.register(SystemMetrics, SystemMetricsAdmin)
admin.site.register(SystemLog, SystemLogAdmin)
admin.site.register(SystemHealth, SystemHealthAdmin)

# Custom dashboard view
def admin_dashboard_view(request):
    """Custom admin dashboard"""
    context = {
        'title': 'SAPBot API Dashboard',
        'app_list': admin.site.get_app_list(request),
    }
    return render(request, 'admin/sapbot_dashboard.html', context)

# Admin customizations
class SAPBotAdminConfig:
    """SAPBot admin konfigürasyon sınıfı"""
    
    @staticmethod
    def customize_admin():
        """Admin interface'i özelleştir"""
        
        # Admin CSS/JS dosyaları
        admin.site.enable_nav_sidebar = True
        
        # Custom actions
        admin.site.add_action(admin.actions.delete_selected, 'delete_selected')
        
        # Index template
        admin.site.index_template = 'admin/sapbot_index.html'
        
        return True

# Konfigürasyonu uygula
SAPBotAdminConfig.customize_admin()

# Tüm admin class'ları export et
__all__ = [
    # Document admins
    'DocumentSourceAdmin',
    'KnowledgeChunkAdmin',
    'DocumentAnalyticsView',
    'BulkDocumentProcessView',
    
    # Chat admins
    'ChatConversationAdmin',
    'ChatMessageAdmin',
    'MessageFeedbackAdmin',
    
    # User admins
    'UserProfileAdmin',
    'UserPreferencesAdmin',
    'UserSessionAdmin',
    'UserActivityAdmin',
    
    # Analytics admins
    'QueryAnalyticsAdmin',
    'UserFeedbackAdmin',
    'UsageStatisticsAdmin',
    'PerformanceMetricsAdmin',
    'ErrorLogAdmin',
    
    # System admins
    'SystemConfigurationAdmin',
    'SystemMetricsAdmin',
    'SystemLogAdmin',
    'SystemHealthAdmin',
    
    # Utilities
    'admin_dashboard_view',
    'SAPBotAdminConfig',
    'admin_site'
]