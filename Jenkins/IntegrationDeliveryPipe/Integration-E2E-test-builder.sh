#!/bin/bash

#docker login -u admin -p dogreat12 https://secure-registry.gsintlab.com

ip=`curl -s http://whatismyip.akamai.com ; echo`

echo "[Docker Login]
username = gemini
password = dogreat12

[User Config]
build_deploy_mode = 0
build_id = latest
clean_setup = 2
self_signed_crt = 1
self_signed_crt_dir =
chef_ssl_crt = 1
chef_ssl_crt_dir =
deploy_chef = 1
deploy_mode = 1
on_prem_emailid = admin@apporbit.com
hostip = $ip
themename = apporbit-v2
api_version = v2
registry_url = jenkin-registry.gsintlab.com
internal_repo = http://repos.gsintlab.com/repos
volume_mount = " > Customer/KIT/appOrbitDeploy/src/local.conf

echo "waiting for apporbit launch ...."
cd Customer/KIT/appOrbitDeploy/src
./apporbitlauncher.py
echo "waiting for 3000 .."
sleep 3000

cd $WORKSPACE
rm -rf test_auto
git clone https://sajithgem:dogreat12@github.com/Gemini-sys/test_auto.git

cd test_auto
git checkout integration

rm -rf conf/gemini.conf
rm -rf data/default/openstack/add_openstack_data.json
cp -Rf /home/gemini.conf conf/gemini.conf
#cp -Rf /home/add_openstack_data.json data/default/openstack/add_openstack_data.json
cp -Rf /home/add_openstack_data.json data/default/openstack/add_cloud_data.json


#Ramendra updated ap19
#./trun.py --precleanup --init --cloud openstack --tclevel 0 testcases/smoke/smoke.py

#ramendra updated apr 1
#./trun.py --precleanup --init --cloud openstack --tclevel 0 testcases/

#ramendra may 4
#bash <(curl -s "http://downloads.apporbit.com/test-auto/install.sh") -n integration.gsintlab.com -k /root/.ssh/id_rsa -f /home/add_openstack_data.json -c openstack -i yes -e yes -t 0 -m gopalakrishnan@apporbit.com,ramendra@apporbit.com,manish@apporbit.com


./trun.py --precleanup --init --cloud openstack --email --tclevel 0 testcases/


value=`cat results/openstack_execution.log | grep "Tests Failed" | awk '{print $4}'`
if [ "${value}" = '' ]; then
exit 1;
elif [ "${value}" -eq 0 ];then
echo "0";
else
exit 1;
fi




#./trun.py --precleanup --init --cloud openstack testcases/smoke/smoke.py







