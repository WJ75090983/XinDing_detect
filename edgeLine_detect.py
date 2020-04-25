import cv2
import numpy as np

def Inside_point(Pt, img):
    height, width = img.shape[:2]
    if Pt[0] < 0 or Pt[0] >= width or Pt[1] < 0 or Pt[1] >= height:
        return False
    else:
        return True

def gen_data_hen(Pt, img, distance):
    points_value = []
    p9_x = int(Pt[0])
    p9_y = int(Pt[1])
    p1 = (p9_x - 1, p9_y - distance)
    p2 = (p9_x, p9_y - distance)
    p3 = (p9_x + 1, p9_y - distance)
    p5 = (p9_x + 1, p9_y + distance)
    p6 = (p9_x, p9_y + distance)
    p7 = (p9_x - 1, p9_y + distance)

    if (not Inside_point(p1, img)) or (not Inside_point(p7, img)):
        p1 = (p9_x, p9_y)
        p7 = (p9_x, p9_y)

    if (not Inside_point(p2, img)) or (not Inside_point(p6, img)):
        p2 = (p9_x, p9_y)
        p6 = (p9_x, p9_y)

    if (not Inside_point(p3, img)) or (not Inside_point(p5, img)):
        p3 = (p9_x, p9_y)
        p5 = (p9_x, p9_y)

    points_value.append(img[p1[1], p1[0]])
    points_value.append(img[p2[1], p2[0]])
    points_value.append(img[p3[1], p3[0]])
    points_value.append(img[p5[1], p5[0]])
    points_value.append(img[p6[1], p6[0]])
    points_value.append(img[p7[1], p7[0]])

    return points_value

def gen_data_shu(Pt, img, distance):
    points_value = []
    p9_x = int(Pt[0])
    p9_y = int(Pt[1])
    p1 = (p9_x - distance, p9_y - 1)
    p3 = (p9_x + distance, p9_y - 1)
    p4 = (p9_x + distance, p9_y)
    p5 = (p9_x + distance, p9_y + 1)
    p7 = (p9_x - distance, p9_y + 1)
    p8 = (p9_x - distance, p9_y)

    if not Inside_point(p1, img) or not Inside_point(p3, img):
        p1 = (p9_x, p9_y)
        p3 = (p9_x, p9_y)

    if not Inside_point(p8, img) or not Inside_point(p4, img):
        p8 = (p9_x, p9_y)
        p4 = (p9_x, p9_y)

    if not Inside_point(p7, img) or not Inside_point(p5, img):
        p7 = (p9_x, p9_y)
        p5 = (p9_x, p9_y)

    points_value.append(img[p1[1], p1[0]])
    points_value.append(img[p8[1], p8[0]])
    points_value.append(img[p7[1], p7[0]])
    points_value.append(img[p3[1], p3[0]])
    points_value.append(img[p4[1], p4[0]])
    points_value.append(img[p5[1], p5[0]])

    return points_value

def getLindDiff(line, state, img, thresh, distance):
    [x1, y1, x2, y2] = line[0]
    series_points = np.linspace((x1, y1), (x2, y2), 10, endpoint=False)
    if state == "shu_xian":
        points_Diss = []
        for point in series_points:
            if Inside_point(point, img):
                points_value = gen_data_shu(point, img, distance)
                left_value = -1 * points_value[0] + -2 * points_value[1] + -1 * points_value[2]
                right_value = 1 * points_value[3] + 2 * points_value[4] + 1 * points_value[5]
                diss = abs(left_value + right_value)
                points_Diss.append(diss)

        avg_Diss = int(sum(points_Diss) / len(points_Diss))
        print("shu_xian:  " + str(avg_Diss))
        if avg_Diss > thresh:
            return line
        else:
            return None

    elif state == "hen_xian":
        points_Diss = []
        for point in series_points:
            if Inside_point(point, img):
                points_value = gen_data_hen(point, img, distance)
                up_value = -1 * points_value[0] + -2 * points_value[1] + -1 * points_value[2]
                down_value = 1 * points_value[3] + 2 * points_value[4] + 1 * points_value[5]
                diss = abs(up_value + down_value)
                points_Diss.append(diss)

        avg_Diss = int(sum(points_Diss) / len(points_Diss))
        print("hen_xian:  " + str(avg_Diss))
        if avg_Diss > thresh:
            return line
        else:
            return None

img = cv2.imread("roi1.jpg")
height, width = img.shape[:2]
print([height, width])

center_x = int(width / 2)
center_y = int(height / 2)

cv2.circle(img, (center_x, center_y), 3, (255, 0, 0), 2)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(hsv)
blur = cv2.GaussianBlur(v, (5, 5), 0)
edge = cv2.Canny(blur, 50, 255)

# use hough transform to detect line
lines_shu = []
lines_hen = []
lines = cv2.HoughLinesP(edge, 1, np.pi/180, int(min(width, height)/4), maxLineGap=max(center_y, center_x))
#print(len(lines))
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y2 - y1) > abs(x2 - x1):
            state = "shu_xian"
            line = getLindDiff(line, state, v, thresh=250, distance=2)
            if line is not None:
                #lines_shu.append(line[0])
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        else:
            state = "hen_xian"
            line = getLindDiff(line, state, v, thresh=250, distance=2)
            if line is not None:
                #lines_hen.append(line[0])
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

cv2.imshow("img", img)
cv2.imshow("v", v)
cv2.imshow("Canny", edge)

cv2.waitKey(0)
cv2.destroyAllWindows()
