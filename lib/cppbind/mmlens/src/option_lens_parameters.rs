//
// Copyright (C) 2023, 2024 David Cattermole.
//
// This file is part of mmSolver.
//
// mmSolver is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// mmSolver is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
// ====================================================================
//

use crate::cxxbridge::ffi::OptionParameters3deAnamorphicStdDeg4;
use crate::cxxbridge::ffi::OptionParameters3deAnamorphicStdDeg4Rescaled;
use crate::cxxbridge::ffi::OptionParameters3deAnamorphicStdDeg6;
use crate::cxxbridge::ffi::OptionParameters3deAnamorphicStdDeg6Rescaled;
use crate::cxxbridge::ffi::OptionParameters3deClassic;
use crate::cxxbridge::ffi::OptionParameters3deRadialStdDeg4;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg4;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg4Rescaled;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg6;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg6Rescaled;
use crate::cxxbridge::ffi::Parameters3deClassic;
use crate::cxxbridge::ffi::Parameters3deRadialStdDeg4;

impl OptionParameters3deClassic {
    pub fn new_as_none() -> OptionParameters3deClassic {
        OptionParameters3deClassic {
            exists: false,
            value: Parameters3deClassic {
                distortion: 0.0,
                anamorphic_squeeze: 1.0,
                curvature_x: 0.0,
                curvature_y: 0.0,
                quartic_distortion: 0.0,
            },
        }
    }

    pub fn new_as_some(
        distortion: f64,
        anamorphic_squeeze: f64,

        curvature_x: f64,
        curvature_y: f64,
        quartic_distortion: f64,
    ) -> OptionParameters3deClassic {
        OptionParameters3deClassic {
            exists: true,
            value: Parameters3deClassic {
                distortion,
                anamorphic_squeeze,
                curvature_x,
                curvature_y,
                quartic_distortion,
            },
        }
    }
}

impl OptionParameters3deRadialStdDeg4 {
    pub fn new_as_none() -> OptionParameters3deRadialStdDeg4 {
        OptionParameters3deRadialStdDeg4 {
            exists: false,
            value: Parameters3deRadialStdDeg4 {
                degree2_distortion: 0.0,
                degree2_u: 0.0,
                degree2_v: 0.0,
                degree4_distortion: 0.0,
                degree4_u: 0.0,
                degree4_v: 0.0,
                cylindric_direction: 0.0,
                cylindric_bending: 0.0,
            },
        }
    }

    pub fn new_as_some(
        degree2_distortion: f64,
        degree2_u: f64,
        degree2_v: f64,
        degree4_distortion: f64,
        degree4_u: f64,
        degree4_v: f64,
        cylindric_direction: f64,
        cylindric_bending: f64,
    ) -> OptionParameters3deRadialStdDeg4 {
        OptionParameters3deRadialStdDeg4 {
            exists: true,
            value: Parameters3deRadialStdDeg4 {
                degree2_distortion,
                degree2_u,
                degree2_v,
                degree4_distortion,
                degree4_u,
                degree4_v,
                cylindric_direction,
                cylindric_bending,
            },
        }
    }
}

impl OptionParameters3deAnamorphicStdDeg4 {
    pub fn new_as_none() -> OptionParameters3deAnamorphicStdDeg4 {
        OptionParameters3deAnamorphicStdDeg4 {
            exists: false,
            value: Parameters3deAnamorphicStdDeg4 {
                degree2_cx02: 0.0,
                degree2_cy02: 0.0,
                degree2_cx22: 0.0,
                degree2_cy22: 0.0,
                degree4_cx04: 0.0,
                degree4_cy04: 0.0,
                degree4_cx24: 0.0,
                degree4_cy24: 0.0,
                degree4_cx44: 0.0,
                degree4_cy44: 0.0,
                lens_rotation: 0.0,
                squeeze_x: 1.0,
                squeeze_y: 1.0,
            },
        }
    }

