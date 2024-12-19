# Copyright (C) 2022, 2024 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Contains constant values for the Load Lens tool.
"""

# TODO: Add fisheye lens distortion.
# TODO: Add anamorphic standard degree 6 lens distortion model.

# Maya node types
MAYA_MM_LENS_MODEL_3DE = 'mmLensModel3de'


# Nuke node types.
NUKE_3DE4_CLASSIC = 'LD_3DE_Classic_LD_Model'
NUKE_3DE4_RADIAL_STD_DEG4 = 'LD_3DE4_Radial_Standard_Degree_4'
NUKE_3DE4_ANAMORPHIC_STD_DEG4 = 'LD_3DE4_Anamorphic_Standard_Degree_4'
NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED = 'LD_3DE4_Anamorphic_Rescaled_Degree_4'
NUKE_3DE4_ANAMORPHIC_STD_DEG6 = 'LD_3DE4_Anamorphic_Standard_Degree_6'
NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED = 'LD_3DE4_Anamorphic_Rescaled_Degree_6'
NUKE_3DE4_ANAMORPHIC_DEG6 = 'LD_3DE4_Anamorphic_Degree_6'


# Lens Model values
LENS_MODEL_UNINITIALIZED_VALUE = 0
LENS_MODEL_PASSTHROUGH_VALUE = 1
LENS_MODEL_3DE4_CLASSIC_VALUE = 2
LENS_MODEL_3DE4_RADIAL_STANDARD_DEG4_VALUE = 3
LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG4_VALUE = 4
LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG4_RESCALED_VALUE = 5
LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG6_VALUE = 6
LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG6_RESCALED_VALUE = 7
LENS_MODEL_3DE4_ANAMORPHIC_DEG6_VALUE = 8  # Currently unsupported.


NUKE_NODE_TYPE_TO_NODE_TYPE_TO_LENS_MODEL_VALUE = {
    NUKE_3DE4_CLASSIC: {MAYA_MM_LENS_MODEL_3DE: LENS_MODEL_3DE4_CLASSIC_VALUE},
    NUKE_3DE4_RADIAL_STD_DEG4: {
        MAYA_MM_LENS_MODEL_3DE: LENS_MODEL_3DE4_RADIAL_STANDARD_DEG4_VALUE,
    },
    NUKE_3DE4_ANAMORPHIC_STD_DEG4: {
        MAYA_MM_LENS_MODEL_3DE: LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG4_VALUE,
    },
    NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: {
        MAYA_MM_LENS_MODEL_3DE: LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG4_RESCALED_VALUE,
    },
    NUKE_3DE4_ANAMORPHIC_DEG6: {
        MAYA_MM_LENS_MODEL_3DE: LENS_MODEL_3DE4_ANAMORPHIC_DEG6_VALUE,
    },
    NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: {
        MAYA_MM_LENS_MODEL_3DE: LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG6_RESCALED_VALUE,
    },
}


NODE_TYPE_TO_LENS_MODEL_VALUE_TO_NUKE_NODE_TYPE = {
    MAYA_MM_LENS_MODEL_3DE: {
        LENS_MODEL_3DE4_CLASSIC_VALUE: NUKE_3DE4_CLASSIC,
        LENS_MODEL_3DE4_RADIAL_STANDARD_DEG4_VALUE: NUKE_3DE4_RADIAL_STD_DEG4,
        LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG4_VALUE: NUKE_3DE4_ANAMORPHIC_STD_DEG4,
        LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG4_RESCALED_VALUE: NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED,
        LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG6_VALUE: NUKE_3DE4_ANAMORPHIC_STD_DEG6,
        LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG6_RESCALED_VALUE: NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED,
        LENS_MODEL_3DE4_ANAMORPHIC_DEG6_VALUE: NUKE_3DE4_ANAMORPHIC_DEG6,
    },
}


NODE_TYPE_PARAMETER_NAME_TO_ATTRIBUTE_NAMES = {
    # NUKE_3DE4_CLASSIC
    (NUKE_3DE4_CLASSIC, 'Distortion'): [
        'tdeClassic_distortion',
    ],
    (NUKE_3DE4_CLASSIC, 'Anamorphic_Squeeze'): [
        'tdeClassic_anamorphicSqueeze',
    ],
    (NUKE_3DE4_CLASSIC, 'Curvature_X'): [
        'tdeClassic_curvatureX',
    ],
    (NUKE_3DE4_CLASSIC, 'Curvature_Y'): [
        'tdeClassic_curvatureY',
    ],
    (NUKE_3DE4_CLASSIC, 'Quartic_Distortion'): [
        'tdeClassic_quarticDistortion',
    ],
    # NUKE_3DE4_RADIAL_STD_DEG4
    (NUKE_3DE4_RADIAL_STD_DEG4, 'Distortion_Degree_2'): [
        'tdeRadialStdDeg4_degree2_distortion',
    ],
    (NUKE_3DE4_RADIAL_STD_DEG4, 'U_Degree_2'): [
        'tdeRadialStdDeg4_degree2_u',
    ],
    (NUKE_3DE4_RADIAL_STD_DEG4, 'V_Degree_2'): [
        'tdeRadialStdDeg4_degree2_v',
    ],
    (NUKE_3DE4_RADIAL_STD_DEG4, 'Quartic_Distortion_Degree_4'): [
        'tdeRadialStdDeg4_degree4_distortion',
    ],
    (NUKE_3DE4_RADIAL_STD_DEG4, 'U_Degree_4'): [
        'tdeRadialStdDeg4_degree4_u',
    ],
    (NUKE_3DE4_RADIAL_STD_DEG4, 'V_Degree_4'): [
        'tdeRadialStdDeg4_degree4_v',
    ],
    (NUKE_3DE4_RADIAL_STD_DEG4, 'Phi_Cylindric_Direction'): [
        'tdeRadialStdDeg4_cylindricDirection',
    ],
    (NUKE_3DE4_RADIAL_STD_DEG4, 'B_Cylindric_Bending'): [
        'tdeRadialStdDeg4_cylindricBending',
    ],
    # NUKE_3DE4_ANAMORPHIC_STD_DEG4
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cx02_Degree_2'): [
        'tdeAnamorphicStdDeg4_degree2_cx02',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cy02_Degree_2'): [
        'tdeAnamorphicStdDeg4_degree2_cy02',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cx22_Degree_2'): [
        'tdeAnamorphicStdDeg4_degree2_cx22',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cy22_Degree_2'): [
        'tdeAnamorphicStdDeg4_degree2_cy22',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cx04_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cx04',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cy04_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cy04',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cx24_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cx24',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cy24_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cy24',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cx44_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cx44',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Cy44_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cy44',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Lens_Rotation'): [
        'tdeAnamorphicStdDeg4_lensRotation',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Squeeze_X'): [
        'tdeAnamorphicStdDeg4_squeeze_x',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4, 'Squeeze_Y'): [
        'tdeAnamorphicStdDeg4_squeeze_y',
    ],
    # NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cx02_Degree_2'): [
        'tdeAnamorphicStdDeg4_degree2_cx02',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cy02_Degree_2'): [
        'tdeAnamorphicStdDeg4_degree2_cy02',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cx22_Degree_2'): [
        'tdeAnamorphicStdDeg4_degree2_cx22',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cy22_Degree_2'): [
        'tdeAnamorphicStdDeg4_degree2_cy22',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cx04_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cx04',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cy04_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cy04',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cx24_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cx24',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cy24_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cy24',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cx44_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cx44',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Cy44_Degree_4'): [
        'tdeAnamorphicStdDeg4_degree4_cy44',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Lens_Rotation'): [
        'tdeAnamorphicStdDeg4_lensRotation',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Squeeze_X'): [
        'tdeAnamorphicStdDeg4_squeeze_x',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Squeeze_Y'): [
        'tdeAnamorphicStdDeg4_squeeze_y',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED, 'Rescale'): [
        'tdeAnamorphicStdDeg4_rescale',
    ],
    # NUKE_3DE4_ANAMORPHIC_STD_DEG6
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cx02_Degree_2'): [
        'tdeAnamorphicStdDeg6_degree2_cx02',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cy02_Degree_2'): [
        'tdeAnamorphicStdDeg6_degree2_cy02',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cx22_Degree_2'): [
        'tdeAnamorphicStdDeg6_degree2_cx22',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cy22_Degree_2'): [
        'tdeAnamorphicStdDeg6_degree2_cy22',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cx04_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cx04',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cy04_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cy04',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cx24_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cx24',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cy24_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cy24',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cx44_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cx44',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cy44_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cy44',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cx06_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cx06',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cy06_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cy06',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cx26_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cx26',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cy26_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cy26',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cx46_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cx46',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cy46_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cy46',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cx66_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cx66',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Cy66_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cy66',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Lens_Rotation'): [
        'tdeAnamorphicStdDeg6_lensRotation',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Squeeze_X'): [
        'tdeAnamorphicStdDeg6_squeeze_x',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6, 'Squeeze_Y'): [
        'tdeAnamorphicStdDeg6_squeeze_y',
    ],
    # NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cx02_Degree_2'): [
        'tdeAnamorphicStdDeg6_degree2_cx02',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cy02_Degree_2'): [
        'tdeAnamorphicStdDeg6_degree2_cy02',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cx22_Degree_2'): [
        'tdeAnamorphicStdDeg6_degree2_cx22',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cy22_Degree_2'): [
        'tdeAnamorphicStdDeg6_degree2_cy22',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cx04_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cx04',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cy04_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cy04',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cx24_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cx24',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cy24_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cy24',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cx44_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cx44',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cy44_Degree_4'): [
        'tdeAnamorphicStdDeg6_degree4_cy44',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cx06_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cx06',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cy06_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cy06',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cx26_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cx26',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cy26_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cy26',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cx46_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cx46',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cy46_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cy46',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cx66_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cx66',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Cy66_Degree_6'): [
        'tdeAnamorphicStdDeg6_degree6_cy66',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Lens_Rotation'): [
        'tdeAnamorphicStdDeg6_lensRotation',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Squeeze_X'): [
        'tdeAnamorphicStdDeg6_squeeze_x',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Squeeze_Y'): [
        'tdeAnamorphicStdDeg6_squeeze_y',
    ],
    (NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED, 'Rescale'): [
        'tdeAnamorphicStdDeg6_rescale',
    ],
    # NUKE_3DE4_ANAMORPHIC_DEG6
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cx02_Degree_2'): [
        'tdeAnamorphicDeg6_degree2_cx02',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cy02_Degree_2'): [
        'tdeAnamorphicDeg6_degree2_cy02',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cx22_Degree_2'): [
        'tdeAnamorphicDeg6_degree2_cx22',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cy22_Degree_2'): [
        'tdeAnamorphicDeg6_degree2_cy22',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cx04_Degree_4'): [
        'tdeAnamorphicDeg6_degree4_cx04',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cy04_Degree_4'): [
        'tdeAnamorphicDeg6_degree4_cy04',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cx24_Degree_4'): [
        'tdeAnamorphicDeg6_degree4_cx24',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cy24_Degree_4'): [
        'tdeAnamorphicDeg6_degree4_cy24',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cx44_Degree_4'): [
        'tdeAnamorphicDeg6_degree4_cx44',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cy44_Degree_4'): [
        'tdeAnamorphicDeg6_degree4_cy44',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cx06_Degree_6'): [
        'tdeAnamorphicDeg6_degree6_cx06',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cy06_Degree_6'): [
        'tdeAnamorphicDeg6_degree6_cy06',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cx26_Degree_6'): [
        'tdeAnamorphicDeg6_degree6_cx26',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cy26_Degree_6'): [
        'tdeAnamorphicDeg6_degree6_cy26',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cx46_Degree_6'): [
        'tdeAnamorphicDeg6_degree6_cx46',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cy46_Degree_6'): [
        'tdeAnamorphicDeg6_degree6_cy46',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cx66_Degree_6'): [
        'tdeAnamorphicDeg6_degree6_cx66',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG6, 'Cy66_Degree_6'): [
        'tdeAnamorphicDeg6_degree6_cy66',
    ],
}


ATTR_NAME_TO_NUKE_NODE_TYPE_AND_KNOB_NAME = {
    # NUKE_3DE4_*
    # TODO: Add 'tde4_pixel_aspect' for the Pixel Aspect Ratio.
    'focalLength': {
        NUKE_3DE4_CLASSIC: 'tde4_focal_length_cm',
        NUKE_3DE4_RADIAL_STD_DEG4: 'tde4_focal_length_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'tde4_focal_length_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'tde4_focal_length_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'tde4_focal_length_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'tde4_focal_length_cm',
        NUKE_3DE4_ANAMORPHIC_DEG6: 'tde4_focal_length_cm',
    },
    'focusDistance': {
        NUKE_3DE4_CLASSIC: 'tde4_custom_focus_distance_cm',
        NUKE_3DE4_RADIAL_STD_DEG4: 'tde4_custom_focus_distance_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'tde4_custom_focus_distance_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'tde4_custom_focus_distance_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'tde4_custom_focus_distance_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'tde4_custom_focus_distance_cm',
        NUKE_3DE4_ANAMORPHIC_DEG6: 'tde4_custom_focus_distance_cm',
    },
    'horizontalFilmAperture': {
        NUKE_3DE4_CLASSIC: 'tde4_filmback_width_cm',
        NUKE_3DE4_RADIAL_STD_DEG4: 'tde4_filmback_width_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'tde4_filmback_width_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'tde4_filmback_width_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'tde4_filmback_width_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'tde4_filmback_width_cm',
        NUKE_3DE4_ANAMORPHIC_DEG6: 'tde4_filmback_width_cm',
    },
    'verticalFilmAperture': {
        NUKE_3DE4_CLASSIC: 'tde4_filmback_height_cm',
        NUKE_3DE4_RADIAL_STD_DEG4: 'tde4_filmback_height_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'tde4_filmback_height_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'tde4_filmback_height_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'tde4_filmback_height_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'tde4_filmback_height_cm',
        NUKE_3DE4_ANAMORPHIC_DEG6: 'tde4_filmback_height_cm',
    },
    'horizontalFilmOffset': {
        NUKE_3DE4_CLASSIC: 'tde4_lens_center_offset_x_cm',
        NUKE_3DE4_RADIAL_STD_DEG4: 'tde4_lens_center_offset_x_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'tde4_lens_center_offset_x_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'tde4_lens_center_offset_x_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'tde4_lens_center_offset_x_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'tde4_lens_center_offset_x_cm',
        NUKE_3DE4_ANAMORPHIC_DEG6: 'tde4_lens_center_offset_x_cm',
    },
    'verticalFilmOffset': {
        NUKE_3DE4_CLASSIC: 'tde4_lens_center_offset_y_cm',
        NUKE_3DE4_RADIAL_STD_DEG4: 'tde4_lens_center_offset_y_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'tde4_lens_center_offset_y_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'tde4_lens_center_offset_y_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'tde4_lens_center_offset_y_cm',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'tde4_lens_center_offset_y_cm',
        NUKE_3DE4_ANAMORPHIC_DEG6: 'tde4_lens_center_offset_y_cm',
    },
    # NUKE_3DE4_CLASSIC
    'tdeClassic_distortion': {NUKE_3DE4_CLASSIC: 'Distortion'},
    'tdeClassic_anamorphicSqueeze': {NUKE_3DE4_CLASSIC: 'Anamorphic_Squeeze'},
    'tdeClassic_curvatureX': {NUKE_3DE4_CLASSIC: 'Curvature_X'},
    'tdeClassic_curvatureY': {NUKE_3DE4_CLASSIC: 'Curvature_Y'},
    'tdeClassic_quarticDistortion': {NUKE_3DE4_CLASSIC: 'Quartic_Distortion'},
    # NUKE_3DE4_RADIAL_STD_DEG4
    'tdeRadialStdDeg4_degree2_distortion': {
        NUKE_3DE4_RADIAL_STD_DEG4: 'Distortion_Degree_2'
    },
    'tdeRadialStdDeg4_degree2_u': {NUKE_3DE4_RADIAL_STD_DEG4: 'U_Degree_2'},
    'tdeRadialStdDeg4_degree2_v': {NUKE_3DE4_RADIAL_STD_DEG4: 'V_Degree_2'},
    'tdeRadialStdDeg4_degree4_distortion': {
        NUKE_3DE4_RADIAL_STD_DEG4: 'Quartic_Distortion_Degree_4'
    },
    'tdeRadialStdDeg4_degree4_u': {NUKE_3DE4_RADIAL_STD_DEG4: 'U_Degree_4'},
    'tdeRadialStdDeg4_degree4_v': {NUKE_3DE4_RADIAL_STD_DEG4: 'V_Degree_4'},
    'tdeRadialStdDeg4_cylindricDirection': {
        NUKE_3DE4_RADIAL_STD_DEG4: 'Phi_Cylindric_Direction'
    },
    'tdeRadialStdDeg4_cylindricBending': {
        NUKE_3DE4_RADIAL_STD_DEG4: 'B_Cylindric_Bending'
    },
    # NUKE_3DE4_ANAMORPHIC_STD_DEG4 and NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED
    'tdeAnamorphicStdDeg4_degree2_cx02': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cx02_Degree_2',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cx02_Degree_2',
    },
    'tdeAnamorphicStdDeg4_degree2_cy02': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cy02_Degree_2',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cy02_Degree_2',
    },
    'tdeAnamorphicStdDeg4_degree2_cx22': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cx22_Degree_2',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cx22_Degree_2',
    },
    'tdeAnamorphicStdDeg4_degree2_cy22': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cy22_Degree_2',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cy22_Degree_2',
    },
    'tdeAnamorphicStdDeg4_degree4_cx04': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cx04_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cx04_Degree_4',
    },
    'tdeAnamorphicStdDeg4_degree4_cy04': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cy04_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cy04_Degree_4',
    },
    'tdeAnamorphicStdDeg4_degree4_cx24': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cx24_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cx24_Degree_4',
    },
    'tdeAnamorphicStdDeg4_degree4_cy24': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cy24_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cy24_Degree_4',
    },
    'tdeAnamorphicStdDeg4_degree4_cx44': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cx44_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cx44_Degree_4',
    },
    'tdeAnamorphicStdDeg4_degree4_cy44': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Cy44_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Cy44_Degree_4',
    },
    'tdeAnamorphicStdDeg4_lensRotation': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Lens_Rotation',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Lens_Rotation',
    },
    'tdeAnamorphicStdDeg4_squeeze_x': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Squeeze_X',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Squeeze_X',
    },
    'tdeAnamorphicStdDeg4_squeeze_y': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG4: 'Squeeze_Y',
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Squeeze_Y',
    },
    # NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED
    'tdeAnamorphicStdDeg4_rescale': {NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: 'Rescale'},
    # NUKE_3DE4_ANAMORPHIC_STD_DEG6 and NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED
    'tdeAnamorphicStdDeg6_degree2_cx02': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cx02_Degree_2',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cx02_Degree_2',
    },
    'tdeAnamorphicStdDeg6_degree2_cy02': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cy02_Degree_2',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cy02_Degree_2',
    },
    'tdeAnamorphicStdDeg6_degree2_cx22': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cx22_Degree_2',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cx22_Degree_2',
    },
    'tdeAnamorphicStdDeg6_degree2_cy22': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cy22_Degree_2',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cy22_Degree_2',
    },
    'tdeAnamorphicStdDeg6_degree4_cx04': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cx04_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cx04_Degree_4',
    },
    'tdeAnamorphicStdDeg6_degree4_cy04': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cy04_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cy04_Degree_4',
    },
    'tdeAnamorphicStdDeg6_degree4_cx24': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cx24_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cx24_Degree_4',
    },
    'tdeAnamorphicStdDeg6_degree4_cy24': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cy24_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cy24_Degree_4',
    },
    'tdeAnamorphicStdDeg6_degree4_cx44': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cx44_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cx44_Degree_4',
    },
    'tdeAnamorphicStdDeg6_degree4_cy44': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cy44_Degree_4',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cy44_Degree_4',
    },
    'tdeAnamorphicStdDeg6_degree6_cx06': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cx06_Degree_6',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cx06_Degree_6',
    },
    'tdeAnamorphicStdDeg6_degree6_cy06': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cy06_Degree_6',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cy06_Degree_6',
    },
    'tdeAnamorphicStdDeg6_degree6_cx26': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cx26_Degree_6',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cx26_Degree_6',
    },
    'tdeAnamorphicStdDeg6_degree6_cy26': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cy26_Degree_6',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cy26_Degree_6',
    },
    'tdeAnamorphicStdDeg6_degree6_cx46': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cx46_Degree_6',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cx46_Degree_6',
    },
    'tdeAnamorphicStdDeg6_degree6_cy46': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cy46_Degree_6',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cy46_Degree_6',
    },
    'tdeAnamorphicStdDeg6_degree6_cx66': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cx66_Degree_6',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cx66_Degree_6',
    },
    'tdeAnamorphicStdDeg6_degree6_cy66': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Cy66_Degree_6',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Cy66_Degree_6',
    },
    'tdeAnamorphicStdDeg6_lensRotation': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Lens_Rotation',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Lens_Rotation',
    },
    'tdeAnamorphicStdDeg6_squeeze_x': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Squeeze_X',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Squeeze_X',
    },
    'tdeAnamorphicStdDeg6_squeeze_y': {
        NUKE_3DE4_ANAMORPHIC_STD_DEG6: 'Squeeze_Y',
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Squeeze_Y',
    },
    # NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED
    'tdeAnamorphicStdDeg6_rescale': {NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: 'Rescale'},
    # NUKE_3DE4_ANAMORPHIC_DEG6
    'tdeAnamorphicDeg6_degree2_cx02': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cx02_Degree_2'},
    'tdeAnamorphicDeg6_degree2_cy02': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cy02_Degree_2'},
    'tdeAnamorphicDeg6_degree2_cx22': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cx22_Degree_2'},
    'tdeAnamorphicDeg6_degree2_cy22': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cy22_Degree_2'},
    'tdeAnamorphicDeg6_degree4_cx04': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cx04_Degree_4'},
    'tdeAnamorphicDeg6_degree4_cy04': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cy04_Degree_4'},
    'tdeAnamorphicDeg6_degree4_cx24': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cx24_Degree_4'},
    'tdeAnamorphicDeg6_degree4_cy24': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cy24_Degree_4'},
    'tdeAnamorphicDeg6_degree4_cx44': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cx44_Degree_4'},
    'tdeAnamorphicDeg6_degree4_cy44': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cy44_Degree_4'},
    'tdeAnamorphicDeg6_degree6_cx06': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cx06_Degree_6'},
    'tdeAnamorphicDeg6_degree6_cy06': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cy06_Degree_6'},
    'tdeAnamorphicDeg6_degree6_cx26': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cx26_Degree_6'},
    'tdeAnamorphicDeg6_degree6_cy26': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cy26_Degree_6'},
    'tdeAnamorphicDeg6_degree6_cx46': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cx46_Degree_6'},
    'tdeAnamorphicDeg6_degree6_cy46': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cy46_Degree_6'},
    'tdeAnamorphicDeg6_degree6_cx66': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cx66_Degree_6'},
    'tdeAnamorphicDeg6_degree6_cy66': {NUKE_3DE4_ANAMORPHIC_DEG6: 'Cy66_Degree_6'},
}


NODE_TYPE_TO_MODEL_TYPE_TO_ATTRIBUTE_NAMES = {
    MAYA_MM_LENS_MODEL_3DE: {
        LENS_MODEL_3DE4_CLASSIC_VALUE: [
            'tdeClassic_distortion',
            'tdeClassic_anamorphicSqueeze',
            'tdeClassic_curvatureX',
            'tdeClassic_curvatureY',
            'tdeClassic_quarticDistortion',
        ],
        LENS_MODEL_3DE4_RADIAL_STANDARD_DEG4_VALUE: [
            'tdeRadialStdDeg4_degree2_distortion',
            'tdeRadialStdDeg4_degree2_u',
            'tdeRadialStdDeg4_degree2_v',
            'tdeRadialStdDeg4_degree4_distortion',
            'tdeRadialStdDeg4_degree4_u',
            'tdeRadialStdDeg4_degree4_v',
            'tdeRadialStdDeg4_cylindricDirection',
            'tdeRadialStdDeg4_cylindricBending',
        ],
        LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG4_VALUE: [
            'tdeAnamorphicStdDeg4_degree2_cx02',
            'tdeAnamorphicStdDeg4_degree2_cy02',
            'tdeAnamorphicStdDeg4_degree2_cx22',
            'tdeAnamorphicStdDeg4_degree2_cy22',
            'tdeAnamorphicStdDeg4_degree4_cx04',
            'tdeAnamorphicStdDeg4_degree4_cy04',
            'tdeAnamorphicStdDeg4_degree4_cx24',
            'tdeAnamorphicStdDeg4_degree4_cy24',
            'tdeAnamorphicStdDeg4_degree4_cx44',
            'tdeAnamorphicStdDeg4_degree4_cy44',
            'tdeAnamorphicStdDeg4_lensRotation',
            'tdeAnamorphicStdDeg4_squeeze_x',
            'tdeAnamorphicStdDeg4_squeeze_y',
        ],
        LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG4_RESCALED_VALUE: [
            'tdeAnamorphicStdDeg4_degree2_cx02',
            'tdeAnamorphicStdDeg4_degree2_cy02',
            'tdeAnamorphicStdDeg4_degree2_cx22',
            'tdeAnamorphicStdDeg4_degree2_cy22',
            'tdeAnamorphicStdDeg4_degree4_cx04',
            'tdeAnamorphicStdDeg4_degree4_cy04',
            'tdeAnamorphicStdDeg4_degree4_cx24',
            'tdeAnamorphicStdDeg4_degree4_cy24',
            'tdeAnamorphicStdDeg4_degree4_cx44',
            'tdeAnamorphicStdDeg4_degree4_cy44',
            'tdeAnamorphicStdDeg4_lensRotation',
            'tdeAnamorphicStdDeg4_squeeze_x',
            'tdeAnamorphicStdDeg4_squeeze_y',
            'tdeAnamorphicStdDeg4_rescale',
        ],
        LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG6_VALUE: [
            'tdeAnamorphicStdDeg6_degree2_cx02',
            'tdeAnamorphicStdDeg6_degree2_cy02',
            'tdeAnamorphicStdDeg6_degree2_cx22',
            'tdeAnamorphicStdDeg6_degree2_cy22',
            'tdeAnamorphicStdDeg6_degree4_cx04',
            'tdeAnamorphicStdDeg6_degree4_cy04',
            'tdeAnamorphicStdDeg6_degree4_cx24',
            'tdeAnamorphicStdDeg6_degree4_cy24',
            'tdeAnamorphicStdDeg6_degree4_cx44',
            'tdeAnamorphicStdDeg6_degree4_cy44',
            'tdeAnamorphicStdDeg6_degree6_cx06',
            'tdeAnamorphicStdDeg6_degree6_cy06',
            'tdeAnamorphicStdDeg6_degree6_cx26',
            'tdeAnamorphicStdDeg6_degree6_cy26',
            'tdeAnamorphicStdDeg6_degree6_cx46',
            'tdeAnamorphicStdDeg6_degree6_cy46',
            'tdeAnamorphicStdDeg6_degree6_cx66',
            'tdeAnamorphicStdDeg6_degree6_cy66',
            'tdeAnamorphicStdDeg6_lensRotation',
            'tdeAnamorphicStdDeg6_squeeze_x',
            'tdeAnamorphicStdDeg6_squeeze_y',
        ],
        LENS_MODEL_3DE4_ANAMORPHIC_STD_DEG6_RESCALED_VALUE: [
            'tdeAnamorphicStdDeg6_degree2_cx02',
            'tdeAnamorphicStdDeg6_degree2_cy02',
            'tdeAnamorphicStdDeg6_degree2_cx22',
            'tdeAnamorphicStdDeg6_degree2_cy22',
            'tdeAnamorphicStdDeg6_degree4_cx04',
            'tdeAnamorphicStdDeg6_degree4_cy04',
            'tdeAnamorphicStdDeg6_degree4_cx24',
            'tdeAnamorphicStdDeg6_degree4_cy24',
            'tdeAnamorphicStdDeg6_degree4_cx44',
            'tdeAnamorphicStdDeg6_degree4_cy44',
            'tdeAnamorphicStdDeg6_degree6_cx06',
            'tdeAnamorphicStdDeg6_degree6_cy06',
            'tdeAnamorphicStdDeg6_degree6_cx26',
            'tdeAnamorphicStdDeg6_degree6_cy26',
            'tdeAnamorphicStdDeg6_degree6_cx46',
            'tdeAnamorphicStdDeg6_degree6_cy46',
            'tdeAnamorphicStdDeg6_degree6_cx66',
            'tdeAnamorphicStdDeg6_degree6_cy66',
            'tdeAnamorphicStdDeg6_lensRotation',
            'tdeAnamorphicStdDeg6_squeeze_x',
            'tdeAnamorphicStdDeg6_squeeze_y',
            'tdeAnamorphicStdDeg6_rescale',
        ],
        LENS_MODEL_3DE4_ANAMORPHIC_DEG6_VALUE: [
            'tdeAnamorphicDeg6_degree2_cx02',
            'tdeAnamorphicDeg6_degree2_cy02',
            'tdeAnamorphicDeg6_degree2_cx22',
            'tdeAnamorphicDeg6_degree2_cy22',
            'tdeAnamorphicDeg6_degree4_cx04',
            'tdeAnamorphicDeg6_degree4_cy04',
            'tdeAnamorphicDeg6_degree4_cx24',
            'tdeAnamorphicDeg6_degree4_cy24',
            'tdeAnamorphicDeg6_degree4_cx44',
            'tdeAnamorphicDeg6_degree4_cy44',
            'tdeAnamorphicDeg6_degree6_cx06',
            'tdeAnamorphicDeg6_degree6_cy06',
            'tdeAnamorphicDeg6_degree6_cx26',
            'tdeAnamorphicDeg6_degree6_cy26',
            'tdeAnamorphicDeg6_degree6_cx46',
            'tdeAnamorphicDeg6_degree6_cy46',
            'tdeAnamorphicDeg6_degree6_cx66',
            'tdeAnamorphicDeg6_degree6_cy66',
        ],
    }
}
