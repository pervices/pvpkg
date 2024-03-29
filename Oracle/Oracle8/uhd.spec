%ifarch aarch64
%bcond_without neon
%else
%bcond_with neon
%endif
%undefine _annotated_build
%undefine _hardened_build
%ifarch %{arm}
%if %{with neon}
%global my_optflags %(echo -n "%{optflags}" | sed 's/-mfpu=[^ \\t]\\+//g'; echo " -mfpu=neon")
%{expand: %global optflags %{my_optflags}}
%global mfpu_neon -Dhave_mfpu_neon=1
%else
%global mfpu_neon -Dhave_mfpu_neon=0
%endif
%endif

#Disable generation of the debug packages because as we haven't quite figured out
#a way to package them that doesn't also cause rpm build issues.
%global debug_package %{nil}

Name:           uhd
URL:            http://github.com/pervices/uhd
Version:        3.13.0.0
Release:        master
License:        GPLv3+
Provides: uhd
Conflicts: uhd
BuildRequires:  gcc-toolset-11
BuildRequires:  cmake
BuildRequires:  boost-python3-devel, libusb1-devel, python3-cheetah, ncurses-devel
BuildRequires:  python3-docutils, doxygen, pkgconfig, libpcap-devel
BuildRequires:  python3-numpy, python3-tkinter, vim-common, octave, dpdk
%if %{with wireshark}
BuildRequires:  wireshark-devel
%endif
BuildRequires:  python3-mako, python3-requests, python3-devel, tar
%if ! %{with binary_firmware}
BuildRequires: sed
%endif
Requires(pre):  shadow-utils, glibc-common
Requires:       python3-tkinter
Summary:        Universal Hardware Driver for Ettus Research products
#Source0:       %%{url}/archive/v%%{version}/uhd-%%{version}.tar.gz
Source0:        uhd.tar.gz

%description
The UHD is the universal hardware driver for Ettus Research products.
The goal of the UHD is to provide a host driver and API for current and
future Ettus Research products. It can be used standalone without GNU Radio.


%prep
%setup -q -n %{name}


%build
source /opt/rh/gcc-toolset-11/enable
# fix python shebangs (run again for generated scripts)
find . -type f -name "*.py" -exec sed -i '/^#!/ s|.*|#!%{__python3}|' {} \;
mkdir -p host/build
pushd host/build
%cmake %{?have_neon} -DPKG_LIB_DIR="/usr/lib/uhd" -DENABLE_CRIMSON_TNG="ON" -DENABLE_CYAN_16T="ON" -DENABLE_CYAN_64T="OFF" -DENABLE_CYAN_P1HDR16T="ON" -DENABLE_CYAN_P1HDR32T="ON" -DENABLE_EXAMPLES="ON" -DENABLE_TESTS="OFF"  -DENABLE_N300="OFF"  -DENABLE_E320="OFF" -DENABLE_USRP1="OFF" -DENABLE_B200="OFF" -DENABLE_X300="OFF" -DENABLE_OCTOCLOCK="OFF" -DENABLE_DOXYGEN="OFF" -DENABLE_USB="OFF" -DENABLE_CYAN_8R="ON" -DENABLE_CYAN_4R4T="ON"  \
 ../
make %{?_smp_mflags}
#make -j1 
popd

# tools
#pushd tools/uhd_dump
#make %{?_smp_mflags} CFLAGS="%{optflags}" LDFLAGS="%{?__global_ldflags}"
#popd


#%%check
#cd host/build
#make test

%install
pushd host/build
make install DESTDIR=%{buildroot}

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
#install -Dpm 0755 tools/uhd_dump/chdr_log %{buildroot}%{_bindir}/chdr_log

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
%doc %{_docdir}/%{name}/doxygen
%{_includedir}/*
%{_bindir}/*
%{_mandir}/man1/*.1*
%{_datadir}/uhd
%{python3_sitearch}/uhd
%{python3_sitearch}/usrp_mpm/*
# %exclude /usr/lib/debug/*
/usr/lib/*
/usr/lib64/libuhd.*
/usr/lib64/cmake/*
/usr/lib64/pkgconfig/uhd.pc





%changelog
