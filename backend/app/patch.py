import sys

# Workaround for Python 3.14 + protobuf metaclass bug
sys.modules['google._upb._message'] = None

# Workaround for Windows Application Control policy blocking grpc native DLL (cygrpc)
class MockObject:
    def __getattr__(self, name):
        return self
    def __call__(self, *args, **kwargs):
        return self
    def __getitem__(self, item):
        return self

sys.modules['grpc._cython.cygrpc'] = MockObject()
