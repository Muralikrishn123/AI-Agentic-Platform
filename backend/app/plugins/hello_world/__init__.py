"""
HelloWorld Plugin - Validates the platform architecture.

This is the simplest possible plugin to prove that:
1. Plugin registration works
2. Capability registration works
3. Agent resolution works
4. Workflow execution works
"""

from .plugin import HelloWorldPlugin
from .agent import HelloWorldAgent

__all__ = ["HelloWorldPlugin", "HelloWorldAgent"]
