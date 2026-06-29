"""
Standalone Platform Test - No External Dependencies

Tests all core components without requiring MongoDB or Gemini.
This proves the architecture works before connecting external services.
"""

import asyncio
import uuid
from typing import Dict, Any

# Test if imports work
print("🧪 Testing Platform Architecture (Standalone)\n")
print("=" * 60)

try:
    from app.core.interfaces import Agent, Plugin, AgentContext, AgentResponse
    print("✅ Core interfaces imported")
except Exception as e:
    print(f"❌ Failed to import interfaces: {e}")
    exit(1)

try:
    from app.services.agent_registry import get_agent_registry
    from app.services.tool_registry import get_tool_registry
    from app.services.capability_registry import get_capability_registry, CapabilityCategory
    print("✅ Registries imported")
except Exception as e:
    print(f"❌ Failed to import registries: {e}")
    exit(1)
# Mock MongoDB database connection for standalone testing
import app.database.connection

class MockCollection:
    async def insert_one(self, data):
        class Result:
            inserted_id = "mock_id"
        return Result()
    async def update_one(self, query, update):
        return None
    async def find_one(self, query):
        return None
    def find(self, *args, **kwargs):
        class Cursor:
            async def to_list(self, length):
                return []
            def limit(self, limit):
                return self
            def sort(self, key, direction=-1):
                return self
        return Cursor()

class MockDB:
    def __getattr__(self, name):
        return MockCollection()

app.database.connection.database = MockDB()


# ============================================================================
# Mock Components (No external dependencies)
# ============================================================================

class MockLLMProvider:
    """Mock LLM provider for testing."""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        return "Mock LLM response"
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"goal": "Test goal", "steps": [], "required_plugin": "none"}
    
    async def health_check(self) -> bool:
        return True


class TestAgent(Agent):
    """Simple test agent."""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        return AgentResponse(
            success=True,
            data={"message": f"{self.name} executed successfully"},
            confidence=1.0
        )


class TestPlugin(Plugin):
    """Simple test plugin."""
    
    def __init__(self):
        super().__init__(
            name="TestPlugin",
            version="1.0.0",
            description="Test plugin for architecture validation"
        )
    
    async def initialize(self):
        """Register test capability."""
        agent_registry = get_agent_registry()
        capability_registry = get_capability_registry()
        
        # Register test agent
        agent_registry.register(TestAgent("TestPluginAgent"))
        
        # Register test capability
        capability_registry.register(
            name="test_capability",
            description="Test capability for validation",
            category=CapabilityCategory.ANALYSIS,
            agent_name="TestPluginAgent"
        )
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        return AgentResponse(
            success=True,
            data={"result": "Test plugin executed"},
            confidence=1.0
        )
    
    def get_capabilities(self):
        return {"test_capability": {"description": "Test", "category": "analysis"}}


# ============================================================================
# Test Suite
# ============================================================================

async def test_agent_registry():
    """Test Agent Registry."""
    print("\n" + "=" * 60)
    print("TEST 1: Agent Registry")
    print("=" * 60)
    
    registry = get_agent_registry()
    registry.clear()  # Start fresh
    
    # Register agents
    agent1 = TestAgent("Agent1")
    agent2 = TestAgent("Agent2")
    
    registry.register(agent1)
    registry.register(agent2)
    
    # Test retrieval
    retrieved = registry.get("Agent1")
    assert retrieved is not None, "Agent1 should exist"
    assert retrieved.name == "Agent1", "Agent name should match"
    
    # Test listing
    agents = registry.list_agents()
    assert len(agents) == 2, "Should have 2 agents"
    
    # Test has_agent
    assert registry.has_agent("Agent1"), "Should have Agent1"
    assert not registry.has_agent("NonExistent"), "Should not have NonExistent"
    
    print("✅ Agent Registry: PASS")
    print(f"   - Registered: 2 agents")
    print(f"   - Retrieved: Agent1")
    print(f"   - Listed: {len(agents)} agents")
    return True


async def test_tool_registry():
    """Test Tool Registry."""
    print("\n" + "=" * 60)
    print("TEST 2: Tool Registry")
    print("=" * 60)
    
    registry = get_tool_registry()
    registry.clear()  # Start fresh
    
    # Define test tool
    async def test_tool(param1: str) -> str:
        return f"Tool executed with: {param1}"
    
    # Register tool
    registry.register(
        name="test_tool",
        description="A test tool",
        category="testing",
        parameters={"param1": {"type": "string"}},
        executor=test_tool
    )
    
    # Test retrieval
    tool = registry.get("test_tool")
    assert tool is not None, "Tool should exist"
    assert tool.name == "test_tool", "Tool name should match"
    
    # Test execution
    result = await registry.execute("test_tool", param1="hello")
    assert result == "Tool executed with: hello", "Tool should execute correctly"
    
    # Test listing
    tools = registry.list_tools()
    assert len(tools) == 1, "Should have 1 tool"
    
    print("✅ Tool Registry: PASS")
    print(f"   - Registered: 1 tool")
    print(f"   - Executed: test_tool")
    print(f"   - Result: {result}")
    return True


