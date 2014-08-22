######  clean #####################################################
sh ./clean.sh
######  build #####################################################
set -e

###### debian package #############################################
rm -fr debian
rm -f *.deb

# my app dir
mkdir -p debian/opt/odp/src
mkdir -p debian/opt/odp/bin
mkdir -p debian/opt/odp/var/hosts
mkdir -p debian/opt/odp/log



# debian dir
mkdir -p debian/usr/share/man/man1
mkdir -p debian/usr/share/doc/odp
mkdir -p debian/DEBIAN
find ./debian -type d | xargs chmod 755 

# debian copy 
cp pkgsrc/DEBIAN/* debian/DEBIAN/
find ./debian -type f | xargs chmod 755 
# cp pkgsrc/usr/share/man/man1/* debian/usr/share/man/man1/
# cp pkgsrc/usr/share/doc/odp/* debian/usr/share/doc/odp/
# debian man doc compress
# gzip --best debian/usr/share/man/man1/*
# gzip --best debian/usr/share/doc/odp/changelog*

# myapp copy 
cp -fr src/odp  debian/opt/odp/src/
cp -fr src/bin  debian/opt/odp/

# change perm
find ./debian/opt/odp/bin -type f | xargs chmod ugo+x
find ./debian/opt/odp/src -type f | xargs chmod ugo-x

dpkg-deb  --build debian
mv debian.deb odp_1.0-0_all.deb

