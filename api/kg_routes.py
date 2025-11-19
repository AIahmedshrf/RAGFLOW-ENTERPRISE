"""
Knowledge Graph API Routes
"""
from flask import Blueprint, request
from graphrag.knowledge_graph import knowledge_graph, entity_extractor
from api.security import require_api_key, rate_limit


kg_bp = Blueprint('knowledge_graph', __name__, url_prefix='/api/v1/kg')


@kg_bp.route('/nodes', methods=['POST'])
@require_api_key
@rate_limit('basic')
def create_node():
    """Create a node in knowledge graph"""
    try:
        data = request.get_json()
        
        node = knowledge_graph.add_node(
            label=data['label'],
            properties=data.get('properties', {}),
            node_id=data.get('node_id')
        )
        
        return {
            'success': True,
            'node': {
                'node_id': node.node_id,
                'label': node.label,
                'properties': node.properties,
                'created_at': node.created_at
            }
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@kg_bp.route('/nodes/<node_id>', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_node(node_id):
    """Get a node by ID"""
    node = knowledge_graph.get_node(node_id)
    
    if not node:
        return {'error': 'Node not found', 'code': 404}, 404
    
    return {
        'success': True,
        'node': {
            'node_id': node.node_id,
            'label': node.label,
            'properties': node.properties,
            'created_at': node.created_at
        }
    }


@kg_bp.route('/edges', methods=['POST'])
@require_api_key
@rate_limit('basic')
def create_edge():
    """Create an edge in knowledge graph"""
    try:
        data = request.get_json()
        
        edge = knowledge_graph.add_edge(
            source_id=data['source_id'],
            target_id=data['target_id'],
            relationship_type=data['relationship_type'],
            properties=data.get('properties', {}),
            edge_id=data.get('edge_id')
        )
        
        return {
            'success': True,
            'edge': {
                'edge_id': edge.edge_id,
                'source_id': edge.source_id,
                'target_id': edge.target_id,
                'relationship_type': edge.relationship_type,
                'properties': edge.properties,
                'created_at': edge.created_at
            }
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@kg_bp.route('/neighbors/<node_id>', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_neighbors(node_id):
    """Get neighboring nodes"""
    relationship_type = request.args.get('relationship_type')
    direction = request.args.get('direction', 'outgoing')
    
    neighbors = knowledge_graph.get_neighbors(
        node_id=node_id,
        relationship_type=relationship_type,
        direction=direction
    )
    
    return {
        'success': True,
        'neighbors': [
            {
                'node_id': n.node_id,
                'label': n.label,
                'properties': n.properties
            }
            for n in neighbors
        ],
        'total': len(neighbors)
    }


@kg_bp.route('/path', methods=['POST'])
@require_api_key
@rate_limit('professional')
def find_path():
    """Find paths between two nodes"""
    try:
        data = request.get_json()
        
        paths = knowledge_graph.find_path(
            start_id=data['start_id'],
            end_id=data['end_id'],
            max_depth=data.get('max_depth', 5)
        )
        
        return {
            'success': True,
            'paths': paths,
            'total_paths': len(paths)
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@kg_bp.route('/query', methods=['POST'])
@require_api_key
@rate_limit('basic')
def query_by_property():
    """Query nodes by property"""
    try:
        data = request.get_json()
        
        results = knowledge_graph.query_by_property(
            property_name=data['property_name'],
            property_value=data['property_value'],
            node_label=data.get('node_label')
        )
        
        return {
            'success': True,
            'results': [
                {
                    'node_id': n.node_id,
                    'label': n.label,
                    'properties': n.properties
                }
                for n in results
            ],
            'total': len(results)
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@kg_bp.route('/subgraph', methods=['POST'])
@require_api_key
@rate_limit('professional')
def get_subgraph():
    """Get subgraph around nodes"""
    try:
        data = request.get_json()
        
        subgraph = knowledge_graph.get_subgraph(
            node_ids=data['node_ids'],
            depth=data.get('depth', 1)
        )
        
        return {
            'success': True,
            'subgraph': subgraph
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@kg_bp.route('/statistics', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_statistics():
    """Get knowledge graph statistics"""
    stats = knowledge_graph.get_statistics()
    
    return {
        'success': True,
        'statistics': stats
    }


@kg_bp.route('/extract', methods=['POST'])
@require_api_key
@rate_limit('professional')
def extract_from_text():
    """Extract entities and build knowledge graph from text"""
    try:
        data = request.get_json()
        text = data['text']
        
        result = entity_extractor.build_graph_from_text(text, knowledge_graph)
        
        return {
            'success': True,
            'extraction': result
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@kg_bp.route('/export/cypher', methods=['GET'])
@require_api_key
@rate_limit('professional')
def export_cypher():
    """Export graph to Cypher statements"""
    statements = knowledge_graph.export_to_cypher()
    
    return {
        'success': True,
        'statements': statements,
        'total': len(statements)
    }
