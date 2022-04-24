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

#include "ImagePlaneGeometryOverride.h"

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>

// Maya
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MEventMessage.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MPoint.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>
#include <maya/MPxGeometryOverride.h>
#include <maya/MShaderManager.h>
#include <maya/MUserData.h>
#include <maya/MGeometryExtractor.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {

const MString renderItemName_imagePlaneWireframe = MString("imagePlaneWireframe");
const MString renderItemName_imagePlaneShaded = MString("imagePlaneShaded");

ImagePlaneGeometryOverride::ImagePlaneGeometryOverride(const MObject &obj)
        : MHWRender::MPxGeometryOverride(obj)
        , m_this_node(obj)
        , m_geometry_node_type(MFn::kInvalid) {}

ImagePlaneGeometryOverride::~ImagePlaneGeometryOverride() {}

MHWRender::DrawAPI
ImagePlaneGeometryOverride::supportedDrawAPIs() const {
    return (MHWRender::kOpenGL
            | MHWRender::kDirectX11
            | MHWRender::kOpenGLCoreProfile);
}

bool getUpstreamNodeFromConnection(
    const MObject &this_node,
    const MString &attr_name,
    MPlugArray &out_connections
) {
    MStatus status;
    MFnDependencyNode mfn_depend_node(this_node);

    bool wantNetworkedPlug = true;
    MPlug message_plug = mfn_depend_node.findPlug(
        attr_name,
        wantNetworkedPlug,
        &status);
    if (status != MStatus::kSuccess) {
        CHECK_MSTATUS(status);
        return false;
    }
    if (message_plug.isNull()) {
        MMSOLVER_WRN(
            "Could not get plug for \""
            << mfn_depend_node.name()
            << "." << attr_name.asChar() << "\" node.");
        return false;
    }

    bool as_destination = true;
    bool as_source = false;
    // Ask for plugs connecting to this node's ".shaderNode"
    // attribute.
    message_plug.connectedTo(
        out_connections,
        as_destination,
        as_source,
        &status);
    if (status != MStatus::kSuccess) {
        CHECK_MSTATUS(status);
        return false;
    }
    if (out_connections.length() == 0) {
        MMSOLVER_WRN(
            "No connections to the \""
            << mfn_depend_node.name()
            << "." << attr_name.asChar() << "\" attribute.");
        return false;
    }
    return true;
}

void ImagePlaneGeometryOverride::updateDG() {
    if (!m_geometry_node_path.isValid()) {
        MString attr_name = "geometryNode";
        MPlugArray connections;
        bool ok = getUpstreamNodeFromConnection(
            m_this_node,
            attr_name,
            connections);

        if (ok) {
            for (uint32_t i = 0; i < connections.length(); ++i) {
                MObject node = connections[i].node();

                if (node.hasFn(MFn::kMesh))
                {
                    MDagPath path;
                    MDagPath::getAPathTo(node, path);
                    m_geometry_node_path = path;
                    m_geometry_node_type = path.apiType();
                    // MMSOLVER_INFO(
                    //     "Validated geometry node: "
                    //     << " path=" << m_geometry_node_path.fullPathName().asChar()
                    //     << " type=" << node.apiTypeStr());
                    break;
                } else {
                    MMSOLVER_WRN(
                        "Geometry node is not correct type:"
                        << " path=" << m_geometry_node_path.fullPathName().asChar()
                        << " type=" << node.apiTypeStr());
                }
            }
        }
    }

    if (m_shader_node.isNull()) {
        MString attr_name = "shaderNode";
        MPlugArray connections;
        bool ok = getUpstreamNodeFromConnection(
            m_this_node,
            attr_name,
            connections);

        if (ok) {
            for (uint32_t i = 0; i < connections.length(); ++i) {
                MObject node = connections[i].node();

                MFnDependencyNode mfn_depend_node(node);
                if (node.hasFn(MFn::kSurfaceShader)
                    || node.hasFn(MFn::kHwShaderNode)
                    || node.hasFn(MFn::kPluginHardwareShader)
                    || node.hasFn(MFn::kPluginHwShaderNode))
                {
                    m_shader_node = node;
                    m_shader_node_type = node.apiType();
                    // MMSOLVER_INFO(
                    //     "Validated shader node:"
                    //     << " name=" << mfn_depend_node.name().asChar()
                    //     << " type=" << node.apiTypeStr());
                    break;
                } else {
                    MMSOLVER_WRN(
                        "Shader node is not correct type: "
                        << " name=" << mfn_depend_node.name().asChar()
                        << " type=" << node.apiTypeStr());
                }
            }
        }
    }
}

