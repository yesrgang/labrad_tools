import mahotas
import numpy as np

def get_norm_indicies(image, norm):
    x_max = image.shape[1]
    y_max = image.shape[0]
    x, y = np.meshgrid(range(x_max), range(y_max))    
    r2 = (x - x_max / 2.)**2 + (y - y_max / 2.)**2
    return (r2 > norm[2]**2) & (r2 < norm[3]**2)

def get_roi_corners(image, roi, theta=0):
    x_max = image.shape[1]
    y_max = image.shape[0]
    
    R = np.matrix([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    h, w, x0, y0 = roi
    corners = [
        np.array([x0-w, y0-h]), 
        np.array([x0-w, y0+h]), 
        np.array([x0+w, y0+h]), 
        np.array([x0+w, y0-h]),
        ]
    for i, pt in enumerate(corners):
        corners[i] = np.dot(pt, R.T).astype('int').tolist()[0]
    
    return corners + np.array([x_max, y_max]) / 2.

def region_pts(pts):
    x_pts, y_pts = zip (*pts)
    x_min, x_max = np.min(x_pts), np.max(x_pts)
    y_min, y_max = np.min(y_pts), np.max(y_pts)

    new_pts = [(int(x - x_min), int(y - y_min)) for x, y in pts]

    X = x_max - x_min + 1
    Y = y_max - y_min + 1
    grid = np.zeros((X.astype(np.int_), Y.astype(np.int_)))
    mahotas.polygon.fill_polygon(new_pts, grid)
    return [(int(x + x_min), int(y + y_min)) for (x, y) in zip(*np.nonzero(grid))]


def fix_image_gradient(image1, image2, norm):
    x_max = image1.shape[1]
    y_max = image1.shape[0]
    x, y = np.meshgrid(range(x_max), range(y_max))    

    norm_indicies = get_norm_indicies(image1, norm)
    x0 = np.mean(x[norm_indicies])
    y0 = np.mean(y[norm_indicies])
    x2 = np.mean(x[norm_indicies] * (x[norm_indicies] - x0))
    y2 = np.mean(y[norm_indicies] * (y[norm_indicies] - y0))
    
    m_x = np.mean(x[norm_indicies] * (image1[norm_indicies] - image2[norm_indicies])) / x2
    m_y = np.mean(y[norm_indicies] * (image1[norm_indicies] - image2[norm_indicies])) / y2
                       
    correction = m_x * (x - x0) + m_y * (y - y0)
    return image1, image2 + correction
