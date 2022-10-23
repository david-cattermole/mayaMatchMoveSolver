Other Nodes
===========

The following `other` nodes are miscellaneous and do not fit neatly
into the other categories of nodes.

``mmMarkerScale`` Node
++++++++++++++++++++++

The ``mmMarkerScale`` is used to compute scale and translate values
for a transform.

========================== ================================= ======= =========
  Attribute Name           Description                        Input   Output
========================== ================================= ======= =========
  focalLength              Camera focal length (mm)           Yes     No
  cameraAperture           Aperture parent attribute          Yes     No
  horizontalFilmAperture   Width of aperture (inches)         Yes     No
  verticalFilmApertre      Height of aperture (inches)        Yes     No
  filmOffset               Aperture offset parent attribute   Yes     No
  horizontalFilmOffset     Width of offset (inches)           Yes     No
  verticalFilmOffset       Heigth of offset (inches)          Yes     No
  depth                    Depth of the scale plane           Yes     No
  overscan                 Overscan factor of the plane       Yes     No
  outTranslate             Translate parent attribute         No      Yes
  outTranslateX            Translate X in camera-space        No      Yes
  outTranslateY            Translate Y in camera-space        No      Yes
  outTranslateZ            Translate Z in camera-space        No      Yes
  outScale                 Scale parent attribute             No      Yes
  outScaleX                Scale X in camera-space            No      Yes
  outScaleY                Scale Y in camera-space            No      Yes
  outScaleZ                Scale Z in camera-space            No      Yes
========================== ================================= ======= =========

``mmReprojection`` Node
+++++++++++++++++++++++

The ``mmReprojection`` node computes the screen-space position of an
input ``transformWorldMatrix`` attribute.
A Maya camera node must be connected to the camera attributes.
The camera is used for all camera/screen-space values.
The node can be used to feed into a camera display pan, effectively
centering the screen.

======================================== ======================================================================================== ======= =========
  Attribute Name                          Description                                                                              Input   Output
======================================== ======================================================================================== ======= =========
  transformWorldMatrix                    The matrix of the input transform to compute, matrix is expected to be in world-space.   Yes     No
  cameraWorldMatrix                       The camera transform matrix.                                                             Yes     No
  applyMatrix                             Apply a screen-space matrix to the transform matrix.                                     Yes     No
  overrideScreenX                         Override the screen-space transform coordinate in X?                                     Yes     No
  overrideScreenY                         Override the screen-space transform coordinate in Y?                                     Yes     No
  overrideScreenZ                         Override the screen-space transform coordinate in Z?                                     Yes     No
  screenX                                 Used for the screen-space point, in X (left-right).                                      Yes     No
  screenY                                 Used for the screen-space point, in Y (up-down).                                         Yes     No
  screenZ                                 Used for the screen-space point, in Z (depth).                                           Yes     No
  depthScale                              Multiply the depth screen value.                                                         Yes     No
  focalLength                             The camera focal length.                                                                 Yes     No
  cameraAperture                          Camera film back (parent attribute).                                                     Yes     No
  horizontalFilmAperture                  Camera film back width.                                                                  Yes     No
  verticalFilmAperture                    Camera film back height.                                                                 Yes     No
  filmOffset                              Camera film offset (parent attribute).                                                   Yes     No
  horizontalFilmOffset                    Camera film offset width.                                                                Yes     No
  verticalFilmOffset                      Camera film offset height.                                                               Yes     No
  filmFit                                 Camera film fit, how the film back maps to the image.                                    Yes     No
  nearClipPlane                           Camera near clipping plane.                                                              Yes     No
  farClipPlane                            Camera far clipping plane.                                                               Yes     No
  cameraScale                             Camera scale value.                                                                      Yes     No
  imageWidth                              The render image width.                                                                  Yes     No
  imageHeight                             The render Image height.                                                                 Yes     No
  outCoord                                Output coordinate (parent attribute).                                                    No      Yes
  outCoordX                               Screen-space coordinate in X (-1.0 to 1.0)                                               No      Yes
  outCoordY                               Screen-space coordinate in Y (-1.0 to 1.0)                                               No      Yes
  outNormCoord                            Output normalized coordinate (parent attribute).                                         No      Yes
  outNormCoordX                           Normalized screen-space coordinate in X (0.0 to 1.0; lower-left corner is 0.0, 0.0)      No      Yes
  outNormCoordY                           Normalized screen-space coordinate in Y (0.0 to 1.0; lower-left corner is 0.0, 0.0)      No      Yes
  outPixel                                Output pixel coordinate (parent attribute)                                               No      Yes
  outPixelX                               Pixel coordinate in X (uses imageWidth and imageHeight)                                  No      Yes
  outPixelY                               Pixel coordinate in Y (uses imageWidth and imageHeight)                                  No      Yes
  outInsideFrustum                        Is the point inside the frustum?                                                         No      Yes
  outPoint                                Output point (parent attribute).                                                         No      Yes
  outPointX                               Point in camera-space in X.                                                              No      Yes
  outPointY                               Point in camera-space in Y.                                                              No      Yes
  outPointZ                               Point in camera-space in Z.                                                              No      Yes
  outWorldPoint                           Output point (parent attribute).                                                         No      Yes
  outWorldPointX                          Point in world-space in X.                                                               No      Yes
  outWorldPointY                          Point in world-space in Y.                                                               No      Yes
  outWorldPointZ                          Point in world-space in Z.                                                               No      Yes
  outMatrix                               Output matrix in camera-space.                                                           No      Yes
  outWorldMatrix                          Output matrix in world-space.                                                            No      Yes
  outCameraProjectionMatrix               Camera projection matrix in camera-space.                                                No      Yes
  outInverseCameraProjectionMatrix        Camera projection inverse matrix in camera-space.                                        No      Yes
  outWorldCameraProjectionMatrix          Camera projection matrix in world-space.                                                 No      Yes
  outWorldInverseCameraProjectionMatrix   Camera projection inverse matrix in world-space.                                         No      Yes
  outPan                                  Output Pan attribute                                                                     No      Yes
  outHorizontalPan                        The computed pan value in X.                                                             No      Yes
  outVerticalPan                          The computed pan value in Y.                                                             No      Yes
======================================== ======================================================================================== ======= =========


``mmCameraCalibrate`` Nodes
+++++++++++++++++++++++++++

*To be written.*

``mmLineIntersect`` Nodes
+++++++++++++++++++++++++

*To be written.*
