from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from nodes.nodes import NODE_TYPES, IMAGE
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NodeSchema(BaseModel):
    id: str
    type: str
    attrs: Optional[Dict[str, Any]] = None

class EdgeSchema(BaseModel):
    fromNode: str
    fromSocket: int
    toNode: str
    toSocket: int

class GraphSchema(BaseModel):
    nodes: List[NodeSchema]
    edges: List[EdgeSchema]


@app.post("/api/compute")
def compute_graph(graph: GraphSchema):
    node_instances = {}
    

    # 1. Instantiate all nodes
    for n in graph.nodes:
        if n.type not in NODE_TYPES:
            raise HTTPException(status_code=400, detail=f"Unknown node type: {n.type}")
        node_instances[n.id] = NODE_TYPES[n.type](n.id, n.attrs)
        
    # 2. Wire up edges
    out_degrees = {n.id: 0 for n in graph.nodes}
    
    for edge in graph.edges:
        if edge.toNode not in node_instances or edge.fromNode not in node_instances:
            continue
            
        target_node = node_instances[edge.toNode]
        source_node = node_instances[edge.fromNode]
        
        if hasattr(target_node, "connectInput"):
            target_node.connectInput(edge.toSocket, source_node, edge.fromSocket)
            out_degrees[edge.fromNode] += 1
            
    # 3. Find graph sinks (nodes with out_degree 0)
    sinks = [n_id for n_id, out_deg in out_degrees.items() if out_deg == 0]
    
    results = {}
    
    # 4. Compute backwards from sinks
    for n_id in sinks:
        sink_node = node_instances[n_id]
        sink_node.compute()
        # Collect image outputs or any meaningful output
        if sink_node.outputs and len(sink_node.outputs) > 0 and sink_node.outputs[0][0] == IMAGE:
            results[n_id] = sink_node.outputs[0][1]
            
    return {"results": results}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
