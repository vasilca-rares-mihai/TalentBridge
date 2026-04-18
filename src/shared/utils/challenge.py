from service.analysis_worker.app.analyzers import SquatAnalyzer, PushupAnalyzer, StepAnalyzer, PullupAnalyzer, VerticalJumpAnalyzer, SitupAnalyzer, KickAnalyzer
ANALYZERS = {
    'pushup': PushupAnalyzer, #1
    'squat': SquatAnalyzer, #3
    'treadmill': StepAnalyzer, #4
    'pullup': PullupAnalyzer, #2
    'vertical jump': VerticalJumpAnalyzer, #5
    'situp': SitupAnalyzer, #6
    "kick": KickAnalyzer, #7
}
videos_dir = "service/video_storage/"

#default password when trying to create first admin account
defpassword = "admin"