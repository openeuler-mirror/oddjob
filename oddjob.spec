Name:    oddjob
Version: 0.34.6
Release: 2
URL:     https://pagure.io/oddjob
Source0: https://releases.pagure.org/oddjob/oddjob-%{version}.tar.gz
Summary: A D-Bus service which runs odd jobs on behalf of client applications
License: BSD
BuildRequires:   gcc dbus-devel >= 0.22, dbus-x11, libselinux-devel, libxml2-devel docbook-dtds, xmlto
BuildRequires:   pam-devel, python3-devel, pkgconfig cyrus-sasl-devel, krb5-devel, openldap-devel
BuildRequires:   systemd-units
Requires(post):  systemd-units
Requires(preun): systemd-units
Requires(postun):systemd-units
Requires(post):  systemd-sysv /usr/bin/dbus-send grep sed psmisc
Requires:  dbus
Obsoletes: oddjob-devel < 0.30, oddjob-libs < 0.30, oddjob-python < 0.30 
Provides:  %{name}-mkhomedir = %{version}-%{release}
Obsoletes: %{name}-mkhomedir < %{version}-%{release}
Provides:  config(oddjob-mkhomedir) = %{version}-%{release}

%description
The oddjobd service receives requests to do things over the D-Bus system bus.
Depending on whether or not the requesting user is authorized to have oddjobd
do what it asked, the daemon will spawn a helper process to actually do the work.
When the helper exits, oddjobd collects its output and exit status and sends them
back to the original requester.

It's kind of like CGI, except it's for D-Bus instead of a web server.

%package_help

%prep
%autosetup  -n %{name}-%{version} -p1

%build
%configure --disable-static --enable-pie --enable-now  --with-selinux-acls --with-selinux-labels \
           --without-python --enable-xml-docs --enable-compat-dtd --enable-systemd --disable-sysvinit 
make %{_smp_mflags}

%install
rm -rf %{buildroot}
%make_install
%delete_la_and_a
mkdir -p sample-install-root/sample/{%{_sysconfdir}/{dbus-1/system.d,%{name}d.conf.d},%{_libdir}/%{name}}
install -m644 sample/oddjobd-sample.conf        sample-install-root/sample/%{_sysconfdir}/%{name}d.conf.d/
install -m644 sample/oddjob-sample.conf         sample-install-root/sample/%{_sysconfdir}/dbus-1/system.d/
install -m755 sample/oddjob-sample.sh           sample-install-root/sample/%{_libdir}/%{name}/

chmod -x src/reload src/mkhomedirfor src/mkmyhomedir

touch -r src/oddjobd-mkhomedir.conf.in  %{buildroot}/%{_sysconfdir}/oddjobd.conf.d/oddjobd-mkhomedir.conf
touch -r src/oddjob-mkhomedir.conf.in   %{buildroot}/%{_sysconfdir}/dbus-1/system.d/oddjob-mkhomedir.conf

%check
make check

%post
if test $1 -eq 1 ; then
   killall -HUP dbus-daemon 2>&1 > /dev/null
fi
%systemd_post oddjobd.service
cfg=%{_sysconfdir}/oddjobd.conf.d/oddjobd-mkhomedir.conf
if grep -q %{_libdir}/%{name}/mkhomedir $cfg ; then
        sed -i 's^%{_libdir}/%{name}/mkhomedir^%{_libexecdir}/%{name}/mkhomedir^g' $cfg
fi
if test $1 -eq 1 ; then
        killall -HUP dbus-daemon 2>&1 > /dev/null
fi
exit 0

%postun
%systemd_postun_with_restart oddjobd.service
exit 0

%preun
%systemd_preun oddjobd.service
exit 0

%triggerun -- oddjobd < 0.31.3
%{_bindir}/systemd-sysv-convert --save oddjobd >/dev/null 2>&1 ||:
/sbin/chkconfig --del oddjobd >/dev/null 2>&1 || :
/bin/systemctl try-restart oddjobd.service >/dev/null 2>&1 || :
exit 0

%files
%doc *.dtd COPYING src/reload sample-install-root/sample src/mkhomedirfor src/mkmyhomedir
%{_unitdir}/oddjobd.service
%{_bindir}/*
%{_sbindir}/*
%config(noreplace) %{_sysconfdir}/dbus-*/system.d/oddjob.conf
%config(noreplace) %{_sysconfdir}/oddjobd.conf
%dir %{_sysconfdir}/oddjobd.conf.d
%config(noreplace) %{_sysconfdir}/oddjobd.conf.d/*
%config(noreplace) %{_sysconfdir}/dbus-*/system.d/oddjob-mkhomedir.conf
%dir %{_sysconfdir}/%{name}
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/*
%{_libdir}/security/pam_oddjob_mkhomedir.so

%files help
%doc NEWS QUICKSTART doc/oddjob.html
%{_mandir}/*/*

%changelog
* Fri Oct 30 2020 shixuantong <shixuantong@huawei.com> - 0.34.6-2
- remove python2

* Wed Jul 22 2020 shixuantong <shixuantong@huawei.com> - 0.34.6-1
- update to 0.34.6-1

* Wed Apr 8 2020 openEuler Buildteam <buildteam@openeuler.org> - 0.34.4-9
- Delete redundant scripts and file

* Fri Feb 14 2020 openEuler Buildteam <buildteam@openeuler.org> - 0.34.4-8
- Enable check

* Tue Sep 17 2019 openEuler Buildteam <buildteam@openeuler.org> - 0.34.4-7
- Package init
