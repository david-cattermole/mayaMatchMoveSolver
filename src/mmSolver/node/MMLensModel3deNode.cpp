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
#include <cstring>
#include <cmath>
#include <algorithm>

// Maya
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnPluginData.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MTypeId.h>

// MM Solver
#include "MMLensData.h"
#include "mmSolver/lens/lens_model_3de_classic.h"
#include "mmSolver/lens/lens_model_3de_anamorphic_deg_4_rotate_squeeze_xy.h"
#include "mmSolver/lens/lens_model_3de_radial_decentered_deg_4_cylindric.h"
#include "mmSolver/lens/lens_model.h"
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

MObject MMLensModel3deNode::a_tdeClassic_distortion;
MObject MMLensModel3deNode::a_tdeClassic_anamorphicSqueeze;
MObject MMLensModel3deNode::a_tdeClassic_curvatureX;
MObject MMLensModel3deNode::a_tdeClassic_curvatureY;
MObject MMLensModel3deNode::a_tdeClassic_quarticDistortion;

MObject MMLensModel3deNode::a_tdeRadialDecenteredDeg4Cylindric_degree2_distortion;
MObject MMLensModel3deNode::a_tdeRadialDecenteredDeg4Cylindric_degree2_u;
MObject MMLensModel3deNode::a_tdeRadialDecenteredDeg4Cylindric_degree2_v;
MObject MMLensModel3deNode::a_tdeRadialDecenteredDeg4Cylindric_degree4_distortion;
MObject MMLensModel3deNode::a_tdeRadialDecenteredDeg4Cylindric_degree4_u;
MObject MMLensModel3deNode::a_tdeRadialDecenteredDeg4Cylindric_degree4_v;
MObject MMLensModel3deNode::a_tdeRadialDecenteredDeg4Cylindric_cylindricDirection;
MObject MMLensModel3deNode::a_tdeRadialDecenteredDeg4Cylindric_cylindricBending;

MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx02;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy02;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx22;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy22;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx04;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy04;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx24;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy24;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx44;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy44;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_lensRotation;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_x;
MObject MMLensModel3deNode::a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_y;

// Output Attributes
MObject MMLensModel3deNode::a_outLens;


MMLensModel3deNode::MMLensModel3deNode() {}

MMLensModel3deNode::~MMLensModel3deNode() {}

