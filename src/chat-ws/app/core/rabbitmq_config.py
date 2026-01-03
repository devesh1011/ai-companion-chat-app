import pika
from .config import get_settings

settings = get_settings()


def get_rabbitmq_channel():
    """
    Create and return a new RabbitMQ channel.
    This should be called per-request to avoid connection issues.
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                connection_attempts=3,
                retry_delay=2,
            )
        )
        channel = connection.channel()
        return connection, channel
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}", flush=True)
        raise


# Legacy support - will be deprecated
try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(settings.RABBITMQ_HOST)
    )
    channel = connection.channel()
except Exception as e:
    print(f"Warning: Could not create initial RabbitMQ connection: {e}", flush=True)
    connection = None
    channel = None
