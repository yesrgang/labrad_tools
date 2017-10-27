import matplotlib as mpl

x = 0.9

cdict = {'red': ((0., x, x),
                 (0.03, x, x),
                 (0.11, 0, 0),
                 (0.66, 1, 1),
                 (0.89, 1, 1),
                 (1, 0.5, 0.5)),
         'green': ((0., x, x),
                   (0.03, x, x),
                   (0.11, 0, 0),
                   (0.375, 1, 1),
                   (0.64, 1, 1),
                   (0.91, 0, 0),
                   (1, 0, 0)),
         'blue': ((0., x, x),
                  (0.03, x, x),
                  (0.11, 1, 1),
                  (0.34, 1, 1),
                  (0.65, 0, 0),
                  (1, 0, 0))}

my_cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)
