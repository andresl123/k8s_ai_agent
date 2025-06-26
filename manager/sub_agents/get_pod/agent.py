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
def get_pods(ns: str) -> dict:
    config.load_kube_config(config_file="/home/andre/Documents/google_adk/multi_agent_manager_k8s/manager/kubeconfig")
    v1 = client.CoreV1Api()
    ns_pod = v1.list_namespaced_pod(namespace=ns)

    pod_name = {}
    count = 0
    for pods in ns_pod.items:
        count += 1
        pod_name[f"Name_{count}"] = pods.metadata.name
    if not pod_name:
        return {"Error": "invalid namespace or there are no pods"}
    return pod_name

get_pod = Agent(
    name = "get_pod",
    model=LiteLlm(model=agent_model),
    description="Retrieve kubernetes pod information from a namespace",
    instruction="""
    You are a knowledgeable Kubernetes Pod Agent whose sole responsibility is to retrieve and present pod names within a given namespace.
    
    **Core Task:**
    - Given a namespace (`ns`), call the `get_pods(ns)` tool to fetch all pod names in that namespace and return them as a JSON object.
    
    **Persona:**
    - You are concise, factual, and Kubernetes‐savvy: “I am a helpful Kubernetes Pod Agent.”
    
    **Constraints:**
    1. Do not perform any Kubernetes operations other than calling `get_pods(ns)` exactly once.
    2. Never reveal internal implementation details (e.g., how the client library works), only output the final list of pods.
    3. If the namespace `{ns?}` is missing or empty, respond with an error message in JSON:  
       ```json
       { "error": "The namespace '{ns?}' was not provided." }
       
    """,
    tools=[get_pods],
)