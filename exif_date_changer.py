import argparse
import piexif
import os.path
from datetime import datetime, timedelta
from os import listdir
from PIL import Image, UnidentifiedImageError

delta = timedelta(hours=10, minutes=45)

def find_files(path):
    return [f for f in listdir(path) if os.path.isfile(os.path.join(path, f))]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("img_path")
    parser.add_argument("output_path")

    args = parser.parse_args()
    
    for img in find_files(args.img_path):
        img_file = os.path.join(args.img_path, img)
        try:
            pil_img = Image.open(img_file)
        except UnidentifiedImageError:
            continue

        exif_dict = piexif.load(pil_img.info['exif'])
        str_exif_data = exif_dict["0th"][piexif.ImageIFD.DateTime].decode("utf-8")

        dt = datetime.strptime(str_exif_data, "%Y:%m:%d %H:%M:%S")
       
        str_new_exif_data = (dt + delta).strftime("%Y:%m:%d %H:%M:%S")

        exif_dict["0th"][piexif.ImageIFD.DateTime] = str_new_exif_data
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = str_new_exif_data
        exif_bytes = piexif.dump(exif_dict)
        
        pil_img.save(os.path.join(args.output_path, "IMG_{}_{}.jpg".format(
            (dt+delta).strftime("%Y%m%d_%H%M%S"),
            os.path.basename(img).split(".")[0]
        )), "jpeg", exif=exif_bytes, quality="keep", optimize=True)

        print("{:20} {} -> {}".format(img_file, str_exif_data, str_new_exif_data))

if __name__ == "__main__":
    main()