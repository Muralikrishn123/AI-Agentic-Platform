import sys

# Workaround for Python 3.14 + protobuf metaclass bug
sys.modules['google._upb._message'] = None

# Workaround for Windows Application Control policy blocking grpc native DLL (cygrpc)
class MockObject(int):
    def __new__(cls, *args, **kwargs):
        return int.__new__(cls, 0)
    def __getattr__(self, name):
        return self
    def __call__(self, *args, **kwargs):
        return self
    def __getitem__(self, item):
        return self

sys.modules['grpc._cython.cygrpc'] = MockObject()

# Try importing google-generativeai with REST transport
try:
    import google.generativeai as genai
    from config.settings import settings
    
    # Configure to use HTTP/REST transport
    genai.configure(api_key=settings.GEMINI_API_KEY, transport="rest")
    
    print("Testing generate_content via REST transport...")
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Hello, this is a test. Reply with 'Success' if you can read this.")
    print("Gemini response:", response.text)
    print("google.generativeai imported and executed successfully via REST!")
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
