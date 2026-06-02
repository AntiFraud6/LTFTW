#agents/create.py
#用于创建具体的agent。
#Used to create specific agents.
from agents.agent_factory import AgentFactory
Gemini = AgentFactory.create_agent('Gemini')
v3 = AgentFactory.create_agent('DeepSeekv3')





