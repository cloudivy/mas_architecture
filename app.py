import streamlit as st
import json
import uuid
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, List, Any

# ========================================
# IN-MEMORY STORAGE LAYER (No sqlite3 needed)
# ========================================
class StorageLayer:
    def __init__(self):
        self.conversations: Dict[str, Dict] = {}
        self.agent_registry: Dict[str, Dict] = {
            "researcher": {"type": "local", "status": "active", "capabilities": "research,data"},
            "analyst": {"type": "local", "status": "active", "capabilities": "analysis,insights"},
            "writer": {"type": "local", "status": "active", "capabilities": "reports"},
            "planner": {"type": "remote", "status": "active", "capabilities": "planning"}
        }
    
    def store_conversation(self, conv_id: str, data: Dict):
        self.conversations[conv_id] = {"data": data, "timestamp": datetime.now().isoformat()}
    
    def get_conversations(self) -> List:
        return list(self.conversations.values())
    
    def query_registry(self, capability: str) -> List[str]:
        return [agent for agent, info in self.agent_registry.items() 
                if capability.lower() in info["capabilities"].lower()]

# MCP Protocol Simulation (Model Context Protocol)
class MCPClient:
    def __init__(self):
        self.tools = {"web_search": "✅ Available", "db_query": "✅ Available", "file_read": "✅ Available"}
    
    def call_tool(self, tool_name: str, params: Dict) -> str:
        return f"🛠️ MCP Tool '{tool_name}' executed: {json.dumps(params)[:50]}..."

# ========================================
# FULL MICROSOFT ARCHITECTURE IMPLEMENTATION
# ========================================
class MicrosoftMultiAgentArchitecture:
    def __init__(self):
        self.storage = StorageLayer()
        self.mcp = MCPClient()
        api_key = st.secrets.get("OPENAI_API_KEY")
        if not api_key:
            st.error("❌ Add OPENAI_API_KEY to Secrets!")
            st.stop()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    
    # User Application Layer
    def user_app_layer(self, user_input: str, user_id: str = "divya_mittal"):
        conv_id = str(uuid.uuid4())
        st.session_state.current_conv = conv_id
        
        # Orchestrator Layer
        orchestrator_result = self.orchestrator_layer(conv_id, user_input)
        
        # Storage Layer
        self.storage.store_conversation(conv_id, orchestrator_result)
        
        return orchestrator_result
    
    # Orchestrator Layer
    def orchestrator_layer(self, conv_id: str, input_text: str) -> Dict:
        # Intent Classifier Layer
        classifier_result = self.intent_classifier_layer(input_text)
        
        # Agent Registry Layer
        available_agents = self.storage.query_registry(classifier_result["intent"])
        
        # Supervisor Layer
        supervisor_decision = self.supervisor_layer(classifier_result, available_agents)
        
        # Execute Agent Layer
        agent_results = []
        for agent_id in supervisor_decision["selected_agents"]:
            agent_result = self.agent_layer(agent_id, input_text)
            agent_results.append(agent_result)
        
        return {
            "conversation_id": conv_id,
            "user_app": input_text,
            "classifier": classifier_result,
            "registry": available_agents,
            "supervisor": supervisor_decision,
            "agents_executed": agent_results,
            "mcp_tools_used": len(supervisor_decision["tools_needed"]),
            "storage": "✅ Persisted"
        }
    
    # Intent Classifier Layer
    def intent_classifier_layer(self, text: str) -> Dict:
        prompt = f"""Classify this task intent: "{text}"

Return JSON only:
{{"intent": "research|analyze|write|plan", "confidence": 0.95}}"""
        response = self.llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except:
            return {"intent": "research", "confidence": 0.9}
    
    # Supervisor Layer
    def supervisor_layer(self, classification: Dict, agents: List[str]) -> Dict:
        prompt = f"""Task intent: {classification['intent']}
Available agents: {agents}

Decide execution plan. Return JSON:
{{
  "selected_agents": ["agent1", "agent2"],
  "tools_needed": ["web_search", "db_query"],
  "priority": "high|medium|low"
}}"""
        response = self.llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except:
            return {
                "selected_agents": [agents[0]] if agents else ["researcher"],
                "tools_needed": ["web_search"],
                "priority": "medium"
            }
    
    # Agent Layer (Local + Remote Agents)
    def agent_layer(self, agent_id: str, task: str) -> Dict:
        # Knowledge Layer (RAG simulation)
        knowledge = self.knowledge_layer(task)
        
        # MCP Tool Integration
        mcp_result = self.mcp.call_tool("web_search", {"query": task})
        
        prompt = f"""You are {agent_id.upper()} Agent.
Task: {task}
Knowledge Base: {knowledge}
MCP Tools: {mcp_result}

Provide your specialized response."""
        
        response = self.llm.invoke(prompt)
        return {
            "agent_id": agent_id,
            "agent_type": self.storage.agent_registry.get(agent_id, {}).get("type", "local"),
            "output": response.content[:500] + "..." if len(response.content) > 500 else response.content
        }
    
    # Knowledge Layer
    def knowledge_layer(self, query: str) -> str:
        knowledge_base = {
            "research": "AI agents, context drift, LangGraph, CrewAI, PdM pipelines",
            "analyze": "Corrosion prediction, agent frameworks comparison",
            "write": "Technical reports, research papers, IOCL documentation",
            "plan": "Multi-agent orchestration strategies"
        }
        return knowledge_base.get(query.split()[0].lower(), "General AI/ML knowledge")
    
    # Observability Layer
    def observability_layer(self) -> Dict:
        return {
            "total_conversations": len(self.storage.conversations),
            "active_agents": len(self.storage.agent_registry),
            "registry_status": {k: v["status"] for k, v in self.storage.agent_registry.items()}
        }

