import sys
import cv2
from typing import Tuple
import numpy as np
import cv2.typing
import cv2.aruco
import cwipc

ARUCO_PARAMETERS = cv2.aruco.DetectorParameters()
ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
ARUCO_DETECTOR = cv2.aruco.ArucoDetector(ARUCO_DICT, ARUCO_PARAMETERS)

def main():
    if len(sys.argv) <= 1:
        print("Usage: {sys.argv[0]} filename [...]", file=sys.stderr)
        sys.exit(1)
    for fn in sys.argv[1:]:
        if fn.endswith(".ply"):
            find_aruco_in_plyfile(fn)
        else:
            find_aruco_in_imagefile(fn)

def find_aruco_in_plyfile(filename : str):
    full_pc = cwipc.cwipc_read(filename, 0)
    for tile in [1, 2, 4, 8]:
        pc = cwipc.cwipc_tilefilter(full_pc, tile)
        find_aruco_in_pointcloud(pc)
    

def find_aruco_in_imagefile(filename : str):
    if not cv2.haveImageReader(filename):
        assert False, f"No opencv image reader for {filename}"
    img = cv2.imread(filename)
    assert img is not None, "file could not be read, check with os.path.exists()"
    print('Shape', img.shape)
    find_aruco_in_image(img)

def find_aruco_in_pointcloud(pc : cwipc.cwipc_wrapper):
    width = 512
    height = 512
    img_rgb, img_xyz = project_pointcloud_to_images(pc, width, height)
    find_aruco_in_image(img_rgb)


def find_aruco_in_image(img : cv2.typing.MatLike):
    corners, ids, rejected  = ARUCO_DETECTOR.detectMarkers(img)
    print("corners", corners)
    print("ids", ids)
    print("rejected", rejected)
    if True:
        outputImage = img.copy()
        cv2.aruco.drawDetectedMarkers(outputImage, corners, ids)
        cv2.imshow("Detected markers", outputImage)
        while True:
            ch = cv2.waitKey()
            if ch == 27:
                break
            print(f"ignoring key {ch}")

def project_pointcloud_to_images(pc : cwipc.cwipc_wrapper, width : int, height : int) -> Tuple[cv2.typing.MatLike, cv2.typing.MatLike]:

    img_rgb = np.zeros(shape=(width, height, 3), dtype=np.uint8)
    img_xyz = np.zeros(shape=(width, height, 3), dtype=np.float32)
    cv2.rectangle(img_rgb, pt1=[2,2], pt2=[width-4, height-4], color=[0,255,0], thickness=-1)
    # xxxjack should do this with numpy
    xyz_array, rgb_array = _get_nparrays_for_pc(pc)
    x_array = xyz_array[:,0]
    y_array = xyz_array[:,1]
    min_x = np.min(x_array)
    max_x = np.max(x_array)
    min_y = np.min(y_array)
    max_y = np.max(y_array)
    print(f"x range: {min_x}..{max_x}, y range: {min_y}..{max_y}")
    x_factor = (width-1) / (max_x - min_x)
    y_factor = (height-1) / (max_y - min_y)
    for i in range(len(xyz_array)):
        xyz = xyz_array[i]
        rgb = rgb_array[i]
        x = xyz[0]
        y = xyz[1]
        img_x = int((x-min_x) * x_factor)
        img_y = int((y-min_y) * y_factor)
        img_rgb[img_x][img_y] = rgb
    return img_rgb, img_xyz

def _get_nparrays_for_pc(pc : cwipc.cwipc_wrapper) -> Tuple[cv2.typing.MatLike, cv2.typing.MatLike]:
    # Get the points (as a cwipc-style array) and convert them to a NumPy array-of-structs
    pointarray = np.ctypeslib.as_array(pc.get_points())
    # Extract the relevant fields (X, Y, Z coordinates)
    xyzarray = pointarray[['x', 'y', 'z']]
    rgbarray = pointarray[['r', 'g', 'b']]
    # Turn this into an N by 3 2-dimensional array
    np_xyzarray = np.column_stack([xyzarray['x'], xyzarray['y'], xyzarray['z']])
    np_rgbarray = np.column_stack([rgbarray['r'], rgbarray['g'], rgbarray['b']])
    return np_xyzarray, np_rgbarray

if __name__ == '__main__':
    main()