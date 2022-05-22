# Copyright (C) 2022 David Cattermole.
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

# Maya node types
MAYA_MM_LENS_MODEL_3DE = 'mmLensModel3de'

# Nuke node types.
NUKE_3DE4_CLASSIC = 'LD_3DE_Classic_LD_Model'
NUKE_3DE4_RADIAL_STANDARD_DEG4 = 'LD_3DE4_Radial_Standard_Degree_4'
NUKE_3DE4_ANAMORPHIC_DEG4 = 'LD_3DE4_Anamorphic_Standard_Degree_4'
NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4 = 'LD_3DE4_Anamorphic_Rescaled_Degree_4'
NUKE_3DE4_ANAMORPHIC_DEG6 = 'LD_3DE4_Anamorphic_Degree_6'

NUKE_NODE_TYPE_TO_NODE_TYPE_TO_VALUE = {
    NUKE_3DE4_CLASSIC: {
            MAYA_MM_LENS_MODEL_3DE: 2
    },
    NUKE_3DE4_RADIAL_STANDARD_DEG4: {
        MAYA_MM_LENS_MODEL_3DE: 3,
    },
    NUKE_3DE4_ANAMORPHIC_DEG4: {
        MAYA_MM_LENS_MODEL_3DE: 4,
    },
    NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4: {
        MAYA_MM_LENS_MODEL_3DE: None,  # Currently unsupported.
    },
    NUKE_3DE4_ANAMORPHIC_DEG6: {
        MAYA_MM_LENS_MODEL_3DE: None,  # Currently unsupported.
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

    # NUKE_3DE4_RADIAL_STANDARD_DEG4
    (NUKE_3DE4_RADIAL_STANDARD_DEG4, 'Distortion_Degree_2'): [
        'tdeRadialDeg4_degree2_distortion',
    ],
    (NUKE_3DE4_RADIAL_STANDARD_DEG4, 'U_Degree_2'): [
        'tdeRadialDeg4_degree2_u',
    ],
    (NUKE_3DE4_RADIAL_STANDARD_DEG4, 'V_Degree_2'): [
        'tdeRadialDeg4_degree2_v',
    ],
    (NUKE_3DE4_RADIAL_STANDARD_DEG4, 'Quartic_Distortion_Degree_4'): [
        'tdeRadialDeg4_degree4_distortion',
    ],
    (NUKE_3DE4_RADIAL_STANDARD_DEG4, 'U_Degree_4'): [
        'tdeRadialDeg4_degree4_u',
    ],
    (NUKE_3DE4_RADIAL_STANDARD_DEG4, 'V_Degree_4'): [
        'tdeRadialDeg4_degree4_v',
    ],
    (NUKE_3DE4_RADIAL_STANDARD_DEG4, 'Phi_Cylindric_Direction'): [
        'tdeRadialDeg4_cylindricDirection',
    ],
    (NUKE_3DE4_RADIAL_STANDARD_DEG4, 'B_Cylindric_Bending'): [
        'tdeRadialDeg4_cylindricBending',
    ],

    # NUKE_3DE4_ANAMORPHIC_DEG4
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cx02_Degree_2'): [
        'tdeAnamorphicDeg4_degree2_cx02',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cy02_Degree_2'): [
        'tdeAnamorphicDeg4_degree2_cy02',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cx22_Degree_2'): [
        'tdeAnamorphicDeg4_degree2_cx22',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cy22_Degree_2'): [
        'tdeAnamorphicDeg4_degree2_cy22',
    ],

    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cx04_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cx04',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cy04_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cy04',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cx24_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cx24',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cy24_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cy24',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cx44_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cx44',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Cy44_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cy44',
    ],

    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Lens_Rotation'): [
        'tdeAnamorphicDeg4_lensRotation',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Squeeze_X'): [
        'tdeAnamorphicDeg4_squeeze_x',
    ],
    (NUKE_3DE4_ANAMORPHIC_DEG4, 'Squeeze_Y'): [
        'tdeAnamorphicDeg4_squeeze_y',
    ],

    # NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cx02_Degree_2'): [
        'tdeAnamorphicDeg4_degree2_cx02',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cy02_Degree_2'): [
        'tdeAnamorphicDeg4_degree2_cy02',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cx22_Degree_2'): [
        'tdeAnamorphicDeg4_degree2_cx22',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cy22_Degree_2'): [
        'tdeAnamorphicDeg4_degree2_cy22',
    ],

    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cx04_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cx04',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cy04_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cy04',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cx24_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cx24',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cy24_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cy24',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cx44_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cx44',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Cy44_Degree_4'): [
        'tdeAnamorphicDeg4_degree4_cy44',
    ],

    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Lens_Rotation'): [
        'tdeAnamorphicDeg4_lensRotation',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Squeeze_X'): [
        'tdeAnamorphicDeg4_squeeze_x',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Squeeze_Y'): [
        'tdeAnamorphicDeg4_squeeze_y',
    ],
    (NUKE_3DE4_ANAMORPHIC_RESCALED_DEG4, 'Rescale'): [
        'tdeAnamorphicDeg4_rescale',
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
