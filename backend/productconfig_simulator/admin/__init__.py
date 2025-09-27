# backend/productconfig_simulator/admin/__init__.py
from django.contrib import admin
from ..models.simulation_job import SimulationJob
from ..models.simulated_variant import SimulatedVariant
from ..models.simulation_error import SimulationError
from .simulation_job_admin import SimulationJobAdmin
from .simulated_variant_admin import SimulatedVariantAdmin
from .simulation_error_admin import SimulationErrorAdmin

# Admin paneli kayıtları
admin.site.register(SimulationJob, SimulationJobAdmin)
admin.site.register(SimulatedVariant, SimulatedVariantAdmin)
admin.site.register(SimulationError, SimulationErrorAdmin)

# __all__ tanımlaması - dışarıdan import edilebilecek sınıfları belirtir
__all__ = [
    'SimulationJobAdmin',
    'SimulatedVariantAdmin', 
    'SimulationErrorAdmin',
]