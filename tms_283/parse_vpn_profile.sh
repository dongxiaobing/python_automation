#!/bin/bash

httpserver="http://10.226.200.96/"
vpnprofilename="airwatch.mobileconfig"

if [ ! -d "/tmp/vpn" ]; then
   mkdir /tmp/vpn
fi
cp get_pwd_plist.py /tmp/vpn
cd /tmp/vpn

if [ ! -f $vpnprofilename ]; then
wget $httpserver$vpnprofilename -o log
fi

openssl smime -verify -noverify -nochain -inform DER -in $vpnprofilename | grep verification
python get_pwd_plist.py $vpnprofilename
openssl pkcs12 -in user.p12 -out user.cert -passin file:passin -nodes 
openssl x509 -in pem -in user.cert -noout -text | tr -d ' ' |  grep "Username:" | sed 's/;/\n/g'
cat pacfile
echo ''
