install(FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/mmCopy.ogsfx
  ${CMAKE_CURRENT_SOURCE_DIR}/mmDepth.ogsfx
  ${CMAKE_CURRENT_SOURCE_DIR}/mmEdge.ogsfx
  ${CMAKE_CURRENT_SOURCE_DIR}/mmLayerMerge.ogsfx
  ${CMAKE_CURRENT_SOURCE_DIR}/mmSilhouette.ogsfx
  ${CMAKE_CURRENT_SOURCE_DIR}/mmImagePlane.ogsfx
  ${CMAKE_CURRENT_SOURCE_DIR}/ocgImagePlaneSolid.ogsfx
  ${CMAKE_CURRENT_SOURCE_DIR}/ocgImagePlaneTextured.ogsfx
  DESTINATION "${MODULE_FULL_NAME}/shader")
