from service.analysis_worker.app.analyzers import SquatAnalyzer, PushupAnalyzer, StepAnalyzer, PullupAnalyzer, VerticalJumpAnalyzer
ANALYZERS = {
    'pushup': PushupAnalyzer, #1
    'squat': SquatAnalyzer, #3
    'treadmill': StepAnalyzer, #4
    'pullup': PullupAnalyzer, #2
    'vertical jump': VerticalJumpAnalyzer, #5
}
videos_dir = "service/shared_storage/videos"