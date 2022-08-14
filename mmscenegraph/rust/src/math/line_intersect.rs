//
// Copyright (C) 2022 David Cattermole.
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
/// Find the closest point on a (straight) line.
///
/// See "Minimum Distance between a Point and a Line":
/// http://paulbourke.net/geometry/pointlineplane/
///
use crate::constant::Real;

#[derive(Copy, Clone, Debug, PartialEq)]
pub struct Point3 {
    pub x: Real,
    pub y: Real,
    pub z: Real,
}

fn distance(point_a: Point3, point_b: Point3) -> Real {
    let x = point_b.x - point_a.x;
    let y = point_b.y - point_a.y;
    let z = point_b.z - point_a.z;
    let length = ((x * x) + (y * y) + (z * z)).sqrt();
    length
}

pub fn line_point_intersection(
    point: Point3,
    line_a: Point3,
    line_b: Point3,
) -> Option<Point3> {
    let line_length = distance(line_b, line_a);
    let line_length_squared = line_length * line_length;

    let u = (((point.x - line_a.x) * (line_b.x - line_a.x))
        + ((point.y - line_a.y) * (line_b.y - line_a.y))
        + ((point.z - line_a.z) * (line_b.z - line_a.z)))
        / line_length_squared;

    if u < 0.0 || u > 1.0 {
        None
    } else {
        let x = line_a.x + u * (line_b.x - line_a.x);
        let y = line_a.y + u * (line_b.y - line_a.y);
        let z = line_a.z + u * (line_b.z - line_a.z);

        // Intersection point
        Some(Point3 { x, y, z })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    const EPSILON: Real = 1.0e-5;

    #[test]
    fn test_line_point_intersection_1() {
        let line_a = Point3 {
            x: 50.0,
            y: 80.0,
            z: 300.0,
        };
        let line_b = Point3 {
            x: 50.0,
            y: -800.0,
            z: 1000.0,
        };
        let point = Point3 {
            x: 20.0,
            y: 1000.0,
            z: 400.0,
        };

        let intersection_point = line_point_intersection(point, line_a, line_b);
        println!("Intersection Point: {:?}", intersection_point);

        match intersection_point {
            Some(closest_point) => {
                println!("Hit");
            }
            None => println!("Miss"),
        }
        assert_eq!(intersection_point, None);
    }

    #[test]
    fn test_line_point_intersection_2() {
        let line_a = Point3 {
            x: 0.0,
            y: 0.0,
            z: 50.0,
        };
        let line_b = Point3 {
            x: 0.0,
            y: 0.0,
            z: -50.0,
        };
        let point = Point3 {
            x: 10.0,
            y: 50.0,
            z: 10.0,
        };

        let intersection_point = line_point_intersection(point, line_a, line_b);
        println!("Intersection Point: {:?}", intersection_point);

        match intersection_point {
            Some(closest_point) => {
                println!("Hit");
                println!("Closest Point: {:?}", closest_point);
                let closest_distance = distance(point, closest_point);
                println!("Closest Distance: {}", closest_distance);
                assert_relative_eq!(closest_point.x, 0.0, epsilon = EPSILON);
                assert_relative_eq!(closest_point.y, 0.0, epsilon = EPSILON);
                assert_relative_eq!(closest_point.z, 10.0, epsilon = EPSILON);
                assert_relative_eq!(
                    closest_distance,
                    50.99019513592785,
                    epsilon = EPSILON
                );
            }
            None => println!("Miss"),
        }
    }

    #[test]
    fn test_line_point_intersection_3() {
        let line_a = Point3 {
            x: 0.0,
            y: 0.0,
            z: 10.0,
        };
        let line_b = Point3 {
            x: 0.0,
            y: 0.0,
            z: -10.0,
        };
        let point = Point3 {
            x: 0.0,
            y: 10.0,
            z: 5.0,
        };

        let intersection_point = line_point_intersection(point, line_a, line_b);
        println!("Intersection Point: {:?}", intersection_point);

        match intersection_point {
            Some(closest_point) => {
                println!("Hit");
                println!("Closest Point: {:?}", closest_point);
                println!("Point: {:?}", point);
                let closest_distance = distance(point, closest_point);
                println!("Closest Distance: {}", closest_distance);
                assert_relative_eq!(closest_point.x, 0.0, epsilon = EPSILON);
                assert_relative_eq!(closest_point.y, 0.0, epsilon = EPSILON);
                assert_relative_eq!(closest_point.z, 5.0, epsilon = EPSILON);
                assert_relative_eq!(closest_distance, 10.0, epsilon = EPSILON);
            }
            None => println!("Miss"),
        }
    }
}
