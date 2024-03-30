import pika
import json

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"Received ID: {data['id']}")  # Existing print statement
    # Debug: Confirming a message has been received and processed
    print(f"Processed message with ID: {data['id']}")

def main():
    print("Main function called")
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='db_entries')

    channel.basic_consume(queue='db_entries',
                          auto_ack=True,
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    # Debug: Indicating the consumer has started
    print("[DEBUG] Consumer is now waiting for messages...")
    channel.start_consuming()
    # Debug: This line will not execute until the consuming is stopped, e.g., by a keyboard interrupt
    print("[DEBUG] Consumer has stopped.")

if __name__ == '__main__':
    print("Process Start")
    main()