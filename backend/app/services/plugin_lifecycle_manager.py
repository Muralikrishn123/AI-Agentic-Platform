from typing import Dict, Optional, List, Any
from enum import Enum
from datetime import datetime
from app.core.interfaces import Plugin
from app.services.agent_registry import get_agent_registry
from app.services.tool_registry import get_tool_registry
from app.services.capability_registry import get_capability_registry
from app.database.models import PluginModel


class PluginState(str, Enum):
    """Plugin lifecycle states."""
    UNINSTALLED = "uninstalled"
    INSTALLED = "installed"
    INITIALIZED = "initialized"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class PluginLifecycleManager:
    """
    Plugin Lifecycle Manager - Manages complete plugin lifecycle.
    
    Think of this like VS Code extensions or browser plugins.
    Each plugin has a lifecycle: install → load → initialize → enable
    
    Responsibilities:
    - Install plugin
    - Load plugin code
    - Initialize plugin (call plugin.initialize())
    - Register plugin's agents
    - Register plugin's tools
    - Register plugin's capabilities
    - Enable/disable plugin
    - Unload plugin
    - Update plugin version
    - Handle plugin errors
    
    Lifecycle Phases:
    1. UNINSTALLED → INSTALLED: Plugin files added
    2. INSTALLED → INITIALIZED: Plugin initialized, dependencies ready
    3. INITIALIZED → ENABLED: Plugin active and usable
    4. ENABLED ↔ DISABLED: Toggle plugin on/off
    """
    
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self._states: Dict[str, PluginState] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        
        self.agent_registry = get_agent_registry()
        self.tool_registry = get_tool_registry()
        self.capability_registry = get_capability_registry()
    
    async def install_plugin(
        self,
        plugin: Plugin,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Install a plugin.
        
        Phase 1: Add plugin to system
        """
        plugin_name = plugin.name
        
        if plugin_name in self._plugins:
            return {
                "success": False,
                "error": f"Plugin '{plugin_name}' already installed"
            }
        
        try:
            self._plugins[plugin_name] = plugin
            self._states[plugin_name] = PluginState.INSTALLED
            self._metadata[plugin_name] = {
                "installed_at": datetime.utcnow().isoformat(),
                "version": plugin.version,
                "description": plugin.description,
                **(metadata or {})
            }
            
            # Persist to database
            await PluginModel.create_plugin({
                "name": plugin_name,
                "version": plugin.version,
                "description": plugin.description,
                "enabled": False,
                "state": PluginState.INSTALLED.value,
                "capabilities": plugin.get_capabilities()
            })
            
            print(f"📦 Installed plugin: {plugin_name} v{plugin.version}")
            
            return {
                "success": True,
                "plugin_name": plugin_name,
                "state": PluginState.INSTALLED.value
            }
        
        except Exception as e:
            self._states[plugin_name] = PluginState.ERROR
            return {
                "success": False,
                "error": str(e)
            }
    
    async def initialize_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """
        Initialize a plugin.
        
        Phase 2: Call plugin.initialize(), register components
        """
        if plugin_name not in self._plugins:
            return {"success": False, "error": "Plugin not installed"}
        
        if self._states[plugin_name] != PluginState.INSTALLED:
            return {"success": False, "error": f"Plugin state is {self._states[plugin_name]}"}
        
        try:
            plugin = self._plugins[plugin_name]
            
            # Initialize plugin
            await plugin.initialize()
            
            # Plugin should have registered its components during initialize()
            # But we can verify and help register if needed
            
            self._states[plugin_name] = PluginState.INITIALIZED
            
            print(f"🔧 Initialized plugin: {plugin_name}")
            
            return {
                "success": True,
                "plugin_name": plugin_name,
                "state": PluginState.INITIALIZED.value
            }
        
        except Exception as e:
            self._states[plugin_name] = PluginState.ERROR
            return {"success": False, "error": str(e)}
    
    async def enable_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """
        Enable a plugin.
        
        Phase 3: Make plugin active and usable
        """
        if plugin_name not in self._plugins:
            return {"success": False, "error": "Plugin not installed"}
        
        current_state = self._states[plugin_name]
        
        if current_state == PluginState.ERROR:
            return {"success": False, "error": "Plugin in error state"}
        
        # If not initialized, initialize first
        if current_state == PluginState.INSTALLED:
            init_result = await self.initialize_plugin(plugin_name)
            if not init_result["success"]:
                return init_result
        
        try:
            plugin = self._plugins[plugin_name]
            plugin.enabled = True
            
            self._states[plugin_name] = PluginState.ENABLED
            
            # Update database
            await PluginModel.update_plugin(plugin_name, {
                "enabled": True,
                "state": PluginState.ENABLED.value
            })
            
            print(f"✅ Enabled plugin: {plugin_name}")
            
            return {
                "success": True,
                "plugin_name": plugin_name,
                "state": PluginState.ENABLED.value
            }
        
        except Exception as e:
            self._states[plugin_name] = PluginState.ERROR
            return {"success": False, "error": str(e)}
    
    async def disable_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Disable a plugin without uninstalling."""
        if plugin_name not in self._plugins:
            return {"success": False, "error": "Plugin not installed"}
        
        try:
            plugin = self._plugins[plugin_name]
            plugin.enabled = False
            
            self._states[plugin_name] = PluginState.DISABLED
            
            # Update database
            await PluginModel.update_plugin(plugin_name, {
                "enabled": False,
                "state": PluginState.DISABLED.value
            })
            
            print(f"⏸️  Disabled plugin: {plugin_name}")
            
            return {
                "success": True,
                "plugin_name": plugin_name,
                "state": PluginState.DISABLED.value
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}

    
    async def uninstall_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """
        Uninstall a plugin.
        
        Final phase: Clean up and remove plugin
        """
        if plugin_name not in self._plugins:
            return {"success": False, "error": "Plugin not installed"}
        
        try:
            plugin = self._plugins[plugin_name]
            
            # Cleanup plugin resources
            await plugin.cleanup()
            
            # Remove from registries (this is where it gets complex in real systems)
            # In production, you'd need to track which agents/tools/capabilities
            # belong to which plugin for proper cleanup
            
            # Remove plugin
            del self._plugins[plugin_name]
            del self._states[plugin_name]
            del self._metadata[plugin_name]
            
            # Remove from database
            await PluginModel.delete_plugin(plugin_name)
            
            print(f"🗑️  Uninstalled plugin: {plugin_name}")
            
            return {
                "success": True,
                "plugin_name": plugin_name
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self._plugins.get(plugin_name)
    
    def get_plugin_state(self, plugin_name: str) -> Optional[PluginState]:
        """Get plugin state."""
        return self._states.get(plugin_name)
    
    def list_plugins(
        self,
        state: Optional[PluginState] = None
    ) -> List[Dict[str, Any]]:
        """List all plugins, optionally filtered by state."""
        
        plugins = []
        for name, plugin in self._plugins.items():
            plugin_state = self._states[name]
            
            if state and plugin_state != state:
                continue
            
            plugins.append({
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "state": plugin_state.value,
                "enabled": plugin.enabled,
                "capabilities": plugin.get_capabilities(),
                "metadata": self._metadata.get(name, {})
            })
        
        return plugins
    
    async def update_plugin(
        self,
        plugin_name: str,
        new_plugin: Plugin
    ) -> Dict[str, Any]:
        """Update a plugin to a new version."""
        if plugin_name not in self._plugins:
            return {"success": False, "error": "Plugin not installed"}
        
        try:
            # Disable old version
            await self.disable_plugin(plugin_name)
            
            # Uninstall old version
            await self.uninstall_plugin(plugin_name)
            
            # Install new version
            install_result = await self.install_plugin(new_plugin)
            if not install_result["success"]:
                return install_result
            
            # Enable new version
            enable_result = await self.enable_plugin(new_plugin.name)
            
            print(f"🔄 Updated plugin: {plugin_name} → v{new_plugin.version}")
            
            return enable_result
        
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
_manager = PluginLifecycleManager()


def get_plugin_lifecycle_manager() -> PluginLifecycleManager:
    """Get the global plugin lifecycle manager instance."""
    return _manager
