# MM lens

The 'mmlens' library allows us to apply lens distortion operations;
undistort and redistort.

'mmlens' wraps the Science-D-Visions Lens Distortion Plug-in Kit
(LDPK) maths into mmSolver classes, trying to gain performance over
the LDPK "plug-ins" by avoiding virtual calls on each calculation
trying to improve code inlining. C++ template functions are used to
improve performance with multiple 2D coordinates being processed at
once.

This library is primarily written in C++.

# Structure

mmlens is only defined in the 'cppbind/mmlens' directory.

'cppbind/mmlens' is a Rust crate to define C++ bindings with the help
of the CXX crate.

'cppbind/mmlens' can mix both C++ and Rust.

# Build Process

'cppbind/mmlens' and 'rust/mmlens' are built as part of
'mmsolverlibs'.

# How To Add A New Lens Model?

For new (LDPK) lens distortion models, there are a number of different
tools affected.
- mmsolverlibs mmlens core library (Rust / C++).
- Lens Parameters I/O - Reading lens parameters from Nuke files (.nk).
- Load Lens tool (Maya Python).
- mmSolver Core Solver - Lens Distortion Support (Maya Plug-in C++).
- Lens Distortion ST-Maps Tool (C++ standalone tool)

Below are all the files needing changes, based on the individual
tools.

## mmsolverlibs mmlens core library

The example implementation should follow patterns similar to existing
models like `3deClassic` or `3deRadialStdDeg4`, adapting the mathematics
and parameter handling for your specific lens model requirements.

### Overview of Files to Change

Edit files:
```
lib/cppbind/mmlens/include/mmlens/distortion_layers.h
lib/cppbind/mmlens/include/mmlens/distortion_process.h
lib/cppbind/mmlens/include/mmlens/mmlens.h
lib/cppbind/mmlens/src/constants.rs
lib/cppbind/mmlens/src/cxxbridge.rs
lib/cppbind/mmlens/src/distortion_layers.cpp
lib/cppbind/mmlens/src/distortion_layers.rs
lib/cppbind/mmlens/src/distortion_process.cpp
lib/cppbind/mmlens/src/distortion_process.rs
lib/cppbind/mmlens/src/distortion_structs.h
lib/cppbind/mmlens/src/option_lens_parameters.rs
lib/mmsolverlibs/src/CMakeLists.txt
```

Add files:
```
lib/cppbind/mmlens/include/mmlens/lens_model_EXAMPLE.h
lib/cppbind/mmlens/src/lens_model_EXAMPLE.cpp
```

### Important Implementation Considerations

Parameter Organization:

- Keep parameters logically grouped
- Use clear naming conventions
- Document the purpose and valid ranges of each parameter

Thread Safety:

- Ensure thread-safe access to parameters
- Use appropriate synchronization in multi-threaded processing

Performance:

- Optimize mathematical operations
- Consider using look-up tables for complex calculations
- Implement efficient memory management


Error Handling:

- Add appropriate parameter validation
- Handle edge cases gracefully
- Provide meaningful error messages


Testing:

- Create unit tests for the new model
- Test both single-threaded and multi-threaded operations
- Verify accuracy against reference implementations


Documentation:

- Document mathematical formulas and algorithms.
- Explain parameter interactions.
- Provide usage examples.



### 0) option_lens_parameters.rs and cxxbridge.rs

#### Add Option Parameter Type

In `option_lens_parameters.rs` add:

```rust
struct OptionParametersExample {
    exists: bool,
    value: ParametersExample,
}
```

Define parameter structures in `cxxbridge.rs`:

```rust
#[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
struct OptionParametersExample {
    exists: bool,
    value: ParametersExample,
}
```


### 1) cxxbridge.rs

#### Add New Type Enum

Add a new variant to `LensModelType` enum in `cxxbridge.rs`:

```rust
#[repr(u8)]
pub(crate) enum LensModelType {
    // ... existing types ...
    TdeExample = <next_number>,  // Add new type
}
```

#### Create Main Parameter Struct

Define parameter structures in `cxxbridge.rs`:

```rust
#[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
pub(crate) struct ParametersExample {
    // Define the parameters needed for your lens model
    parameter1: f64,
    parameter2: f64,
    // etc...
}
```

