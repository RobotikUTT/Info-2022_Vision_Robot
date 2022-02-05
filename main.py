import argparse
from Scripts.aruco_detection import aruco_detection
from Scripts.corrected_preview import corrected_preview
from Scripts.generate_calibration import generate_calibration
from Scripts.image_capture import begin_image_capture
from Scripts.image_preview import image_preview

parser = argparse.ArgumentParser(
    description="Main entry point."
)

parser.add_argument("--preview_url", "-u", default="/output",
    help="The URL to be used when an image preview is available."
)

parser.add_argument('--calib_file', "-c", default="calibration.json")

subparser = parser.add_subparsers(dest='command')

img_pre = subparser.add_parser('raw', 
    help="Preview the raw camera capture."
)

img_cap = subparser.add_parser('img_cap', 
    help="Capture images for the purposes of calibrating the camera."
)

gen_calib = subparser.add_parser('gen_calib', 
    help='''Create a camera calibration file from a folder containing calibration 
            images (see 'img_cap').'''
)
undistorted = subparser.add_parser('corrected',
    help="Start a preview of the corrected camera view."
)
aruco = subparser.add_parser('aruco_detection',
    help="Output a list of detected aruco codes as well as the screen coordinates of their corners."
)

img_cap.add_argument('--img_folder', "-i", default="/tmp/calibration_img",
    help="The folder in which the calibration images will be stored."
)

gen_calib.add_argument('--img_folder', "-i", default="/tmp/calibration_img", 
    help="The folder containing the images to be used to generate the calibration file."
)

args = parser.parse_args()
print(args)

cmd = args.command
calib_file = args.calib_file
preview_url = args.preview_url
if cmd == "raw":
    image_preview(preview_url)
elif cmd == "img_cap":
    begin_image_capture(preview_url, args.img_folder)
elif cmd == "gen_calib":
    generate_calibration(args.img_folder, calib_file)
elif cmd == "corrected":
    corrected_preview(args.calib_file, preview_url)
elif cmd == "aruco_detection":
    aruco_detection(preview_url, calib_file)