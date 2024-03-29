file(COPY ${CMAKE_SOURCE_DIR}/examples/iris.dat DESTINATION ${CMAKE_BINARY_DIR}/examples)
file(COPY ${CMAKE_SOURCE_DIR}/examples/Equirectangular-projection.jpg DESTINATION ${CMAKE_BINARY_DIR}/examples)
add_executable(mgl_example wnd_samples.cpp full_test.cpp samples.cpp)
target_link_libraries(mgl_example mgl-static ${getopt_lib-static})

if(MGL_HAVE_FLTK)
	include_directories(${FLTK_INCLUDE_DIR})
	add_executable(mgl_fltk_example wnd_samples.cpp fltk_example.cpp)
	target_link_libraries(mgl_fltk_example mgl-fltk)
endif(MGL_HAVE_FLTK)

if(MGL_HAVE_GLUT)
	add_executable(mgl_glut_example wnd_samples.cpp glut_example.cpp)
	target_link_libraries(mgl_glut_example mgl-glut)
endif(MGL_HAVE_GLUT)

if(MGL_HAVE_WX)
	include(${wxWidgets_USE_FILE})
	add_executable(mgl_wx_example wnd_samples.cpp wx_example.cpp)
	target_link_libraries(mgl_wx_example mgl-wx)
endif(MGL_HAVE_WX)

if(QT_ENABLED)
	add_executable(mgl_qt_example wnd_samples.cpp qt_example.cpp)
	if(enable-qt5)
		include(../scripts/qt5.cmake)
		target_link_libraries(mgl_qt_example mgl-qt5)
	else(enable-qt5)
		include(../scripts/qt4.cmake)
		target_link_libraries(mgl_qt_example mgl-qt4)
	endif(enable-qt5)
	
	if(MGL_HAVE_OPENGL)
		add_executable(mgl_qgl_example wnd_samples.cpp qgl_example.cpp)
		if(enable-qt5)
			target_link_libraries(mgl_qgl_example mgl ${MGL_QT5_LIBS})
		else(enable-qt5)
			target_link_libraries(mgl_qgl_example mgl ${MGL_QT4_LIBS})
		endif(enable-qt5)
	endif(MGL_HAVE_OPENGL)
endif(QT_ENABLED)

if(MGL_HAVE_LTDL)
	add_library(mgl_module MODULE mgl_module.cpp)
	target_link_libraries(mgl_module mgl)	# for compatibility with win32
endif(MGL_HAVE_LTDL)

