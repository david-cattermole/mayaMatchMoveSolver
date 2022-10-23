# Camera and Lens Calibration

Camera and lens calibration is the task of finding the intrinsic
(angle of view, lens parameters) and extrinsic parameters (translation
and rotation).

There are many techniques for calibration, and currently we support
using vanishing points to estimate the camera and lens parameters.

Currently estimating lens distortion is not supported in this
directory.

## Vanishing Points

We can use one user given vanishing point to calculate the camera
external parameters, and with two user given vanishing points we can
also estimate the angle of view of the lens.

The following papers were used as reference for this implementation,
and inspiration from the [fSpy](https://github.com/stuffmatic/fSpy/)
application too.

- "Camera calibration using two or three vanishing points" (2012)
  - Radu Orghidan, Joaquim Salvi, Mihaela Gordan and Bogdan Orza.

- "Using vanishing points for camera calibration and coarse 3D
  reconstruction from a single image" (2000)
  - E. Guillou, D. Meneveaux, E. Maisel, K. Bouatouch.

- "Camera calibration from vanishing points in images of architectural
  scenes" (1998)
  - R. Cipolla, T. Drummond and D. Robertson.

- Tips for vanishing points, horizon lines, and parallel lines.
  - [Algorithms for Automated-Driving - Camera Basics](https://thomasfermi.github.io/Algorithms-for-Automated-Driving/LaneDetection/CameraBasics.html)
  - [Algorithms for Automated-Driving - Vanishing Point Camera Calibration](https://thomasfermi.github.io/Algorithms-for-Automated-Driving/CameraCalibration/VanishingPointCameraCalibration.html)
