from django.contrib import admin
from .models import Activity, Category, User

# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username' , 'email' , 'first_name' , 'last_name' , 'avatar' , 'bio' )
    list_filter = ('is_staff', 'is_superuser', 'is_active')




class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'location_city', 'start_time', 'end_time', 'proposer', 'category')
    list_filter = ('category', 'start_time', 'location_city')
    search_fields = ('title', 'description', 'location_city')
    filter_horizontal = ('attendees',)
    date_hierarchy = 'start_time'


admin.site.register(User, CustomUserAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Category, CategoryAdmin)