void ImagePlaneGeometryOverride::updateRenderItems(
    const MDagPath &path,
    MRenderItemList &list
) {
    if (!m_geometry_node_path.isValid()) {
        // MMSOLVER_WRN("mmImagePlaneShape: Geometry node DAG path is not valid.");
        return;
    }

    MRenderer *renderer = MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_WRN("mmImagePlaneShape: Could not get MRenderer.");
        return;
    }

    const MShaderManager *shaderManager = renderer->getShaderManager();
    if (!shaderManager) {
        MMSOLVER_WRN("mmImagePlaneShape: Could not get MShaderManager.");
        return;
    }

    if (m_geometry_node_type != MFn::kMesh)  {
        MMSOLVER_WRN(
            "mmImagePlaneShape: Only Meshes are supported, geometry node given is not a mesh.");
        return;
    }

    bool draw_wireframe = false;
    int index = 0;

    MRenderItem *wireframeItem = nullptr;
    if (draw_wireframe) {
        // Add render item for drawing wireframe on the mesh
        index = list.indexOf(renderItemName_imagePlaneWireframe);
        if (index >= 0){
            wireframeItem = list.itemAt(index);
        } else {
            // MMSOLVER_INFO("mmImagePlaneShape: Generate wireframe MRenderItem...");
            wireframeItem = MRenderItem::Create(
                renderItemName_imagePlaneWireframe,
                MRenderItem::DecorationItem,
                MGeometry::kLines);

            // auto draw_mode = MGeometry::kWireframe;
            // auto draw_mode = MGeometry::kShaded;
            // auto draw_mode = MGeometry::kTextured;
            // auto draw_mode = MGeometry::kBoundingBox;
            // // Draw only for selection - not visible in viewport -
            // // can be combined with wire/shaded to further restrict
            // // draw modes.
            // auto draw_mode = MGeometry::kSelectionOnly;
            // // Draw only if selection highlighting is enabled - can
            // // be combined with wire/shaded to further restrict
            // // draw modes.
            // auto draw_mode = MGeometry::kSelectionHighlighting;
            auto draw_mode = MGeometry::kAll;  // Draw in all visible modes.
            wireframeItem->setDrawMode(draw_mode);

            // auto depth_priority = MRenderItem::sDormantFilledDepthPriority;
            // auto depth_priority = MRenderItem::sDormantWireDepthPriority;
            // auto depth_priority = MRenderItem::sHiliteWireDepthPriority;
            auto depth_priority = MRenderItem::sActiveWireDepthPriority;
            // auto depth_priority = MRenderItem::sDormantPointDepthPriority;
            // auto depth_priority = MRenderItem::sActivePointDepthPriority;
            wireframeItem->depthPriority(depth_priority);

            list.append(wireframeItem);

            MShaderInstance *shader = shaderManager->getStockShader(
                MShaderManager::k3dSolidShader);
            if (shader) {
                static const float theColor[] = {1.0f, 0.0f, 0.0f, 1.0f};
                shader->setParameter("solidColor", theColor);
                wireframeItem->setShader(shader);
                shaderManager->releaseShader(shader);
            }
        }
    }

    // Add render item for drawing shaded on the mesh
    MRenderItem *shadedItem = nullptr;
    index = list.indexOf(renderItemName_imagePlaneShaded);
    if (index >= 0){
        shadedItem = list.itemAt(index);
    } else {
        // MMSOLVER_INFO("mmImagePlaneShape: Generate shaded MRenderItem...");
        shadedItem = MRenderItem::Create(
                renderItemName_imagePlaneShaded,
                MRenderItem::NonMaterialSceneItem,
                MGeometry::kTriangles);

        // auto draw_mode = MGeometry::kWireframe;
        // auto draw_mode = MGeometry::kShaded;
        // auto draw_mode = MGeometry::kTextured;
        // auto draw_mode = MGeometry::kBoundingBox;
        // // Draw only for selection - not visible in viewport -
        // // can be combined with wire/shaded to further restrict
        // // draw modes.
        // auto draw_mode = MGeometry::kSelectionOnly;
        // // Draw only if selection highlighting is enabled - can
        // // be combined with wire/shaded to further restrict
        // // draw modes.
        // auto draw_mode = MGeometry::kSelectionHighlighting;
        auto draw_mode = MGeometry::kAll;  // Draw in all visible modes.
        shadedItem->setDrawMode(draw_mode);

        // auto depth_priority = MRenderItem::sDormantFilledDepthPriority;
        auto depth_priority = MRenderItem::sDormantWireDepthPriority;
        // auto depth_priority = MRenderItem::sHiliteWireDepthPriority;
        // auto depth_priority = MRenderItem::sActiveWireDepthPriority;
        // auto depth_priority = MRenderItem::sDormantPointDepthPriority;
        // auto depth_priority = MRenderItem::sActivePointDepthPriority;
        shadedItem->depthPriority(depth_priority);

        list.append(shadedItem);

        // Apply shader.
        if (!m_shader_node.isNull()) {
            // TODO: Implement callback to detect when the shader
            // needs to be re-compiled.
            auto linkLostCb = nullptr;
            auto linkLostUserData = nullptr;
            bool nonTextured = false;
            shadedItem->setShaderFromNode(
                m_shader_node,
                m_geometry_node_path,
                linkLostCb,
                linkLostUserData,
                nonTextured);
        } else {
            MMSOLVER_WRN(
                "mmImagePlaneShape: Shader node is not valid, using fallback blue shader.");
            MShaderInstance *shader = shaderManager->getStockShader(
                MShaderManager::k3dSolidShader);
            if (shader) {
                static const float theColor[] = {0.0f, 0.0f, 1.0f, 1.0f};
                shader->setParameter("solidColor", theColor);
                shadedItem->setShader(shader);
                shaderManager->releaseShader(shader);
            }
        }
    }

    if (shadedItem) {
        shadedItem->enable(true);
    }
    if (wireframeItem) {
        wireframeItem->enable(true);
    }
}

