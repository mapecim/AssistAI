from fastapi import FastAPI
from .chat.main import router as chat_router
from .performance_prediction.main import router as pred_router
from .player_report.main import router as report_router
from .team_report.main import router as team_report_router
from .search_similar.main import router as search_similar
from .database.main import router as db_router

app = FastAPI()

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(pred_router, prefix="/performance-prediction", tags=["Performance Prediction"])
app.include_router(report_router, prefix="/player-report", tags=["Player Report"])
app.include_router(team_report_router, prefix="/team-report", tags=["Team Report"])
app.include_router(search_similar, prefix="/search-similar", tags=["Search Similar"])
app.include_router(db_router, prefix="/database", tags=["Database"])

@app.get("/health")
def health_check():
    return {"status": "ok", "success": True}