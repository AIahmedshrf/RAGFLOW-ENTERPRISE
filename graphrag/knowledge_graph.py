"""
Knowledge Graph Integration for RAGFlow Enterprise
Provides graph-based knowledge representation and querying
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class Node:
    """Graph node representing an entity"""
    node_id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Edge:
    """Graph edge representing a relationship"""
    edge_id: str
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class KnowledgeGraph:
    """In-memory knowledge graph (for Neo4j integration later)"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)
        self.node_counter = 0
        self.edge_counter = 0
    
    def add_node(
        self,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
        node_id: Optional[str] = None
    ) -> Node:
        """Add a node to the graph"""
        if not node_id:
            self.node_counter += 1
            node_id = f"node_{self.node_counter}"
        
        node = Node(
            node_id=node_id,
            label=label,
            properties=properties or {}
        )
        
        self.nodes[node_id] = node
        return node
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        edge_id: Optional[str] = None
    ) -> Edge:
        """Add an edge to the graph"""
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Source or target node not found")
        
        if not edge_id:
            self.edge_counter += 1
            edge_id = f"edge_{self.edge_counter}"
        
        edge = Edge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            properties=properties or {}
        )
        
        self.edges[edge_id] = edge
        self.adjacency[source_id].append(edge_id)
        self.reverse_adjacency[target_id].append(edge_id)
        
        return edge
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by ID"""
        return self.edges.get(edge_id)
    
    def get_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        direction: str = 'outgoing'  # outgoing, incoming, both
    ) -> List[Node]:
        """Get neighboring nodes"""
        if node_id not in self.nodes:
            return []
        
        neighbors = []
        
        # Outgoing edges
        if direction in ['outgoing', 'both']:
            for edge_id in self.adjacency[node_id]:
                edge = self.edges[edge_id]
                if not relationship_type or edge.relationship_type == relationship_type:
                    neighbors.append(self.nodes[edge.target_id])
        
        # Incoming edges
        if direction in ['incoming', 'both']:
            for edge_id in self.reverse_adjacency[node_id]:
                edge = self.edges[edge_id]
                if not relationship_type or edge.relationship_type == relationship_type:
                    neighbors.append(self.nodes[edge.source_id])
        
        return neighbors
    
    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5
    ) -> List[List[str]]:
        """Find paths between two nodes using BFS"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        
        paths = []
        queue = [([start_id], set([start_id]))]
        
        while queue:
            path, visited = queue.pop(0)
            current = path[-1]
            
            if len(path) > max_depth:
                continue
            
            if current == end_id:
                paths.append(path)
                continue
            
            # Explore neighbors
            for edge_id in self.adjacency[current]:
                edge = self.edges[edge_id]
                neighbor = edge.target_id
                
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    new_visited = visited | {neighbor}
                    queue.append((new_path, new_visited))
        
        return paths
    
    def query_by_property(
        self,
        property_name: str,
        property_value: Any,
        node_label: Optional[str] = None
    ) -> List[Node]:
        """Query nodes by property"""
        results = []
        
        for node in self.nodes.values():
            # Check label match
            if node_label and node.label != node_label:
                continue
            
            # Check property match
            if node.properties.get(property_name) == property_value:
                results.append(node)
        
        return results
    
    def get_subgraph(
        self,
        node_ids: List[str],
        depth: int = 1
    ) -> Dict[str, Any]:
        """Extract subgraph around specified nodes"""
        subgraph_nodes = set(node_ids)
        subgraph_edges = set()
        
        # Expand to specified depth
        for _ in range(depth):
            new_nodes = set()
            
            for node_id in list(subgraph_nodes):
                # Outgoing edges
                for edge_id in self.adjacency.get(node_id, []):
                    edge = self.edges[edge_id]
                    subgraph_edges.add(edge_id)
                    new_nodes.add(edge.target_id)
                
                # Incoming edges
                for edge_id in self.reverse_adjacency.get(node_id, []):
                    edge = self.edges[edge_id]
                    subgraph_edges.add(edge_id)
                    new_nodes.add(edge.source_id)
            
            subgraph_nodes.update(new_nodes)
        
        return {
            'nodes': [self.nodes[nid].__dict__ for nid in subgraph_nodes if nid in self.nodes],
            'edges': [self.edges[eid].__dict__ for eid in subgraph_edges if eid in self.edges]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        # Count nodes by label
        label_counts = defaultdict(int)
        for node in self.nodes.values():
            label_counts[node.label] += 1
        
        # Count edges by type
        edge_counts = defaultdict(int)
        for edge in self.edges.values():
            edge_counts[edge.relationship_type] += 1
        
        # Calculate degree distribution
        out_degrees = [len(self.adjacency[nid]) for nid in self.nodes]
        in_degrees = [len(self.reverse_adjacency[nid]) for nid in self.nodes]
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'nodes_by_label': dict(label_counts),
            'edges_by_type': dict(edge_counts),
            'avg_out_degree': sum(out_degrees) / len(out_degrees) if out_degrees else 0,
            'avg_in_degree': sum(in_degrees) / len(in_degrees) if in_degrees else 0,
            'max_out_degree': max(out_degrees) if out_degrees else 0,
            'max_in_degree': max(in_degrees) if in_degrees else 0,
        }
    
    def export_to_cypher(self) -> List[str]:
        """Export graph to Cypher statements (for Neo4j)"""
        statements = []
        
        # Create nodes
        for node in self.nodes.values():
            props = json.dumps(node.properties)
            statements.append(
                f"CREATE (n:{node.label} {{id: '{node.node_id}', properties: {props}}})"
            )
        
        # Create edges
        for edge in self.edges.values():
            props = json.dumps(edge.properties)
            statements.append(
                f"MATCH (a {{id: '{edge.source_id}'}}), (b {{id: '{edge.target_id}'}}) "
                f"CREATE (a)-[r:{edge.relationship_type} {{properties: {props}}}]->(b)"
            )
        
        return statements


