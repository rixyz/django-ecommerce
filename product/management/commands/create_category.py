import csv
from django.core.management.base import BaseCommand
from product.models import Category

class Command(BaseCommand):
    help = 'Import categories from a CSV file'
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        csv_categories = set()  
        try:
            with open(csv_file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    category_title = row[0].strip()
                    csv_categories.add(category_title)
                    category, created = Category.objects.update_or_create(
                        title=category_title,
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Category "{category_title}" added successfully.'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Category "{category_title}" already exists.'))
                self.delete_categories_not_in_csv(csv_categories)

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{csv_file_path}" not found.'))

    def delete_categories_not_in_csv(self, csv_categories):
        categories_in_db = set(Category.objects.values_list('title', flat=True))
        categories_to_delete = categories_in_db - csv_categories
        if categories_to_delete:
            Category.objects.filter(title__in=categories_to_delete).delete()
            self.stdout.write(self.style.WARNING(f'Deleted categories: {", ".join(categories_to_delete)}'))
