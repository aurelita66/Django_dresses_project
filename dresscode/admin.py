from django.contrib import admin
from .models import Designer, Size, Style, Dress, DressRental, Profile, DressReview


class DressRentalInline(admin.TabularInline):
    """Įterpiamas modelis, skirtas rodyti DressRental objektus DressAdmin puslapyje"""
    model = DressRental
    extra = 0


class DressAdmin(admin.ModelAdmin):
    """Modelio Dress administravimo klasė.

            list_display: Laukeliai, kurie bus rodomi,
            search_fields: Laukeliai, pagal kuriuos bus galima ieškoti,
            inlines: Įterpiami modeliai (DressRentalInline)"""

    list_display = ('item_code', 'designer', 'display_sizes', 'display_styles')
    search_fields = ('item_code', 'designer__surname')
    inlines = (DressRentalInline,)


class DressRentalAdmin(admin.ModelAdmin):
    """Modelio DressRental administravimo klasė.

            list_display: Laukeliai, kurie bus rodomi,
            list_filter: Laukeliai, pagal kuriuos bus galima filtruoti,
            search_fields: Laukeliai, pagal kuriuos bus galima ieškoti,
            list_editable: Laukeliai, kuriuos galima redaguoti"""

    list_display = ('dress', 'size', 'user', 'start_date', 'return_date', 'status')
    list_filter = ('status', 'return_date', 'user')
    search_fields = ('dress__item_code', 'dress__designer__surname')
    list_editable = ('size', 'start_date', 'return_date', 'status', 'user')


class DesignerAdmin(admin.ModelAdmin):
    """Modelio Designer administravimo klasė.

            list_display: Laukeliai, kurie bus rodomi"""

    list_display = ('name', 'surname')


admin.site.register(Designer, DesignerAdmin)
admin.site.register(Size)
admin.site.register(Style)
admin.site.register(Dress, DressAdmin)
admin.site.register(DressRental, DressRentalAdmin)
admin.site.register(DressReview)
admin.site.register(Profile)
