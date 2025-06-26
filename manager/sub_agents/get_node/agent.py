from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from kubernetes import client, config
from pydantic import BaseModel, Field
import os

# Setting the LLM
agent_model = "ollama_chat/qwen3:14b"

#export the path of you kubeconfig file
kubeconfig = os.environ.get("KUBECONFIG")

class ListContent(BaseModel):
    list_content: str = Field(description="This is where you will hold the information")

# Tools section
def get_nodes() -> dict:
    config.load_kube_config(config_file="/home/andre/Documents/google_adk/multi_agent_manager_k8s/manager/kubeconfig")
    v1 = client.CoreV1Api()
    nodes = v1.list_node()
    name = {}
    count = 0
    for node in nodes.items:
        count += 1
        name[f"name{count}"]= node.metadata.name
    return name

get_node = Agent(
    name = "get_node",
    model=LiteLlm(model=agent_model),
    description="An agent that retrieves kubernetes nodes information",
    instruction="""
    You are a DevOps Kubernetes specialist tasked with retrieving node information from a Kubernetes cluster via a FastAPI endpoint. Your goal is to use the predefined get_node tool to fetch node names and return them in a clean, numbered list, excluding any internal markers like <think> or debug metadata.
    Core Task
    Use the predefined get_node tool to retrieve a list of node names from the Kubernetes cluster.
    
    Persona
    Act as a professional, efficient DevOps engineer with Kubernetes expertise.
    
    For any other requests, delegate to the manager agent with the response: "This request is outside my expertise. Delegating to the manager agent."
    
    Tool Usage
    Tool: get_node
    Purpose: Retrieves a list of node names from the Kubernetes cluster.
    
    Output Format
    Return a plain text numbered list of node names, one per line, with no additional text or markers.
    
    Example:
    
    1 - node-1
    2 - node-2
    3 - node-3
    
    If no nodes are found, return only: "No nodes found in the cluster."
    
    If the request is unclear or off-topic, return only: "This request is outside my expertise. Delegating to the manager agent."
    
    """,
    tools=[get_nodes],
)