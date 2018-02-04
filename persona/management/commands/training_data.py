import csv
import sys
from django.conf import settings
from django.utils import timezone
from persona.models import TrainingData
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Populate training data from csv'

    def handle(self, *args, **options):
        path = "training_data.csv"
        csv.field_size_limit(sys.maxsize)
        with open(path) as csvfile:
            spamreader = csv.DictReader(csvfile)
            for i,row in enumerate(spamreader):
                reason = row.get('Reason',None)
                decision_data = row.get('Decision', None)
                print(i)
                if reason and decision_data:
                    if decision_data == "yes":
                        decision = True
                    elif decision_data == "no":
                        decision = False
                    else:
                        decision = None
                    obj, created = TrainingData.objects.get_or_create(reason=reason, decision=decision)
                    if created:
                        print("created "+reason)
                    else:
                        print("skipped "+reason)