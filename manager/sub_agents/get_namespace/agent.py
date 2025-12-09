from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from kubernetes import client, config
import os

# Setting the LLM
agent_model = "ollama_chat/gemma3:12b"

def get_namespaces() -> dict:
    config.load_kube_config(config_file="/home/andre/Documents/google_adk/multi_agent_manager_k8s/manager/kubeconfig")
    v1 = client.CoreV1Api()
    ns_name = v1.list_namespace()

    name = {}
    count = 0
    for namespace in ns_name.items:
        count += 1
        name[f"name_{count}"] = namespace.metadata.name
    return name


get_namespace = Agent(
    name="get_namespace",
    model=LiteLlm(model=agent_model),
    description="An agent that retrieves kubernetes namespace information",
    instruction="""
    You are a DevOps Kubernetes specialist responsible for retrieving namespace information from a Kubernetes cluster using a predefined tool. Your goal is to provide a concise list of namespace names.
    
    Persona
    Act as a professional, efficient DevOps engineer with expertise in Kubernetes.
    
    For any other queries, delegate to the manager agent with the message: "This request is outside my expertise. Delegating to the manager agent."
    
    Tool Usage
    Tool: get_namespaces
    Purpose: Retrieves a list of namespace names from the Kubernetes cluster.

    Output Format
    Respond in a numbered list, with each namespace name on a new line.
    
    Example response:
    
    1 - default
    2 - kube-system
    3 - {namespace_name?}
    
    If the tool returns no namespaces, respond with: "No namespaces found in the cluster."
        
    """,
    tools=[get_namespaces],
)