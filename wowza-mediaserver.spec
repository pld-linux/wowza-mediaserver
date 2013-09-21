Summary:	Wowza Media Server
Name:		wowza-mediaserver
Version:	3.6.2
Release:	1
License:	Wowza EULA v3.6
Group:		Networking/Daemons
Source0:	http://www.wowza.com/downloads/WowzaMediaServer-3-6-2/WowzaMediaServer-%{version}.rpm.bin
# NoSource0-md5:	01aa5e93f3683de9affdab0c250716d8
NoSource:	0
URL:		http://www.wowza.com/
BuildRequires:	fakeroot
BuildRequires:	rpm-utils
BuildRequires:	rpmbuild(macros) >= 1.595
Requires:	jre
Conflicts:	WowzaMediaServer
ExclusiveArch:	%{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# already stripped
%define		_enable_debug_packages	0

# use same install path, not to go around fixing paths
%define		_appdir	%{_prefix}/local/WowzaMediaServer

# list of files (regexps) which don't generate Provides
%define		_noautoprovfiles	%{_appdir}/lib-native
%define		req_syslibs  		libgcc_s.so.1 libogg.so.0 libstdc++.so.6 libvorbis.so.0 libvorbisenc.so.2
%define		req_wms				libcudart.so.5.0 libcudawrapper.so libiomp5.so libmc_.*.so libwms-.*.so
#  libva.so.1(VA_API_0.34.0) does not solve currently in PLD
%define		_noautoreq  		%{req_wms} %{req_syslibs} 'libva.so.1\(VA_API_0.34.0\)\(64bit\)'

%description
Wowza Media Server.

%prep
%setup -qcT
ln -s %{SOURCE0} src.bin

sed -ne '/^tail -n +/ s/$0.*/"$1"/p' src.bin > extract.sh
sh extract.sh src.bin > src.rpm
rpm2cpio src.rpm | fakeroot cpio -i -d -m

mv usr/local/WowzaMediaServer-%{version} wowza
mv wowza/{examples,legal,documentation,README.html} .

# extract license
lineno=$(grep -n '^EOF$' src.bin | cut -d: -f1)
head -n +$((lineno + 1)) src.bin | sed -ne '/EOF/,/^EOF$/p' | grep -v EOF > LICENSE.txt

%ifos Linux
rm wowza/bin/WowzaMediaServerOSX
rm wowza/bin/com.wowza.WowzaMediaServer.plist
%endif

%post
%banner -e -o <<EOF

Install Location: %{_appdir}

To get license key, visit http://www.wowza.com/pricing

To enter license key:
  cd %{_prefix}/local/WowzaMediaServer/bin
  ./startup.sh
EOF

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_bindir},%{_appdir}}

install -p etc/init.d/WowzaMediaServer $RPM_BUILD_ROOT/etc/rc.d/init.d
install -p usr/bin/WowzaMediaServerd $RPM_BUILD_ROOT%{_bindir}
cp -a wowza/* $RPM_BUILD_ROOT%{_appdir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc LICENSE.txt README.html legal examples documentation
%attr(754,root,root) /etc/rc.d/init.d/WowzaMediaServer
%attr(755,root,root) %{_bindir}/WowzaMediaServerd
%dir %{_appdir}

%dir %{_appdir}/bin
%{_appdir}/bin/*.jar
%attr(755,root,root) %{_appdir}/bin/WowzaMediaServer
%attr(755,root,root) %{_appdir}/bin/WowzaMediaServerd
%attr(755,root,root) %{_appdir}/bin/*.sh

%dir %{_appdir}/conf
%config(noreplace) %verify(not md5 mtime size) %{_appdir}/conf/*.access
%config(noreplace) %verify(not md5 mtime size) %{_appdir}/conf/*.password
%config(noreplace) %verify(not md5 mtime size) %{_appdir}/conf/*.properties
%config(noreplace) %verify(not md5 mtime size) %{_appdir}/conf/*.xml
%dir %{_appdir}/conf/vod
%config(noreplace) %verify(not md5 mtime size) %{_appdir}/conf/vod/*.xml

%dir %{_appdir}/content
%config(missingok) %{_appdir}/content/*

%dir %{_appdir}/lib-native
%dir %{_appdir}/lib-native/linux64
%{_appdir}/lib-native/linux64/*.so*
%{_appdir}/lib-native/linux64/transcoder.list

%dir %{_appdir}/lib
%{_appdir}/lib/*.jar

%{_appdir}/transcoder
