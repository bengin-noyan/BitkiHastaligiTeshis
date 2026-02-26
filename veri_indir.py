

from roboflow import Roboflow
rf = Roboflow(api_key="VwRlrotjxhLZc92fvGWv")
project = rf.workspace("bengins-workspace-n2nmq").project("plant-disease-tmyq8-eav1r")
version = project.version(1)
dataset = version.download("yolov8")
                