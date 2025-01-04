/*
 * Copyright (C) 2022 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 */

// Do not define 'min' and 'max' macros on MS Windows (with MSVC),
// added to fix errors with LDPK.
#define NOMINMAX

#include "MMLensModel3deNode.h"

// STL
#include <algorithm>
#include <cmath>
#include <cstring>

// Maya
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnPluginData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>

// MM Solver
#include <mmlens/lens_model.h>
#include <mmlens/lens_model_3de_anamorphic_deg_4_rotate_squeeze_xy.h>
#include <mmlens/lens_model_3de_anamorphic_deg_4_rotate_squeeze_xy_rescaled.h>
#include <mmlens/lens_model_3de_anamorphic_deg_6_rotate_squeeze_xy.h>
#include <mmlens/lens_model_3de_anamorphic_deg_6_rotate_squeeze_xy_rescaled.h>
#include <mmlens/lens_model_3de_classic.h>
#include <mmlens/lens_model_3de_radial_decentered_deg_4_cylindric.h>
#include <mmlens/lens_model_passthrough.h>

#include "MMLensData.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

MTypeId MMLensModel3deNode::m_id(MM_LENS_MODEL_3DE_TYPE_ID);

// Input Attributes
MObject MMLensModel3deNode::a_inLens;
MObject MMLensModel3deNode::a_enable;
MObject MMLensModel3deNode::a_lensModel;

MObject MMLensModel3deNode::a_tdeClassic_heading;
MObject MMLensModel3deNode::a_tdeClassic_distortion;
MObject MMLensModel3deNode::a_tdeClassic_anamorphicSqueeze;
MObject MMLensModel3deNode::a_tdeClassic_curvatureX;
MObject MMLensModel3deNode::a_tdeClassic_curvatureY;
MObject MMLensModel3deNode::a_tdeClassic_quarticDistortion;

MObject MMLensModel3deNode::a_tdeRadialStdDeg4_heading;
MObject MMLensModel3deNode::a_tdeRadialStdDeg4_degree2_distortion;
MObject MMLensModel3deNode::a_tdeRadialStdDeg4_degree2_u;
MObject MMLensModel3deNode::a_tdeRadialStdDeg4_degree2_v;
MObject MMLensModel3deNode::a_tdeRadialStdDeg4_degree4_distortion;
MObject MMLensModel3deNode::a_tdeRadialStdDeg4_degree4_u;
MObject MMLensModel3deNode::a_tdeRadialStdDeg4_degree4_v;
MObject MMLensModel3deNode::a_tdeRadialStdDeg4_cylindricDirection;
MObject MMLensModel3deNode::a_tdeRadialStdDeg4_cylindricBending;

MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_heading;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree2_cx02;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree2_cy02;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree2_cx22;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree2_cy22;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree4_cx04;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree4_cy04;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree4_cx24;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree4_cy24;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree4_cx44;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_degree4_cy44;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_lensRotation;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_squeeze_x;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_squeeze_y;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg4_rescale;

MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_heading;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree2_cx02;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree2_cy02;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree2_cx22;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree2_cy22;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree4_cx04;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree4_cy04;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree4_cx24;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree4_cy24;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree4_cx44;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree4_cy44;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree6_cx06;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree6_cy06;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree6_cx26;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree6_cy26;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree6_cx46;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree6_cy46;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree6_cx66;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_degree6_cy66;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_lensRotation;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_squeeze_x;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_squeeze_y;
MObject MMLensModel3deNode::a_tdeAnamorphicStdDeg6_rescale;

// Output Attributes
MObject MMLensModel3deNode::a_outLens;

MMLensModel3deNode::MMLensModel3deNode() {}

MMLensModel3deNode::~MMLensModel3deNode() {}

MString MMLensModel3deNode::nodeName() { return MString("mmLensModel3de"); }

void MMLensModel3deNode::postConstructor() {
    MObject thisNode = thisMObject();

    MPlug tdeClassicPlug(thisNode, MMLensModel3deNode::a_tdeClassic_heading);
    MPlug tdeRadialStdDeg4Plug(thisNode,
                               MMLensModel3deNode::a_tdeRadialStdDeg4_heading);
    MPlug tdeAnamorphicStdDeg4Plug(
        thisNode, MMLensModel3deNode::a_tdeAnamorphicStdDeg4_heading);

    tdeClassicPlug.setLocked(true);
    tdeRadialStdDeg4Plug.setLocked(true);
    tdeAnamorphicStdDeg4Plug.setLocked(true);
}

