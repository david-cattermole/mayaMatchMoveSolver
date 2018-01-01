/*
 * An object for the camera.
 */

#include <maya/MPlug.h>
#include <maya/MObject.h>
#include <maya/MDataHandle.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MFloatMatrix.h>
#include <maya/MPoint.h>
#include <maya/MFnCamera.h>

// TODO: Use this header to re-implement the camera projection
// matrix, without the Maya API.
//#include <utilities/cgCameraUtils.h>

#include <mayaUtils.h>
#include <Marker.h>
#include <Camera.h>

// NOTE: Turning this on will slow down the solve a lot, since
// Maya seems to switch the current time when computing the
// camera projection matrix internally, even when given
// only a DGContext.
#define USE_MAYA_PROJECTION_MATRIX 0

// The node in the Maya scene which containts the render resolution.
#define RENDER_RES_NODE "defaultResolution"

// Conversion constants
#define MM_TO_INCH 0.03937
#define MM_TO_CM 0.1
#define INCH_TO_MM 25.4
#define INCH_TO_CM 2.54


Camera::Camera() :
        m_transformNodeName(""),
        m_transformObject(),
        m_shapeNodeName(""),
        m_shapeObject(),
        m_matrix(),
        m_filmbackWidth(),
        m_filmbackHeight(),
        m_filmbackOffsetX(),
        m_filmbackOffsetY(),
        m_focalLength() {

    // Attribute names
    m_matrix.setAttrName("worldMatrix");
    m_filmbackWidth.setAttrName("horizontalFilmAperture");
    m_filmbackHeight.setAttrName("verticalFilmAperture");
    m_filmbackOffsetX.setAttrName("horizontalFilmOffset");
    m_filmbackOffsetY.setAttrName("verticalFilmOffset");
    m_focalLength.setAttrName("focalLength");
    m_cameraScale.setAttrName("cameraScale");
    m_nearClipPlane.setAttrName("nearClipPlane");
    m_farClipPlane.setAttrName("farClipPlane");
    m_filmFit.setAttrName("filmFit");

    // Default Resolution node exists in every scene.
    // These attributes are used when constructing the camera projection matrix
    m_renderWidth.setNodeName(RENDER_RES_NODE);
    m_renderHeight.setNodeName(RENDER_RES_NODE);
    m_renderAspect.setNodeName(RENDER_RES_NODE);
    m_renderWidth.setAttrName("width");
    m_renderHeight.setAttrName("height");
    m_renderAspect.setAttrName("deviceAspectRatio");
}

MString Camera::getTransformNodeName() {
    return m_transformNodeName;
}

void Camera::setTransformNodeName(MString value) {
    if (value != m_transformNodeName) {
        m_matrix.setNodeName(value);
    }
    m_transformNodeName = value;
}

MObject Camera::getTransformObject() {
    MStatus status;
    MString name = Camera::getTransformNodeName();
    status = getAsObject(name, m_transformObject);
    return m_transformObject;
}

MString Camera::getShapeNodeName() {
    return m_shapeNodeName;
}

void Camera::setShapeNodeName(MString value) {
    if (value != m_shapeNodeName) {
        m_filmbackWidth.setNodeName(value);
        m_filmbackHeight.setNodeName(value);
        m_filmbackOffsetX.setNodeName(value);
        m_filmbackOffsetY.setNodeName(value);
        m_focalLength.setNodeName(value);
        m_cameraScale.setNodeName(value);
        m_nearClipPlane.setNodeName(value);
        m_farClipPlane.setNodeName(value);
        m_filmFit.setNodeName(value);
    }
    m_shapeNodeName = value;
}

MObject Camera::getShapeObject() {
    MStatus status;
    MString name = Camera::getShapeNodeName();
    MObject object;
    status = getAsObject(name, object);
    return object;
}

bool Camera::getProjectionDynamic() const {
    return m_isProjectionDynamic;
}

MStatus Camera::setProjectionDynamic(bool value) {
    MStatus status = MS::kSuccess;
    m_isProjectionDynamic = value;
    return status;
}

Attr &Camera::getMatrixAttr() {
    return m_matrix;
}

Attr &Camera::getFilmbackWidthAttr() {
    return m_filmbackWidth;
}

Attr &Camera::getFilmbackHeightAttr() {
    return m_filmbackHeight;
}

Attr &Camera::getFilmbackOffsetXAttr() {
    return m_filmbackOffsetX;
}