void ImagePlaneGeometryOverride::populateGeometry(
    const MGeometryRequirements &requirements,
    const MRenderItemList &renderItems,
    MGeometry &data
) {
    if (!m_geometry_node_path.isValid()) {
        // MMSOLVER_WRN("mmImagePlaneShape: Geometry node DAG path is not valid.");
        return;
    }

    MStatus status;

    // kPolyGeom_Normal = Normal Indicates the polygon performs the
    // default geometry.
    //
    // kPolyGeom_NotSharing = NotSharing Indicates if you don't want
    // vertex sharing to be computed by the extractor. Vertex buffer
    // size will not be reduced if sharing can be performed.
    //
    // kPolyGeom_BaseMesh = BaseMesh Indicates if you want the base
    // geometry in smoothCage mode. The geometry in extractor is
    // always the base geometry in normal mode.
    MHWRender::MPolyGeomOptions polygon_geometry_options =
        MHWRender::kPolyGeom_Normal
        | MHWRender::kPolyGeom_BaseMesh;

    MGeometryExtractor extractor(
        requirements,
        m_geometry_node_path,
        polygon_geometry_options,
        &status);
    if (status == MS::kFailure) {
        CHECK_MSTATUS(status);
        return;
    }

    const MVertexBufferDescriptorList &descList = requirements.vertexRequirements();
    for (int reqNum = 0; reqNum < descList.length(); ++reqNum) {
        MVertexBufferDescriptor desc;
        if (!descList.getDescriptor(reqNum, desc)) {
            continue;
        }

        auto desc_semantic = desc.semantic();
        if ((desc_semantic == MGeometry::kPosition)
            || (desc_semantic == MGeometry::kNormal)
            || (desc_semantic == MGeometry::kTexture)
            || (desc_semantic == MGeometry::kTangent)
            || (desc_semantic == MGeometry::kBitangent)
            || (desc_semantic == MGeometry::kColor))
        {
            MVertexBuffer *vertexBuffer = data.createVertexBuffer(desc);
            if (vertexBuffer) {
                // MGeometryExtractor::vertexCount and
                // MGeometryExtractor::populateVertexBuffer.  since
                // the plugin node has the same vertex data as its
                // linked scene object, call vertexCount to allocate
                // vertex buffer of the same size, and then call
                // populateVertexBuffer to copy the data.
                uint32_t vertexCount = extractor.vertexCount();
                bool writeOnly = true;  // We don't need the current buffer values.
                float *data = static_cast<float*>(
                    vertexBuffer->acquire(
                        vertexCount,
                        writeOnly));
                if (data) {
                    status = extractor.populateVertexBuffer(data, vertexCount, desc);
                    if (status == MS::kFailure)
                        return;
                    vertexBuffer->commit(data);
                }
            }
        }
    }

    for (int i = 0; i < renderItems.length(); ++i) {
        const MRenderItem *item = renderItems.itemAt(i);
        if (!item) {
            continue;
        }

        MIndexBuffer *indexBuffer = data.createIndexBuffer(MGeometry::kUnsignedInt32);
        if (!indexBuffer) {
            continue;
        }

        if (item->primitive() == MGeometry::kTriangles) {
            MIndexBufferDescriptor triangleDesc(
                MIndexBufferDescriptor::kTriangle,
                MString(),
                MGeometry::kTriangles,
                3);
            uint32_t numTriangles = extractor.primitiveCount(triangleDesc);
            bool writeOnly = true;  // We don't need the current buffer values.
            uint32_t *indices = static_cast<uint32_t*>(
                indexBuffer->acquire(
                    3 * numTriangles,
                    writeOnly));

            status = extractor.populateIndexBuffer(
                indices,
                numTriangles,
                triangleDesc);
            if (status == MS::kFailure) {
                return;
            }
            indexBuffer->commit(indices);
        } else if (item->primitive() == MGeometry::kLines) {
            MIndexBufferDescriptor edgeDesc(
                MIndexBufferDescriptor::kEdgeLine,
                MString(),
                MGeometry::kLines,
                2);
            uint32_t numEdges = extractor.primitiveCount(edgeDesc);
            bool writeOnly = true;  // We don't need the current buffer values.
            uint32_t *indices = static_cast<uint32_t*>(
                indexBuffer->acquire(
                    2 * numEdges,
                    writeOnly));

            status = extractor.populateIndexBuffer(
                indices,
                numEdges,
                edgeDesc);
            if (status == MS::kFailure) {
                return;
            }
            indexBuffer->commit(indices);
        }

        item->associateWithIndexBuffer(indexBuffer);
    }
}

void ImagePlaneGeometryOverride::cleanUp() {}

bool ImagePlaneGeometryOverride::requiresGeometryUpdate() const
{
    return true;  // Always update the geometry.
}

bool ImagePlaneGeometryOverride::hasUIDrawables() const {return false;}

void ImagePlaneGeometryOverride::addUIDrawables(
    const MDagPath &path,
    MUIDrawManager &drawManager,
    const MFrameContext &frameContext
) {
    // drawManager.beginDrawable();
    // drawManager.setColor(MColor(1.0f, 0.0f, 0.0f));
    // drawManager.text(MPoint(0, 0, 0), MString("Replicate"));
    // drawManager.endDrawable();
}


} // namespace mmsolver
