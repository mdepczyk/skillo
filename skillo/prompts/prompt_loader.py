"""YAML prompt loader for Skillo agents."""

from pathlib import Path
from typing import Any, Dict

import yaml

from skillo.exceptions import ConfigurationError, PromptLoadingError


class PromptLoader:
    """Simple YAML prompt configuration loader."""

    def __init__(self):
        """Initialize the prompt loader."""
        self.prompts_dir = Path(__file__).parent
        self._cache = {}

    def load_prompt(self, prompt_file: str, prompt_key: str) -> Dict[str, Any]:
        """
        Load a prompt configuration from YAML file.

        Args:
            prompt_file: Name of the YAML file (without extension)
            prompt_key: Key of the specific prompt within the file

        Returns:
            Dictionary containing prompt configuration

        Raises:
            PromptLoadingError: If prompt file or key not found
        """
        cache_key = f"{prompt_file}.{prompt_key}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        file_path = self.prompts_dir / f"{prompt_file}.yaml"

        if not file_path.exists():
            raise PromptLoadingError(
                prompt_file, prompt_key, f"File not found: {file_path}"
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if prompt_key not in data:
                raise PromptLoadingError(
                    prompt_file,
                    prompt_key,
                    f"Key not found in {prompt_file}.yaml",
                )

            prompt_config = data[prompt_key]
            self._validate_prompt_config(prompt_config)

            self._cache[cache_key] = prompt_config
            return prompt_config

        except yaml.YAMLError as e:
            raise PromptLoadingError(
                prompt_file, prompt_key, f"Invalid YAML: {str(e)}"
            )
        except Exception as e:
            raise PromptLoadingError(
                prompt_file, prompt_key, f"Loading error: {str(e)}"
            )

    def get_llm_config(self, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract LLM configuration parameters from prompt config.

        Args:
            prompt_config: Prompt configuration dictionary

        Returns:
            Dictionary with LLM parameters for ChatOpenAI
        """
        return {
            "model_name": prompt_config.get("model", "gpt-4o-mini"),
            "temperature": prompt_config.get("temperature", 0.1),
            "max_tokens": prompt_config.get("max_tokens", 1000),
        }

    def get_formatted_messages(
        self, prompt_config: Dict[str, Any], **variables
    ) -> Dict[str, str]:
        """
        Get formatted system and user messages with variables substituted.

        Args:
            prompt_config: Prompt configuration dictionary
            **variables: Variables to substitute in the prompt

        Returns:
            Dictionary with 'system_message' and 'user_message' keys
        """
        messages = {}

        if "system_message" in prompt_config:
            messages["system_message"] = prompt_config[
                "system_message"
            ].format(**variables)

        if "user_message" in prompt_config:
            messages["user_message"] = prompt_config["user_message"].format(
                **variables
            )

        return messages

    def _validate_prompt_config(self, config: Dict[str, Any]) -> None:
        """
        Validate prompt configuration structure.

        Args:
            config: Configuration to validate

        Raises:
            ConfigurationError: If configuration is invalid
        """
        required_fields = ["system_message", "user_message"]

        for field in required_fields:
            if field not in config:
                raise ConfigurationError(
                    f"Missing required field '{field}' in prompt config"
                )

        if "model" in config and not isinstance(config["model"], str):
            raise ConfigurationError("Field 'model' must be a string")

        if "temperature" in config:
            temp = config["temperature"]
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                raise ConfigurationError(
                    "Field 'temperature' must be a number between 0 and 2"
                )

        if "max_tokens" in config:
            tokens = config["max_tokens"]
            if not isinstance(tokens, int) or tokens < 1:
                raise ConfigurationError(
                    "Field 'max_tokens' must be a positive integer"
                )

    def list_available_prompts(self) -> Dict[str, list[str]]:
        """
        List all available prompts in the prompts directory.

        Returns:
            Dictionary mapping filename to list of prompt keys
        """
        prompts = {}

        for yaml_file in self.prompts_dir.glob("*.yaml"):
            if (
                yaml_file.name.startswith("__")
                or yaml_file.name == "prompt_loader.py"
            ):
                continue

            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                filename = yaml_file.stem
                prompts[filename] = list(data.keys())

            except Exception:

                continue

        return prompts

    def clear_cache(self) -> None:
        """Clear the internal prompt cache."""
        self._cache.clear()


prompt_loader = PromptLoader()
