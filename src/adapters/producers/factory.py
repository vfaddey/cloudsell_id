from contextlib import asynccontextmanager


class ProducerFactory:
    def __init__(self,
                 _class,
                 **kwargs):
        self._class = _class
        self._kwargs = kwargs

    @asynccontextmanager
    async def get_publisher(self):
        async with self._class(**self._kwargs) as producer:
            yield producer
