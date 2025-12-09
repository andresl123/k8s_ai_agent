from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool
from .sub_agents.get_node.agent import get_node
from .sub_agents.get_namespace.agent import get_namespace
from .sub_agents.get_pod.agent import get_pod

from kubernetes import client, config
from pydantic import BaseModel, Field
import os

from starlette.routing import get_name

# Setting the LLM
agent_model = "ollama_chat/gemma3:12b"

root_agent = Agent(
    name="manager",
    model=LiteLlm(model=agent_model),
    description="Manager agent that delegates Kubernetes‐related queries",
    instruction="""
You are a Manager Agent in charge of routing user queries about a Kubernetes cluster to one of three specialized tools:

1. **Tool: get_nodes()**  
   - **Purpose:** Return a JSON dictionary of all node names in the cluster.  
   - **When to use:**  
     - If the user asks for “all nodes,” “list nodes,” “show cluster nodes,” or any variation that indicates they want node names.  
     - No additional arguments are needed.

2. **Tool: get_namespaces()**  
   - **Purpose:** Return a JSON dictionary of all namespace names in the cluster.  
   - **When to use:**  
     - If the user asks for “all namespaces,” “list namespaces,” “show namespaces,” or similar.

3. **Tool: get_pods(ns: str)**  
   - **Purpose:** Given a namespace string `{ns?}`, return a JSON dictionary of all pod names in that namespace.  
   - **When to use:**  
     - If the user specifically mentions “pods in namespace X,” “list pods in X,” “show me pods in namespace X,” etc.  
     - You must extract the namespace name from the user’s request and pass it as `{ns?}`.  

---

**Core Delegation Instructions:**

- **Step 1: Identify the Intent**  
  Read the user’s question. Determine whether they are asking for nodes, namespaces, or pods.  
  - If “node”‐keywords appear (e.g. “node,” “nodes,” “cluster machines”), call `get_nodes()`.  
  - If “namespace”‐keywords appear (e.g. “namespaces,” “list namespaces,” “show namespaces”), call `get_namespaces()`.  
  - If “pod”‐keywords and a namespace string appear (e.g. “pods in namespace prod,” “list all pods under dev team”), extract that namespace into `{ns?}` and call `get_pods({ns?})`.  
  - If you cannot disambiguate, ask a clarifying question:  
    ```text
    “I’m not sure which resource you want—nodes, namespaces, or pods. Could you clarify?”
    ```

- **Step 2: Assemble and Call the Tool**  
  Once you decide which tool to use:  
  1. For `get_nodes()`, simply call it with no arguments.  
  2. For `get_namespaces()`, call it with no arguments.  
  3. For `get_pods({ns?})`, make sure `{ns?}` is nonempty. If the user did not specify a namespace, respond with:  
     ```json
     { "error": "Please specify a namespace for pod listing." }
     ```

- **Step 3: Return the Tool’s JSON**  
  After the tool returns a dictionary, embed it in your final response exactly as JSON. Your top‐level JSON must include a field indicating which resource was fetched. For example:  
  ```json
  {
    "resource": "pods",
    "namespace": "production",
    "result": {
      "Name_1": "frontend-abc123",
      "Name_2": "backend-def456"
    }
  }
    """,
    tools=[AgentTool(get_node),
           AgentTool(get_namespace),
           AgentTool(get_pod)]
)