MString MMLensModel3deNode::nodeName() {
    return MString("mmLensModel3de");
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
        const auto lensModelType = static_cast<LensModelType>(lensModelNum);

        // Create initial plug-in data structure. We don't need to
        // 'new' the data type directly.
        MFnPluginData fnPluginData;
        MTypeId data_type_id(MM_LENS_DATA_TYPE_ID);
        fnPluginData.create(data_type_id, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Get Input Lens
        MDataHandle inLensHandle = data.inputValue(a_inLens, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMLensData* inputLensData = (MMLensData*) inLensHandle.asPluginData();
        std::shared_ptr<LensModel> inputLensModel;
        if (inputLensData != nullptr) {
            inputLensModel = inputLensData->getValue();
        }

        // Output Lens
        MDataHandle outLensHandle = data.outputValue(a_outLens);
        MMLensData* newLensData = (MMLensData*) fnPluginData.data(&status);
        if (enable) {
            if (lensModelType == LensModelType::k3deClassic) {
                MDataHandle k1Handle = data.inputValue(a_tdeClassic_distortion, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle squeezeHandle = data.inputValue(a_tdeClassic_anamorphicSqueeze, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle cxHandle = data.inputValue(a_tdeClassic_curvatureX, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle cyHandle = data.inputValue(a_tdeClassic_curvatureY, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle k2Handle = data.inputValue(a_tdeClassic_quarticDistortion, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                double distortion = k1Handle.asDouble();
                double anamorphicSqueeze = squeezeHandle.asDouble();
                double curvatureX = cxHandle.asDouble();
                double curvatureY = cyHandle.asDouble();
                double quarticDistortion = k2Handle.asDouble();

                // Create a lens distortion function to be passed to the
                // MMLensData.
                auto newLensModel =
                    std::shared_ptr<LensModel3deClassic>(new LensModel3deClassic());

                // Connect the input lens to the newly created lens object.
                newLensModel->setInputLensModel(inputLensModel);
                newLensModel->setDistortion(distortion);
                newLensModel->setAnamorphicSqueeze(anamorphicSqueeze);
                newLensModel->setCurvatureX(curvatureX);
                newLensModel->setCurvatureY(curvatureY);
                newLensModel->setQuarticDistortion(quarticDistortion);

                newLensData->setValue(newLensModel);

            } else if (lensModelType == LensModelType::k3deRadialDecenteredDeg4Cylindric) {
                MDataHandle deg2DistortionHandle = data.inputValue(a_tdeRadialDecenteredDeg4Cylindric_degree2_distortion, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle deg2UHandle = data.inputValue(a_tdeRadialDecenteredDeg4Cylindric_degree2_u, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle deg2VHandle = data.inputValue(a_tdeRadialDecenteredDeg4Cylindric_degree2_v, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                MDataHandle deg4DistortionHandle = data.inputValue(a_tdeRadialDecenteredDeg4Cylindric_degree4_distortion, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle deg4UHandle = data.inputValue(a_tdeRadialDecenteredDeg4Cylindric_degree4_u, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle deg4VHandle = data.inputValue(a_tdeRadialDecenteredDeg4Cylindric_degree4_v, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                MDataHandle cylindricDirHandle = data.inputValue(a_tdeRadialDecenteredDeg4Cylindric_cylindricDirection, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle cylindricBendHandle = data.inputValue(a_tdeRadialDecenteredDeg4Cylindric_cylindricBending, &status);
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
                auto newLensModel = std::shared_ptr<LensModel3deRadialDecenteredDeg4Cylindric>(
                    new LensModel3deRadialDecenteredDeg4Cylindric());

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

            } else if (lensModelType == LensModelType::k3deAnamorphicDeg4RotateSqueezeXY) {
                MDataHandle deg2Cx02Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx02, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle deg2Cy02Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy02, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                MDataHandle deg2Cx22Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx22, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle deg2Cy22Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy22, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                MDataHandle deg4Cx04Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx04, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle deg4Cy04Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy04, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                MDataHandle deg4Cx24Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx24, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle deg4Cy24Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy24, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                MDataHandle deg4Cx44Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx44, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle deg4Cy44Handle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy44, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                MDataHandle lensRotationHandle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_lensRotation, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle squeezeXHandle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_x, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                MDataHandle squeezeYHandle = data.inputValue(a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_y, &status);
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

                // Create a lens distortion function to be passed to the
                // MMLensData.
                auto newLensModel = std::shared_ptr<LensModel3deAnamorphicDeg4RotateSqueezeXY>(
                    new LensModel3deAnamorphicDeg4RotateSqueezeXY());

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

            } else {
                MMSOLVER_ERR(
                    "LensModelType value is invalid: nodeName=" << name().asChar()
                    << " lensModelType=" << static_cast<int>(lensModelType));
            }
        } else {
            newLensData->setValue(nullptr);
        }
        outLensHandle.setMPxData(newLensData);
        outLensHandle.setClean();
        status = MS::kSuccess;
    }

    return status;
}

void *MMLensModel3deNode::creator() {
    return (new MMLensModel3deNode());
}

MStatus MMLensModel3deNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnEnumAttribute enumAttr;
    MFnTypedAttribute typedAttr;

    // In Lens
    MTypeId data_type_id(MM_LENS_DATA_TYPE_ID);
    a_inLens = typedAttr.create(
        "inLens", "ilns",
        data_type_id);
    CHECK_MSTATUS(typedAttr.setStorable(false));
    CHECK_MSTATUS(typedAttr.setKeyable(false));
    CHECK_MSTATUS(typedAttr.setReadable(true));
    CHECK_MSTATUS(typedAttr.setWritable(true));
    CHECK_MSTATUS(addAttribute(a_inLens));

    // Enable
    a_enable = numericAttr.create(
        "enable", "enb",
        MFnNumericData::kBoolean, true);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_enable));

    // Lens Model
    auto defaultLensModel = static_cast<short>(LensModelType::k3deRadialDecenteredDeg4Cylindric);
    a_lensModel = enumAttr.create(
        "lensModel", "lnsmdl", defaultLensModel, &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(enumAttr.addField(
                      "3DE Classic LD Model",
                      static_cast<short>(LensModelType::k3deClassic)));
    CHECK_MSTATUS(enumAttr.addField(
                      "3DE4 Radial - Standard, Degree 4",
                      static_cast<short>(LensModelType::k3deRadialDecenteredDeg4Cylindric)));
    CHECK_MSTATUS(enumAttr.addField(
                      "3DE4 Anamorphic - Standard, Degree 4",
                      static_cast<short>(LensModelType::k3deAnamorphicDeg4RotateSqueezeXY)));
//     CHECK_MSTATUS(enumAttr.addField(
//             "3DE4 Anamorphic - Rescaled, Degree 4",
//             static_cast<short>(LensModelType::k3deClassic)));
//     CHECK_MSTATUS(enumAttr.addField(
//             "3DE4 Anamorphic, Degree 6",
//             static_cast<short>(LensModelType::k3deClassic)));
    CHECK_MSTATUS(enumAttr.setStorable(true));
    CHECK_MSTATUS(enumAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_lensModel));

    // 3DE Classic
    {
        a_tdeClassic_distortion = numericAttr.create(
            "tdeClassic_distortion",
            "tdeClassic_distortion",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Distortion"));
        CHECK_MSTATUS(addAttribute(a_tdeClassic_distortion));

        // Anamorphic Squeeze
        a_tdeClassic_anamorphicSqueeze = numericAttr.create(
            "tdeClassic_anamorphicSqueeze",
            "tdeClassic_anamorphicSqueeze",
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
        a_tdeClassic_curvatureX = numericAttr.create(
            "tdeClassic_curvatureX",
            "tdeClassic_curvatureX",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Curvature X"));
        CHECK_MSTATUS(addAttribute(a_tdeClassic_curvatureX));

        // Curvature Y
        a_tdeClassic_curvatureY = numericAttr.create(
            "tdeClassic_curvatureY",
            "tdeClassic_curvatureY",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Curvature Y"));
        CHECK_MSTATUS(addAttribute(a_tdeClassic_curvatureY));

        // Quartic Distortion
        a_tdeClassic_quarticDistortion = numericAttr.create(
            "tdeClassic_quarticDistortion",
            "tdeClassic_quarticDistortion",
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
        // Distortion - Degree 2
        a_tdeRadialDecenteredDeg4Cylindric_degree2_distortion = numericAttr.create(
            "tdeRadialDecenteredDeg4Cylindric_degree2_distortion",
            "tdeRadialDecenteredDeg4Cylindric_degree2_distortion",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Distortion - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialDecenteredDeg4Cylindric_degree2_distortion));

        // U - Degree 2
        a_tdeRadialDecenteredDeg4Cylindric_degree2_u = numericAttr.create(
            "tdeRadialDecenteredDeg4Cylindric_degree2_u",
            "tdeRadialDecenteredDeg4Cylindric_degree2_u",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("U - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialDecenteredDeg4Cylindric_degree2_u));

        // V - Degree 2
        a_tdeRadialDecenteredDeg4Cylindric_degree2_v = numericAttr.create(
            "tdeRadialDecenteredDeg4Cylindric_degree2_v",
            "tdeRadialDecenteredDeg4Cylindric_degree2_v",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("V - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialDecenteredDeg4Cylindric_degree2_v));

        // Distortion - Degree 4
        a_tdeRadialDecenteredDeg4Cylindric_degree4_distortion = numericAttr.create(
            "tdeRadialDecenteredDeg4Cylindric_degree4_distortion",
            "tdeRadialDecenteredDeg4Cylindric_degree4_distortion",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Distortion - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialDecenteredDeg4Cylindric_degree4_distortion));

        // U - Degree 4
        a_tdeRadialDecenteredDeg4Cylindric_degree4_u = numericAttr.create(
            "tdeRadialDecenteredDeg4Cylindric_degree4_u",
            "tdeRadialDecenteredDeg4Cylindric_degree4_u",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("U - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialDecenteredDeg4Cylindric_degree4_u));

        // V - Degree 4
        a_tdeRadialDecenteredDeg4Cylindric_degree4_v = numericAttr.create(
            "tdeRadialDecenteredDeg4Cylindric_degree4_v",
            "tdeRadialDecenteredDeg4Cylindric_degree4_v",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("V - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialDecenteredDeg4Cylindric_degree4_v));

        // Phi - Cylindric Direction
        a_tdeRadialDecenteredDeg4Cylindric_cylindricDirection = numericAttr.create(
            "tdeRadialDecenteredDeg4Cylindric_cylindricDirection",
            "tdeRadialDecenteredDeg4Cylindric_cylindricDirection",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-90.0));
        CHECK_MSTATUS(numericAttr.setSoftMax(90.0));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Phi - Cylindric Direction"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialDecenteredDeg4Cylindric_cylindricDirection));

        // B - Cylindric Bending
        a_tdeRadialDecenteredDeg4Cylindric_cylindricBending = numericAttr.create(
            "tdeRadialDecenteredDeg4Cylindric_cylindricBending",
            "tdeRadialDecenteredDeg4Cylindric_cylindricBending",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.1));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.1));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("B - Cylindric Bending"));
        CHECK_MSTATUS(addAttribute(a_tdeRadialDecenteredDeg4Cylindric_cylindricBending));
    }

    // 3DE Anamorphic - Standard, Degree 4
    {
        // Cx02 - Degree 2
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx02 = numericAttr.create(
                "tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx02",
                "tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx02",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx02 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx02));

        // Cy02 - Degree 2
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy02 = numericAttr.create(
                "tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy02",
                "tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy02",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy02 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy02));

        // Cx22 - Degree 2
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx22 = numericAttr.create(
                "tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx22",
                "tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx22",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx22 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx22));

        // Cy22 - Degree 2
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy22 = numericAttr.create(
                "tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy22",
                "tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy22",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy22 - Degree 2"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy22));

        // Cx04 - Degree 4
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx04 = numericAttr.create(
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx04",
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx04",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx04 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx04));

        // Cy04 - Degree 4
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy04 = numericAttr.create(
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy04",
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy04",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy04 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy04));

        // Cx24 - Degree 4
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx24 = numericAttr.create(
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx24",
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx24",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx24 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx24));

        // Cy24 - Degree 4
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy24 = numericAttr.create(
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy24",
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy24",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy24 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy24));

        // Cx44 - Degree 4
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx44 = numericAttr.create(
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx44",
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx44",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cx44 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx44));

        // Cy44 - Degree 4
        a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy44 = numericAttr.create(
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy44",
            "tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy44",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-0.5));
        CHECK_MSTATUS(numericAttr.setSoftMax(0.5));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Cy44 - Degree 4"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy44));

        // Lens Rotation
        a_tdeAnamorphicDeg4RotateSqueezeXY_lensRotation = numericAttr.create(
            "tdeAnamorphicDeg4RotateSqueezeXY_lensRotation",
            "tdeAnamorphicDeg4RotateSqueezeXY_lensRotation",
            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(-2.0));
        CHECK_MSTATUS(numericAttr.setSoftMax(2.0));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Lens Rotation"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_lensRotation));

        // Squeeze X
        a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_x = numericAttr.create(
                "tdeAnamorphicDeg4RotateSqueezeXY_squeeze_x",
                "tdeAnamorphicDeg4RotateSqueezeXY_squeeze_x",
                MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(0.9));
        CHECK_MSTATUS(numericAttr.setSoftMax(1.1));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Squeeze-X"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_x));

        // Squeeze Y
        a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_y = numericAttr.create(
                "tdeAnamorphicDeg4RotateSqueezeXY_squeeze_y",
                "tdeAnamorphicDeg4RotateSqueezeXY_squeeze_y",
                MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(numericAttr.setSoftMin(0.9));
        CHECK_MSTATUS(numericAttr.setSoftMax(1.1));
        CHECK_MSTATUS(numericAttr.setNiceNameOverride("Squeeze-Y"));
        CHECK_MSTATUS(addAttribute(a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_y));
    }

    // Out Lens
    a_outLens = typedAttr.create(
        "outLens", "olns",
        data_type_id);
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

    inputAttrs.append(a_tdeRadialDecenteredDeg4Cylindric_degree2_distortion);
    inputAttrs.append(a_tdeRadialDecenteredDeg4Cylindric_degree2_u);
    inputAttrs.append(a_tdeRadialDecenteredDeg4Cylindric_degree2_v);
    inputAttrs.append(a_tdeRadialDecenteredDeg4Cylindric_degree4_distortion);
    inputAttrs.append(a_tdeRadialDecenteredDeg4Cylindric_degree4_u);
    inputAttrs.append(a_tdeRadialDecenteredDeg4Cylindric_degree4_v);
    inputAttrs.append(a_tdeRadialDecenteredDeg4Cylindric_cylindricDirection);
    inputAttrs.append(a_tdeRadialDecenteredDeg4Cylindric_cylindricBending);

    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx02);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy02);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cx22);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree2_cy22);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx04);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy04);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx24);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy24);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cx44);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_degree4_cy44);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_lensRotation);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_x);
    inputAttrs.append(a_tdeAnamorphicDeg4RotateSqueezeXY_squeeze_y);

    MObjectArray outputAttrs;
    outputAttrs.append(a_outLens);

    CHECK_MSTATUS(MMNodeInitUtils::attributeAffectsMulti(
                      inputAttrs,
                      outputAttrs));

    return MS::kSuccess;
}

} // namespace mmsolver
