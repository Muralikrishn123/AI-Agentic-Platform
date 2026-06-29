from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel
from config.settings import settings as env_settings


class ConfigScope(str, Enum):
    """Configuration scope levels."""
    SYSTEM = "system"      # Platform-wide settings
    PLUGIN = "plugin"      # Plugin-specific settings
    USER = "user"          # User-specific settings
    WORKFLOW = "workflow"  # Workflow-specific settings


class Configuration(BaseModel):
    """Configuration entry."""
    key: str
    value: Any
    scope: ConfigScope
    description: Optional[str] = None
    editable: bool = True
    metadata: Dict[str, Any] = {}


class ConfigurationManager:
    """
    Configuration Manager - Centralized configuration management.
    
    Instead of only .env files, provide a runtime configuration system
    that can be changed through the dashboard or API.
    
    Stores:
    - Current LLM provider (Gemini/OpenAI)
    - LLM parameters (temperature, max_tokens)
    - Enabled plugins
    - Default workflow settings
    - Tool configurations
    - Feature flags
    
    Benefits:
    - Change config without restart
    - Dashboard can edit values
    - Per-plugin configuration
    - Per-user configuration
    - Configuration validation
    - Configuration history (future)
    
    Example:
        # Get config
        provider = config_manager.get("llm.provider")  # "gemini"
        
        # Set config
        config_manager.set("llm.provider", "openai", scope=ConfigScope.SYSTEM)
        
        # Dashboard can update these values
    """
    
    def __init__(self):
        self._configs: Dict[str, Configuration] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default platform configurations."""
        
        # LLM Configuration
        self.set(
            "llm.provider",
            "gemini" if env_settings.GEMINI_API_KEY else "openai",
            scope=ConfigScope.SYSTEM,
            description="Active LLM provider",
            editable=True
        )
        
        self.set(
            "llm.temperature",
            0.7,
            scope=ConfigScope.SYSTEM,
            description="LLM temperature",
            editable=True
        )
        
        self.set(
            "llm.max_tokens",
            1000,
            scope=ConfigScope.SYSTEM,
            description="Max tokens for LLM responses",
            editable=True
        )
        
        # Workflow Configuration
        self.set(
            "workflow.max_retries",
            2,
            scope=ConfigScope.SYSTEM,
            description="Maximum workflow retries",
            editable=True
        )
        
        self.set(
            "workflow.timeout_seconds",
            300,
            scope=ConfigScope.SYSTEM,
            description="Workflow timeout in seconds",
            editable=True
        )
        
        # Reflection Configuration
        self.set(
            "reflection.enabled",
            True,
            scope=ConfigScope.SYSTEM,
            description="Enable reflection agent",
            editable=True
        )
        
        self.set(
            "reflection.confidence_threshold",
            0.7,
            scope=ConfigScope.SYSTEM,
            description="Minimum confidence to pass",
            editable=True
        )
        
        # Tool Configuration
        self.set(
            "tools.rate_limit_enabled",
            False,
            scope=ConfigScope.SYSTEM,
            description="Enable tool rate limiting",
            editable=True
        )
        
        # Feature Flags
        self.set(
            "features.async_tool_execution",
            False,
            scope=ConfigScope.SYSTEM,
            description="Execute tools asynchronously",
            editable=True
        )
        
        self.set(
            "features.event_bus_enabled",
            True,
            scope=ConfigScope.SYSTEM,
            description="Enable event bus",
            editable=True
        )
    
    def set(
        self,
        key: str,
        value: Any,
        scope: ConfigScope = ConfigScope.SYSTEM,
        description: Optional[str] = None,
        editable: bool = True,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Set a configuration value."""
        
        config = Configuration(
            key=key,
            value=value,
            scope=scope,
            description=description,
            editable=editable,
            metadata=metadata or {}
        )
        
        self._configs[key] = config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        config = self._configs.get(key)
        return config.value if config else default
    
    def get_config(self, key: str) -> Optional[Configuration]:
        """Get full configuration object."""
        return self._configs.get(key)
    
    def list_configs(
        self,
        scope: Optional[ConfigScope] = None,
        editable_only: bool = False
    ) -> Dict[str, Any]:
        """List all configurations."""
        
        configs = self._configs.values()
        
        if scope:
            configs = [c for c in configs if c.scope == scope]
        
        if editable_only:
            configs = [c for c in configs if c.editable]
        
        return {
            config.key: {
                "value": config.value,
                "scope": config.scope.value,
                "description": config.description,
                "editable": config.editable,
                "metadata": config.metadata
            }
            for config in configs
        }
    
    def update(self, key: str, value: Any) -> bool:
        """Update a configuration value if it exists and is editable."""
        
        if key not in self._configs:
            return False
        
        config = self._configs[key]
        
        if not config.editable:
            print(f"⚠️  Configuration '{key}' is not editable")
            return False
        
        config.value = value
        print(f"✏️  Updated configuration: {key} = {value}")
        return True
    
    def delete(self, key: str) -> bool:
        """Delete a configuration."""
        if key in self._configs:
            del self._configs[key]
            return True
        return False
    
    def reset_to_defaults(self) -> None:
        """Reset all configurations to defaults."""
        self._configs.clear()
        self._initialize_defaults()
        print("🔄 Reset all configurations to defaults")


# Global instance
_config_manager = ConfigurationManager()


def get_configuration_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    return _config_manager