### 2) lens_model_example.cpp/.h - Create Lens Model Class

Add `lens_model_example.cpp` and `lens_model_example.h`, define the
'Example' lens model class inheriting from LensModel, and implement
the lens model distortion calculations.

Create new header file `lens_model_example.h`:

```rust
class LensModelExample : public LensModel {
public:
    LensModelExample();
    LensModelExample(/* parameter constructor */);

    // Required overrides from LensModel base class
    std::unique_ptr<LensModel> cloneAsUniquePtr() const override;
    std::shared_ptr<LensModel> cloneAsSharedPtr() const override;
    void applyModelUndistort(const double x, const double y, double &out_x, double &out_y) override;
    void applyModelDistort(const double x, const double y, double &out_x, double &out_y) override;
    mmhash::HashValue hashValue() override;

private:
    ParametersExample m_lens;
};
```

### 3) distortion_structs.h

#### Implement Distortion Operations

Create distortion class implementing the Distortion interface in `distortion_structs.h`.

Implement the distortion calculations specific to your lens model.

```cpp
class DistortionExample : public Distortion {
    // Implement required methods
}
```

### 4) distortion_process.h/.cpp

- Add new processing functions in `distortion_process.h` and `distortion_process.cpp`.
- Implement both single-threaded and multi-threaded versions.
- Include variants for different precision types (f32/f64).

```cpp
void apply_identity_to_f64(...);
void apply_identity_to_f32(...);
void apply_f64_to_f64(...);
void apply_f64_to_f32(...);
```


### 5) constants.rs

Add parameter count constant in `constants.rs`:

```rust
pub const PARAMETER_COUNT_EXAMPLE: ParameterSize = <number_of_parameters>;
pub const NUKE_EXAMPLE: &str = "LD_EXAMPLE";
```

### 6) distortion_layers.h/.cpp/.rs - Layer Support

Add support in `distortion_layers.h/.cpp/.rs` for the new model type.
Implement parameter handling and conversion functions.

```cpp
OptionParametersExample layer_lens_parameters_example(...);
```

### 7) CMakeLists.txt - Update Build System


Add new source files to `CMakeLists.txt`.
Add any new dependencies if required.

```
set(lib_source_files
    # ...
    ${mmlens_source_dir}/lens_model_example.cpp
    # ...
)
```


### 8) mmlens.h - Register with Main Headers

Add the new lens model header into `mmlens.h`.

```
#include "lens_model_example.h"
```

## Lens Parameters I/O

Lens Parameter I/O is used to read text files and parse them into

The `lens_io.rs` file must be updated to support the new 'example'
lens model. This will include finding and adding code to each `match`
statement.

Edit files:
```
lib/cppbind/mmlens/src/lens_io.rs
```

## mmSolver Core Solver

The mmSolver core solver must be adjusted to work with the new lens
model.

Update `maya_attr.h` to specify the attribute solver type ids for each
attribute, and the mapping for Maya node attribute name to the
specific type.

Update `maya_lens_model_utils.cpp` to include the new solver attribute
type from `maya_attr.h`.

Add new attributes `MMLensModel3deNode.cpp` and `MMLensModel3deNode.h`
and update the conditional for the new lens model name and the mapping
from the Maya attribute plugs to the internal lens distortion model.

Finally `AEmmLensModel3deTemplate.mel` must be updated with the new
Maya node attributes added to `MMLensModel3deNode.cpp` and
`MMLensModel3deNode.h`.

Edit files:
```
src/mmSolver/mayahelper/maya_attr.h
src/mmSolver/mayahelper/maya_lens_model_utils.cpp
src/mmSolver/node/MMLensModel3deNode.cpp
src/mmSolver/node/MMLensModel3deNode.h
mel/AETemplates/AEmmLensModel3deTemplate.mel
```

## Load Lens tool

The Load Lens tool relies on the Lens Parameter I/O, and a number of
data structures defined in the `constant.py` file. These data
structures contain mappings between the Maya attributes and the
internal lens distortion model.

Edit files:
```
python/mmSolver/tools/loadlens/constant.py
```

## Lens Distortion ST-Maps

To make the lens distortion tool work, you must add new conditionals
for the new lens model.

Edit files:
```
tools/lensdistortion/src/steps.h
```
