
# Creating installers
if(APPLE)
    set(CPACK_GENERATOR TGZ)
    set(CPACK_SOURCE_GENERATOR TGZ)
elseif(UNIX)
    set(CPACK_GENERATOR DEB)
    set(CPACK_SOURCE_GENERATOR TGZ)
    set(CPACK_DEBIAN_PACKAGE_MAINTAINER "Jack Jansen")
    set(CPACK_DEBIAN_PACKAGE_PREDEPENDS "python3 (>=3.8), python3-pip (>=20.0)")
    set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS YES)
elseif(WIN32)
    set(CPACK_GENERATOR NSIS)
    set(CPACK_SOURCE_GENERATOR ZIP)
else()
    message(WARNING Cannot create packages for this system)
endif()
set(CPACK_PACKAGE_VENDOR "CWI DIS Group")
set(CPACK_PACKAGE_CONTACT "Jack.Jansen@cwi.nl")
set(CPACK_PACKAGE_VERSION ${CWIPC_VERSION})
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE.txt")
set(CPACK_RESOURCE_FILE_README "${CMAKE_CURRENT_SOURCE_DIR}/readme.md")
set(CPACK_OUTPUT_FILE_PREFIX "${CMAKE_CURRENT_BINARY_DIR}/package")
set(CPACK_PACKAGE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
string(TOLOWER ${CMAKE_SYSTEM_PROCESSOR} _arch)
string(TOLOWER ${CMAKE_SYSTEM_NAME} _sys)
string(TOLOWER ${PROJECT_NAME} _project_lower)
set(CPACK_PACKAGE_FILE_NAME "${_project_lower}-${CWIPC_VERSION}-${_sys}-${_arch}")
set(CPACK_SOURCE_PACKAGE_FILE_NAME "${_project_lower}-${CWIPC_VERSION}")

# not .gitignore as its regex syntax is distinct
file(READ ${CMAKE_CURRENT_LIST_DIR}/.cpack_ignore _cpack_ignore)
string(REGEX REPLACE "\n" ";" _cpack_ignore ${_cpack_ignore})
set(CPACK_SOURCE_IGNORE_FILES "${_cpack_ignore}")

install(FILES ${CPACK_RESOURCE_FILE_README} ${CPACK_RESOURCE_FILE_LICENSE}
  DESTINATION share/docs/${PROJECT_NAME})

include(CPack)
