"""Simple test to debug HelloWorld plugin."""

import asyncio
from app.plugins.hello_world import HelloWorldPlugin
from app.services.capability_registry import CapabilityCategory

async def test():
    print("Testing HelloWorld Plugin...")
    
    try:
        plugin = HelloWorldPlugin()
        print(f"✅ Plugin created: {plugin.name}")
        
        print("\nAttempting initialization...")
        await plugin.initialize()
        print("✅ Plugin initialized")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
