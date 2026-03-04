from ultralytics import YOLO

if __name__ == '__main__':
    # Küçük ve hızlı modelimizi çağırıyoruz
    model = YOLO("yolov8s.pt") 

    # batch=8 : Fotoğrafları 8'erli gruplar halinde işler (bilgisayarı yormaz)
    # workers=0 : Windows'un işlemciyi kilitlemesini engeller
    results = model.train(data="C:\\Users\\bengi\\PycharmProjects\\BitkiHastaligiTeshis\\Plant-Disease-1\\data.yaml", epochs=15, imgsz=640, workers=0, batch=8)
    
    print("15 Epoch'luk hafif sıklet eğitim tamamlandı!")