"""Pydantic representations for the PaymentProcess environment configuration."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict


class FrozenConfigModel(BaseModel):
    """Base model enforcing immutability for env configuration structures."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class DirEnv(FrozenConfigModel):
    """Directory pointers exported from the legacy configuration."""

    arch_dir: str | None
    data_dir: str | None
    log_dir: str | None
    utils_dir: str | None
    scripts_dir: str | None
    app_dir: str | None


class MongoConfig(FrozenConfigModel):
    """Primary Mongo cluster configuration."""

    host: str | None
    auth: str | None
    replicaset: str | None
    user: str | None
    password: str | None
    timezone: str


class AuditMongoConfig(FrozenConfigModel):
    """Audit Mongo cluster configuration."""

    host: str | None
    auth: str | None
    replicaset: str | None
    user: str | None
    password: str | None
    timezone: str


class MCPMongoDB(FrozenConfigModel):
    """Named MCP Mongo databases."""

    fin: str | None
    mcp: str | None
    import_db: str | None


class AuditMongoDB(FrozenConfigModel):
    """Named audit Mongo databases."""

    eh: str | None
    hta: str | None


class OracleConfig(FrozenConfigModel):
    """Generic Oracle connection parameters."""

    user: str | None
    password: str | None
    tns: str | None
    host: str | None
    port: str | None
    protocol: str | None
    service_name: str | None


class PbmFinOracleConfig(FrozenConfigModel):
    """PBM FIN Oracle connection."""

    user: str | None
    password: str | None
    tns: str | None
    host: str | None
    port: str | None
    protocol: str | None
    service_name: str | None


class PbmProdOracleConfig(FrozenConfigModel):
    """PBM PROD Oracle connection."""

    user: str | None
    password: str | None
    tns: str | None
    host: str | None
    port: str | None
    protocol: str | None
    service_name: str | None


class NHOracleConfig(FrozenConfigModel):
    """NH Oracle connection."""

    user: str | None
    password: str | None
    tns: str | None
    host: str | None
    port: str | None
    protocol: str | None
    service_name: str | None


class BusinessConfig(FrozenConfigModel):
    """Business metadata exported from the environment."""

    business_id: int
    name: str | None
    code: str | None


class EnvConfig(FrozenConfigModel):
    """Strongly-typed configuration values sourced from ``.env``."""

    env_name: str
    env_file: Path
    payment_db_uri: str
    timezone: str
    directories: DirEnv
    mongo_config: MongoConfig
    audit_mongo_config: AuditMongoConfig
    mcp_mongo_db: MCPMongoDB
    audit_mongo_db: AuditMongoDB
    oracle: OracleConfig
    pbm_fin_oracle: PbmFinOracleConfig
    pbm_prod_oracle: PbmProdOracleConfig
    nh_oracle: NHOracleConfig
    business: BusinessConfig
