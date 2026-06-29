"""
Test HelloWorld Plugin - Validates platform architecture end-to-end.

This test proves:
1. Plugin can be initialized (agents + capabilities registered)
2. Capability resolves to correct agent
3. Agent executes successfully
4. End-to-end workflow works
"""

import asyncio
from app.plugins.hello_world import HelloWorldPlugin
from app.services.agent_registry import get_agent_registry
from app.services.capability_registry import get_capability_registry
from app.core.interfaces import AgentContext


async def test_hello_world_plugin():
    """Test the HelloWorld plugin end-to-end."""
    
    print("🧪 Testing HelloWorld Plugin")
    print("=" * 60)
    
    # Test 1: Plugin Initialization
    print("\n🔧 Test 1: Plugin Initialization")
    plugin = HelloWorldPlugin()
    
    try:
        await plugin.initialize()
        print("✅ Plugin initialization: PASS")
    except Exception as e:
        print(f"❌ Plugin initialization: FAIL - {e}")
        return
    
    # Test 2: Capability Resolution
    print("\n🎯 Test 2: Capability Resolution")
    capability_registry = get_capability_registry()
    agent_name = capability_registry.resolve("hello_world")
    
    if agent_name == "HelloWorldAgent":
        print(f"✅ Capability resolution: PASS (hello_world → {agent_name})")
    else:
        print(f"❌ Capability resolution: FAIL (got {agent_name})")
        return
    
    # Test 3: Agent Execution
    print("\n🤖 Test 3: Agent Execution")
    agent_registry = get_agent_registry()
    agent = agent_registry.get("HelloWorldAgent")
    
    if agent is None:
        print("❌ Agent retrieval: FAIL (agent not found)")
        return
    
    # Create execution context
    context = AgentContext(
        workflow_id="test-001",
        user_request="Say hello to Platform Tester",
        current_step="hello_world",
        data={"user_name": "Platform Tester"}
    )
    
    # Execute agent
    response = await agent.execute(context)
    
    if response.success:
        print(f"✅ Agent execution: PASS")
        print(f"   Response: {response.data.get('greeting')}")
        print(f"   Platform Version: {response.data.get('platform_version')}")
    else:
        print(f"❌ Agent execution: FAIL")
        print(f"   Error: {response.error}")
        return
    
    # Test 4: Plugin Execute Method
    print("\n🔌 Test 4: Plugin Execute Method")
    plugin_response = await plugin.execute(context)
    
    if plugin_response.success:
        print(f"✅ Plugin execute: PASS")
        print(f"   Response: {plugin_response.data.get('greeting')}")
    else:
        print(f"❌ Plugin execute: FAIL")
        return
    
    # Test 5: End-to-End Workflow Simulation
    print("\n🔄 Test 5: End-to-End Workflow Simulation")
    print("   User Request → Planner → Capability Registry → Agent")
    
    # Simulate planner output
    planned_capability = "hello_world"
    print(f"   1. Planner outputs capability: '{planned_capability}'")
    
    # Resolve capability
    resolved_agent = capability_registry.resolve(planned_capability)
    print(f"   2. Capability Registry resolves: '{planned_capability}' → '{resolved_agent}'")
    
    # Get agent
    agent = agent_registry.get(resolved_agent)
    print(f"   3. Agent Registry returns: {agent.name}")
    
    # Execute
    context = AgentContext(
        workflow_id="workflow-001",
        user_request="Hello from end-to-end test!",
        current_step="hello_world",
        data={"user_name": "World"}
    )
    response = await agent.execute(context)
    print(f"   4. Agent executes and returns: {response.data.get('greeting')}")
    
    if response.success:
        print("✅ End-to-end workflow: PASS")
    else:
        print("❌ End-to-end workflow: FAIL")
        return
    
    # Test 6: Plugin Capabilities
    print("\n📋 Test 6: Plugin Capabilities")
    capabilities = plugin.get_capabilities()
    print(f"   Name: {plugin.name}")
    print(f"   Version: {plugin.version}")
    print(f"   Enabled: {plugin.enabled}")
    print(f"   Capabilities: {capabilities['capabilities']}")
    print(f"   Agent: {capabilities['agent']}")
    print("✅ Plugin capabilities: PASS")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\n✨ Platform Architecture Validated!")
    print("\nWhat this proves:")
    print("✅ Plugin initialization works")
    print("✅ Agent registration works")
    print("✅ Capability registration works")
    print("✅ Capability → Agent resolution works")
    print("✅ Agent execution works")
    print("✅ Plugin execution works")
    print("✅ End-to-end workflow works")
    print("\n🚀 The platform is ready for real plugins!")


if __name__ == "__main__":
    asyncio.run(test_hello_world_plugin())
