import math


def deg2rad(degrees):
    """
    Convert degrees to radians.
    """
    return degrees * (math.pi / 180.0)


def rad2deg(radians):
    """
    Convert radians to degrees.
    """
    return radians * (180.0 / math.pi)


def calc_distance(theta, dist):
    """
    Calculate x and y offsets for moving forward `dist` units at heading `theta`.
    `theta` is in degrees.
    """
    rad = deg2rad(theta)
    x = dist * math.cos(rad)
    y = dist * math.sin(rad)
    return (x, y)


def rotate_coords(cx, cy, x, y, theta):
    """
    Rotate coordinate (x, y) about (cx, cy) by angle theta in degrees.
    Return the resulting (xrot, yrot)
    """
    theta = deg2rad(theta)
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    x0 = x - cx
    y0 = y - cy
    xnew = x0 * cos_theta - y0 * sin_theta
    ynew = x0 * sin_theta + y0 * cos_theta
    xnew += cx
    ynew += cy
    return (xnew, ynew)
