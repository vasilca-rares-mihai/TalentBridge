class Athlete():
    def __init__(self, first_name, second_name, age, gender, height, weight):
        self.first_name = first_name
        self.second_name = second_name
        self.age = int(age)
        self.gender = gender
        self.height = float(height)
        self.weight = float(weight)

    def __str__(self):
        return f"{self.first_name} {self.second_name}, {self.age} ani, {self.gender}, {self.height} m, {self.weight} kg"
