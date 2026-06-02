#agents/agent_factory.py
import Agently
from config.settings import settings


class AgentFactory:
    @staticmethod
    def create_agent(model_name):
        config = settings.MODELS_CONFIG[model_name]

        model_options = {
            "model": config.model_name,
            "max_tokens": config.max_tokens
        }

        return (Agently.create_agent()
                .set_settings("current_model", "OAIClient")
                .set_settings("model.OAIClient.auth", {"api_key": config.api_key.strip()})
                .set_settings("model.OAIClient.url", config.base_url.strip())
                .set_settings("model.OAIClient.options", model_options)
                )

