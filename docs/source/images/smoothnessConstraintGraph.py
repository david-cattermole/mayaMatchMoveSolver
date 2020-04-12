"""
Creates Smoothness Constraint Graph.
"""

import numpy as np
import matplotlib.pyplot as plt

title = 'Smoothness'
label_y = 'Values'
label_x = 'Frame'

left = 0.0
right = 5.0
top = 0.8
bottom = 0.5

values = [0.5, 0.6, 0.65, 0.67]
variance = 0.025
smooth = 0.675
solve = 0.62

x1 = np.linspace(0.0, 3.0, num=4)
y1 = values

x2 = [3.0, 4.0]
y2 = [values[-1], solve]

x3 = [3.0, 4.0]
y3 = [values[-1], smooth]

x4 = [4.0, 4.0]
y4 = [smooth - variance,
      smooth + variance]


def frame(plt, frame, x1, y1, x2, y2, x3, y3, x4, y4):
      fig1, ax = plt.subplots()
      if frame == 0:
            ax.plot(x1[:1], y1[:1], 'o-', label='Values')

      if frame == 1:
            ax.plot(x1[:2], y1[:2], 'o-', label='Values')

      if frame == 2:
            ax.plot(x1[:3], y1[:3], 'o-', label='Values')

      if frame == 3:
            ax.plot(x1, y1, 'o-', label='Values')

      elif frame == 4:
            ax.plot(x1, y1, 'o-', label='Values')
            ax.plot(x2, y2, '+--', label='Next Value')

      elif frame == 5:
            ax.plot(x1, y1, 'o-', label='Values')
            ax.plot(x2, y2, '+--', label='Next Value')
            ax.plot(x3, y3, 'D-.', label='Reference Value')
            ax.plot(x4, y4, '_', label='Variance')

      legend = ax.legend(loc='upper left', shadow=True, fontsize='x-large')

      plt.title(title)
      plt.ylabel(label_y)
      plt.xlabel(label_x)
      plt.xlim((left, right))
      plt.ylim((bottom, top))

      frame_path = 'smoothnessConstraintGraph_%s.png' % frame
      plt.savefig(frame_path)


for i in range(6):
      frame(
          plt, i,
          x1, y1,
          x2, y2,
          x3, y3,
          x4, y4
      )