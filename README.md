ssh -p 222 c1mckay@testdrive.aeoncomputing.com

sudo yum install -y ansible nano git

edit /etc/hosts

edit /etc/ansible/hosts
-add host ips

-add ssh key
sudo chmod 400 ~/.ssh/id_rsa

ansible all -m ping # sets host key

example urls
http://132.249.238.22:9090/graph?g0.range_input=1h&g0.expr=request_processing_seconds_count&g0.tab=1
http://132.249.238.22:9090/graph?g0.range_input=1h&g0.expr=node_cpu_seconds_total&g0.tab=1