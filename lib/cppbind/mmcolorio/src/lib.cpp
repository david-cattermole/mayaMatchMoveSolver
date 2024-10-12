/*
 * Copyright (C) 2023 David Cattermole.
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

// Stop OpenColorIO header error on Windows.
//
// https://stackoverflow.com/questions/6884093/warning-c4003-not-enough-actual-parameters-for-macro-max-visual-studio-2010
#ifndef NOMINMAX
#define NOMINMAX
#endif

// C++ Standard Library
#include <cstddef>
#include <cstring>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

// MM Solver
#include <mmcolorio/lib.h>
#include <mmsolverlibs/debug.h>

// OpenColorIO
#include <OpenColorIO/OpenColorIO.h>

namespace OCIO = OCIO_NAMESPACE;

namespace mmcolorio {

void print_ocio_config_details(OCIO::ConstConfigRcPtr &config) {
    MMSOLVER_CORE_INFO(std::cout, "mmcolorio: ----------------------------");
    MMSOLVER_CORE_INFO(std::cout,
                       "mmcolorio: OpenColorIO Version=" << OCIO_VERSION);

    if (!config) {
        MMSOLVER_CORE_ERR(
            std::cerr, "mmcolorio: print_ocio_config_details: config is null.");
        return;
    }

    try {
        MMSOLVER_CORE_INFO(
            std::cout, "mmcolorio: OCIO Config:"
                           << " MajorVersion=" << config->getMajorVersion()
                           << " MinorVersion=" << config->getMinorVersion());

        MMSOLVER_CORE_INFO(std::cout, "mmcolorio: OCIO Config:"
                                          << " Name=\"" << config->getName()
                                          << "\"");

        MMSOLVER_CORE_INFO(std::cout, "mmcolorio: OCIO Config:"
                                          << " FamilySeparator=\""
                                          << config->getFamilySeparator()
                                          << "\"");

        MMSOLVER_CORE_INFO(std::cout, "mmcolorio: OCIO Config:"
                                          << " Description=\""
                                          << config->getDescription() << "\"");

        MMSOLVER_CORE_INFO(std::cout, "mmcolorio: OCIO Config:"
                                          << " SearchPath=\""
                                          << config->getSearchPath() << "\"");
        MMSOLVER_CORE_INFO(std::cout, "mmcolorio: OCIO Config:"
                                          << " WorkingDir=\""
                                          << config->getWorkingDir() << "\"");

        const auto searchReferenceType =
            OCIO::SearchReferenceSpaceType::SEARCH_REFERENCE_SPACE_SCENE;
        const auto visibility = OCIO::ColorSpaceVisibility::COLORSPACE_ACTIVE;

        MMSOLVER_CORE_INFO(std::cout,
                           "mmcolorio: ----------------------------");
        const int32_t numColorSpaces =
            config->getNumColorSpaces(searchReferenceType, visibility);
        // const int32_t numColorSpaces = config->getNumColorSpaces();
        for (auto i = 0; i < numColorSpaces; i++) {
            const char *colorSpaceName = config->getColorSpaceNameByIndex(i);
            OCIO::ConstColorSpaceRcPtr colorSpaceRcPtr =
                config->getColorSpace(colorSpaceName);
            MMSOLVER_CORE_INFO(std::cout, "mmcolorio: OCIO Config: i="
                                              << i << " colorSpaceName=\""
                                              << colorSpaceName << "\"");
        }

        MMSOLVER_CORE_INFO(std::cout,
                           "mmcolorio: ----------------------------");
        const int32_t numRoles = config->getNumRoles();
        for (auto i = 0; i < numRoles; i++) {
            const char *roleName = config->getRoleName(i);
            const char *roleColorSpaceName = config->getRoleColorSpace(i);
            MMSOLVER_CORE_INFO(std::cout, "mmcolorio: OCIO Config: i="
                                              << i << " roleName=\"" << roleName
                                              << "\" roleColorSpaceName=\""
                                              << roleColorSpaceName << "\"");
        }

        MMSOLVER_CORE_INFO(std::cout,
                           "mmcolorio: ----------------------------");
        const char *defaultDisplayName = config->getDefaultDisplay();
        MMSOLVER_CORE_INFO(std::cout,
                           "mmcolorio: OCIO Config: defaultDisplayName=\""
                               << defaultDisplayName << "\"");

        const char *activeDisplays = config->getActiveDisplays();
        MMSOLVER_CORE_INFO(std::cout,
                           "mmcolorio: OCIO Config: activeDisplays=\""
                               << activeDisplays << "\"");

        const char *activeViews = config->getActiveViews();
        MMSOLVER_CORE_INFO(std::cout, "mmcolorio: OCIO Config: activeViews=\""
                                          << activeViews << "\"");

        MMSOLVER_CORE_INFO(std::cout,
                           "mmcolorio: ----------------------------");
        const int numDisplay = config->getNumDisplays();
        for (auto i = 0; i < numDisplay; i++) {
            const char *displayName = config->getDisplay(i);
            MMSOLVER_CORE_INFO(std::cout, "mmcolorio: OCIO Config: i="
                                              << i << " displayName=\""
                                              << displayName << "\"");
        }
    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(
            std::cerr,
            "mmcolorio: OpenColorIO Error: print_ocio_config_details: "
                << exception.what());
    }

    return;
}

// This is an example function used to validate OpenColorIO was
// working. This should not be used and can be removed at a later
// date.
void test_opencolorio(uint8_t *pixels, const uint32_t width,
                      const uint32_t height, const uint8_t number_of_channels) {
    const bool verbose = false;

    mmsolver::debug::TimestampBenchmark timer_total;
    mmsolver::debug::TimestampBenchmark timer_a;
    mmsolver::debug::TimestampBenchmark timer_b;
    mmsolver::debug::TimestampBenchmark timer_c;
    mmsolver::debug::TimestampBenchmark timer_d;
    mmsolver::debug::TimestampBenchmark timer_e;

    timer_total.start();
    try {
        OCIO::ConstConfigRcPtr config = OCIO::GetCurrentConfig();
        if (verbose) {
            timer_c.start();
            print_ocio_config_details(config);
            timer_c.stop();
        }

        // Built-in OCIO config (used as a fallback)
        if (std::strlen(config->getName()) == 0) {
            timer_a.start();

            MMSOLVER_CORE_WRN(std::cerr,
                              "mmcolorio: OpenColorIO could not get config, "
                              "using default config.");

            const char *filename = "ocio://default";
            config = OCIO::Config::CreateFromFile(filename);
            OCIO::SetCurrentConfig(config);
            timer_a.stop();

            if (verbose) {
                timer_c.start();
                print_ocio_config_details(config);
                timer_c.stop();
            }
        }

        OCIO::BitDepth inBitDepth = OCIO::BitDepth::BIT_DEPTH_UINT8;
        OCIO::BitDepth outBitDepth = OCIO::BitDepth::BIT_DEPTH_UINT8;

        // // TODO: Support 16-bit half or 32-bit float output.
        // OCIO::BitDepth outBitDepth = OCIO::BitDepth::BIT_DEPTH_F16;
        // OCIO::BitDepth outBitDepth = OCIO::BitDepth::BIT_DEPTH_F32;

        {
            timer_d.start();

            OCIO::ConstProcessorRcPtr processor = config->getProcessor(
                OCIO::ROLE_COLOR_PICKING, OCIO::ROLE_SCENE_LINEAR);

            OCIO::OptimizationFlags oFlags =
                OCIO::OptimizationFlags::OPTIMIZATION_DEFAULT;

            OCIO::ConstCPUProcessorRcPtr cpu =
                processor->getOptimizedCPUProcessor(inBitDepth, outBitDepth,
                                                    oFlags);

            timer_d.stop();

            {
                timer_e.start();

                // Apply the color transform to an existing RGB(A) image.
                void *imageData = static_cast<void *>(pixels);
                const long width_long = static_cast<long>(width);
                const long height_long = static_cast<long>(height);
                const long numChannels = static_cast<long>(number_of_channels);
                const ptrdiff_t chanStrideBytes = sizeof(uint8_t);
                const ptrdiff_t xStrideBytes = numChannels * sizeof(uint8_t);
                const ptrdiff_t yStrideBytes =
                    numChannels * width_long * sizeof(uint8_t);
                OCIO::PackedImageDesc img(
                    imageData, width_long, height_long, numChannels, inBitDepth,
                    chanStrideBytes, xStrideBytes, yStrideBytes);

                // TODO: Allow a different image data type as the output. We
                // need to pass another 'OCIO::PackedImageDesc' as a second
                // argument here.
                cpu->apply(img);
                timer_e.stop();
            }
        }
    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: OpenColorIO Error: test_opencolorio: "
                              << exception.what());
    }

    timer_total.stop();

    MMSOLVER_CORE_VRB(
        std::cout, "mmcolor: timer_a: " << timer_a.get_seconds() << " seconds");
    MMSOLVER_CORE_VRB(
        std::cout, "mmcolor: timer_b: " << timer_b.get_seconds() << " seconds");
    MMSOLVER_CORE_VRB(
        std::cout, "mmcolor: timer_c: " << timer_c.get_seconds() << " seconds");
    MMSOLVER_CORE_VRB(
        std::cout, "mmcolor: timer_d: " << timer_d.get_seconds() << " seconds");
    MMSOLVER_CORE_VRB(
        std::cout, "mmcolor: timer_e: " << timer_e.get_seconds() << " seconds");
    MMSOLVER_CORE_VRB(
        std::cout,
        "mmcolor: timer_total: " << timer_total.get_seconds() << " seconds");

    return;
}

// Never make this function public, otherwise we leak the OCIO data
// types.
//
// This function is expected to be used inside a try/catch.
OCIO::ConstConfigRcPtr get_config() {
    const bool verbose = false;

    OCIO::ConstConfigRcPtr config = OCIO::GetCurrentConfig();
    if (verbose) {
        print_ocio_config_details(config);
    }

    // Built-in OCIO config (used as a fallback)
    if (!config || std::strlen(config->getName()) == 0) {
        MMSOLVER_CORE_WRN(std::cerr,
                          "mmcolorio: OpenColorIO could not get config, "
                          "using default config.");

        const char *filename = "ocio://default";
        config = OCIO::Config::CreateFromFile(filename);
        OCIO::SetCurrentConfig(config);

        if (verbose) {
            print_ocio_config_details(config);
        }
    }

    return config;
}

const char *get_config_name() {
    try {
        OCIO::ConstConfigRcPtr config = get_config();
        if (!config) {
            MMSOLVER_CORE_ERR(std::cerr,
                              "mmcolorio: get_config_name: config is null.");
            return "";
        }

        return config->getName();
    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: get_config_name: "
                          "OpenColorIO Error: "
                              << exception.what());
    }

    return "";
}

const char *get_config_description() {
    try {
        OCIO::ConstConfigRcPtr config = get_config();
        if (!config) {
            MMSOLVER_CORE_ERR(
                std::cerr,
                "mmcolorio: get_config_description: config is null.");
            return "";
        }

        return config->getDescription();
    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: get_config_description: "
                          "OpenColorIO Error: "
                              << exception.what());
    }

    return "";
}

const char *get_config_search_path() {
    try {
        OCIO::ConstConfigRcPtr config = get_config();
        if (!config) {
            MMSOLVER_CORE_ERR(
                std::cerr,
                "mmcolorio: get_config_search_path: config is null.");
            return "";
        }

        return config->getSearchPath();
    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: get_config_search_path: "
                          "OpenColorIO Error: "
                              << exception.what());
    }

    return "";
}

const char *get_config_working_directory() {
    try {
        OCIO::ConstConfigRcPtr config = get_config();
        if (!config) {
            MMSOLVER_CORE_ERR(
                std::cerr,
                "mmcolorio: config_working_directory: config is null.");
            return "";
        }

        return config->getWorkingDir();
    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: get_config_working_directory: "
                          "OpenColorIO Error: "
                              << exception.what());
    }

    return "";
}

bool color_space_name_exists(const char *color_space_name) {
    try {
        OCIO::ConstConfigRcPtr config = get_config();
        if (!config) {
            MMSOLVER_CORE_ERR(
                std::cerr,
                "mmcolorio: color_space_name_exists: config is null.");
            return false;
        }

        OCIO::ConstColorSpaceRcPtr color_space =
            config->getColorSpace(color_space_name);
        if (color_space) {
            const char *found_name = color_space->getName();
            if (std::strlen(found_name) > 0) {
                return true;
            }
        }
    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: guess_color_space_name_from_file_path: "
                          "OpenColorIO Error: "
                              << exception.what());
    }

    return false;
}

const char *guess_color_space_name_from_file_path(const char *file_path) {
    try {
        OCIO::ConstConfigRcPtr config = get_config();
        if (!config) {
            MMSOLVER_CORE_ERR(
                std::cerr,
                "mmcolorio: guess_color_space_name_from_file_path: config is "
                "null.");
            return "";
        }

        const char *color_space_name =
            config->getColorSpaceFromFilepath(file_path);
        return color_space_name;

    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: guess_color_space_name_from_file_path: "
                          "OpenColorIO Error: "
                              << exception.what());
    }

    return "";
}

static const char *color_space_role_convert_mmcolorio_to_ocio(
    const ColorSpaceRole value) {
    if (value == ColorSpaceRole::kDefault) {
        return OCIO::ROLE_DEFAULT;
    } else if (value == ColorSpaceRole::kReference) {
        return OCIO::ROLE_REFERENCE;
    } else if (value == ColorSpaceRole::kData) {
        return OCIO::ROLE_DATA;
    } else if (value == ColorSpaceRole::kColorPicking) {
        return OCIO::ROLE_COLOR_PICKING;
    } else if (value == ColorSpaceRole::kSceneLinear) {
        return OCIO::ROLE_SCENE_LINEAR;
    } else if (value == ColorSpaceRole::kCompositingLog) {
        return OCIO::ROLE_COMPOSITING_LOG;
    } else if (value == ColorSpaceRole::kColorTiming) {
        return OCIO::ROLE_COLOR_TIMING;
    } else if (value == ColorSpaceRole::kTexturePaint) {
        return OCIO::ROLE_TEXTURE_PAINT;
    } else if (value == ColorSpaceRole::kMattePaint) {
        return OCIO::ROLE_MATTE_PAINT;
    } else if (value == ColorSpaceRole::kRendering) {
        return OCIO::ROLE_RENDERING;
    } else if (value == ColorSpaceRole::kInterchangeScene) {
        return OCIO::ROLE_INTERCHANGE_SCENE;
    } else if (value == ColorSpaceRole::kInterchangeDisplay) {
        return OCIO::ROLE_INTERCHANGE_DISPLAY;
    } else {
        MMSOLVER_CORE_ERR(
            std::cerr,
            "mmcolorio: color_space_role_convert_mmcolorio_to_ocio: "
            "Invalid mmcolorio::ColorSpaceRole: "
                << static_cast<uint32_t>(value));
    }
    return OCIO::ROLE_DEFAULT;
}

const char *get_role_color_space_name(const ColorSpaceRole role) {
    const bool verbose = false;

    try {
        OCIO::ConstConfigRcPtr config = get_config();
        if (!config) {
            MMSOLVER_CORE_ERR(
                std::cerr,
                "mmcolorio: get_role_color_space_name: config is null.");
            return "";
        }

        const char *role_name =
            color_space_role_convert_mmcolorio_to_ocio(role);
        MMSOLVER_CORE_VRB(std::cout,
                          "mmcolor: get_role_color_space_name: role_name=\""
                              << role_name << "\"");

        OCIO::ConstColorSpaceRcPtr role_color_space =
            config->getColorSpace(role_name);
        if (role_color_space) {
            return role_color_space->getName();
        }
    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: get_role_color_space_name: "
                          "OpenColorIO Error: "
                              << exception.what());
    }

    return "";
}

static OCIO::ColorSpaceVisibility
color_space_visibility_convert_mmcolorio_to_ocio(
    const ColorSpaceVisibility value) {
    if (value == ColorSpaceVisibility::kActive) {
        return OCIO::ColorSpaceVisibility::COLORSPACE_ACTIVE;
    } else if (value == ColorSpaceVisibility::kInactive) {
        return OCIO::ColorSpaceVisibility::COLORSPACE_INACTIVE;
    } else if (value == ColorSpaceVisibility::kAll) {
        return OCIO::ColorSpaceVisibility::COLORSPACE_ALL;
    } else {
        MMSOLVER_CORE_ERR(
            std::cerr,
            "mmcolorio: color_space_visibility_convert_mmcolorio_to_ocio: "
            "Invalid mmcolorio::ColorSpaceVisibility: "
                << static_cast<uint32_t>(value));
    }
    return OCIO::ColorSpaceVisibility::COLORSPACE_ALL;
}

std::vector<std::string> get_color_space_names(
    const ColorSpaceVisibility visibility) {
    try {
        OCIO::ConstConfigRcPtr config = get_config();

        auto names = std::vector<std::string>();
        if (!config) {
            MMSOLVER_CORE_ERR(
                std::cerr, "mmcolorio: get_color_space_names: config is null.");
            return names;
        }

        const auto searchReferenceType =
            OCIO::SearchReferenceSpaceType::SEARCH_REFERENCE_SPACE_SCENE;

        const auto ocio_visibility =
            color_space_visibility_convert_mmcolorio_to_ocio(visibility);

        const int32_t num_color_spaces =
            config->getNumColorSpaces(searchReferenceType, ocio_visibility);

        for (auto i = 0; i < num_color_spaces; i++) {
            std::string color_space_name =
                std::string(config->getColorSpaceNameByIndex(i));
            names.push_back(color_space_name);
        }

        return names;
    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: get_color_space_names: "
                          "OpenColorIO Error: "
                              << exception.what());
    }

    auto names = std::vector<std::string>();
    return names;
}

void generate_shader_text(const char *input_color_space_name,
                          const char *output_color_space_name,
                          std::string &out_shader_text) {
    const bool verbose = false;

    MMSOLVER_CORE_VRB(
        std::cout, "mmcolorio: generate_shader_text: input_color_space_name=\""
                       << input_color_space_name << "\".");
    MMSOLVER_CORE_VRB(
        std::cout, "mmcolorio: generate_shader_text: output_color_space_name=\""
                       << output_color_space_name << "\".");

    mmsolver::debug::TimestampBenchmark timer_total;
    timer_total.start();

    out_shader_text.clear();
    try {
        OCIO::ConstConfigRcPtr config = get_config();
        if (!config) {
            MMSOLVER_CORE_ERR(
                std::cerr, "mmcolorio: generate_shader_text: config is null.");
            return;
        }

        OCIO::ConstColorSpaceRcPtr input_color_space =
            config->getColorSpace(input_color_space_name);
        OCIO::ConstColorSpaceRcPtr output_color_space =
            config->getColorSpace(output_color_space_name);

        OCIO::ConstProcessorRcPtr processor =
            config->getProcessor(input_color_space, output_color_space);

        // NOTE: Cache ID will change when the processor values
        // change.
        MMSOLVER_CORE_VRB(
            std::cout, "mmcolor: generate_shader_text: processor cache id: \""
                           << processor->getCacheID() << "\"");

        OCIO::OptimizationFlags oFlags =
            OCIO::OptimizationFlags::OPTIMIZATION_DEFAULT;
        OCIO::ConstGPUProcessorRcPtr gpu_processor =
            processor->getOptimizedGPUProcessor(oFlags);

        // unsigned edgelen = 32;
        // OCIO::ConstGPUProcessorRcPtr gpu_processor =
        //     processor->getOptimizedLegacyGPUProcessor(oFlags, edgelen);

        // NOTE: Cache ID will change when the gpu_processor values
        // change.
        MMSOLVER_CORE_VRB(
            std::cout, "mmcolor: generate_shader_text: processor cache id: \""
                           << gpu_processor->getCacheID() << "\"");

        // OCIO::GpuShaderDescRcPtr shader_desc =
        // OCIO::GpuShaderDesc::Create();
        OCIO::GpuShaderDescRcPtr shader_desc =
            OCIO::GpuShaderDesc::CreateShaderDesc();  // ->clone()
        // OCIO::GPU_LANGUAGE_GLSL_1_2
        // OCIO::GPU_LANGUAGE_GLSL_1_3
        // OCIO::GPU_LANGUAGE_GLSL_4_0
        // OCIO::GPU_LANGUAGE_GLSL_ES_1_0
        // OCIO::GPU_LANGUAGE_GLSL_ES_3_0
        shader_desc->setLanguage(OCIO::GPU_LANGUAGE_GLSL_4_0);
        shader_desc->setFunctionName("OCIODisplay");
        shader_desc->setResourcePrefix("ocio_");
        shader_desc->finalize();
        gpu_processor->extractGpuShaderInfo(shader_desc);

        MMSOLVER_CORE_VRB(
            std::cout,
            "mmcolor: generate_shader_text: shader desc unique id: \""
                << shader_desc->getUniqueID() << "\"");
        MMSOLVER_CORE_VRB(
            std::cout,
            "mmcolor: generate_shader_text: shader desc pixel name: \""
                << shader_desc->getPixelName() << "\"");

        // NOTE: Cache ID will change when the shader_desc values
        // change.
        MMSOLVER_CORE_VRB(
            std::cout, "mmcolor: generate_shader_text: shader desc cache id: \""
                           << shader_desc->getCacheID() << "\"");
        MMSOLVER_CORE_VRB(std::cout,
                          "mmcolor: generate_shader_text: shader desc "
                          "texture max width: "
                              << shader_desc->getTextureMaxWidth());
        MMSOLVER_CORE_VRB(std::cout,
                          "mmcolor: generate_shader_text: shader desc "
                          "num dynamic properties: "
                              << shader_desc->getNumDynamicProperties());
        MMSOLVER_CORE_VRB(std::cout,
                          "mmcolor: generate_shader_text: shader desc "
                          "num uniform: "
                              << shader_desc->getNumUniforms());
        MMSOLVER_CORE_VRB(std::cout,
                          "mmcolor: generate_shader_text: shader desc "
                          "num textures: "
                              << shader_desc->getNumTextures());
        MMSOLVER_CORE_VRB(std::cout,
                          "mmcolor: generate_shader_text: shader desc "
                          "num 3d textures: "
                              << shader_desc->getNum3DTextures());

        const char *shader_text = shader_desc->getShaderText();
        MMSOLVER_CORE_VRB(std::cout,
                          "mmcolor: generate_shader_text: shader text start:");
        MMSOLVER_CORE_VRB(std::cout, shader_text);
        MMSOLVER_CORE_VRB(std::cout,
                          "mmcolor: generate_shader_text: shader text end.");
        out_shader_text += shader_text;

        // TODO: Work out how to get and upload all the shader
        // and texture information.

        // const unsigned numUniforms = shader_desc->getNumUniforms();
        // const unsigned numTextures = shader_desc->getNumTextures();
        // const unsigned num3dTextures = shader_desc->getNum3DTextures();
        // shader_desc->get3DTexture(index, textureName, samplerName,
        // edgelen, interpolation);

    } catch (OCIO::Exception &exception) {
        MMSOLVER_CORE_ERR(std::cerr,
                          "mmcolorio: generate_shader_text: OpenColorIO Error: "
                              << exception.what());
    }

    timer_total.stop();

    MMSOLVER_CORE_VRB(std::cout, "mmcolor: generate_shader_text: timer_total: "
                                     << timer_total.get_seconds()
                                     << " seconds");

    return;
}

}  // namespace mmcolorio
