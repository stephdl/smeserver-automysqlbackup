%define name smeserver-automysqlbackup
%define version 3.0.RC6
%define release 3
%define rpmver   3.0.RC6


Summary:            automysqlbackup is a script to backup your msql database on sme8
Name:               %{name}
Version:            %{version}
Release:            %{release}%{?dist}
License:            GPL
Group:              /Web/Application
Source:             %{name}-%{version}.tar.gz
URL:                http://sourceforge.net/projects/automysqlbackup/
BuildRoot:          /var/tmp/%{name}-%{version}-%{release}-buildroot
BuildArchitectures: noarch
Requires:           e-smith-base, e-smith-release >= 8
Requires:		pax
Requires: automysqlbackup
BuildRequires:      e-smith-devtools

%description
This RPM is an unofficial addon for the SME Server 8.x.  
The target audience is the Linux/E-smith administrator 
who wants to backup their mysql databases with an automatic way.
This script is based on automysqlbackup V3.0



%changelog
* Sun Oct 27 2013 Stephane de Labrusse <stephdl@de-labrusse.fr> 3.0.RC6.3
- split the contrib in two versions smeserver-automysqlbackup and automysqlbackup
* Mon Apr 22 2013 Stephane de Labrusse <stephdl@de-labrusse.fr>
- [3.0.RC6] version Based on automysqlbackup V3.0 RC6
* Mon Apr 08 2013 Stephane de Labrusse <stephdl@de-labrusse.fr>
- [0.01] Initial version Based on automysqlbackup V3.0 RC6

%prep
rm -rf $RPM_BUILD_ROOT

%setup

%build

%install
/bin/rm -rf $RPM_BUILD_ROOT
(cd root   ;/usr/bin/find . -depth -print | /bin/cpio -dump $RPM_BUILD_ROOT)
/bin/rm -f %{name}-%{version}-filelist
/sbin/e-smith/genfilelist $RPM_BUILD_ROOT > %{name}-%{version}-filelist


%files -f %{name}-%{version}-filelist

%defattr(-,root,root)

%clean 
rm -rf $RPM_BUILD_ROOT

%pre

%post
SMEDB=automysqlbackup
MYSQLUSER=backupuser
# Expland template
/etc/e-smith/events/actions/initialize-default-databases

echo "========================================================================================="
echo "	Your Databases are saved in /root/backup/db "
echo "	only Root can access to these folders"                         
echo "	a mail is send to Admin for all logs "
echo " "                                                                   
echo "	Configuration file is /etc/automysqlbackup/myserver.conf"
echo " "
echo "	For a manual play you can use directly"
echo "	automysqlbackup /etc/automysqlbackup/myserver.conf "
echo "	else backups are done every night at 04H00 AM with /etc/cron.daily/runmysqlbackup"
echo "========================================================================================="
echo "	RESTORING"
echo " 	In a root terminal"
echo "	cd /root/backup/db/ and choose your backup"
echo "	gunzip file-name.sql.gz"
echo "	Next you will need to use the mysql client to restore the DB from the sql file."
echo "	mysql database < /path/file.sql"
echo "	NOTE: Make sure you use < and not > in the above command because you are piping the file.sql" 
echo "	to mysql and not the other way around"
echo "========================================================================================="
echo "	Some db configuration for handle this contrib"
echo "	Mailcontent (stdout/log/files/quiet)"
echo "	# What would you like to be mailed to you?"
echo "	# - log   : send only log file (default)"
echo "	# - files : send log file and sql files as attachments (see docs)"
echo "	#- stdout : will simply output the log to the screen if run manually."
echo "	#- quiet : Only send logs if an error occurs to the MAILADDR."
echo "	Sizemail=8000 (bytes)"
echo "	Mailto=root (or any other user@domaine.com)"
echo "	Backupdir=path to the folder where mysql files are saved"
echo " "
echo "	ex: config setprop automysqlbackup Mailcontent files"
echo "========================================================================================="



#create backupuser and give rights
MYSQLPASS=$(/sbin/e-smith/config getprop $SMEDB DbPassword)
mysql -e " GRANT SELECT,LOCK TABLES ON *.* TO $MYSQLUSER@'localhost' "
mysql -u root -e "SET PASSWORD FOR $MYSQLUSER@localhost = PASSWORD( '$MYSQLPASS' ) "
mysqladmin flush-privileges
/etc/rc.d/init.d/mysql.init start

#protect the backup folder
chmod -R 700 /root/backup/db
			     
%preun
%postun
if [ $1 = 0 ] ; then
SMEDB=automysqlbackup
MYSQLUSER=backupuser
echo "======================================================================="
echo "	delete mysql user and revoque all permissions"
# This section deletes backupuser
mysql -u root -e "REVOKE ALL PRIVILEGES ON *.* FROM '$MYSQLUSER'@'localhost';"
mysql -u root -e "DROP USER $MYSQLUSER@localhost;"
echo "	"
# Delete custom template fragment
echo "	delete db configuration automysqlbackup"
echo "======================================================================="

/sbin/e-smith/config delete $SMEDB
fi
