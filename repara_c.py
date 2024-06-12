
import torch
from models.yolo import Model

device = torch.device("cpu")
cfg = '/home/julian/work/yolov9/models/detect/tiip-c.yaml'
ckpt_path = '/home/julian/work/yolov9/runs/train/yolov9-c7/weights/best.pt'
# output_path = '/home/julian/work/yolov9/runs/train/yolov9-c7/weights/best-converted.pt'
output_path = '/home/julian/work/yolov9/runs/train/yolov9-c7/weights/best-converted-2.pt'


ckpt_path = '/home/julian/work/yolov9/runs/train/yolov9c-scratch_s1-s17_s21/weights/best.pt'
output_path = '/home/julian/work/yolov9/runs/train/yolov9c-scratch_s1-s17_s21/weights/best-converted.pt'
nc = 23

model = Model(cfg, ch=3, nc=nc, anchors=3)
#model = model.half()
model = model.to(device)
_ = model.eval()
ckpt = torch.load(ckpt_path, map_location='cpu')
model.names = ckpt['model'].names
model.nc = ckpt['model'].nc

idx = 0
for k, v in model.state_dict().items():
    if "model.{}.".format(idx) in k:
        if idx < 22:
            kr = k.replace("model.{}.".format(idx), "model.{}.".format(idx+1))
            model.state_dict()[k] -= model.state_dict()[k]
            model.state_dict()[k] += ckpt['model'].state_dict()[kr]
        elif "model.{}.cv2.".format(idx) in k:
            kr = k.replace("model.{}.cv2.".format(idx), "model.{}.cv4.".format(idx+16))
            model.state_dict()[k] -= model.state_dict()[k]
            model.state_dict()[k] += ckpt['model'].state_dict()[kr]
        elif "model.{}.cv3.".format(idx) in k:
            kr = k.replace("model.{}.cv3.".format(idx), "model.{}.cv5.".format(idx+16))
            model.state_dict()[k] -= model.state_dict()[k]
            model.state_dict()[k] += ckpt['model'].state_dict()[kr]
        elif "model.{}.dfl.".format(idx) in k:
            kr = k.replace("model.{}.dfl.".format(idx), "model.{}.dfl2.".format(idx+16))
            model.state_dict()[k] -= model.state_dict()[k]
            model.state_dict()[k] += ckpt['model'].state_dict()[kr]
    else:
        while True:
            idx += 1
            if "model.{}.".format(idx) in k:
                break
        if idx < 22:
            kr = k.replace("model.{}.".format(idx), "model.{}.".format(idx+1))
            model.state_dict()[k] -= model.state_dict()[k]
            model.state_dict()[k] += ckpt['model'].state_dict()[kr]
        elif "model.{}.cv2.".format(idx) in k:
            kr = k.replace("model.{}.cv2.".format(idx), "model.{}.cv4.".format(idx+16))
            model.state_dict()[k] -= model.state_dict()[k]
            model.state_dict()[k] += ckpt['model'].state_dict()[kr]
        elif "model.{}.cv3.".format(idx) in k:
            kr = k.replace("model.{}.cv3.".format(idx), "model.{}.cv5.".format(idx+16))
            model.state_dict()[k] -= model.state_dict()[k]
            model.state_dict()[k] += ckpt['model'].state_dict()[kr]
        elif "model.{}.dfl.".format(idx) in k:
            kr = k.replace("model.{}.dfl.".format(idx), "model.{}.dfl2.".format(idx+16))
            model.state_dict()[k] -= model.state_dict()[k]
            model.state_dict()[k] += ckpt['model'].state_dict()[kr]
_ = model.eval()

m_ckpt = {'model': model.half(),
          'optimizer': None,
          'best_fitness': None,
          'ema': None,
          'updates': None,
          'opt': None,
          'git': None,
          'date': None,
          'epoch': -1}
torch.save(m_ckpt, output_path)