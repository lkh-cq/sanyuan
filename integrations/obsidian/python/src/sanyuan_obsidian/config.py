from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    database_path: Path
    fts_table: str | None = None
    fts_path_column: str | None = None
    fts_title_column: str | None = None
    fts_content_column: str | None = None
    routing_table_path: Path | None = None
    coarse_multiplier: int = 4
    max_query_chars: int = 20_000

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        database = os.environ.get("SANYUAN_OBSIDIAN_DB", "obsidian-memory.db")
        routing = os.environ.get("SANYUAN_ROUTING_TABLE")
        return cls(
            database_path=Path(database).expanduser(),
            fts_table=os.environ.get("SANYUAN_FTS_TABLE"),
            fts_path_column=os.environ.get("SANYUAN_FTS_PATH_COLUMN"),
            fts_title_column=os.environ.get("SANYUAN_FTS_TITLE_COLUMN"),
            fts_content_column=os.environ.get("SANYUAN_FTS_CONTENT_COLUMN"),
            routing_table_path=Path(routing).expanduser() if routing else None,
            coarse_multiplier=max(
                2, int(os.environ.get("SANYUAN_COARSE_MULTIPLIER", "4"))
            ),
        )


@dataclass(frozen=True, slots=True)
class EmbeddingConfig:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float = 30.0

    @property
    def enabled(self) -> bool:
        return bool(self.base_url and self.api_key and self.model)

    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        return cls(
            base_url=os.environ.get("DOUBAO_EMBEDDING_BASE_URL", ""),
            api_key=os.environ.get("DOUBAO_EMBEDDING_API_KEY", ""),
            model=os.environ.get("DOUBAO_EMBEDDING_MODEL", ""),
            timeout_seconds=float(os.environ.get("DOUBAO_EMBEDDING_TIMEOUT", "30")),
        )
