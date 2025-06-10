from dataclasses import dataclass


@dataclass()
class ClassesArray:
    CLASSES = ["5-А", "5-Б", "6-А", "6-Б", "6-В", "7-А", "7-Б", "8-А",
               "8-Б", "9-А", "9-Б", "10-А", "10-Б", "11-А", "11-Б"]

classes = ClassesArray()

# TODO: перемістить цей файл в src/settings
