from typing import Dict, Any, Optional, List
from app.core.interfaces import Plugin
from app.database.models import PluginModel


class PluginManager:
    """
    Plugin Manager - Manages plugin lifecycle.
    
    Responsibilities:
    - Register new plugins
    - Enable/disable plugins
    - Execute plugins
    - List available plugins
    - Remove plugins
    """
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
    
    async def register_plugin(
        self,
        plugin: Plugin,
        persist: bool = True
    ) -> Dict[str, Any]:
        """Register a new plugin."""
        
        # Initialize plugin
        await plugin.initialize()
        
        # Store in memory
        self.plugins[plugin.name] = plugin
        
        # Persist to database
        if persist:
            plugin_data = {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "enabled": plugin.enabled,
                "capabilities": plugin.get_capabilities()
            }
            await PluginModel.create_plugin(plugin_data)
        
        return {
            "name": plugin.name,
            "version": plugin.version,
            "status": "registered"
        }
    
    async def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self.plugins.get(plugin_name)
    
    async def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins."""
        
        plugins_list = []
        for name, plugin in self.plugins.items():
            plugins_list.append({
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "enabled": plugin.enabled,
                "capabilities": plugin.get_capabilities()
            })
        
        # Merge custom plugins from MongoDB
        try:
            from app.database.models import CustomPluginModel
            customs = await CustomPluginModel.get_plugins()
            for cp in customs:
                # Avoid duplicate names if registered in memory
                if any(p["name"] == cp["name"] for p in plugins_list):
                    continue
                plugins_list.append({
                    "name": cp["name"],
                    "version": "1.0.0",
                    "description": cp["description"],
                    "enabled": cp.get("enabled", True),
                    "capabilities": {
                        "capabilities": ["research_agent", "qualification_agent", "contact_discovery_agent"],
                        "description": cp["description"],
                        "version": "1.0.0",
                        "stage": "Dynamic Custom Domain",
                        "custom": True,
                        "icp_config": cp.get("icp_config"),
                        "personas": cp.get("personas"),
                        "rules": cp.get("rules")
                    }
                })
        except Exception as e:
            print("Error merging custom plugins in list_plugins:", e)
            
        return plugins_list
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        
        plugin = self.plugins.get(plugin_name)
        if plugin:
            plugin.enabled = True
            await PluginModel.update_plugin(plugin_name, {"enabled": True})
            return True
        return False
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        
        plugin = self.plugins.get(plugin_name)
        if plugin:
            plugin.enabled = False
            await PluginModel.update_plugin(plugin_name, {"enabled": False})
            return True
        return False
    
    async def remove_plugin(self, plugin_name: str) -> bool:
        """Remove a plugin."""
        
        plugin = self.plugins.get(plugin_name)
        if plugin:
            await plugin.cleanup()
            del self.plugins[plugin_name]
            await PluginModel.delete_plugin(plugin_name)
            return True
        return False
    
    async def load_plugins_from_db(self):
        """Load registered plugins from database on startup."""
        # This will be implemented when we add database models
        pass
