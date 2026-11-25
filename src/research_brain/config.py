"""Single owner of Research Brain configuration and vault path resolution."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "research-brain" / "config.toml"
DEFAULT_VAULT_PATH = Path.home() / "research-brain-vault"


@dataclass(frozen=True)
class ProofBounds:
    max_depth: int = 3
    reviewers_per_round: int = 2
    max_rounds: int = 3


@dataclass(frozen=True)
class Config:
    vault_path: Path
    max_context_percent: int = 50
    proof: ProofBounds = ProofBounds()
    spelling: str = "US"


def _find_project_override(start: Path) -> Path | None:
    """Walk upward from start looking for .research-brain.toml."""
    current = start.resolve()
    for candidate in (current, *current.parents):
        marker = candidate / ".research-brain.toml"
        if marker.is_file():
            return marker
    return None


def load_config(cwd: Path | None = None, config_path: Path | None = None) -> Config:
    """Resolve configuration with precedence: env > project marker > user config > default."""
    cfg_file = config_path or DEFAULT_CONFIG_PATH
    raw: dict = {}
    if cfg_file.is_file():
        with cfg_file.open("rb") as fh:
            raw = tomllib.load(fh)

    vault_str = raw.get("vault", {}).get("path")
    proof_raw = dict(raw.get("proof", {}))
    max_ctx = int(raw.get("operations", {}).get("max_context_percent", 50))
    spelling = str(raw.get("conventions", {}).get("spelling", "US"))

    if cwd is not None:
        proj_marker = _find_project_override(cwd)
        if proj_marker is not None:
            with proj_marker.open("rb") as fh:
                proj_raw = tomllib.load(fh)
            if "vault" in proj_raw and "path" in proj_raw["vault"]:
                vault_str = proj_raw["vault"]["path"]
            if "proof" in proj_raw:
                proof_raw.update(proj_raw["proof"])

    env_vault = os.environ.get("RESEARCH_BRAIN_VAULT")
    if env_vault:
        vault_path = Path(env_vault).expanduser().resolve()
    elif vault_str:
        vault_path = Path(vault_str).expanduser().resolve()
    else:
        vault_path = DEFAULT_VAULT_PATH.resolve()

    bounds = ProofBounds(
        max_depth=int(proof_raw.get("max_depth", 3)),
        reviewers_per_round=int(proof_raw.get("reviewers_per_round", 2)),
        max_rounds=int(proof_raw.get("max_rounds", 3)),
    )
    return Config(
        vault_path=vault_path,
        max_context_percent=max_ctx,
        proof=bounds,
        spelling=spelling,
    )


def write_default_config(vault_path: Path, config_path: Path | None = None) -> Path:
    """Create user config.toml if absent; return its path."""
    cfg_file = config_path or DEFAULT_CONFIG_PATH
    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    if not cfg_file.exists():
        content = (
            "[vault]\n"
            f'path = "{vault_path}"\n\n'
            "[operations]\n"
            "max_context_percent = 50\n\n"
            "[proof]\n"
            "max_depth = 3\n"
            "reviewers_per_round = 2\n"
            "max_rounds = 3\n\n"
            "[conventions]\n"
            'spelling = "US"\n'
        )
        cfg_file.write_text(content, encoding="utf-8")
    return cfg_file
