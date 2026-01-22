import os
import platform

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_sessions_dir() -> str:
    """Get the default Claude Cowork sessions directory based on platform."""
    system = platform.system()
    if system == "Darwin":  # macOS
        return os.path.expanduser(
            "~/Library/Application Support/Claude/local-agent-mode-sessions"
        )
    elif system == "Windows":
        return os.path.join(
            os.environ.get("APPDATA", ""),
            "Claude",
            "local-agent-mode-sessions"
        )
    else:  # Linux and others
        return os.path.expanduser("~/.config/claude/local-agent-mode-sessions")


class ClaudeCoworkSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='CLAUDECOWORK_')
    sessions_dir: str = Field(
        default_factory=get_default_sessions_dir,
        description='Claude Cowork local agent mode sessions directory'
    )


claudecowork_settings = ClaudeCoworkSettings()
