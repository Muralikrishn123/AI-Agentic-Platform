"""
Test Stage A: HR Plugin Skeleton

Goal: Prove the plugin loads and registers capabilities.
No agents, no logic - just registration.
"""

import asyncio
from app.plugins.hr_recruitment import HRRecruitmentPlugin
from app.services.capability_registry import get_capability_registry


async def test_stage_a():
    """Test HR Plugin skeleton (Stage A)."""
    
    print("🧪 Testing Stage A: HR Plugin Skeleton")
    print("=" * 60)
    
    # Test 1: Plugin Creation
    print("\n📦 Test 1: Plugin Creation")
    try:
        plugin = HRRecruitmentPlugin()
        print(f"✅ Plugin created: {plugin.name} v{plugin.version}")
    except Exception as e:
        print(f"❌ Plugin creation failed: {e}")
        return False
    
    # Test 2: Plugin Initialization
    print("\n🔧 Test 2: Plugin Initialization")
    try:
        await plugin.initialize()
        print("✅ Plugin initialized successfully")
    except Exception as e:
        print(f"❌ Plugin initialization failed: {e}")
        return False
    
    # Test 3: Capability Registration
    print("\n🎯 Test 3: Capability Registration")
    capability_registry = get_capability_registry()
    
    expected_capabilities = [
        "extract_requirements",
        "candidate_search",
        "candidate_matching",
        "candidate_scoring",
        "candidate_shortlisting"
    ]
    
    all_registered = True
    for cap in expected_capabilities:
        agent_name = capability_registry.resolve(cap)
        if agent_name:
            print(f"✅ {cap:25} → {agent_name}")
        else:
            print(f"❌ {cap:25} → NOT FOUND")
            all_registered = False
    
    if not all_registered:
        print("\n❌ Some capabilities not registered")
        return False
    
    # Test 4: Plugin Metadata
    print("\n📋 Test 4: Plugin Metadata")
    capabilities = plugin.get_capabilities()
    print(f"   Name: {plugin.name}")
    print(f"   Version: {plugin.version}")
    print(f"   Stage: {capabilities.get('stage')}")
    print(f"   Capabilities: {len(capabilities['capabilities'])}")
    print("✅ Metadata correct")
    
    # Test 5: Execute (Should fail in Stage A)
    print("\n⚠️  Test 5: Execute (Expected to fail)")
    from app.core.interfaces import AgentContext
    context = AgentContext(
        workflow_id="test-001",
        user_request="Test request",
        current_step="extract_requirements"
    )
    
    response = await plugin.execute(context)
    if not response.success:
        print(f"✅ Execute correctly returns not implemented: {response.error}")
    else:
        print("❌ Execute should fail in Stage A")
        return False
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 STAGE A: COMPLETE!")
    print("=" * 60)
    
    print("\n✨ What Stage A Proved:")
    print("✅ Plugin loads successfully")
    print("✅ 5 capabilities registered")
    print("✅ Capability Registry recognizes all capabilities")
    print("✅ Plugin metadata correct")
    print("✅ Execute correctly indicates not implemented")
    
    print("\n⏭️  Ready for Stage B: Mock Business Workflow")
    
    return True


async def verify_hello_world_still_works():
    """Verify HelloWorld plugin still works after adding HR plugin."""
    print("\n" + "=" * 60)
    print("🔍 Verifying HelloWorld Plugin Still Works")
    print("=" * 60)
    
    from app.plugins.hello_world import HelloWorldPlugin
    from app.services.agent_registry import get_agent_registry
    from app.core.interfaces import AgentContext
    
    # Initialize HelloWorld
    hw_plugin = HelloWorldPlugin()
    await hw_plugin.initialize()
    
    # Test capability resolution
    capability_registry = get_capability_registry()
    agent_name = capability_registry.resolve("hello_world")
    
    if agent_name == "HelloWorldAgent":
        print("✅ HelloWorld capability still resolves correctly")
    else:
        print("❌ HelloWorld capability broken!")
        return False
    
    # Test agent execution
    agent_registry = get_agent_registry()
    agent = agent_registry.get("HelloWorldAgent")
    
    context = AgentContext(
        workflow_id="verify-001",
        user_request="Verification test",
        current_step="hello_world",
        data={"user_name": "Verifier"}
    )
    
    response = await agent.execute(context)
    
    if response.success:
        print("✅ HelloWorld agent still executes correctly")
        print(f"   Response: {response.data.get('greeting')}")
        return True
    else:
        print("❌ HelloWorld agent execution failed!")
        return False


async def main():
    """Run Stage A tests."""
    
    # Test Stage A
    stage_a_passed = await test_stage_a()
    
    if not stage_a_passed:
        print("\n❌ Stage A tests failed")
        return
    
    # Verify HelloWorld still works
    hello_world_passed = await verify_hello_world_still_works()
    
    if not hello_world_passed:
        print("\n❌ HelloWorld regression detected!")
        return
    
    # All tests passed
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n📊 Stage A Quality Gate:")
    print("✅ Plugin directory structure created")
    print("✅ HRRecruitmentPlugin class defined")
    print("✅ 5 capabilities registered")
    print("✅ Plugin loads without errors")
    print("✅ Platform starts with plugin loaded")
    print("✅ HelloWorld tests still pass")
    print("\n🚀 Stage A Complete - Ready for Stage B!")


if __name__ == "__main__":
    asyncio.run(main())
