import os
from celery import Celery

# Importăm analizoarele aici, unde avem OpenCV/Torch instalat
from service.analysis_worker.app.analyzers import (
    SquatAnalyzer, PushupAnalyzer, StepAnalyzer,
    PullupAnalyzer, VerticalJumpAnalyzer, SitupAnalyzer,
    KickAnalyzer, LongJumpAnalyzer, DubleAnalyzer
)

# Registrul central de analizoare
ANALYZERS = {
    'pushup': PushupAnalyzer,
    'squat': SquatAnalyzer,
    'treadmill': StepAnalyzer,
    'pullup': PullupAnalyzer,
    'vertical_jump': VerticalJumpAnalyzer,
    'situp': SitupAnalyzer,
    'kick': KickAnalyzer,
    'long_jumps': LongJumpAnalyzer,
    'double': DubleAnalyzer
}

# Configurare Celery
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://talent-bridge-redis:6379/0")

celery_app = Celery(
    "analysis_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["service.analysis_worker.app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Bucharest",
    enable_utc=True,
    worker_prefetch_multiplier=1
)