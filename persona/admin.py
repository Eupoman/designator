from django.contrib import admin
from persona.models import Benefactors, Benefactor, UserStatus, BenefactorProfile, TrainingData


admin.site.register(Benefactors)
admin.site.register(TrainingData)
admin.site.register(Benefactor)
admin.site.register(UserStatus)
admin.site.register(BenefactorProfile)
