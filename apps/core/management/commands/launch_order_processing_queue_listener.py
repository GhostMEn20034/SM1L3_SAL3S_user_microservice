from django.core.management.base import BaseCommand
from apps.core.queue_listeners.order_processing_queue_listener import OrderProcessingQueueListener

class Command(BaseCommand):
    help = 'Launches Listener for order processing messages: RabbitMQ'
    def handle(self, *args, **options):
        td = OrderProcessingQueueListener()
        td.start()

        self.stdout.write("Started Order Processing Consumer Thread")
