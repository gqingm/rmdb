from django.contrib import admin
from R6K import models

admin.site.register(models.user_info)
admin.site.register(models.line_manager)
admin.site.register(models.node_info)
admin.site.register(models.node2user)
admin.site.register(models.utilization)
admin.site.register(models.event)