    pub fn new_as_some(
        degree2_cx02: f64,
        degree2_cy02: f64,
        degree2_cx22: f64,
        degree2_cy22: f64,
        degree4_cx04: f64,
        degree4_cy04: f64,
        degree4_cx24: f64,
        degree4_cy24: f64,
        degree4_cx44: f64,
        degree4_cy44: f64,
        lens_rotation: f64,
        squeeze_x: f64,
        squeeze_y: f64,
    ) -> OptionParameters3deAnamorphicStdDeg4 {
        OptionParameters3deAnamorphicStdDeg4 {
            exists: true,
            value: Parameters3deAnamorphicStdDeg4 {
                degree2_cx02,
                degree2_cy02,
                degree2_cx22,
                degree2_cy22,
                degree4_cx04,
                degree4_cy04,
                degree4_cx24,
                degree4_cy24,
                degree4_cx44,
                degree4_cy44,
                lens_rotation,
                squeeze_x,
                squeeze_y,
            },
        }
    }
}

impl OptionParameters3deAnamorphicStdDeg4Rescaled {
    pub fn new_as_none() -> OptionParameters3deAnamorphicStdDeg4Rescaled {
        OptionParameters3deAnamorphicStdDeg4Rescaled {
            exists: false,
            value: Parameters3deAnamorphicStdDeg4Rescaled {
                degree2_cx02: 0.0,
                degree2_cy02: 0.0,
                degree2_cx22: 0.0,
                degree2_cy22: 0.0,
                degree4_cx04: 0.0,
                degree4_cy04: 0.0,
                degree4_cx24: 0.0,
                degree4_cy24: 0.0,
                degree4_cx44: 0.0,
                degree4_cy44: 0.0,
                lens_rotation: 0.0,
                squeeze_x: 1.0,
                squeeze_y: 1.0,
                rescale: 1.0,
            },
        }
    }

    pub fn new_as_some(
        degree2_cx02: f64,
        degree2_cy02: f64,
        degree2_cx22: f64,
        degree2_cy22: f64,
        degree4_cx04: f64,
        degree4_cy04: f64,
        degree4_cx24: f64,
        degree4_cy24: f64,
        degree4_cx44: f64,
        degree4_cy44: f64,
        lens_rotation: f64,
        squeeze_x: f64,
        squeeze_y: f64,
        rescale: f64,
    ) -> OptionParameters3deAnamorphicStdDeg4Rescaled {
        OptionParameters3deAnamorphicStdDeg4Rescaled {
            exists: true,
            value: Parameters3deAnamorphicStdDeg4Rescaled {
                degree2_cx02,
                degree2_cy02,
                degree2_cx22,
                degree2_cy22,
                degree4_cx04,
                degree4_cy04,
                degree4_cx24,
                degree4_cy24,
                degree4_cx44,
                degree4_cy44,
                lens_rotation,
                squeeze_x,
                squeeze_y,
                rescale,
            },
        }
    }
}

impl OptionParameters3deAnamorphicStdDeg6 {
    pub fn new_as_none() -> OptionParameters3deAnamorphicStdDeg6 {
        OptionParameters3deAnamorphicStdDeg6 {
            exists: false,
            value: Parameters3deAnamorphicStdDeg6 {
                degree2_cx02: 0.0,
                degree2_cy02: 0.0,
                degree2_cx22: 0.0,
                degree2_cy22: 0.0,
                degree4_cx04: 0.0,
                degree4_cy04: 0.0,
                degree4_cx24: 0.0,
                degree4_cy24: 0.0,
                degree4_cx44: 0.0,
                degree4_cy44: 0.0,
                degree6_cx06: 0.0,
                degree6_cy06: 0.0,
                degree6_cx26: 0.0,
                degree6_cy26: 0.0,
                degree6_cx46: 0.0,
                degree6_cy46: 0.0,
                degree6_cx66: 0.0,
                degree6_cy66: 0.0,
                lens_rotation: 0.0,
                squeeze_x: 1.0,
                squeeze_y: 1.0,
            },
        }
    }