Attr &Camera::getFilmbackOffsetYAttr() {
    return m_filmbackOffsetY;
}

Attr &Camera::getFocalLengthAttr() {
    return m_focalLength;
}

Attr &Camera::getCameraScaleAttr() {
    return m_cameraScale;
}

Attr &Camera::getNearClippingAttr() {
    return m_nearClipPlane;
}

Attr &Camera::getFarClippingAttr() {
    return m_farClipPlane;
}

Attr &Camera::getFilmFitAttr() {
    return m_filmFit;
}

Attr &Camera::getRenderWidthAttr() {
    return m_renderWidth;
}

Attr &Camera::getRenderHeightAttr() {
    return m_renderHeight;
}

Attr &Camera::getRenderAspectAttr() {
    return m_renderAspect;
}

MStatus Camera::getWorldProjMatrix(MMatrix &value) {
    MTime time = MAnimControl::currentTime();
    return Camera::getWorldProjMatrix(value, time);
}

MStatus Camera::getWorldProjMatrix(MMatrix &value, const MTime &time) {
    MStatus status;

    MTime::Unit unit = MTime::uiUnit();
    double timeDouble = time.as(unit);
    DoubleMatrixMapCIt found = m_worldProjMatrixCache.find(timeDouble);

    if (found == m_worldProjMatrixCache.end()) {
        // To entry in the cache... lets compute and add it.

        // Get world matrix at time
        MMatrix worldMat;
        status = m_matrix.getValue(worldMat, time);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        worldMat = worldMat.inverse();

        // Get the projection matrix.
#if USE_MAYA_PROJECTION_MATRIX == 1
        // TODO: Querying the projection matrix from Maya at a specific time
        // is VERY slow, we need to find a faster way to compute this ourselves.
        // The tricky part will be making sure to match Maya's computation perfectly.
        MFnCamera cameraFn(Camera::getShapeObject(), &status);
        MDGContext ctx(time);
        MFloatMatrix floatProjMat = cameraFn.projectionMatrix(ctx, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix projMat = MMatrix(&floatProjMat.matrix[0]);
#else
        // Controls where we print out the print statements below
        const bool verbose = false; // this is used by the 'VRB' macro.

        Attr filmbackWidthAttr = getFilmbackWidthAttr();
        Attr filmbackHeightAttr = getFilmbackHeightAttr();
        Attr focalLengthAttr = getFocalLengthAttr();
        Attr offsetXAttr = getFilmbackOffsetXAttr();
        Attr offsetYAttr = getFilmbackOffsetYAttr();
        Attr cameraScaleAttr = getCameraScaleAttr();
        Attr nearClippingAttr = getNearClippingAttr();
        Attr farClippingAttr = getFarClippingAttr();
        Attr filmFitAttr = getFilmFitAttr();
        Attr renderWidthAttr = getRenderWidthAttr();
        Attr renderHeightAttr = getRenderHeightAttr();
        Attr renderAspectAttr = getRenderAspectAttr();

        int filmFit = 1; // 0=fill, 1=horizontal, 2=vertical, 3=overscan
        int imageWidth = 1920;
        int imageHeight = 1080;
        double imageAspectRatio = (double)imageWidth / (double)imageHeight;
        double filmWidth = 0.0;
        double filmHeight = 0.0;
        double focal = 0.0;
        double filmOffsetX = 0.0;
        double filmOffsetY = 0.0;
        double cameraScale = 1.0;
        double near = 0.1;
        double far = 1000.0;
        filmbackWidthAttr.getValue(filmWidth, time);
        filmbackHeightAttr.getValue(filmHeight, time);
        focalLengthAttr.getValue(focal, time);
        offsetXAttr.getValue(filmOffsetX, time);
        offsetYAttr.getValue(filmOffsetY, time);
        cameraScaleAttr.getValue(cameraScale, time);
        nearClippingAttr.getValue(near, time);
        farClippingAttr.getValue(far, time);
        filmFitAttr.getValue(filmFit, time);
        renderWidthAttr.getValue(imageWidth, time);
        renderHeightAttr.getValue(imageHeight, time);
        renderAspectAttr.getValue(imageAspectRatio, time);

        // Convert everything into millimetres
        filmWidth *= INCH_TO_MM;
        filmHeight *= INCH_TO_MM;
        filmOffsetX *= INCH_TO_MM;
        filmOffsetY *= INCH_TO_MM;

        double filmAspectRatio = filmWidth / filmHeight;

        VRB("perspective focal=" << focal);
        VRB("perspective filmWidth=" << filmWidth);
        VRB("perspective filmHeight=" << filmHeight);
        VRB("perspective filmOffsetX=" << filmOffsetX);
        VRB("perspective filmOffsetY=" << filmOffsetY);
        VRB("perspective filmAspectRatio=" << filmAspectRatio);
        VRB("perspective cameraScale=" << cameraScale);
        VRB("perspective film_fit=" << filmFit);
        VRB("perspective imageWidth=" << imageWidth);
        VRB("perspective imageHeight=" << imageHeight);
        VRB("perspective imageAspect=" << imageAspectRatio);

        double right =   (((0.5 * filmWidth) + filmOffsetX) / focal) * near;
        double left =   -(((0.5 * filmWidth) - filmOffsetX) / focal) * near;
        double top =     (((0.5 * filmHeight) + filmOffsetY) / focal) * near;
        double bottom = -(((0.5 * filmHeight) - filmOffsetY) / focal) * near;
        if (verbose) {
            MFnCamera cameraFn(Camera::getShapeObject(), &status);
            double right_maya = 0.0;
            double left_maya = 0.0;
            double top_maya = 0.0;
            double bottom_maya = 0.0;
            cameraFn.getRenderingFrustum(filmAspectRatio, left_maya, right_maya, bottom_maya, top_maya);

            VRB("perspective -------------");
            VRB("perspective right=" << right << " == " << right_maya);
            VRB("perspective left=" << left << " == " << left_maya);
            VRB("perspective top=" << top << " == " << top_maya);
            VRB("perspective bottom=" << bottom << " == " << bottom_maya);
        }

        /*
         * 'Film Fit', from the Maya command documentation...
         *
         * This describes how the digital image (in pixels) relates to the film back. Since the film back is defined
         * in terms of real numbers with some arbitrary film aspect, and the digital image is defined in integer pixels
         * with an equally arbitrary (and different) resolution, relating the two can get complicated.
         * There are 4 choices:
         *
         * Horizontal
         * In this case the digital image is made to fit the film back exactly in the horizontal direction. This then
         * gives each pixel a horizontal size = (film back width) / (horizontal resolution). The pixel height
         * is then = (pixel width) / (pixel aspect ratio). Now that the pixel has a size, resolution gives us a
         * complete image. That image will match the film back exactly in width. It will almost never match in
         * height, either being too tall or too short. By playing with the numbers you can get it pretty close
         * though.
         *
         * vertical
         * This is the same idea as horizontal fit, only applied vertically. Thus the digital image will match the
         * film back exactly in height, but miss in width.
         *
         * fill
         * This is a convenience item. The system calculates both horizontal and vertical fits and then applies the
         * one that makes the digital image larger than the film back.
         *
         * overscan
         * Overscanning the film gate in the camera view allows us to choreograph action outside of the frustum from
         * within the camera view without having to resort to a dolly or zoom. This feature is also essential for
         * animating image planes.
         *
         * Also look at scratchapixel:
         * https://www.scratchapixel.com/lessons/3d-basic-rendering/3d-viewing-pinhole-camera/implementing-virtual-pinhole-camera
         */
        VRB("perspective film fit --------------");
        double filmFitScaleX = 1.0;
        double filmFitScaleY = 1.0;
        double screenSizeX = 0.0;
        double screenSizeY = 0.0;
        double screenRight = right;
        double screenLeft = left;
        double screenTop = top;
        double screenBottom = bottom;
        switch (filmFit) {
            default:
            case 1:
                // horizontal
                VRB("perspective film fit == horizontal");
                filmFitScaleY = imageAspectRatio / filmAspectRatio;
                screenSizeX = right - left;
                screenSizeY = screenSizeX / imageAspectRatio;
                break;
            case 2:
                // vertical
                VRB("perspective film fit == vertical");
                filmFitScaleX = 1.0 / (imageAspectRatio / filmAspectRatio);
                screenSizeY = top - bottom;
                screenSizeX = screenSizeY * imageAspectRatio;
                break;
            case 0:
                // fill
                VRB("perspective film fit == fill");
                if (filmAspectRatio > imageAspectRatio) {
                    VRB("perspective film fit | filmAspectRatio > imageAspectRatio");
                    filmFitScaleX = filmAspectRatio / imageAspectRatio;
                    screenSizeY = top - bottom;
                    screenSizeX = screenSizeY * imageAspectRatio;
                } else {
                    VRB("perspective film fit | filmAspectRatio < imageAspectRatio");
                    filmFitScaleY = imageAspectRatio / filmAspectRatio;
                    screenSizeX = right - left;
                    screenSizeY = (screenSizeX * (filmAspectRatio / imageAspectRatio)) / filmAspectRatio;
                }
                break;
            case 3:
                // overscan
                VRB("perspective film fit == overscan");
                if (filmAspectRatio > imageAspectRatio) {
                    VRB("perspective film fit | filmAspectRatio > imageAspectRatio");
                    filmFitScaleY = imageAspectRatio / filmAspectRatio;
                    screenSizeX = right - left;
                    screenSizeY = (right - left) / imageAspectRatio;
                } else {
                    VRB("perspective film fit | filmAspectRatio < imageAspectRatio");
                    filmFitScaleX = filmAspectRatio / imageAspectRatio;
                    screenSizeX = (right - left) * (imageAspectRatio / filmAspectRatio);
                    screenSizeY = top - bottom;
                }
                break;
        }
        screenRight *= filmFitScaleX;
        screenLeft *= filmFitScaleX;
        screenTop *= filmFitScaleY;
        screenBottom *= filmFitScaleY;
        VRB("perspective -------------");
        VRB("perspective filmFitScaleX=" << filmFitScaleX);
        VRB("perspective filmFitScaleY=" << filmFitScaleY);
        VRB("perspective screenSizeX=" << screenSizeX);
        VRB("perspective screenSizeY=" << screenSizeY);
        VRB("perspective screenRight=" << screenRight);
        VRB("perspective screenLeft=" << screenLeft);
        VRB("perspective screenTop=" << screenTop);
        VRB("perspective screenBottom=" << screenBottom);

        // Projection Matrix
        MMatrix projMat;
        projMat[0][0] = 1.0 / (screenSizeX * 0.5) * MM_TO_CM;
        projMat[0][1] = 0;
        projMat[0][2] = 0;
        projMat[0][3] = 0;

        projMat[1][0] = 0;
        projMat[1][1] = 1.0 / (screenSizeY * 0.5) * MM_TO_CM;
        projMat[1][2] = 0;
        projMat[1][3] = 0;

        projMat[2][0] = (screenRight + screenLeft) / (screenRight - screenLeft) * filmFitScaleX;
        projMat[2][1] = (screenTop + screenBottom) / (screenTop - screenBottom) * filmFitScaleY;
        projMat[2][2] = (far + near) / (far - near);
        projMat[2][3] = -1;

        projMat[3][0] = 0;
        projMat[3][1] = 0;
        projMat[3][2] = 2 * far * near / (far - near);
        projMat[3][3] = 0;

        if (verbose) {
            MFnCamera cameraFn(Camera::getShapeObject(), &status);
            MFloatMatrix floatProjMat_maya = cameraFn.projectionMatrix();
            MMatrix projMat_maya = MMatrix(&floatProjMat_maya.matrix[0]);
            VRB("perspective -------------");
            VRB("projection[0][0] | " << projMat[0][0] << " == " << projMat_maya(0, 0));
            VRB("projection[1][1] | " << projMat[1][1] << " == " << projMat_maya(1, 1));
            VRB("projection[2][0] | " << projMat[2][0] << " == " << projMat_maya(2, 0));
            VRB("projection[2][1] | " << projMat[2][1] << " == " << projMat_maya(2, 1));
            VRB("projection[2][2] | " << projMat[2][2] << " == " << projMat_maya(2, 2));
            VRB("projection[2][3] | " << projMat[2][3] << " == " << projMat_maya(2, 3));
            VRB("projection[3][2] | " << projMat[3][2] << " == " << projMat_maya(3, 2));
        }
#endif

        // MMatrix postProjMat = MMatrix(cameraFn.postProjectionMatrix(ctx).matrix);
        value = worldMat * projMat; //* postProjMat;

        // Add into the cache.
        DoubleMatrixPair timeMatrixPair (timeDouble, value);
        m_worldProjMatrixCache.insert(timeMatrixPair);
    } else {
        value = found->second;
    }
    return status;
}

MStatus Camera::clearWorldProjMatrixCache() {
    m_worldProjMatrixCache.clear();
    return MS::kSuccess;
}

