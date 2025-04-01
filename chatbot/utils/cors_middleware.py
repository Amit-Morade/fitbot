from typing import Text, List, Dict, Any

from sanic import Sanic
from sanic.response import HTTPResponse


def cors_middleware() -> Text:
    def decorator(f):
        def decorated_function(request, *args, **kwargs):
            response = f(request, *args, **kwargs)
            
            response.headers.update({
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            })
            
            return response
            
        return decorated_function
    
    return decorator


def setup_cors(app: Sanic, route_handles: List[Dict[Text, Any]]) -> None:
    """Add CORS middleware to all routes."""
    for route_handle in route_handles:
        if route_handle.get("type", "") == "http":
            app.route(
                route_handle.get("route"), methods=route_handle.get("methods")
            )(cors_middleware()(route_handle.get("fn")))