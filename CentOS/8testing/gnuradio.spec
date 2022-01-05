%define _binaries_in_noarch_packages_terminate_build 0
%define _unpackaged_files_terminate_build 0
# NEON support is by default enabled on aarch64 and disabled on other ARMs (it can be overridden)
%ifarch aarch64
%bcond_without neon
%else
%bcond_with neon
%endif

%ifarch %{arm}
%if %{with neon}
%global my_optflags %(echo -n "%{optflags}" | sed 's/-mfpu=[^ \\t]\\+//g'; echo " -mfpu=neon")
%{expand: %global optflags %{my_optflags}}
%global mfpu_neon -Dhave_mfpu_neon=1
%else
%global mfpu_neon -Dhave_mfpu_neon=0
%endif
%endif

# For versions not yet on ftp, pull from git
#%%global git_commit 441a3767e05d15e62c519ea66b848b5adb0f4b3a

#%%global alphatag rc1

Name:		gnuradio
Version:	3.9
Release:	maint
Summary:	Software defined radio framework

License:	GPLv3
URL:		https://www.gnuradio.org/
#Source0:	http://gnuradio.org/releases/gnuradio/gnuradio-%%{version}%%{?alphatag}.tar.xz
#Source0:	http://gnuradio.org/releases/gnuradio/gnuradio-%%{version}.tar.gz
Source0:	https://github.com/pervices/%{name}/archive/refs/heads/gnuradio-maint-3.9.tar.gz
# git clone git://gnuradio.org/gnuradio
# cd gnuradio
# git archive --format=tar --prefix=%%{name}-%%{version}/ %%{git_commit} | \
# gzip > ../%%{name}-%%{version}.tar.gz

Requires(pre):	shadow-utils
Requires:	uhd
Requires:	volk
BuildRequires:	cmake
BuildRequires:	gcc-c++
BuildRequires:	libtool
BuildRequires:	alsa-lib-devel
BuildRequires:	boost-python3-devel
BuildRequires:	codec2-devel
BuildRequires:	cppzmq-devel
BuildRequires:	desktop-file-utils
BuildRequires:	doxygen
BuildRequires:	fftw-devel
BuildRequires:	findutils
BuildRequires:	gmp-devel
BuildRequires:	graphviz
BuildRequires:	gsl-devel
BuildRequires:	gsm-devel
BuildRequires:	gtk3-devel
BuildRequires:	jack-audio-connection-kit-devel
BuildRequires:	log4cpp-devel
BuildRequires:  libsndfile-devel
# mpir is not yet available on ppc64le
%ifnarch ppc64le
BuildRequires:	mpir-devel
%endif
BuildRequires:	orc-devel
BuildRequires:	portaudio-devel
BuildRequires:	python3-devel
BuildRequires:	python3-cairo
BuildRequires:	python3-cheetah
BuildRequires:	python3-click-plugins
BuildRequires:	python3-gobject
BuildRequires:	python3-numpy
BuildRequires:	python3-pyyaml
BuildRequires:	python3-lxml
BuildRequires:  python3-pybind11
BuildRequires:	python3-mako
BuildRequires:	python3-qt5-devel
BuildRequires:	python3-scipy
BuildRequires:	python3-matplotlib
BuildRequires:	python3-six
BuildRequires:	python3-sphinx
BuildRequires:	python3-thrift
BuildRequires:	qwt-qt5-devel
#BuildRequires:	tex(latex)
BuildRequires:	SDL-devel
BuildRequires:	swig
BuildRequires:	thrift
BuildRequires:	xdg-utils
BuildRequires:	xmlto
BuildRequires:	zeromq-devel
BuildRequires:	python3-gobject

Requires:	python3-%{name} = %{version}-%{release}
Requires:	python3-numpy
Requires:	python3-cheetah
Requires:	python3-thrift
%if ! 0%{?rhel}
Requires:	python3-pyopengl
%endif
Requires:	python3-pyyaml
Requires:	python3-gobject
Requires:	gtk3

%description
GNU Radio is a collection of software that when combined with minimal
hardware, allows the construction of radios where the actual waveforms
transmitted and received are defined by software. What this means is
that it turns the digital modulation schemes used in today's high
performance wireless devices into software problems.

%package -n python3-%{name}
Summary:	GNU Radio Python 3 module

%description -n python3-%{name}
GNU Radio Python 3 module

%package     -n libgnuradio
Summary:        Libraries for GNU Radio
Group:          System/Libraries

%description -n libgnuradio
Gnuradio libraries

%package devel
Summary:	GNU Radio
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	cmake
Requires:	boost-devel%{?_isa}

%description devel
GNU Radio Headers

%package doc
Summary:	GNU Radio
Requires:	%{name} = %{version}-%{release}

%description doc
GNU Radio Documentation

%package examples
Summary:	GNU Radio
Requires:	%{name} = %{version}-%{release}

%description examples
GNU Radio examples

%prep
%setup -q -n %{name}

%build
mkdir build
cd build
%cmake \
-DSYSCONFDIR=%{_sysconfdir} \
-DGR_PKG_DOC_DIR=%{_docdir}/%{name} \
-DGR_PYTHON_DIR=%{python3_sitearch} \
-DPYTHON_EXECUTABLE=%{__python3} \
%{?mfpu_neon} \
..
#-DENABLE_DOXYGEN=FALSE \

%make_build CFLAGS="%{optflags} -fno-strict-aliasing" CXXFLAGS="%{optflags} -fno-strict-aliasing"

%install
%make_install -C build
      
%post -n libgnuradio -p /sbin/ldconfig
%postun -n libgnuradio -p /sbin/ldconfig
%ldconfig_scriptlets

%files
%license COPYING
%{_bindir}/*
%{_datadir}/gnuradio
%config(noreplace) %{_sysconfdir}/gnuradio
%exclude %{_datadir}/gnuradio/examples
%exclude %{_docdir}/%{name}/html
%exclude %{_docdir}/%{name}/xml
%doc %{_docdir}/%{name}

%files -n libgnuradio
/usr/lib64/libgnuradio*.so.*

%files -n python3-%{name}
%{python3_sitearch}/%{name}/
%{python3_sitearch}/pmt/


%files devel
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%{_libdir}/cmake/gnuradio

%files doc
%doc %{_docdir}/%{name}/html
%doc %{_docdir}/%{name}/xml

%files examples
%{_datadir}/gnuradio/examples

%changelog
