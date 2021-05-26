#%%global git_commit c52f3f41806622c95573de21be042f966f675543
#%%global git_date 201904023

#%%global git_short_commit %%(echo %{git_commit} | cut -c -8)
#%%global git_suffix %%{git_date}git%{git_short_commit}

# By default include binary_firmware, otherwise try to rebuild
# the firmware from sources. If you want to rebuild all firmware
# images you need to install appropriate tools (e.g. Xilinx ISE).
%bcond_without binary_firmware

# By default do not build with wireshark support, it's currently
# broken (upstream ticket #268)
%bcond_with wireshark

# NEON support is by default disabled on ARMs
# building with --with=neon will enable auto detection
%bcond_with neon

%global wireshark_dissectors chdr zpu octoclock
%global wireshark_ver %((%{__awk} '/^#define VERSION[ \t]+/ { print $NF }' /usr/include/wireshark/config.h 2>/dev/null||echo none)|/usr/bin/tr -d '"')

%ifarch %{arm} aarch64
%if ! %{with neon}
%global have_neon -DHAVE_ARM_NEON_H=0
%endif
%endif


Name:           uhd
URL:            http://github.com/pervices/uhd
Version:        3.13.0.0
Release:        master
License:        GPLv3+
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  boost-python3-devel, libusb1-devel, python3-cheetah, ncurses-devel
BuildRequires:  python3-docutils, doxygen, pkgconfig, libpcap-devel
BuildRequires:  python3-numpy, vim-common
%if %{with wireshark}
BuildRequires:  wireshark-devel
%endif
BuildRequires:  python3-mako, python3-requests, python3-devel, tar
%if ! %{with binary_firmware}
BuildRequires:  sdcc sed
%endif
Requires(pre):  shadow-utils, glibc-common
Requires:       python3-tkinter
Summary:        Universal Hardware Driver for Ettus Research products
#Source0:       %%{url}/archive/v%%{version}/uhd-%%{version}.tar.gz
Source0:        %{url}/archive/refs/heads/master.tar.gz

%description
The UHD is the universal hardware driver for Ettus Research products.
The goal of the UHD is to provide a host driver and API for current and
future Ettus Research products. It can be used standalone without GNU Radio.

%package firmware
Summary:        Firmware files for UHD
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description firmware
Firmware files for the Universal Hardware driver (UHD).

%package devel
Summary:        Development files for UHD
Requires:       %{name} = %{version}-%{release}

%description devel
Development files for the Universal Hardware Driver (UHD).

%package doc
Summary:        Documentation files for UHD
BuildArch:      noarch

%description doc
Documentation for the Universal Hardware Driver (UHD).

%package tools
Summary:        Tools for working with / debugging USRP device
Requires:       %{name} = %{version}-%{release}

%description tools
Tools that are useful for working with and/or debugging USRP device.

%if %{with wireshark}
%package wireshark
Summary:        Wireshark dissector plugins
Requires:       %{name} = %{version}-%{release}
Requires:       wireshark = %{wireshark_ver}

%description wireshark
Wireshark dissector plugins.
%endif

%prep
%setup -q -n %{name}-master


# fix python shebangs
find . -type f -name "*.py" -exec sed -i '/^#!/ s|.*|#!%{__python3}|' {} \;

%build
# firmware
%if ! %{with binary_firmware}
# rebuilt from sources
export PATH=$PATH:%{_libexecdir}/sdcc
pushd images
sed -i '/-name "\*\.twr" | xargs grep constraint | grep met/ s/^/#/' Makefile
make %{?_smp_mflags} images
popd
%endif

mkdir -p host/build
pushd host/build
%cmake %{?have_neon} -DLIB_SUFFIX="/$(DEB_HOST_MULTIARCH)" -DPKG_LIB_DIR="/usr/lib/uhd" -DUHD_RELEASE_MODE="release" -DENABLE_CRIMSON_TNG="ON" -DENABLE_PYTHON3="ON" -DENABLE_CYAN_16T="OFF" -DENABLE_CYAN_64T="OFF" -DENABLE_CYAN_P1HDR16T="OFF" -D Boost_NO_BOOST_CMAKE:BOOL="0" -DBOOST_PYTHON_COMPONENT="python38" -DENABLE_TESTS="OFF" -DENABLE_N230="OFF"  -DENABLE_N300="OFF"  -DENABLE_E320="OFF" -DENABLE_USRP1="OFF" -DENABLE_B200="OFF" -DENABLE_X300="OFF" -DENABLE_OCTOCLOCK="OFF" -DENABLE_DOXYGEN="OFF" -DENABLE_USB="OFF"   \
 ../
make %{?_smp_mflags}
#make -j1
popd

# tools
pushd tools/uhd_dump
make %{?_smp_mflags} CFLAGS="%{optflags}" LDFLAGS="%{?__global_ldflags}"
popd

%if %{with wireshark}
# wireshark dissectors
pushd tools/dissectors
for d in %{wireshark_dissectors}
do
  mkdir "build_$d"
  pushd "build_$d"
  %cmake -DETTUS_DISSECTOR_NAME="$d" ../
  make %{?_smp_mflags}
  popd
done
popd
%endif

#%%check
#cd host/build
#make test

%install
# fix python shebangs (run again for generated scripts)
find . -type f -name "*.py" -exec sed -i '/^#!/ s|.*|#!%{__python3}|' {} \;

pushd host/build
make install DESTDIR=%{buildroot}

# Remove tests, examples binaries
rm -rf %{buildroot}%{_libdir}/uhd/{tests,examples}

popd
# Package base docs to base package
mkdir _tmpdoc
mv %{buildroot}%{_docdir}/%{name}/{LICENSE,README.md} _tmpdoc


# remove win stuff
rm -rf %{buildroot}%{_datadir}/uhd/images/winusb_driver

# convert hardlinks to symlinks (to not package the file twice)
pushd %{buildroot}%{_bindir}
for f in uhd_images_downloader usrp2_card_burner
do
  unlink $f
  ln -s ../..%{_libexecdir}/uhd/${f}.py $f
done
popd

# tools
install -Dpm 0755 tools/usrp_x3xx_fpga_jtag_programmer.sh %{buildroot}%{_bindir}/usrp_x3xx_fpga_jtag_programmer.sh
install -Dpm 0755 tools/uhd_dump/chdr_log %{buildroot}%{_bindir}/chdr_log

%if %{with wireshark}
# wireshark dissectors
pushd tools/dissectors
for d in %{wireshark_dissectors}
do
  pushd "build_$d"
  %make_install
  popd
done
popd
mv %{buildroot}${HOME}/.wireshark %{buildroot}%{_libdir}/wireshark
%endif

%ldconfig_scriptlets

%pre
getent group usrp >/dev/null || \
  %{_sbindir}/groupadd -r usrp >/dev/null 2>&1
exit 0

%files
%doc _tmpdoc/*
%{_bindir}/uhd_*
%{_bindir}/usrp2_*
%{_mandir}/man1/*.1*
%{_datadir}/uhd
%{python3_sitearch}/uhd

%files firmware
%dir %{_datadir}/uhd/images
%{_datadir}/uhd/images/*

%files devel
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/cmake/uhd/*.cmake
%{_libdir}/pkgconfig/*.pc

%files doc
%doc %{_docdir}/%{name}/doxygen

%files tools
%doc tools/README.md
%{_bindir}/usrp_x3xx_fpga_jtag_programmer.sh
%{_bindir}/chdr_log

%if %{with wireshark}
%files wireshark
%{_libdir}/wireshark/plugins/*
%endif

%changelog