MStatus MMLensModel3deNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if (plug == a_outLens) {
        // Enable Attribute toggle
        MDataHandle enableHandle = data.inputValue(a_enable, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        const bool enable = enableHandle.asBool();

        MDataHandle lensModelHandle = data.inputValue(a_lensModel, &status);
        const short lensModelNum = lensModelHandle.asShort();
        const auto lensModelType =
            static_cast<mmlens::LensModelType>(lensModelNum);

        // Create initial plug-in data structure. We don't need to
        // 'new' the data type directly.
        MFnPluginData fnPluginData;
        MTypeId data_type_id(MM_LENS_DATA_TYPE_ID);
        fnPluginData.create(data_type_id, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Get Input Lens
        MDataHandle inLensHandle = data.inputValue(a_inLens, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMLensData *inputLensData = (MMLensData *)inLensHandle.asPluginData();
        std::shared_ptr<mmlens::LensModel> inputLensModel;
        if (inputLensData != nullptr) {
            inputLensModel = inputLensData->getValue();
        }

        // Output Lens
        MDataHandle outLensHandle = data.outputValue(a_outLens);
        MMLensData *newLensData = (MMLensData *)fnPluginData.data(&status);
        if (!enable) {
            // Create a lens distortion function to be passed to the
            // MMLensData.
            auto newLensModel = std::shared_ptr<mmlens::LensModelPassthrough>(
                new mmlens::LensModelPassthrough());

            newLensModel->setInputLensModel(inputLensModel);

            newLensData->setValue(newLensModel);
            outLensHandle.setMPxData(newLensData);
            outLensHandle.setClean();
            status = MS::kSuccess;

        } else if (lensModelType == mmlens::LensModelType::k3deClassic) {
            MDataHandle k1Handle =
                data.inputValue(a_tdeClassic_distortion, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle squeezeHandle =
                data.inputValue(a_tdeClassic_anamorphicSqueeze, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle cxHandle =
                data.inputValue(a_tdeClassic_curvatureX, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle cyHandle =
                data.inputValue(a_tdeClassic_curvatureY, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle k2Handle =
                data.inputValue(a_tdeClassic_quarticDistortion, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            double distortion = k1Handle.asDouble();
            double anamorphicSqueeze = squeezeHandle.asDouble();
            double curvatureX = cxHandle.asDouble();
            double curvatureY = cyHandle.asDouble();
            double quarticDistortion = k2Handle.asDouble();

            // Create a lens distortion function to be passed to the
            // MMLensData.
            auto newLensModel = std::shared_ptr<mmlens::LensModel3deClassic>(
                new mmlens::LensModel3deClassic());

            // Connect the input lens to the newly created lens object.
            newLensModel->setInputLensModel(inputLensModel);
            newLensModel->setDistortion(distortion);
            newLensModel->setAnamorphicSqueeze(anamorphicSqueeze);
            newLensModel->setCurvatureX(curvatureX);
            newLensModel->setCurvatureY(curvatureY);
            newLensModel->setQuarticDistortion(quarticDistortion);

            newLensData->setValue(newLensModel);
            outLensHandle.setMPxData(newLensData);
            outLensHandle.setClean();
            status = MS::kSuccess;

        } else if (lensModelType == mmlens::LensModelType::k3deRadialStdDeg4) {
            MDataHandle deg2DistortionHandle =
                data.inputValue(a_tdeRadialStdDeg4_degree2_distortion, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg2UHandle =
                data.inputValue(a_tdeRadialStdDeg4_degree2_u, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg2VHandle =
                data.inputValue(a_tdeRadialStdDeg4_degree2_v, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg4DistortionHandle =
                data.inputValue(a_tdeRadialStdDeg4_degree4_distortion, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg4UHandle =
                data.inputValue(a_tdeRadialStdDeg4_degree4_u, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg4VHandle =
                data.inputValue(a_tdeRadialStdDeg4_degree4_v, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle cylindricDirHandle =
                data.inputValue(a_tdeRadialStdDeg4_cylindricDirection, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle cylindricBendHandle =
                data.inputValue(a_tdeRadialStdDeg4_cylindricBending, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            double deg2Distortion = deg2DistortionHandle.asDouble();
            double deg2U = deg2UHandle.asDouble();
            double deg2V = deg2VHandle.asDouble();
            double deg4Distortion = deg4DistortionHandle.asDouble();
            double deg4U = deg4UHandle.asDouble();
            double deg4V = deg4VHandle.asDouble();
            double cylindricDirection = cylindricDirHandle.asDouble();
            double cylindricBending = cylindricBendHandle.asDouble();

            // Create a lens distortion function to be passed to the
            // MMLensData.
            auto newLensModel = std::shared_ptr<
                mmlens::LensModel3deRadialDecenteredDeg4Cylindric>(
                new mmlens::LensModel3deRadialDecenteredDeg4Cylindric());

            // Connect the input lens to the newly created lens object.
            newLensModel->setInputLensModel(inputLensModel);
            newLensModel->setDegree2Distortion(deg2Distortion);
            newLensModel->setDegree2U(deg2U);
            newLensModel->setDegree2V(deg2V);
            newLensModel->setDegree4Distortion(deg4Distortion);
            newLensModel->setDegree4U(deg4U);
            newLensModel->setDegree4V(deg4V);
            newLensModel->setCylindricDirection(cylindricDirection);
            newLensModel->setCylindricBending(cylindricBending);

            newLensData->setValue(newLensModel);
            outLensHandle.setMPxData(newLensData);
            outLensHandle.setClean();
            status = MS::kSuccess;

        } else if (lensModelType ==
                       mmlens::LensModelType::k3deAnamorphicStdDeg4 ||
                   lensModelType ==
                       mmlens::LensModelType::k3deAnamorphicStdDeg4Rescaled) {
            MDataHandle deg2Cx02Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree2_cx02, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg2Cy02Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree2_cy02, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg2Cx22Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree2_cx22, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg2Cy22Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree2_cy22, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg4Cx04Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree4_cx04, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg4Cy04Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree4_cy04, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg4Cx24Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree4_cx24, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg4Cy24Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree4_cy24, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg4Cx44Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree4_cx44, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg4Cy44Handle =
                data.inputValue(a_tdeAnamorphicStdDeg4_degree4_cy44, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle lensRotationHandle =
                data.inputValue(a_tdeAnamorphicStdDeg4_lensRotation, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle squeezeXHandle =
                data.inputValue(a_tdeAnamorphicStdDeg4_squeeze_x, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle squeezeYHandle =
                data.inputValue(a_tdeAnamorphicStdDeg4_squeeze_y, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle rescaleHandle =
                data.inputValue(a_tdeAnamorphicStdDeg4_rescale, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            double deg2Cx02 = deg2Cx02Handle.asDouble();
            double deg2Cy02 = deg2Cy02Handle.asDouble();

            double deg2Cx22 = deg2Cx22Handle.asDouble();
            double deg2Cy22 = deg2Cy22Handle.asDouble();

            double deg4Cx04 = deg4Cx04Handle.asDouble();
            double deg4Cy04 = deg4Cy04Handle.asDouble();

            double deg4Cx24 = deg4Cx24Handle.asDouble();
            double deg4Cy24 = deg4Cy24Handle.asDouble();

            double deg4Cx44 = deg4Cx44Handle.asDouble();
            double deg4Cy44 = deg4Cy44Handle.asDouble();

            double lensRotation = lensRotationHandle.asDouble();
            double squeeze_x = squeezeXHandle.asDouble();
            double squeeze_y = squeezeYHandle.asDouble();

            double rescale = rescaleHandle.asDouble();

            if (lensModelType == mmlens::LensModelType::k3deAnamorphicStdDeg4) {
                // Create a lens distortion function to be passed to the
                // MMLensData.
                auto newLensModel = std::shared_ptr<
                    mmlens::LensModel3deAnamorphicDeg4RotateSqueezeXY>(
                    new mmlens::LensModel3deAnamorphicDeg4RotateSqueezeXY());

                // Connect the input lens to the newly created lens object.
                newLensModel->setInputLensModel(inputLensModel);
                newLensModel->setDegree2Cx02(deg2Cx02);
                newLensModel->setDegree2Cy02(deg2Cy02);

                newLensModel->setDegree2Cx22(deg2Cx22);
                newLensModel->setDegree2Cy22(deg2Cy22);

                newLensModel->setDegree4Cx04(deg4Cx04);
                newLensModel->setDegree4Cy04(deg4Cy04);

                newLensModel->setDegree4Cx24(deg4Cx24);
                newLensModel->setDegree4Cy24(deg4Cy24);

                newLensModel->setDegree4Cx44(deg4Cx44);
                newLensModel->setDegree4Cy44(deg4Cy44);

                newLensModel->setLensRotation(lensRotation);
                newLensModel->setSqueezeX(squeeze_x);
                newLensModel->setSqueezeY(squeeze_y);

                newLensData->setValue(newLensModel);
            } else if (lensModelType ==
                       mmlens::LensModelType::k3deAnamorphicStdDeg4Rescaled) {
                // Create a lens distortion function to be passed to the
                // MMLensData.
                auto newLensModel = std::shared_ptr<
                    mmlens::LensModel3deAnamorphicDeg4RotateSqueezeXYRescaled>(
                    new mmlens::
                        LensModel3deAnamorphicDeg4RotateSqueezeXYRescaled());

                // Connect the input lens to the newly created lens object.
                newLensModel->setInputLensModel(inputLensModel);
                newLensModel->setDegree2Cx02(deg2Cx02);
                newLensModel->setDegree2Cy02(deg2Cy02);

                newLensModel->setDegree2Cx22(deg2Cx22);
                newLensModel->setDegree2Cy22(deg2Cy22);

                newLensModel->setDegree4Cx04(deg4Cx04);
                newLensModel->setDegree4Cy04(deg4Cy04);

                newLensModel->setDegree4Cx24(deg4Cx24);
                newLensModel->setDegree4Cy24(deg4Cy24);

                newLensModel->setDegree4Cx44(deg4Cx44);
                newLensModel->setDegree4Cy44(deg4Cy44);

                newLensModel->setLensRotation(lensRotation);
                newLensModel->setSqueezeX(squeeze_x);
                newLensModel->setSqueezeY(squeeze_y);

                // The only different parameter for this lens model.
                newLensModel->setRescale(rescale);

                newLensData->setValue(newLensModel);
            }

            outLensHandle.setMPxData(newLensData);
            outLensHandle.setClean();
            status = MS::kSuccess;

        }

        else if (lensModelType ==
                     mmlens::LensModelType::k3deAnamorphicStdDeg6 ||
                 lensModelType ==
                     mmlens::LensModelType::k3deAnamorphicStdDeg6Rescaled) {
            MDataHandle deg2Cx02Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree2_cx02, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg2Cy02Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree2_cy02, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg2Cx22Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree2_cx22, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg2Cy22Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree2_cy22, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg6Cx04Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree4_cx04, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg6Cy04Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree4_cy04, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg6Cx24Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree4_cx24, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg6Cy24Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree4_cy24, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg6Cx44Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree4_cx44, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg6Cy44Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree4_cy44, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg6Cx06Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree6_cx06, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg6Cy06Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree6_cy06, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg6Cx26Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree6_cx26, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg6Cy26Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree6_cy26, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg6Cx46Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree6_cx46, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg6Cy46Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree6_cy46, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle deg6Cx66Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree6_cx66, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle deg6Cy66Handle =
                data.inputValue(a_tdeAnamorphicStdDeg6_degree6_cy66, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle lensRotationHandle =
                data.inputValue(a_tdeAnamorphicStdDeg6_lensRotation, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle squeezeXHandle =
                data.inputValue(a_tdeAnamorphicStdDeg6_squeeze_x, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MDataHandle squeezeYHandle =
                data.inputValue(a_tdeAnamorphicStdDeg6_squeeze_y, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MDataHandle rescaleHandle =
                data.inputValue(a_tdeAnamorphicStdDeg6_rescale, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            double deg2Cx02 = deg2Cx02Handle.asDouble();
            double deg2Cy02 = deg2Cy02Handle.asDouble();

            double deg2Cx22 = deg2Cx22Handle.asDouble();
            double deg2Cy22 = deg2Cy22Handle.asDouble();

            double deg6Cx04 = deg6Cx04Handle.asDouble();
            double deg6Cy04 = deg6Cy04Handle.asDouble();

            double deg6Cx24 = deg6Cx24Handle.asDouble();
            double deg6Cy24 = deg6Cy24Handle.asDouble();

            double deg6Cx44 = deg6Cx44Handle.asDouble();
            double deg6Cy44 = deg6Cy44Handle.asDouble();

            double deg6Cx06 = deg6Cx06Handle.asDouble();
            double deg6Cy06 = deg6Cy06Handle.asDouble();

            double deg6Cx26 = deg6Cx26Handle.asDouble();
            double deg6Cy26 = deg6Cy26Handle.asDouble();

            double deg6Cx46 = deg6Cx46Handle.asDouble();
            double deg6Cy46 = deg6Cy46Handle.asDouble();

            double deg6Cx66 = deg6Cx66Handle.asDouble();
            double deg6Cy66 = deg6Cy66Handle.asDouble();

            double lensRotation = lensRotationHandle.asDouble();
            double squeeze_x = squeezeXHandle.asDouble();
            double squeeze_y = squeezeYHandle.asDouble();

            double rescale = rescaleHandle.asDouble();

            if (lensModelType == mmlens::LensModelType::k3deAnamorphicStdDeg6) {
                // Create a lens distortion function to be passed to the
                // MMLensData.
                auto newLensModel = std::shared_ptr<
                    mmlens::LensModel3deAnamorphicDeg6RotateSqueezeXY>(
                    new mmlens::LensModel3deAnamorphicDeg6RotateSqueezeXY());

                // Connect the input lens to the newly created lens object.
                newLensModel->setInputLensModel(inputLensModel);
                newLensModel->setDegree2Cx02(deg2Cx02);
                newLensModel->setDegree2Cy02(deg2Cy02);

                newLensModel->setDegree2Cx22(deg2Cx22);
                newLensModel->setDegree2Cy22(deg2Cy22);

                newLensModel->setDegree4Cx04(deg6Cx04);
                newLensModel->setDegree4Cy04(deg6Cy04);

                newLensModel->setDegree4Cx24(deg6Cx24);
                newLensModel->setDegree4Cy24(deg6Cy24);

                newLensModel->setDegree4Cx44(deg6Cx44);
                newLensModel->setDegree4Cy44(deg6Cy44);

                newLensModel->setDegree6Cx06(deg6Cx06);
                newLensModel->setDegree6Cy06(deg6Cy06);

                newLensModel->setDegree6Cx26(deg6Cx26);
                newLensModel->setDegree6Cy26(deg6Cy26);

                newLensModel->setDegree6Cx46(deg6Cx46);
                newLensModel->setDegree6Cy46(deg6Cy46);

                newLensModel->setDegree6Cx66(deg6Cx66);
                newLensModel->setDegree6Cy66(deg6Cy66);

                newLensModel->setLensRotation(lensRotation);
                newLensModel->setSqueezeX(squeeze_x);
                newLensModel->setSqueezeY(squeeze_y);

                newLensData->setValue(newLensModel);
            } else if (lensModelType ==
                       mmlens::LensModelType::k3deAnamorphicStdDeg6Rescaled) {
                // Create a lens distortion function to be passed to the
                // MMLensData.
                auto newLensModel = std::shared_ptr<
                    mmlens::LensModel3deAnamorphicDeg6RotateSqueezeXYRescaled>(
                    new mmlens::
                        LensModel3deAnamorphicDeg6RotateSqueezeXYRescaled());

                // Connect the input lens to the newly created lens object.
                newLensModel->setInputLensModel(inputLensModel);
                newLensModel->setDegree2Cx02(deg2Cx02);
                newLensModel->setDegree2Cy02(deg2Cy02);

                newLensModel->setDegree2Cx22(deg2Cx22);
                newLensModel->setDegree2Cy22(deg2Cy22);

                newLensModel->setDegree4Cx04(deg6Cx04);
                newLensModel->setDegree4Cy04(deg6Cy04);

                newLensModel->setDegree4Cx24(deg6Cx24);
                newLensModel->setDegree4Cy24(deg6Cy24);

                newLensModel->setDegree4Cx44(deg6Cx44);
                newLensModel->setDegree4Cy44(deg6Cy44);

                newLensModel->setDegree6Cx06(deg6Cx06);
                newLensModel->setDegree6Cy06(deg6Cy06);

                newLensModel->setDegree6Cx26(deg6Cx26);
                newLensModel->setDegree6Cy26(deg6Cy26);

                newLensModel->setDegree6Cx46(deg6Cx46);
                newLensModel->setDegree6Cy46(deg6Cy46);

                newLensModel->setDegree6Cx66(deg6Cx66);
                newLensModel->setDegree6Cy66(deg6Cy66);

                newLensModel->setLensRotation(lensRotation);
                newLensModel->setSqueezeX(squeeze_x);
                newLensModel->setSqueezeY(squeeze_y);

                // The only different parameter for this lens model.
                newLensModel->setRescale(rescale);

                newLensData->setValue(newLensModel);
            }

            outLensHandle.setMPxData(newLensData);
            outLensHandle.setClean();
            status = MS::kSuccess;

        }

        else {
            const MString node_name = name();
            MMSOLVER_MAYA_ERR(
                "mmlens::LensModelType value is invalid: nodeName="
                << node_name.asChar()
                << " lensModelType=" << static_cast<int>(lensModelType));
            status = MS::kFailure;

            // Create a lens distortion function to be passed to the
            // MMLensData.
            auto newLensModel = std::shared_ptr<mmlens::LensModelPassthrough>(
                new mmlens::LensModelPassthrough());

            newLensData->setValue(newLensModel);
        }
    }

    return status;
}

void *MMLensModel3deNode::creator() { return (new MMLensModel3deNode()); }

MStatus MMLensModel3deNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnEnumAttribute enumAttr;
    MFnTypedAttribute typedAttr;

    // In Lens
    MTypeId data_type_id(MM_LENS_DATA_TYPE_ID);
    a_inLens = typedAttr.create("inLens", "ilns", data_type_id);
    CHECK_MSTATUS(typedAttr.setStorable(false));
    CHECK_MSTATUS(typedAttr.setKeyable(false));
    CHECK_MSTATUS(typedAttr.setReadable(true));
    CHECK_MSTATUS(typedAttr.setWritable(true));
    CHECK_MSTATUS(addAttribute(a_inLens));

    // Enable
    a_enable =
        numericAttr.create("enable", "enb", MFnNumericData::kBoolean, true);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_enable));

    // Lens Model
    auto defaultLensModels =
        static_cast<short>(mmlens::LensModelType::k3deRadialStdDeg4);
    a_lensModel =
        enumAttr.create("lensModel", "lnsmdl", defaultLensModels, &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(enumAttr.addField(
        "3DE Classic LD Model",
        static_cast<short>(mmlens::LensModelType::k3deClassic)));
    CHECK_MSTATUS(enumAttr.addField(
        "3DE4 Radial - Standard, Degree 4",
        static_cast<short>(mmlens::LensModelType::k3deRadialStdDeg4)));
    CHECK_MSTATUS(enumAttr.addField(
        "3DE4 Anamorphic - Standard, Degree 4",
        static_cast<short>(mmlens::LensModelType::k3deAnamorphicStdDeg4)));
    CHECK_MSTATUS(enumAttr.addField(
        "3DE4 Anamorphic - Rescaled, Degree 4",
        static_cast<short>(
            mmlens::LensModelType::k3deAnamorphicStdDeg4Rescaled)));
    CHECK_MSTATUS(enumAttr.addField(
        "3DE4 Anamorphic - Standard, Degree 6",
        static_cast<short>(mmlens::LensModelType::k3deAnamorphicStdDeg6)));
    CHECK_MSTATUS(enumAttr.addField(
        "3DE4 Anamorphic - Rescaled, Degree 6",
        static_cast<short>(
            mmlens::LensModelType::k3deAnamorphicStdDeg6Rescaled)));
    // CHECK_MSTATUS(enumAttr.addField(
    //         "3DE4 Anamorphic, Degree 6",
    //         static_cast<short>(mmlens::LensModelType::k3deAnamorphicDeg6)));
    CHECK_MSTATUS(enumAttr.setStorable(true));
    CHECK_MSTATUS(enumAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_lensModel));

    // 3DE Classic LD Model
    {
        // Channel Box heading for the lens model. This attribute does
        // nothing to the output of the node.
        a_tdeClassic_heading = enumAttr.create(
            "tdeClassic_heading", "tdeClassic_heading", 0, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(enumAttr.addField("--------", 0));
        CHECK_MSTATUS(enumAttr.setStorable(false));
        CHECK_MSTATUS(enumAttr.setKeyable(false));
        CHECK_MSTATUS(enumAttr.setChannelBox(true));
        CHECK_MSTATUS(enumAttr.setNiceNameOverride("3DE Classic LD Model"));
        CHECK_MSTATUS(addAttribute(a_tdeClassic_heading));

        a_tdeClassic_distortion =
            numericAttr.create("tdeClassic_distortion", "tdeClassic_distortion",
                               MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Distortion"));
        CHECK_MSTATUS(addAttribute(a_tdeClassic_distortion));

        // Anamorphic Squeeze
        a_tdeClassic_anamorphicSqueeze = numericAttr.create(
            "tdeClassic_anamorphicSqueeze", "tdeClassic_anamorphicSqueeze",
            MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setMin(0.1));
        CHECK_MSTATUS(numericAttr.setSoftMin(0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(2.0));
        CHECK_MSTATUS(numericAttr.setMax(4.0));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Anamorphic Squeeze"));
        CHECK_MSTATUS(addAttribute(a_tdeClassic_anamorphicSqueeze));

        // Curvature X
        a_tdeClassic_curvatureX =
            numericAttr.create("tdeClassic_curvatureX", "tdeClassic_curvatureX",
                               MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Curvature X"));
        CHECK_MSTATUS(addAttribute(a_tdeClassic_curvatureX));

        // Curvature Y
        a_tdeClassic_curvatureY =
            numericAttr.create("tdeClassic_curvatureY", "tdeClassic_curvatureY",
                               MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Curvature Y"));
        CHECK_MSTATUS(addAttribute(a_tdeClassic_curvatureY));

        // Quartic Distortion
        a_tdeClassic_quarticDistortion = numericAttr.create(
            "tdeClassic_quarticDistortion", "tdeClassic_quarticDistortion",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Quartic Distortion"));
        CHECK_MSTATUS(addAttribute(a_tdeClassic_quarticDistortion));
    }

    // 3DE Radial Decentered Degree 4 Cylindric
    {
        // Channel Box heading for the lens model. This attribute does
        // nothing to the output of the node.
        a_tdeRadialStdDeg4_heading = enumAttr.create(
            "tdeRadialStdDeg4_heading", "tdeRadialStdDeg4_heading", 0, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(enumAttr.addField("--------", 0));
        CHECK_MSTATUS(enumAttr.setStorable(false));
        CHECK_MSTATUS(enumAttr.setKeyable(false));
        CHECK_MSTATUS(enumAttr.setChannelBox(true));
        CHECK_MSTATUS(
            enumAttr.setNiceNameOverride("3DE4 Radial - Standard, Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialStdDeg4_heading));

        // Distortion - Degree 2
        a_tdeRadialStdDeg4_degree2_distortion =
            numericAttr.create("tdeRadialStdDeg4_degree2_distortion",
                               "tdeRadialStdDeg4_degree2_distortion",
                               MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Distortion - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialStdDeg4_degree2_distortion));

        // U - Degree 2
        a_tdeRadialStdDeg4_degree2_u = numericAttr.create(
            "tdeRadialStdDeg4_degree2_u", "tdeRadialStdDeg4_degree2_u",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("U - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialStdDeg4_degree2_u));

        // V - Degree 2
        a_tdeRadialStdDeg4_degree2_v = numericAttr.create(
            "tdeRadialStdDeg4_degree2_v", "tdeRadialStdDeg4_degree2_v",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("V - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialStdDeg4_degree2_v));

        // Quartic Distortion - Degree 4
        a_tdeRadialStdDeg4_degree4_distortion =
            numericAttr.create("tdeRadialStdDeg4_degree4_distortion",
                               "tdeRadialStdDeg4_degree4_distortion",
                               MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(
            numericAttr.setNiceNameOverride("Quartic Distortion - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialStdDeg4_degree4_distortion));

        // U - Degree 4
        a_tdeRadialStdDeg4_degree4_u = numericAttr.create(
            "tdeRadialStdDeg4_degree4_u", "tdeRadialStdDeg4_degree4_u",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("U - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialStdDeg4_degree4_u));

        // V - Degree 4
        a_tdeRadialStdDeg4_degree4_v = numericAttr.create(
            "tdeRadialStdDeg4_degree4_v", "tdeRadialStdDeg4_degree4_v",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("V - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialStdDeg4_degree4_v));

        // Phi - Cylindric Direction
        a_tdeRadialStdDeg4_cylindricDirection =
            numericAttr.create("tdeRadialStdDeg4_cylindricDirection",
                               "tdeRadialStdDeg4_cylindricDirection",
                               MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-90.0));
        CHECK_MSTATUS(numericAttr.setSoftMax(90.0));
        CHECK_MSTATUS(
            numericAttr.setNiceNameOverride("Phi - Cylindric Direction"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialStdDeg4_cylindricDirection));

        // B - Cylindric Bending
        a_tdeRadialStdDeg4_cylindricBending = numericAttr.create(
            "tdeRadialStdDeg4_cylindricBending",
            "tdeRadialStdDeg4_cylindricBending", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.1));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.1));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("B - Cylindric Bending"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialStdDeg4_cylindricBending));
    }

    // 3DE Anamorphic - Standard, Degree 4 (and 'Rescaled' version)
    {
        // Channel Box heading for the lens model. This attribute does
        // nothing to the output of the node.
        a_tdeAnamorphicStdDeg4_heading =
            enumAttr.create("tdeAnamorphicStdDeg4_heading",
                            "tdeAnamorphicStdDeg4_heading", 0, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(enumAttr.addField("--------", 0));
        CHECK_MSTATUS(enumAttr.setStorable(false));
        CHECK_MSTATUS(enumAttr.setKeyable(false));
        CHECK_MSTATUS(enumAttr.setChannelBox(true));
        CHECK_MSTATUS(enumAttr.setNiceNameOverride(
            "3DE4 Anamorphic - Standard, Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_heading));

        // Cx02 - Degree 2
        a_tdeAnamorphicStdDeg4_degree2_cx02 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree2_cx02",
            "tdeAnamorphicStdDeg4_degree2_cx02", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx02 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree2_cx02));

        // Cy02 - Degree 2
        a_tdeAnamorphicStdDeg4_degree2_cy02 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree2_cy02",
            "tdeAnamorphicStdDeg4_degree2_cy02", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy02 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree2_cy02));

        // Cx22 - Degree 2
        a_tdeAnamorphicStdDeg4_degree2_cx22 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree2_cx22",
            "tdeAnamorphicStdDeg4_degree2_cx22", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx22 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree2_cx22));

        // Cy22 - Degree 2
        a_tdeAnamorphicStdDeg4_degree2_cy22 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree2_cy22",
            "tdeAnamorphicStdDeg4_degree2_cy22", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy22 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree2_cy22));

        // Cx04 - Degree 4
        a_tdeAnamorphicStdDeg4_degree4_cx04 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree4_cx04",
            "tdeAnamorphicStdDeg4_degree4_cx04", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx04 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree4_cx04));

        // Cy04 - Degree 4
        a_tdeAnamorphicStdDeg4_degree4_cy04 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree4_cy04",
            "tdeAnamorphicStdDeg4_degree4_cy04", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy04 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree4_cy04));

        // Cx24 - Degree 4
        a_tdeAnamorphicStdDeg4_degree4_cx24 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree4_cx24",
            "tdeAnamorphicStdDeg4_degree4_cx24", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx24 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree4_cx24));

        // Cy24 - Degree 4
        a_tdeAnamorphicStdDeg4_degree4_cy24 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree4_cy24",
            "tdeAnamorphicStdDeg4_degree4_cy24", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy24 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree4_cy24));

        // Cx44 - Degree 4
        a_tdeAnamorphicStdDeg4_degree4_cx44 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree4_cx44",
            "tdeAnamorphicStdDeg4_degree4_cx44", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx44 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree4_cx44));

        // Cy44 - Degree 4
        a_tdeAnamorphicStdDeg4_degree4_cy44 = numericAttr.create(
            "tdeAnamorphicStdDeg4_degree4_cy44",
            "tdeAnamorphicStdDeg4_degree4_cy44", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy44 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_degree4_cy44));

        // Lens Rotation
        a_tdeAnamorphicStdDeg4_lensRotation = numericAttr.create(
            "tdeAnamorphicStdDeg4_lensRotation",
            "tdeAnamorphicStdDeg4_lensRotation", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-2.0));
        CHECK_MSTATUS(numericAttr.setSoftMax(2.0));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Lens Rotation"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_lensRotation));

        // Squeeze X
        a_tdeAnamorphicStdDeg4_squeeze_x = numericAttr.create(
            "tdeAnamorphicStdDeg4_squeeze_x", "tdeAnamorphicStdDeg4_squeeze_x",
            MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(0.9));
        CHECK_MSTATUS(numericAttr.setSoftMax(1.1));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Squeeze-X"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_squeeze_x));

        // Squeeze Y
        a_tdeAnamorphicStdDeg4_squeeze_y = numericAttr.create(
            "tdeAnamorphicStdDeg4_squeeze_y", "tdeAnamorphicStdDeg4_squeeze_y",
            MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(0.9));
        CHECK_MSTATUS(numericAttr.setSoftMax(1.1));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Squeeze-Y"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_squeeze_y));

        // Rescale
        a_tdeAnamorphicStdDeg4_rescale = numericAttr.create(
            "tdeAnamorphicStdDeg4_rescale", "tdeAnamorphicStdDeg4_rescale",
            MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(0.25));
        CHECK_MSTATUS(numericAttr.setSoftMax(4.0));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Rescale"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg4_rescale));
    }

    // 3DE Anamorphic - Standard, Degree 6 (and 'Rescaled' version)
    {
        // Channel Box heading for the lens model. This attribute does
        // nothing to the output of the node.
        a_tdeAnamorphicStdDeg6_heading =
            enumAttr.create("tdeAnamorphicStdDeg6_heading",
                            "tdeAnamorphicStdDeg6_heading", 0, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(enumAttr.addField("--------", 0));
        CHECK_MSTATUS(enumAttr.setStorable(false));
        CHECK_MSTATUS(enumAttr.setKeyable(false));
        CHECK_MSTATUS(enumAttr.setChannelBox(true));
        CHECK_MSTATUS(enumAttr.setNiceNameOverride(
            "3DE4 Anamorphic - Standard, Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_heading));

        // Cx02 - Degree 2
        a_tdeAnamorphicStdDeg6_degree2_cx02 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree2_cx02",
            "tdeAnamorphicStdDeg6_degree2_cx02", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx02 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree2_cx02));

        // Cy02 - Degree 2
        a_tdeAnamorphicStdDeg6_degree2_cy02 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree2_cy02",
            "tdeAnamorphicStdDeg6_degree2_cy02", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy02 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree2_cy02));

        // Cx22 - Degree 2
        a_tdeAnamorphicStdDeg6_degree2_cx22 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree2_cx22",
            "tdeAnamorphicStdDeg6_degree2_cx22", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx22 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree2_cx22));

        // Cy22 - Degree 2
        a_tdeAnamorphicStdDeg6_degree2_cy22 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree2_cy22",
            "tdeAnamorphicStdDeg6_degree2_cy22", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy22 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree2_cy22));

        // Cx04 - Degree 4
        a_tdeAnamorphicStdDeg6_degree4_cx04 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree4_cx04",
            "tdeAnamorphicStdDeg6_degree4_cx04", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx04 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree4_cx04));

        // Cy04 - Degree 4
        a_tdeAnamorphicStdDeg6_degree4_cy04 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree4_cy04",
            "tdeAnamorphicStdDeg6_degree4_cy04", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy04 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree4_cy04));

        // Cx24 - Degree 4
        a_tdeAnamorphicStdDeg6_degree4_cx24 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree4_cx24",
            "tdeAnamorphicStdDeg6_degree4_cx24", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx24 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree4_cx24));

        // Cy24 - Degree 4
        a_tdeAnamorphicStdDeg6_degree4_cy24 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree4_cy24",
            "tdeAnamorphicStdDeg6_degree4_cy24", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy24 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree4_cy24));

        // Cx44 - Degree 4
        a_tdeAnamorphicStdDeg6_degree4_cx44 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree4_cx44",
            "tdeAnamorphicStdDeg6_degree4_cx44", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx44 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree4_cx44));

        // Cy44 - Degree 4
        a_tdeAnamorphicStdDeg6_degree4_cy44 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree4_cy44",
            "tdeAnamorphicStdDeg6_degree4_cy44", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy44 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree4_cy44));

        // Cx06 - degree 6
        a_tdeAnamorphicStdDeg6_degree6_cx06 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree6_cx06",
            "tdeAnamorphicStdDeg6_degree6_cx06", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx06 - Degree 6"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree6_cx06));

        // Cy06 - degree 6
        a_tdeAnamorphicStdDeg6_degree6_cy06 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree6_cy06",
            "tdeAnamorphicStdDeg6_degree6_cy06", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy06 - Degree 6"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree6_cy06));

        // Cx26 - degree 6
        a_tdeAnamorphicStdDeg6_degree6_cx26 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree6_cx26",
            "tdeAnamorphicStdDeg6_degree6_cx26", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx26 - Degree 6"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree6_cx26));

        // Cy26 - degree 6
        a_tdeAnamorphicStdDeg6_degree6_cy26 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree6_cy26",
            "tdeAnamorphicStdDeg6_degree6_cy26", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy26 - Degree 6"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree6_cy26));

        // Cx46 - degree 6
        a_tdeAnamorphicStdDeg6_degree6_cx46 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree6_cx46",
            "tdeAnamorphicStdDeg6_degree6_cx46", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx46 - Degree 6"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree6_cx46));

        // Cy46 - degree 6
        a_tdeAnamorphicStdDeg6_degree6_cy46 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree6_cy46",
            "tdeAnamorphicStdDeg6_degree6_cy46", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy46 - Degree 6"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree6_cy46));

        // Cx66 - degree 6
        a_tdeAnamorphicStdDeg6_degree6_cx66 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree6_cx66",
            "tdeAnamorphicStdDeg6_degree6_cx66", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx66 - Degree 6"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree6_cx66));

        // Cy66 - degree 6
        a_tdeAnamorphicStdDeg6_degree6_cy66 = numericAttr.create(
            "tdeAnamorphicStdDeg6_degree6_cy66",
            "tdeAnamorphicStdDeg6_degree6_cy66", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy66 - Degree 6"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_degree6_cy66));

        // Lens Rotation
        a_tdeAnamorphicStdDeg6_lensRotation = numericAttr.create(
            "tdeAnamorphicStdDeg6_lensRotation",
            "tdeAnamorphicStdDeg6_lensRotation", MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-2.0));
        CHECK_MSTATUS(numericAttr.setSoftMax(2.0));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Lens Rotation"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_lensRotation));

        // Squeeze X
        a_tdeAnamorphicStdDeg6_squeeze_x = numericAttr.create(
            "tdeAnamorphicStdDeg6_squeeze_x", "tdeAnamorphicStdDeg6_squeeze_x",
            MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(0.9));
        CHECK_MSTATUS(numericAttr.setSoftMax(1.1));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Squeeze-X"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_squeeze_x));

        // Squeeze Y
        a_tdeAnamorphicStdDeg6_squeeze_y = numericAttr.create(
            "tdeAnamorphicStdDeg6_squeeze_y", "tdeAnamorphicStdDeg6_squeeze_y",
            MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(0.9));
        CHECK_MSTATUS(numericAttr.setSoftMax(1.1));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Squeeze-Y"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_squeeze_y));

        // Rescale
        a_tdeAnamorphicStdDeg6_rescale = numericAttr.create(
            "tdeAnamorphicStdDeg6_rescale", "tdeAnamorphicStdDeg6_rescale",
            MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(0.25));
        CHECK_MSTATUS(numericAttr.setSoftMax(4.0));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Rescale"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicStdDeg6_rescale));
    }

    // Out Lens
    a_outLens = typedAttr.create("outLens", "olns", data_type_id);
    CHECK_MSTATUS(typedAttr.setStorable(false));
    CHECK_MSTATUS(typedAttr.setKeyable(false));
    CHECK_MSTATUS(typedAttr.setReadable(true));
    CHECK_MSTATUS(typedAttr.setWritable(false));
    CHECK_MSTATUS(addAttribute(a_outLens));

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(a_inLens);
    inputAttrs.append(a_enable);
    inputAttrs.append(a_lensModel);

    inputAttrs.append(a_tdeClassic_distortion);
    inputAttrs.append(a_tdeClassic_anamorphicSqueeze);
    inputAttrs.append(a_tdeClassic_curvatureX);
    inputAttrs.append(a_tdeClassic_curvatureY);
    inputAttrs.append(a_tdeClassic_quarticDistortion);

    inputAttrs.append(a_tdeRadialStdDeg4_degree2_distortion);
    inputAttrs.append(a_tdeRadialStdDeg4_degree2_u);
    inputAttrs.append(a_tdeRadialStdDeg4_degree2_v);
    inputAttrs.append(a_tdeRadialStdDeg4_degree4_distortion);
    inputAttrs.append(a_tdeRadialStdDeg4_degree4_u);
    inputAttrs.append(a_tdeRadialStdDeg4_degree4_v);
    inputAttrs.append(a_tdeRadialStdDeg4_cylindricDirection);
    inputAttrs.append(a_tdeRadialStdDeg4_cylindricBending);

    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree2_cx02);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree2_cy02);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree2_cx22);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree2_cy22);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree4_cx04);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree4_cy04);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree4_cx24);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree4_cy24);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree4_cx44);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_degree4_cy44);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_lensRotation);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_squeeze_x);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_squeeze_y);
    inputAttrs.append(a_tdeAnamorphicStdDeg4_rescale);

    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree2_cx02);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree2_cy02);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree2_cx22);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree2_cy22);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree4_cx04);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree4_cy04);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree4_cx24);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree4_cy24);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree4_cx44);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree4_cy44);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree6_cx06);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree6_cy06);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree6_cx26);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree6_cy26);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree6_cx46);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree6_cy46);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree6_cx66);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_degree6_cy66);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_lensRotation);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_squeeze_x);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_squeeze_y);
    inputAttrs.append(a_tdeAnamorphicStdDeg6_rescale);

    MObjectArray outputAttrs;
    outputAttrs.append(a_outLens);

    CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return MS::kSuccess;
}

}  // namespace mmsolver
