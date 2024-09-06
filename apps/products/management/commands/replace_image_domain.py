from django.core.management.base import BaseCommand
from urllib.parse import urlparse, urlunparse
from apps.products.models import Product


class Command(BaseCommand):
    help = "Replace the domain in the image URL for each product using bulk update"

    def add_arguments(self, parser):
        # New domain argument
        parser.add_argument('new_domain', type=str, help='The new domain to replace in the image URLs')

    def handle(self, *args, **options):
        new_domain = options['new_domain']

        # Fetch all products
        products = Product.objects.all()

        updated_products = []

        for product in products:
            old_image_url = product.image

            # Parse the URL
            parsed_url = urlparse(old_image_url)

            # Replace the netloc (domain)
            new_image_url = urlunparse(parsed_url._replace(netloc=new_domain))

            # Update the product's image field
            if new_image_url != old_image_url:
                product.image = new_image_url
                updated_products.append(product)

        # Use bulk_update to update all modified products at once
        if updated_products:
            Product.objects.bulk_update(updated_products, ['image'])
            self.stdout.write(self.style.SUCCESS(f"{len(updated_products)} products updated successfully!"))
        else:
            self.stdout.write(self.style.WARNING("No products required updating."))