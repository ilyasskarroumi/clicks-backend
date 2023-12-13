from django.contrib import admin

from api.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Client)
admin.site.register(Payment)
admin.site.register(Campaign)
admin.site.register(Product)
admin.site.register(Page)
admin.site.register(VoiceOver)
admin.site.register(Creative)