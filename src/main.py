from analyzers import SquatAnalyzer, PushupAnalyzer, StepAnalyzer, PullupAnalyzer, VerticalJumpAnalyzer
from models import Athlete
import os
import tkinter as tk
from tkinter import filedialog


class WorkoutManager:
    def __init__(self):
        self.analyzers = {
            'pushup': PushupAnalyzer,
            'squat': SquatAnalyzer,
            'treadmill': StepAnalyzer,
            'pullup': PullupAnalyzer,
            'vjump': VerticalJumpAnalyzer,
        }

    def run_analysis(self, workout_type, athlete):

        workout_type = workout_type.lower()

        if workout_type not in self.analyzers:
            print(f"Error: The workout type '{workout_type}' is not supported.")
            return

        initial_path = os.path.join("../video_dataset", workout_type)
        print(initial_path)

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        video_path = filedialog.askopenfilename(
            title="Alege un clip video",
            initialdir=initial_path,
            filetypes=[("Video files", "*.mp4 *.avig *.mov *.mkv")]
        )


        if not os.path.exists(video_path):
            print(f"Error: The video file '{video_path}' was not found.")
            return
        AnalyzerClass = self.analyzers[workout_type]

        try:
            analyzer = AnalyzerClass(video_path)
            analyzer.analyze(athlete)

        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"An error occurred during the analysis: {e}")


if __name__ == "__main__":
    manager = WorkoutManager()
    #datale vor trebui extrase din baza de date
    with open(r"../data/persoane.txt", "r") as f:
        linie = f.readline().strip()
        firstName, secondName, age, gender, height, weight = linie.split(",")
        a1 = Athlete(firstName, secondName, age, gender, height, weight)

    try:
        with open(r"../data/persoane.txt", "r") as f:
            line = f.readline().strip()
            if not line:
                raise ValueError("Empty athlete data file")
            parts = line.split(",")
            if len(parts) != 6:
                raise ValueError("Invalid athlete data format")
            a1 = Athlete(firstName, secondName, age, gender, height, weight)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Failed to load athlete data: {e}")
        sys.exit(1)

    while True:
        print(f"\nAthlete: {a1}")
        workout = input("Choose the type of analysis (pushup/squat/treadmill/pullup/vjump): ")
        print("\n--- Running Analysis ---")
        manager.run_analysis(workout, a1)
        print("The program has closed.")

