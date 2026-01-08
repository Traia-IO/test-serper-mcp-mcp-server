#!/usr/bin/env python3
"""
Test Serper MCP MCP Server - FastMCP with D402 Transport Wrapper

Uses FastMCP from official MCP SDK with D402MCPTransport wrapper for HTTP 402.

Architecture:
- FastMCP for tool decorators and Context objects
- D402MCPTransport wraps the /mcp route for HTTP 402 interception
- Proper HTTP 402 status codes (not JSON-RPC wrapped)

Generated from OpenAPI: https://serper.dev/docs

Environment Variables:
- SERPER_API_KEY: Server's internal API key (for paid requests)
- SERVER_ADDRESS: Payment address (IATP wallet contract)
- MCP_OPERATOR_PRIVATE_KEY: Operator signing key
- D402_TESTING_MODE: Skip facilitator (default: true)
"""

import os
import logging
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union
from datetime import datetime

import requests
from retry import retry
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test-serper-mcp_mcp')

# FastMCP from official SDK
from mcp.server.fastmcp import FastMCP, Context
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# D402 payment protocol - using Starlette middleware
from traia_iatp.d402.starlette_middleware import D402PaymentMiddleware
from traia_iatp.d402.mcp_middleware import require_payment_for_tool, get_active_api_key
from traia_iatp.d402.payment_introspection import extract_payment_configs_from_mcp
from traia_iatp.d402.types import TokenAmount, TokenAsset, EIP712Domain

# Configuration
STAGE = os.getenv("STAGE", "MAINNET").upper()
PORT = int(os.getenv("PORT", "8000"))
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
if not SERVER_ADDRESS:
    raise ValueError("SERVER_ADDRESS required for payment protocol")

API_KEY = os.getenv("SERPER_API_KEY")
if not API_KEY:
    logger.warning(f"⚠️  SERPER_API_KEY not set - payment required for all requests")

logger.info("="*80)
logger.info(f"Test Serper MCP MCP Server (FastMCP + D402 Wrapper)")
logger.info(f"API: https://google.serper.dev")
logger.info(f"Payment: {SERVER_ADDRESS}")
logger.info(f"API Key: {'✅' if API_KEY else '❌ Payment required'}")
logger.info("="*80)

# Create FastMCP server
mcp = FastMCP("Test Serper MCP MCP Server", host="0.0.0.0")

logger.info(f"✅ FastMCP server created")

# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================
# Tool implementations will be added here by endpoint_implementer_crew
# Each tool will use the @mcp.tool() and @require_payment_for_tool() decorators


# D402 Payment Middleware
# The HTTP 402 payment protocol middleware is already configured in the server initialization.
# It's imported from traia_iatp.d402.mcp_middleware and auto-detects configuration from:
# - PAYMENT_ADDRESS or EVM_ADDRESS: Where to receive payments
# - EVM_NETWORK: Blockchain network (default: base-sepolia)
# - DEFAULT_PRICE_USD: Price per request (default: $0.001)
# - TEST_SERPER_MCP_API_KEY: Server's internal API key for payment mode
#
# All payment verification logic is handled by the traia_iatp.d402 module.
# No custom implementation needed!


# API Endpoint Tool Implementations

