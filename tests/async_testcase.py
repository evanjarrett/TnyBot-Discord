import asyncio
import unittest


class AsyncTestCase(unittest.TestCase):
    # noinspection PyPep8Naming
    def __init__(self, methodName='runTest', loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._function_cache = {}
        super(AsyncTestCase, self).__init__(methodName=methodName)

    def coroutine_function_decorator(self, func):
        def wrapper(*args, **kw):
            self.loop.run_until_complete(self.asyncSetUp(*args, **kw))
            ret = self.loop.run_until_complete(func(*args, **kw))
            self.loop.run_until_complete(self.asyncTearDown(*args, **kw))
            return ret

        return wrapper

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        # run an event loop on each, ignoring underscore functions
        if asyncio.iscoroutinefunction(attr) and item not in ["asyncTearDown", "asyncSetUp"]:
            if item not in self._function_cache:
                self._function_cache[item] = self.coroutine_function_decorator(attr)
            return self._function_cache[item]
        return attr

    async def asyncSetUp(self, *args, **kwargs):
        pass

    async def asyncTearDown(self, *args, **kw):
        pass
