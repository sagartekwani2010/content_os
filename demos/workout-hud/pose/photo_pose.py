"""Find body keypoints in one front-facing, full-body photo for the Score map.
Usage: python photo_pose.py PHOTO OUT_DIR [--weights yolo11n-pose.pt]
Writes OUT_DIR/me.jpg (web-ready) and prints the `pose` object to paste into day.js (week.photo / week.pose)."""
import json, sys
from pathlib import Path
from PIL import Image, ImageOps
from ultralytics import YOLO
NAMES = {5: "l_shoulder", 6: "r_shoulder", 7: "l_elbow", 8: "r_elbow", 9: "l_wrist", 10: "r_wrist",
         11: "l_hip", 12: "r_hip", 13: "l_knee", 14: "r_knee", 15: "l_ankle", 16: "r_ankle"}
def main(photo, out_dir, weights="yolo11n-pose.pt"):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(photo)).convert("RGB"); im.thumbnail((1400, 1400)); im.save(out / "me.jpg", quality=88)
    r = YOLO(weights)(str(out / "me.jpg"), verbose=False)[0]
    if r.keypoints is None or len(r.keypoints) == 0: sys.exit("No person found in the photo.")
    areas = (r.boxes.xywh[:, 2] * r.boxes.xywh[:, 3]).cpu().numpy(); kp = r.keypoints.data[int(areas.argmax())].cpu().numpy()
    w, h = im.size; pose, weak = {}, []
    for i, n in NAMES.items():
        pose[n] = [round(float(kp[i, 0] / w), 4), round(float(kp[i, 1] / h), 4)]
        if kp[i, 2] < 0.4: weak.append(n)
    print(json.dumps({"photo": "me.jpg", "pose": pose, "low_confidence": weak}, indent=1))
if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(a[0], a[1], sys.argv[sys.argv.index("--weights") + 1] if "--weights" in sys.argv else "yolo11n-pose.pt")
