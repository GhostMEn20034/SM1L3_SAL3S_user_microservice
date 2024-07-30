from django.core.management.base import BaseCommand
from apps.core.queue_listeners.product_queue_listener import ProductQueueListener

class Command(BaseCommand):
    help = 'Launches Listener for product messages: RabbitMQ'
    def handle(self, *args, **options):
        td = ProductQueueListener()
        td.start()
        self.stdout.write("Started Consumer Thread")
