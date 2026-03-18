

from roboflow import Roboflow
rf = Roboflow(api_key="Dq0qsCaHoS9QNFkZaX5H")
project = rf.workspace("bengins-workspace-n2nmq").project("plant-disease-tmyq8-eav1r")
version = project.version(1)
dataset = version.download("yolov8")
                