from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- STAGE 1: INTENT SCHEMA ---
class UserIntent(BaseModel):
    raw_summary: str = Field(description="Normalized summary of user requirements.")
    core_features: List[str] = Field(description="List of primary software capabilities extracted.")
    user_roles: List[str] = Field(description="Identified user personas or roles.")
    is_premium_gated: bool = Field(description="True if payments or premium tiers are required.")

# --- STAGE 2 & 3: ARCHITECTURE & COMPILER SCHEMAS ---
class DbColumn(BaseModel):
    name: str = Field(description="Name of the column/field.")
    type: str = Field(description="Data type (e.g., VARCHAR, INTEGER, BOOLEAN, TIMESTAMP).")
    constraints: List[str] = Field(default_factory=list, description="Primary key, Foreign key, Not Null, etc.")

class DbTable(BaseModel):
    table_name: str
    columns: List[DbColumn]

class DatabaseSchema(BaseModel):
    tables: List[DbTable]

class ApiEndpoint(BaseModel):
    path: str = Field(description="Endpoint route URL (e.g., /api/v1/contacts).")
    method: str = Field(description="HTTP Verb (GET, POST, PUT, DELETE).")
    required_auth_role: str = Field(description="Minimum role level allowed to access this endpoint.")
    request_body_fields: List[str] = Field(default_factory=list, description="Fields required in payload.")
    response_mock_fields: List[str] = Field(description="Fields returned by this endpoint.")

class ApiSchema(BaseModel):
    endpoints: List[ApiEndpoint]

class UiComponent(BaseModel):
    component_type: str = Field(description="Button, Form, Table, Chart, Navbar.")
    label: str
    maps_to_api_endpoint: str = Field(description="The exact API endpoint path this UI component interacts with.")
    fields_displayed: List[str]

class UiPage(BaseModel):
    page_name: str
    route: str
    allowed_roles: List[str]
    components: List[UiComponent]

class UiSchema(BaseModel):
    layout_type: str = Field(description="Sidebar, Topnav, Dashboard layout.")
    pages: List[UiPage]

class AuthRule(BaseModel):
    role: str
    permissions: List[str] = Field(description="Explicit actions allowed, e.g., ['read_analytics', 'write_contacts'].")

class AuthSchema(BaseModel):
    enabled: bool
    roles_hierarchy: List[str] = Field(description="Roles listed from lowest to highest privilege.")
    rules: List[AuthRule]

# --- MASTER COMPILER OUTPUT TARGET ---
class CompiledAppConfig(BaseModel):
    app_name: str
    intent_snapshot: UserIntent
    database_schema: DatabaseSchema [cite: 18, 35]
    api_schema: ApiSchema [cite: 17, 34]
    ui_schema: UiSchema [cite: 16, 33]
    auth_schema: AuthSchema [cite: 19, 36]