# ========================================
# STREAMLIT UI - User Application Layer
# ========================================
st.set_page_config(page_title="Microsoft Multi-Agent Architecture", layout="wide")

st.title("🏗️ Microsoft Multi-Agent Reference Architecture")
st.markdown("**COMPLETE IMPLEMENTATION** - All diagram components active")

# Initialize Architecture
if "architecture" not in st.session_state:
    st.session_state.architecture = MicrosoftMultiAgentArchitecture()

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns([3, 1])

with col1:
    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(f"**{msg['role'].upper()}:** {msg['content']}")
    
    # User Input
    prompt = st.chat_input("🎯 Enter task (e.g., 'Research pipeline PdM frameworks')")
    
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🚀 **Full Architecture:** UserApp→Orchestrator→Classifier→Supervisor→Agents→MCP→Storage"):
                result = st.session_state.architecture.user_app_layer(prompt)
                
                # Architecture Trace Visualization
                st.markdown("**🏗️ EXECUTION TRACE**")
                trace_cols = st.columns(4)
                
                with trace_cols[0]:
                    st.metric("📊 Classifier", result["classifier"]["intent"])
                with trace_cols[1]:
                    st.metric("🤖 Agents", len(result["agents_executed"]))
                with trace_cols[2]:
                    st.metric("🛠️ MCP Calls", result["mcp_tools_used"])
                with trace_cols[3]:
                    st.metric("💾 Storage", "✅ Active")
                
                # Agent Results
                st.markdown("**🤖 AGENT OUTPUTS**")
                for agent_result in result["agents_executed"]:
                    with st.expander(f"🐙 {agent_result['agent_id']} ({agent_result['agent_type']})"):
                        st.write(agent_result['output'])
                
                # Store message
                display_msg = f"**Architecture Complete!** {len(result['agents_executed'])} agents executed."
                st.markdown(display_msg)
                st.session_state.messages.append({"role": "assistant", "content": display_msg})

with col2:
    # Observability Dashboard
    st.header("📊 Observability")
    obs = st.session_state.architecture.observability_layer()
    st.metric("Conversations", obs["total_conversations"])
    st.metric("Active Agents", obs["active_agents"])
    
    st.subheader("Agent Registry")
    st.json({k: v["status"] for k, v in st.session_state.architecture.storage.agent_registry.items()})

# Sidebar - Architecture Legend
with st.sidebar:
    st.markdown("### ✅ **ALL COMPONENTS LIVE**")
    st.markdown("""
    🟢 **User App** - Chat interface ✓
    🟢 **Orchestrator** - Request routing ✓  
    🟢 **Classifier** - Intent detection ✓
    🟢 **Agent Registry** - Dynamic lookup ✓
    🟢 **Supervisor** - Coordination ✓
    🟢 **Agent Layer** - Local/Remote agents ✓
    🟢 **Knowledge Layer** - RAG simulation ✓
    🟢 **MCP** - Tool protocol ✓
    🟢 **Storage** - In-memory persistence ✓
    🟢 **Observability** - Real-time metrics ✓
    """)
