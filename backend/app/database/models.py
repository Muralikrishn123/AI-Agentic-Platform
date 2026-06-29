from typing import Dict, Any, Optional, List
from datetime import datetime
from app.database.connection import get_database


class UserModel:
    """User database model."""
    
    @staticmethod
    async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        db = get_database()
        user_data["created_at"] = datetime.utcnow()
        result = await db.users.insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        return user_data
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        db = get_database()
        user = await db.users.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        db = get_database()
        from bson import ObjectId
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user


class WorkflowModel:
    """Workflow database model."""
    
    @staticmethod
    def _sanitize_for_mongo(data):
        """Recursively sanitize data for MongoDB insertion (truncate large strings, stringify unserializable objects)."""
        if isinstance(data, dict):
            return {k: WorkflowModel._sanitize_for_mongo(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [WorkflowModel._sanitize_for_mongo(i) for i in data]
        elif isinstance(data, str) and len(data) > 5000:
            return data[:5000] + "...[truncated]"
        elif isinstance(data, (str, int, float, bool)) or data is None:
            return data
        elif isinstance(data, datetime):
            return data
        else:
            return str(data)[:2000]

    @staticmethod
    async def create_workflow(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow."""
        db = get_database()
        workflow_data["created_at"] = datetime.utcnow()
        safe_data = WorkflowModel._sanitize_for_mongo(workflow_data)
        try:
            result = await db.workflows.insert_one(safe_data)
            workflow_data["_id"] = str(result.inserted_id)
        except Exception as e:
            print(f"⚠️  Failed to save workflow to DB: {e}")
        return workflow_data

    
    @staticmethod
    async def get_workflow(workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID."""
        db = get_database()
        workflow = await db.workflows.find_one({"workflow_id": workflow_id})
        if workflow:
            workflow["_id"] = str(workflow["_id"])
        return workflow
    
    @staticmethod
    async def update_workflow(workflow_id: str, update_data: Dict[str, Any]):
        """Update workflow."""
        db = get_database()
        await db.workflows.update_one(
            {"workflow_id": workflow_id},
            {"$set": update_data}
        )
    
    @staticmethod
    async def list_workflows(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List workflows for a user."""
        db = get_database()
        cursor = db.workflows.find({"user_id": user_id}).limit(limit).sort("created_at", -1)
        workflows = await cursor.to_list(length=limit)
        for workflow in workflows:
            workflow["_id"] = str(workflow["_id"])
        return workflows

    @staticmethod
    async def delete_workflow(workflow_id: str) -> bool:
        """Delete workflow by ID."""
        db = get_database()
        result = await db.workflows.delete_one({"workflow_id": workflow_id})
        return result.deleted_count > 0



class PluginModel:
    """Plugin database model."""
    
    @staticmethod
    async def create_plugin(plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new plugin."""
        db = get_database()
        plugin_data["registered_at"] = datetime.utcnow()
        result = await db.plugins.insert_one(plugin_data)
        plugin_data["_id"] = str(result.inserted_id)
        return plugin_data
    
    @staticmethod
    async def get_plugin(plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get plugin by name."""
        db = get_database()
        plugin = await db.plugins.find_one({"name": plugin_name})
        if plugin:
            plugin["_id"] = str(plugin["_id"])
        return plugin
    
    @staticmethod
    async def list_plugins() -> List[Dict[str, Any]]:
        """List all plugins."""
        db = get_database()
        cursor = db.plugins.find()
        plugins = await cursor.to_list(length=100)
        for plugin in plugins:
            plugin["_id"] = str(plugin["_id"])
        return plugins
    
    @staticmethod
    async def update_plugin(plugin_name: str, update_data: Dict[str, Any]):
        """Update plugin."""
        db = get_database()
        await db.plugins.update_one(
            {"name": plugin_name},
            {"$set": update_data}
        )
    
    @staticmethod
    async def delete_plugin(plugin_name: str):
        """Delete plugin."""
        db = get_database()
        await db.plugins.delete_one({"name": plugin_name})


class LogModel:
    """Log database model."""
    
    @staticmethod
    async def create_log(log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new log entry."""
        db = get_database()
        log_data["timestamp"] = datetime.utcnow()
        result = await db.logs.insert_one(log_data)
        log_data["_id"] = str(result.inserted_id)
        return log_data
    
    @staticmethod
    async def get_logs(
        workflow_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get logs with optional filtering."""
        db = get_database()
        query = {}
        if workflow_id:
            query["workflow_id"] = workflow_id
        
        cursor = db.logs.find(query).limit(limit).sort("timestamp", -1)
        logs = await cursor.to_list(length=limit)
        for log in logs:
            log["_id"] = str(log["_id"])
        return logs


class ReportModel:
    """Report database model."""
    
    @staticmethod
    async def create_report(report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report."""
        db = get_database()
        report_data["created_at"] = datetime.utcnow()
        result = await db.reports.insert_one(report_data)
        report_data["_id"] = str(result.inserted_id)
        return report_data
    
    @staticmethod
    async def get_report(report_id: str) -> Optional[Dict[str, Any]]:
        """Get report by ID."""
        db = get_database()
        report = await db.reports.find_one({"report_id": report_id})
        if report:
            report["_id"] = str(report["_id"])
        return report
    
    @staticmethod
    async def list_reports(limit: int = 50) -> List[Dict[str, Any]]:
        """List reports."""
        db = get_database()
        cursor = db.reports.find().limit(limit).sort("created_at", -1)
        reports = await cursor.to_list(length=limit)
        for report in reports:
            report["_id"] = str(report["_id"])
        return reports


class HITLModel:
    """Human-in-the-Loop approval records."""

    @staticmethod
    async def create_approval(approval_data: Dict[str, Any]) -> Dict[str, Any]:
        db = get_database()
        approval_data["created_at"] = datetime.utcnow()
        result = await db.hitl_approvals.insert_one(approval_data)
        approval_data["_id"] = str(result.inserted_id)
        return approval_data

    @staticmethod
    async def get_approval(workflow_id: str) -> Optional[Dict[str, Any]]:
        db = get_database()
        record = await db.hitl_approvals.find_one({"workflow_id": workflow_id})
        if record:
            record["_id"] = str(record["_id"])
        return record

    @staticmethod
    async def list_pending(limit: int = 50) -> List[Dict[str, Any]]:
        db = get_database()
        cursor = db.hitl_approvals.find({"status": "pending"}).sort("created_at", -1).limit(limit)
        records = await cursor.to_list(length=limit)
        for r in records:
            r["_id"] = str(r["_id"])
        return records

    @staticmethod
    async def list_all(limit: int = 100) -> List[Dict[str, Any]]:
        db = get_database()
        cursor = db.hitl_approvals.find().sort("created_at", -1).limit(limit)
        records = await cursor.to_list(length=limit)
        for r in records:
            r["_id"] = str(r["_id"])
        return records

    @staticmethod
    async def update_status(
        workflow_id: str,
        status: str,
        notes: str = None,
        approved_item_ids: List[str] = None,
        rejected_items: List[Dict[str, Any]] = None
    ) -> bool:
        db = get_database()
        update: Dict[str, Any] = {"status": status}
        if status == "approved":
            update["approved_at"] = datetime.utcnow().isoformat()
        elif status == "rejected":
            update["rejected_at"] = datetime.utcnow().isoformat()
        if notes:
            update["reviewer_notes"] = notes
        if approved_item_ids is not None:
            update["approved_item_ids"] = approved_item_ids
        if rejected_items is not None:
            update["rejected_items"] = rejected_items
            
        result = await db.hitl_approvals.update_one(
            {"workflow_id": workflow_id},
            {"$set": update}
        )
        return result.modified_count > 0



class ICPConfigModel:
    """ICP and Persona configuration per user."""

    @staticmethod
    async def save_config(user_id: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        db = get_database()
        config_data["user_id"] = user_id
        config_data["updated_at"] = datetime.utcnow()
        await db.icp_configs.replace_one(
            {"user_id": user_id},
            config_data,
            upsert=True
        )
        return config_data

    @staticmethod
    async def get_config(user_id: str) -> Optional[Dict[str, Any]]:
        db = get_database()
        config = await db.icp_configs.find_one({"user_id": user_id})
        if config:
            config["_id"] = str(config["_id"])
        return config

    @staticmethod
    async def get_default_config() -> Dict[str, Any]:
        return {
            "icp": {
                "min_employees": 50,
                "max_employees": 5000,
                "sectors": ["SaaS", "Cloud Infrastructure", "AI/ML", "FinTech", "Analytics"],
                "funding_stages": ["Series A", "Series B", "Series C"],
                "preferred_tech": ["Python", "FastAPI", "React"],
                "geographies": ["India"],
                "min_icp_score": 0.5,
                "trigger_types": ["rapid_hiring", "funding_round", "leadership_change"],
                "min_signal_strength": "medium",
            },
            "personas": [
                {"role": "CTO", "seniority": "C-Suite", "department": "Engineering", "priority": 1},
                {"role": "VP Engineering", "seniority": "VP", "department": "Engineering", "priority": 2},
                {"role": "HR Director", "seniority": "Director", "department": "HR", "priority": 3},
                {"role": "Head of Talent", "seniority": "Director", "department": "HR", "priority": 4},
            ],
        }


class CustomPluginModel:
    """Model to persist dynamically created plugin templates in MongoDB."""

    @staticmethod
    async def create_plugin(plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        db = get_database()
        plugin_data["created_at"] = datetime.utcnow()
        # Ensure name acts as unique key
        await db.custom_plugins.replace_one(
            {"name": plugin_data["name"]},
            plugin_data,
            upsert=True
        )
        return plugin_data

    @staticmethod
    async def get_plugins() -> List[Dict[str, Any]]:
        db = get_database()
        cursor = db.custom_plugins.find({})
        plugins = await cursor.to_list(length=100)
        for p in plugins:
            p["_id"] = str(p["_id"])
        return plugins

    @staticmethod
    async def get_plugin_by_name(name: str) -> Optional[Dict[str, Any]]:
        db = get_database()
        p = await db.custom_plugins.find_one({"name": name})
        if p:
            p["_id"] = str(p["_id"])
        return p

    @staticmethod
    async def delete_plugin(name: str) -> bool:
        db = get_database()
        res = await db.custom_plugins.delete_one({"name": name})
        return res.deleted_count > 0