    pub fn new_as_some(
        degree2_cx02: f64,
        degree2_cy02: f64,
        degree2_cx22: f64,
        degree2_cy22: f64,
        degree4_cx04: f64,
        degree4_cy04: f64,
        degree4_cx24: f64,
        degree4_cy24: f64,
        degree4_cx44: f64,
        degree4_cy44: f64,
        degree6_cx06: f64,
        degree6_cy06: f64,
        degree6_cx26: f64,
        degree6_cy26: f64,
        degree6_cx46: f64,
        degree6_cy46: f64,
        degree6_cx66: f64,
        degree6_cy66: f64,
        lens_rotation: f64,
        squeeze_x: f64,
        squeeze_y: f64,
    ) -> OptionParameters3deAnamorphicStdDeg6 {
        OptionParameters3deAnamorphicStdDeg6 {
            exists: true,
            value: Parameters3deAnamorphicStdDeg6 {
                degree2_cx02,
                degree2_cy02,
                degree2_cx22,
                degree2_cy22,
                degree4_cx04,
                degree4_cy04,
                degree4_cx24,
                degree4_cy24,
                degree4_cx44,
                degree4_cy44,
                degree6_cx06,
                degree6_cy06,
                degree6_cx26,
                degree6_cy26,
                degree6_cx46,
                degree6_cy46,
                degree6_cx66,
                degree6_cy66,
                lens_rotation,
                squeeze_x,
                squeeze_y,
            },
        }
    }
}

impl OptionParameters3deAnamorphicStdDeg6Rescaled {
    pub fn new_as_none() -> OptionParameters3deAnamorphicStdDeg6Rescaled {
        OptionParameters3deAnamorphicStdDeg6Rescaled {
            exists: false,
            value: Parameters3deAnamorphicStdDeg6Rescaled {
                degree2_cx02: 0.0,
                degree2_cy02: 0.0,
                degree2_cx22: 0.0,
                degree2_cy22: 0.0,
                degree4_cx04: 0.0,
                degree4_cy04: 0.0,
                degree4_cx24: 0.0,
                degree4_cy24: 0.0,
                degree4_cx44: 0.0,
                degree4_cy44: 0.0,
                degree6_cx06: 0.0,
                degree6_cy06: 0.0,
                degree6_cx26: 0.0,
                degree6_cy26: 0.0,
                degree6_cx46: 0.0,
                degree6_cy46: 0.0,
                degree6_cx66: 0.0,
                degree6_cy66: 0.0,
                lens_rotation: 0.0,
                squeeze_x: 1.0,
                squeeze_y: 1.0,
                rescale: 1.0,
            },
        }
    }

    pub fn new_as_some(
        degree2_cx02: f64,
        degree2_cy02: f64,
        degree2_cx22: f64,
        degree2_cy22: f64,
        degree4_cx04: f64,
        degree4_cy04: f64,
        degree4_cx24: f64,
        degree4_cy24: f64,
        degree4_cx44: f64,
        degree4_cy44: f64,
        degree6_cx06: f64,
        degree6_cy06: f64,
        degree6_cx26: f64,
        degree6_cy26: f64,
        degree6_cx46: f64,
        degree6_cy46: f64,
        degree6_cx66: f64,
        degree6_cy66: f64,
        lens_rotation: f64,
        squeeze_x: f64,
        squeeze_y: f64,
        rescale: f64,
    ) -> OptionParameters3deAnamorphicStdDeg6Rescaled {
        OptionParameters3deAnamorphicStdDeg6Rescaled {
            exists: true,
            value: Parameters3deAnamorphicStdDeg6Rescaled {
                degree2_cx02,
                degree2_cy02,
                degree2_cx22,
                degree2_cy22,
                degree4_cx04,
                degree4_cy04,
                degree4_cx24,
                degree4_cy24,
                degree4_cx44,
                degree4_cy44,
                degree6_cx06,
                degree6_cy06,
                degree6_cx26,
                degree6_cy26,
                degree6_cx46,
                degree6_cy46,
                degree6_cx66,
                degree6_cy66,
                lens_rotation,
                squeeze_x,
                squeeze_y,
                rescale,
            },
        }
    }
}