@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="3000000000000000",  # 0.003 tokens
        asset=TokenAsset(
            address="0x3e17730bb2ca51a8D5deD7E44c003A2e95a4d822",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Perform Google search with advanced filtering and "

)
async def google_search(
    context: Context,
    q: Optional[str] = None,
    gl: str = "us",
    hl: str = "en",
    num: int = 10,
    autocorrect: bool = True,
    page: int = 1,
    type: str = "search"
) -> Dict[str, Any]:
    """
    Perform Google search with advanced filtering and location options

    Generated from OpenAPI endpoint: POST /search

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        q: Search query (optional) Examples: "artificial intelligence", "python programming", "best restaurants"
        gl: Country code (e.g., us, uk, ca) (optional, default: "us") Examples: "us", "gb", "ca"
        hl: Language code (e.g., en, es, fr) (optional, default: "en") Examples: "en", "es", "fr"
        num: Number of results (1-100) (optional, default: 10)
        autocorrect: Enable autocorrect (optional, default: True)
        page: Page number (optional, default: 1)
        type: Search type (search, news, images, places, etc.) (optional, default: "search") Examples: "search", "news"

    Returns:
        Dictionary with API response

    Example Usage:
        await google_search(q="artificial intelligence")

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://google.serper.dev/search"
        params = {}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
            # Also send Bearer for robustness (most APIs use Bearer)
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(
            url,
            json={k: v for k, v in {
                "q": q,
                "gl": gl,
                "hl": hl,
                "num": num,
                "autocorrect": autocorrect,
                "page": page,
                "type": type,
            }.items() if v is not None},
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in google_search: {e}")
        return {"error": str(e), "endpoint": "/search"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="3000000000000000",  # 0.003 tokens
        asset=TokenAsset(
            address="0x3e17730bb2ca51a8D5deD7E44c003A2e95a4d822",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Search Google News with filtering options"

)
async def google_news_search(
    context: Context,
    q: Optional[str] = None,
    gl: str = "us",
    hl: str = "en",
    num: int = 10,
    tbs: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search Google News with filtering options

    Generated from OpenAPI endpoint: POST /news

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        q: News search query (optional) Examples: "bitcoin news", "climate change", "tech industry"
        gl: Country code (optional, default: "us") Examples: "us", "gb", "ca"
        hl: Language code (optional, default: "en") Examples: "en", "es", "fr"
        num: Number of results (optional, default: 10)
        tbs: Time filter (qdr:h - past hour, qdr:d - past day, qdr:w - past week, qdr:m - past month, qdr:y - past year) (optional) Examples: "qdr:d", "qdr:w"

    Returns:
        Dictionary with API response

    Example Usage:
        await google_news_search(q="bitcoin news")

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://google.serper.dev/news"
        params = {}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
            # Also send Bearer for robustness (most APIs use Bearer)
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(
            url,
            json={k: v for k, v in {
                "q": q,
                "gl": gl,
                "hl": hl,
                "num": num,
                "tbs": tbs,
            }.items() if v is not None},
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in google_news_search: {e}")
        return {"error": str(e), "endpoint": "/news"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="2000000000000000",  # 0.002 tokens
        asset=TokenAsset(
            address="0x3e17730bb2ca51a8D5deD7E44c003A2e95a4d822",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Search Google Images"

)
async def google_images_search(
    context: Context,
    q: Optional[str] = None,
    gl: str = "us",
    num: int = 10
) -> Dict[str, Any]:
    """
    Search Google Images

    Generated from OpenAPI endpoint: POST /images

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        q: Image search query (optional) Examples: "mountain landscape", "golden retriever", "modern architecture"
        gl: Country code (optional, default: "us") Examples: "us", "gb", "ca"
        num: Number of results (optional, default: 10)

    Returns:
        Dictionary with API response

    Example Usage:
        await google_images_search(q="mountain landscape")

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://google.serper.dev/images"
        params = {}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
            # Also send Bearer for robustness (most APIs use Bearer)
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(
            url,
            json={k: v for k, v in {
                "q": q,
                "gl": gl,
                "num": num,
            }.items() if v is not None},
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in google_images_search: {e}")
        return {"error": str(e), "endpoint": "/images"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="2000000000000000",  # 0.002 tokens
        asset=TokenAsset(
            address="0x3e17730bb2ca51a8D5deD7E44c003A2e95a4d822",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Search Google Places/Maps"

)
async def google_places_search(
    context: Context,
    q: Optional[str] = None,
    gl: str = "us",
    ll: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search Google Places/Maps

    Generated from OpenAPI endpoint: POST /places

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        q: Place search query (optional) Examples: "coffee shops near me", "restaurants in San Francisco", "hotels in Tokyo"
        gl: Country code (optional, default: "us") Examples: "us", "gb", "ca"
        ll: Latitude,Longitude for location bias (e.g., 40.7128,-74.0060) (optional) Examples: "40.7128,-74.0060", "37.7749,-122.4194"

    Returns:
        Dictionary with API response

    Example Usage:
        await google_places_search(q="coffee shops near me")

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://google.serper.dev/places"
        params = {}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
            # Also send Bearer for robustness (most APIs use Bearer)
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(
            url,
            json={k: v for k, v in {
                "q": q,
                "gl": gl,
                "ll": ll,
            }.items() if v is not None},
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in google_places_search: {e}")
        return {"error": str(e), "endpoint": "/places"}


# TODO: Add your API-specific functions here

# ============================================================================
# APPLICATION SETUP WITH STARLETTE MIDDLEWARE
# ============================================================================

def create_app_with_middleware():
    """
    Create Starlette app with d402 payment middleware.
    
    Strategy:
    1. Get FastMCP's Starlette app via streamable_http_app()
    2. Extract payment configs from @require_payment_for_tool decorators
    3. Add Starlette middleware with extracted configs
    4. Single source of truth - no duplication!
    """
    logger.info("🔧 Creating FastMCP app with middleware...")
    
    # Get FastMCP's Starlette app
    app = mcp.streamable_http_app()
    logger.info(f"✅ Got FastMCP Starlette app")
    
    # Extract payment configs from decorators (single source of truth!)
    tool_payment_configs = extract_payment_configs_from_mcp(mcp, SERVER_ADDRESS)
    logger.info(f"📊 Extracted {len(tool_payment_configs)} payment configs from @require_payment_for_tool decorators")
    
    # D402 Configuration
    facilitator_url = os.getenv("FACILITATOR_URL") or os.getenv("D402_FACILITATOR_URL")
    operator_key = os.getenv("MCP_OPERATOR_PRIVATE_KEY")
    network = os.getenv("NETWORK", "sepolia")
    testing_mode = os.getenv("D402_TESTING_MODE", "false").lower() == "true"
    
    # Log D402 configuration with prominent facilitator info
    logger.info("="*60)
    logger.info("D402 Payment Protocol Configuration:")
    logger.info(f"  Server Address: {SERVER_ADDRESS}")
    logger.info(f"  Network: {network}")
    logger.info(f"  Operator Key: {'✅ Set' if operator_key else '❌ Not set'}")
    logger.info(f"  Testing Mode: {'⚠️  ENABLED (bypasses facilitator)' if testing_mode else '✅ DISABLED (uses facilitator)'}")
    logger.info("="*60)
    
    if not facilitator_url and not testing_mode:
        logger.error("❌ FACILITATOR_URL required when testing_mode is disabled!")
        raise ValueError("Set FACILITATOR_URL or enable D402_TESTING_MODE=true")
    
    if facilitator_url:
        logger.info(f"🌐 FACILITATOR: {facilitator_url}")
        if "localhost" in facilitator_url or "127.0.0.1" in facilitator_url or "host.docker.internal" in facilitator_url:
            logger.info(f"   📍 Using LOCAL facilitator for development")
        else:
            logger.info(f"   🌍 Using REMOTE facilitator for production")
    else:
        logger.warning("⚠️  D402 Testing Mode - Facilitator bypassed")
    logger.info("="*60)
    
    # Add CORS middleware first (processes before other middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
        expose_headers=["mcp-session-id"],  # Expose custom headers to browser
    )
    logger.info("✅ Added CORS middleware (allow all origins, expose mcp-session-id)")
    
    # Add D402 payment middleware with extracted configs
    app.add_middleware(
        D402PaymentMiddleware,
        tool_payment_configs=tool_payment_configs,
        server_address=SERVER_ADDRESS,
        requires_auth=True,  # Extracts API keys + checks payment
        internal_api_key=API_KEY,  # Server's internal key (for Mode 2: paid access)
        testing_mode=testing_mode,
        facilitator_url=facilitator_url,
        facilitator_api_key=os.getenv("D402_FACILITATOR_API_KEY"),
        server_name="test-serper-mcp-mcp-server"  # MCP server ID for tracking
    )
    logger.info("✅ Added D402PaymentMiddleware")
    logger.info("   - Auth extraction: Enabled")
    logger.info("   - Dual mode: API key OR payment")
    
    # Add health check endpoint (bypasses middleware)
    @app.route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        """Health check endpoint for container orchestration."""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "test-serper-mcp-mcp-server",
                "timestamp": datetime.now().isoformat()
            }
        )
    logger.info("✅ Added /health endpoint")
    
    return app

if __name__ == "__main__":
    logger.info("="*80)
    logger.info(f"Starting Test Serper MCP MCP Server")
    logger.info("="*80)
    logger.info("Architecture:")
    logger.info("  1. D402PaymentMiddleware intercepts requests")
    logger.info("     - Extracts API keys from Authorization header")
    logger.info("     - Checks payment → HTTP 402 if no API key AND no payment")
    logger.info("  2. FastMCP processes valid requests with tool decorators")
    logger.info("="*80)
    
    # Create app with middleware
    app = create_app_with_middleware()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
