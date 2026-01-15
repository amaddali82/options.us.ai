from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, exists
from datetime import datetime, timezone
from typing import Optional, List
import uuid
import logging
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from database_async import get_async_db, engine
from models import Recommendation, RecoTarget, OptionIdea, OptionTarget
from schemas import (
    HealthResponse, 
    RecommendationListResponse,
    RecommendationListItem,
    RecommendationDetail,
    PaginationMeta,
    SeedResponse,
    TargetSummary,
    OptionSummary,
    TargetDetail,
    OptionDetail,
    OptionTargetDetail
)
from ranking import calculate_rank_from_model
from reco_generator import generate_batch, SYMBOL_UNIVERSE
from scheduler import start_scheduler, stop_scheduler, update_stock_prices, update_options_data, get_last_sync_times

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['endpoint']
)

active_requests = Gauge(
    'http_requests_active',
    'Number of active requests'
)

app = FastAPI(
    title="Trading Intelligence API",
    description="Multi-target trading recommendations with options support",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with method, path, status, and latency"""
    start_time = time.time()
    active_requests.inc()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Latency: {duration:.3f}s"
        )
        
        # Update metrics
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
    finally:
        active_requests.dec()


@app.on_event("startup")
async def startup_event():
    """Startup event - verify database connection and start scheduler"""
    try:
        async with engine.begin() as conn:
            await conn.execute(select(1))
        logger.info("Database connection established")
        
        # Start background scheduler
        start_scheduler()
        logger.info("Background scheduler started")
    except Exception as e:
        logger.error(f"Failed to start services: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup"""
    stop_scheduler()
    await engine.dispose()
    logger.info("Database connection closed, scheduler stopped")


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - returns API health status"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc)
    )


@app.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connection
        await db.execute(select(1))
        
        # Get last sync times
        sync_times = get_last_sync_times()
        
        return HealthResponse(
            status="ok",
            timestamp=datetime.now(timezone.utc),
            database="connected",
            last_stock_sync=sync_times['stock_prices'],
            last_options_sync=sync_times['options_data']
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            timestamp=datetime.now(timezone.utc),
            database=f"error: {str(e)}"
        )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def parse_cursor(cursor_str: Optional[str]) -> tuple[Optional[datetime], Optional[uuid.UUID]]:
    """Parse cursor string into (asof, reco_id) tuple"""
    if not cursor_str:
        return None, None
    
    try:
        parts = cursor_str.split("|")
        if len(parts) != 2:
            return None, None
        
        asof = datetime.fromisoformat(parts[0])
        reco_id = uuid.UUID(parts[1])
        return asof, reco_id
    except Exception:
        return None, None


def encode_cursor(asof: datetime, reco_id: uuid.UUID) -> str:
    """Encode (asof, reco_id) into cursor string"""
    return f"{asof.isoformat()}|{str(reco_id)}"


