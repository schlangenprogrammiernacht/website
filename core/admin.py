from django.contrib import admin

from core.models import SnakeVersion, SnakeGame, ServerCommand, UserProfile, ApiKey

admin.site.register(SnakeVersion)
admin.site.register(SnakeGame)
admin.site.register(UserProfile)
admin.site.register(ApiKey)


class ServerCommandAdmin(admin.ModelAdmin):
    list_display = ('user', 'dt_created', 'dt_processed', 'command', 'result', 'result_msg')


admin.site.register(ServerCommand, ServerCommandAdmin)
