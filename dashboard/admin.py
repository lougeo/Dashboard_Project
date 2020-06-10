from django.contrib import admin
from .models import *

admin.site.register(Report)
admin.site.register(ReportStandard)
admin.site.register(ReportStandardParametersCompression)
admin.site.register(ReportStandardParametersSieve)
admin.site.register(ConcreteSample)
admin.site.register(SieveSample)


