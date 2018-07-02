sudo yum install -y ansible nano git

edit /etc/hosts

edit /etc/ansible/hosts
-add host ips

-add ssh key
sudo chmod 400 ~/.ssh/id_rsa

ansible all -m ping # sets host key