@app.get("/recommendations", response_model=RecommendationListResponse)
async def list_recommendations(
    limit: int = Query(200, ge=1, le=500, description="Number of recommendations to return"),
    horizon: Optional[str] = Query(None, description="Filter by horizon (e.g., intraday, swing, position)"),
    min_conf: float = Query(0.60, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    symbol: Optional[str] = Query(None, description="Filter by symbol (e.g., AAPL)"),
    sort: str = Query("rank", regex="^(rank|confidence|asof)$", description="Sort order: rank, confidence, or asof"),
    cursor: Optional[str] = Query(None, description="Pagination cursor (asof|reco_id)"),
    options_only: bool = Query(False, description="Show only recommendations with option strategies"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get list of recommendations with lightweight fields
    
    Returns:
    - List of recommendations with TP1/TP2 and option summary
    - Pagination metadata with next cursor
    - Sorted by rank (default) or other fields
    """
    query_start = time.time()
    try:
        # Build base query
        stmt = select(Recommendation)
        
        # Apply filters
        filters = []
        if horizon:
            filters.append(Recommendation.horizon == horizon.lower())
        if min_conf:
            filters.append(Recommendation.confidence_overall >= min_conf)
        if symbol:
            filters.append(Recommendation.symbol == symbol.upper())
        if options_only:
            # Filter for recommendations that have associated option ideas  
            filters.append(
                Recommendation.reco_id.in_(
                    select(OptionIdea.reco_id).distinct()
                )
            )
        
        # Apply cursor-based pagination
        cursor_asof, cursor_reco_id = parse_cursor(cursor)
        if cursor_asof and cursor_reco_id:
            # For cursor pagination, we need to continue from last position
            filters.append(
                or_(
                    Recommendation.asof < cursor_asof,
                    and_(
                        Recommendation.asof == cursor_asof,
                        Recommendation.reco_id > cursor_reco_id
                    )
                )
            )
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        # Apply sorting (we'll re-sort in Python for rank)
        if sort == "asof":
            stmt = stmt.order_by(Recommendation.asof.desc())
        elif sort == "confidence":
            stmt = stmt.order_by(Recommendation.confidence_overall.desc())
        else:  # rank
            stmt = stmt.order_by(Recommendation.asof.desc())  # Get recent ones first
        
        # Fetch limit + 1 to check if there are more
        stmt = stmt.limit(limit + 1)
        
        # Execute query and measure time
        db_start = time.time()
        result = await db.execute(stmt)
        recommendations = result.scalars().all()
        db_duration = time.time() - db_start
        
        # Log DB query timing
        logger.info(f"DB query for recommendations list took {db_duration:.3f}s (returned {len(recommendations)} rows)")
        db_query_duration.labels(endpoint='/recommendations').observe(db_duration)
        
        # Calculate rank for each recommendation
        reco_with_rank = []
        for reco in recommendations:
            rank_score = calculate_rank_from_model(reco)
            reco_with_rank.append((reco, rank_score))
        
        # Sort by rank if requested
        if sort == "rank":
            reco_with_rank.sort(key=lambda x: x[1], reverse=True)
        
        # Check if there are more results
        has_more = len(reco_with_rank) > limit
        if has_more:
            reco_with_rank = reco_with_rank[:limit]
        
        # Build response items
        items = []
        for reco, rank_score in reco_with_rank:
            # Get first two targets
            tp1 = None
            tp2 = None
            if reco.targets:
                sorted_targets = sorted(reco.targets, key=lambda t: t.ordinal)
                if len(sorted_targets) >= 1:
                    tp1 = TargetSummary(
                        ordinal=sorted_targets[0].ordinal,
                        value=float(sorted_targets[0].value),
                        confidence=float(sorted_targets[0].confidence)
                    )
                if len(sorted_targets) >= 2:
                    tp2 = TargetSummary(
                        ordinal=sorted_targets[1].ordinal,
                        value=float(sorted_targets[1].value),
                        confidence=float(sorted_targets[1].confidence)
                    )
            
            # Build option summary if present
            option_summary = None
            if reco.option_idea:
                opt = reco.option_idea
                opt_targets = []
                if opt.option_targets:
                    sorted_opt_targets = sorted(opt.option_targets, key=lambda t: t.ordinal)[:2]
                    opt_targets = [
                        TargetSummary(
                            ordinal=t.ordinal,
                            value=float(t.value),
                            confidence=float(t.confidence)
                        )
                        for t in sorted_opt_targets
                    ]
                
                option_summary = OptionSummary(
                    option_type=opt.option_type,
                    expiry=opt.expiry,
                    strike=float(opt.strike),
                    option_entry_price=float(opt.option_entry_price) if opt.option_entry_price else None,
                    option_targets=opt_targets
                )
            
            item = RecommendationListItem(
                reco_id=reco.reco_id,
                asof=reco.asof,
                symbol=reco.symbol,
                horizon=reco.horizon,
                side=reco.side,
                entry_price=float(reco.entry_price),
                confidence_overall=float(reco.confidence_overall),
                expected_move_pct=float(reco.expected_move_pct) if reco.expected_move_pct else None,
                rank=rank_score,
                tp1=tp1,
                tp2=tp2,
                option_summary=option_summary
            )
            items.append(item)
        
        # Build next cursor
        next_cursor = None
        if has_more and items:
            last_item = reco_with_rank[-1][0]  # Last recommendation
            next_cursor = encode_cursor(last_item.asof, last_item.reco_id)
        
        return RecommendationListResponse(
            recommendations=items,
            meta=PaginationMeta(
                total_returned=len(items),
                has_more=has_more,
                next_cursor=next_cursor
            )
        )
        
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/recommendations/{reco_id}", response_model=RecommendationDetail)
async def get_recommendation_detail(
    reco_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get full recommendation details including rationale and all targets
    
    Args:
        reco_id: UUID of the recommendation
        
    Returns:
        Full recommendation with all fields, targets, and option details
    """
    try:
        # Fetch recommendation with all relationships
        stmt = select(Recommendation).where(Recommendation.reco_id == reco_id)
        result = await db.execute(stmt)
        reco = result.scalar_one_or_none()
        
        if not reco:
            raise HTTPException(status_code=404, detail=f"Recommendation {reco_id} not found")
        
        # Calculate rank
        rank_score = calculate_rank_from_model(reco)
        
        # Build targets list
        targets = []
        if reco.targets:
            sorted_targets = sorted(reco.targets, key=lambda t: t.ordinal)
            targets = [
                TargetDetail(
                    ordinal=t.ordinal,
                    name=t.name,
                    target_type=t.target_type,
                    value=float(t.value),
                    confidence=float(t.confidence),
                    eta_minutes=t.eta_minutes,
                    notes=t.notes
                )
                for t in sorted_targets
            ]
        
        # Build option detail if present
        option_detail = None
        if reco.option_idea:
            opt = reco.option_idea
            opt_targets = []
            if opt.option_targets:
                sorted_opt_targets = sorted(opt.option_targets, key=lambda t: t.ordinal)
                opt_targets = [
                    OptionTargetDetail(
                        ordinal=t.ordinal,
                        name=t.name,
                        value=float(t.value),
                        confidence=float(t.confidence),
                        eta_minutes=t.eta_minutes,
                        notes=t.notes
                    )
                    for t in sorted_opt_targets
                ]
            
            option_detail = OptionDetail(
                option_type=opt.option_type,
                expiry=opt.expiry,
                strike=float(opt.strike),
                option_entry_price=float(opt.option_entry_price),
                greeks=opt.greeks,
                iv=opt.iv,
                notes=opt.notes,
                option_targets=opt_targets
            )
        
        return RecommendationDetail(
            reco_id=reco.reco_id,
            asof=reco.asof,
            symbol=reco.symbol,
            horizon=reco.horizon,
            side=reco.side,
            entry_price=float(reco.entry_price),
            confidence_overall=float(reco.confidence_overall),
            expected_move_pct=float(reco.expected_move_pct) if reco.expected_move_pct else None,
            rationale=reco.rationale,
            quality=reco.quality,
            rank=rank_score,
            targets=targets,
            option_idea=option_detail,
            created_at=reco.created_at,
            updated_at=reco.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recommendation detail: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@app.post("/recommendations/seed", response_model=SeedResponse)
async def seed_recommendations(
    count: int = Query(20, ge=1, le=200, description="Number of recommendations to generate"),
    option_pct: float = Query(0.65, ge=0.0, le=1.0, description="Percentage with options"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Seed database with realistic generated recommendations
    
    Uses reco_generator to create diverse recommendations with:
    - Mix of BUY/SELL/HOLD positions across multiple symbols
    - Different horizons (intraday, swing, position)
    - Realistic targets, stops, and confidence levels
    - Options with Greeks and IV (configurable percentage)
    - Event-driven rationale with sentiment
    
    Query Parameters:
    - count: Number of recommendations (1-200, default 20)
    - option_pct: Percentage with options (0.0-1.0, default 0.65)
    """
    try:
        # Generate recommendations using the generator
        generated_recos = generate_batch(
            num_recommendations=count,
            option_pct=option_pct
        )
        
        created_ids = []
        
        for reco_data in generated_recos:
            # Create Recommendation
            reco = Recommendation(
                reco_id=reco_data["reco_id"],
                asof=reco_data["asof"],
                symbol=reco_data["symbol"],
                horizon=reco_data["horizon"],
                side=reco_data["side"],
                entry_price=reco_data["entry_price"],
                confidence_overall=reco_data["confidence_overall"],
                expected_move_pct=reco_data["expected_move_pct"],
                rationale=reco_data["rationale"],
                quality=reco_data["quality"]
            )
            db.add(reco)
            
            # Add targets
            for target_data in reco_data["targets"]:
                target = RecoTarget(
                    reco_id=reco_data["reco_id"],
                    ordinal=target_data["ordinal"],
                    name=target_data.get("name"),
                    target_type=target_data.get("target_type", "price"),
                    value=target_data["value"],
                    confidence=target_data["confidence"],
                    eta_minutes=target_data.get("eta_minutes")
                )
                db.add(target)
            
            # Add option if present
            if "option_idea" in reco_data:
                opt_data = reco_data["option_idea"]
                option = OptionIdea(
                    reco_id=reco_data["reco_id"],
                    option_type=opt_data["option_type"],
                    expiry=opt_data["expiry"],
                    strike=opt_data["strike"],
                    option_entry_price=opt_data["option_entry_price"],
                    greeks=opt_data.get("greeks"),
                    iv=opt_data.get("iv"),
                    notes=opt_data.get("notes")
                )
                db.add(option)
                
                # Add option targets
                for opt_target_data in opt_data.get("option_targets", []):
                    opt_target = OptionTarget(
                        reco_id=reco_data["reco_id"],
                        ordinal=opt_target_data["ordinal"],
                        name=opt_target_data.get("name"),
                        value=opt_target_data["value"],
                        confidence=opt_target_data["confidence"],
                        eta_minutes=opt_target_data.get("eta_minutes")
                    )
                    db.add(opt_target)
            
            created_ids.append(reco_data["reco_id"])
        
        # Commit all
        await db.commit()
        
        logger.info(f"Successfully seeded {len(created_ids)} recommendations")
        
        return SeedResponse(
            message=f"Generated and seeded {len(created_ids)} recommendations",
            recommendations_created=len(created_ids),
            sample_reco_ids=created_ids[:10]  # Return first 10 IDs
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error seeding recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to seed recommendations: {str(e)}")


@app.post("/recommendations/refresh")
async def refresh_data():
    """
    Trigger immediate refresh of all stock prices and options data
    
    This endpoint manually triggers the scheduled update jobs to fetch
    real-time prices and recalculate targets immediately.
    """
    try:
        logger.info("Manual refresh triggered via API")
        
        # Run both updates
        await update_stock_prices()
        await update_options_data()
        
        return {
            "status": "success",
            "message": "Data refreshed successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error during manual refresh: {e}")
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")


@app.get("/status")
async def status():
    """Detailed API status"""
    return {
        "api_version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc),
        "features": {
            "async_sqlalchemy": True,
            "cursor_pagination": True,
            "ranking_formula": True,
            "multi_target_support": True,
            "options_support": True,
            "recommendation_generator": True
        },
        "endpoints": {
            "health": "/health",
            "list_recommendations": "/recommendations",
            "get_recommendation": "/recommendations/{reco_id}",
            "seed_data": "/recommendations/seed",
            "docs": "/docs"
        },
        "symbol_universe_size": len(SYMBOL_UNIVERSE)
    }