async def test_capability_registry():
    """Test Capability Registry (THE KEY!)."""
    print("\n" + "=" * 60)
    print("TEST 3: Capability Registry ⭐")
    print("=" * 60)
    
    registry = get_capability_registry()
    registry.clear()  # Start fresh
    
    # Register capability
    registry.register(
        name="test_capability",
        description="Test capability",
        category=CapabilityCategory.ANALYSIS,
        agent_name="TestAgent"
    )
    
    # Test resolution: capability → agent
    agent_name = registry.get_agent_for_capability("test_capability")
    assert agent_name == "TestAgent", "Should resolve to TestAgent"
    
    # Test listing
    capabilities = registry.list_capabilities()
    assert len(capabilities) == 1, "Should have 1 capability"
    
    # Test category filtering
    analysis_caps = registry.list_by_category(CapabilityCategory.ANALYSIS)
    assert "test_capability" in analysis_caps, "Should find test_capability"
    
    print("✅ Capability Registry: PASS")
    print(f"   - Registered: 1 capability")
    print(f"   - Resolved: test_capability → TestAgent")
    print(f"   - THIS IS THE KEY TO EXTENSIBILITY! ⭐")
    return True


async def test_plugin_lifecycle():
    """Test Plugin Lifecycle Manager."""
    print("\n" + "=" * 60)
    print("TEST 4: Plugin Lifecycle Manager")
    print("=" * 60)
    
    from app.services.plugin_lifecycle_manager import get_plugin_lifecycle_manager, PluginState
    
    manager = get_plugin_lifecycle_manager()
    plugin = TestPlugin()
    
    # Test install
    result = await manager.install_plugin(plugin)
    assert result["success"], "Install should succeed"
    
    # Test state
    state = manager.get_plugin_state("TestPlugin")
    assert state == PluginState.INSTALLED, "State should be INSTALLED"
    
    # Test initialize
    result = await manager.initialize_plugin("TestPlugin")
    assert result["success"], "Initialize should succeed"
    
    state = manager.get_plugin_state("TestPlugin")
    assert state == PluginState.INITIALIZED, "State should be INITIALIZED"
    
    # Test enable
    result = await manager.enable_plugin("TestPlugin")
    assert result["success"], "Enable should succeed"
    
    state = manager.get_plugin_state("TestPlugin")
    assert state == PluginState.ENABLED, "State should be ENABLED"
    
    # Test listing
    plugins = manager.list_plugins()
    assert len(plugins) == 1, "Should have 1 plugin"
    
    print("✅ Plugin Lifecycle: PASS")
    print(f"   - Installed: TestPlugin")
    print(f"   - Initialized: TestPlugin")
    print(f"   - Enabled: TestPlugin")
    print(f"   - State transitions: INSTALLED → INITIALIZED → ENABLED")
    return True


async def test_end_to_end_workflow():
    """Test end-to-end workflow (simplified, no DB)."""
    print("\n" + "=" * 60)
    print("TEST 5: End-to-End Workflow")
    print("=" * 60)
    
    agent_registry = get_agent_registry()
    capability_registry = get_capability_registry()
    
    # Setup: Register everything
    test_agent = TestAgent("WorkflowAgent")
    agent_registry.register(test_agent)
    
    capability_registry.register(
        name="workflow_test",
        description="Test workflow capability",
        category=CapabilityCategory.ANALYSIS,
        agent_name="WorkflowAgent"
    )
    
    # Simulate workflow
    print("\n   Simulating workflow:")
    print("   User Request → Planner → Capability → Agent → Result")
    
    # Step 1: User request
    user_request = "Test the workflow"
    print(f"\n   1. User Request: '{user_request}'")
    
    # Step 2: Planner would identify capability needed
    required_capability = "workflow_test"
    print(f"   2. Planner identifies capability: '{required_capability}'")
    
    # Step 3: Capability Registry resolves to agent
    agent_name = capability_registry.get_agent_for_capability(required_capability)
    print(f"   3. Capability Registry resolves: '{required_capability}' → '{agent_name}'")
    
    # Step 4: Retrieve agent from Agent Registry
    agent = agent_registry.get(agent_name)
    print(f"   4. Agent Registry retrieves: '{agent_name}'")
    
    # Step 5: Execute agent
    context = AgentContext(
        workflow_id=str(uuid.uuid4()),
        user_request=user_request,
        current_step="test",
        data={}
    )
    response = await agent.execute(context)
    print(f"   5. Agent executes: Success={response.success}")
    print(f"   6. Result: {response.data}")
    
    assert response.success, "Workflow should succeed"
    
    print("\n✅ End-to-End Workflow: PASS")
    print("   THIS PROVES THE ARCHITECTURE WORKS! 🎉")
    return True


# ============================================================================
# Main Test Runner
# ============================================================================

async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AGENTIC AI PLATFORM - ARCHITECTURE VALIDATION")
    print("Testing without external dependencies")
    print("=" * 60)
    
    tests = [
        ("Agent Registry", test_agent_registry),
        ("Tool Registry", test_tool_registry),
        ("Capability Registry", test_capability_registry),
        ("Plugin Lifecycle", test_plugin_lifecycle),
        ("End-to-End Workflow", test_end_to_end_workflow),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name}: FAILED")
            print(f"   Error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Architecture Validated:")
        print("   - Agent Registry works")
        print("   - Tool Registry works")
        print("   - Capability Registry works (THE KEY!)")
        print("   - Plugin Lifecycle works")
        print("   - End-to-end workflow works")
        print("\n🚀 Platform is ready for:")
        print("   1. MongoDB connection")
        print("   2. Gemini API connection")
        print("   3. HelloWorld Plugin")
        print("   4. Real plugins (HR, IT, etc.)")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
