from abc import ABC, abstractmethod

from src.adapters.producers.factory import ProducerFactory


class EmailServiceInterface(ABC):
    @abstractmethod
    async def send_email(self, email_template, data):
        raise NotImplementedError


class EmailService(EmailServiceInterface):
    def __init__(self,
                 producer_factory: ProducerFactory):
        self._producer_factory = producer_factory

    async def send_email(self, email_template, data):
        async with self._producer_factory.get_publisher() as producer:
            data['template_id'] = str(email_template)
            data['user_id'] = str(data['user_id'])
            result = await producer.publish(data)