class EntityExtractor:
    """Extract entities from text for knowledge graph"""
    
    def __init__(self):
        self.entity_types = [
            'PERSON', 'ORGANIZATION', 'LOCATION', 'DATE', 
            'PRODUCT', 'EVENT', 'TECHNOLOGY', 'CONCEPT'
        ]
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text (placeholder for NER)"""
        # In production, use spaCy, transformers, or other NER models
        # This is a simple placeholder
        entities = []
        
        # Example: Extract simple patterns
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 3:
                entities.append({
                    'text': word,
                    'type': 'UNKNOWN',
                    'start': text.find(word),
                    'end': text.find(word) + len(word)
                })
        
        return entities
    
    def extract_relationships(
        self,
        text: str,
        entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        # Placeholder for relationship extraction
        # In production, use dependency parsing or relation extraction models
        relationships = []
        
        # Example: Find entities close to each other
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                distance = abs(entity1['start'] - entity2['start'])
                if distance < 100:  # Within 100 characters
                    relationships.append({
                        'source': entity1['text'],
                        'target': entity2['text'],
                        'type': 'RELATED_TO',
                        'confidence': 0.5
                    })
        
        return relationships
    
    def build_graph_from_text(
        self,
        text: str,
        graph: KnowledgeGraph
    ) -> Dict[str, Any]:
        """Build knowledge graph from text"""
        # Extract entities
        entities = self.extract_entities(text)
        
        # Add entities as nodes
        entity_nodes = {}
        for entity in entities:
            node = graph.add_node(
                label=entity['type'],
                properties={
                    'text': entity['text'],
                    'source': 'extracted'
                }
            )
            entity_nodes[entity['text']] = node
        
        # Extract and add relationships
        relationships = self.extract_relationships(text, entities)
        
        for rel in relationships:
            if rel['source'] in entity_nodes and rel['target'] in entity_nodes:
                graph.add_edge(
                    source_id=entity_nodes[rel['source']].node_id,
                    target_id=entity_nodes[rel['target']].node_id,
                    relationship_type=rel['type'],
                    properties={'confidence': rel['confidence']}
                )
        
        return {
            'entities_extracted': len(entities),
            'relationships_extracted': len(relationships)
        }


# Global instances
knowledge_graph = KnowledgeGraph()
entity_extractor = EntityExtractor()
