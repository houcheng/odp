set -e 
sh ./build-package.sh
dpkg -r odp
dpkg -i odp_1.0-0_all.deb
