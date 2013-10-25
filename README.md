Docker plugin for OpenStack Heat
================================

This plugin enable using Docker containers as resources in a Heat template.

How to use it?
--------------

Obviously the step 0 is to make sure you're running a recent version of Docker.

### 1. Install Heat

I recommend to use
[DevStack](https://wiki.openstack.org/wiki/Heat/GettingStartedUsingDevstack).
Following the steps 1, 2 and 3 is enough since Nova is not needed here.


### 2. Install the Docker plugin in Heat

NOTE: Heat scans the directory /usr/lib/heat to find plugins to load.

Running the following the following commands will actually install the Docker
plugin in an existing Heat setup.

```
pip install -r openstack-heat-docker/requirements.txt
git clone git@github.com:dotcloud/openstack-heat-docker.git
ln -sf $(cd openstack-heat-docker/plugin; pwd) /usr/lib/heat/docker
```


### 3. Restart heat

Only the process "heat-engine" needs to be restarted to load the new installed
plugin. Here is how to do it with devstack

1. Attach to the screen (using the "screen -rd" command);
2. Find the "h-engine" window (ctrl+n to switch to the next window);
3. Interrupt the process and restart it.


### 4. Talk to Heat

Since calls to Heat are authenticated, the Keystone token needs to be loaded
in the environment. With devstack, here is how it works:

```
cd devstack
. openrc
heat stack-list
```

The last comment asks Heat to return the previous created stacks. Since it's a
new setup, nothing will be return. But if there is no error displayed, it means
that all previous steps have be run successfully.


Running an example with Wordpress and MySQL
-------------------------------------------

The example shipped with the project shows how to deploy a blog under Wordpress
using a MySQL database. The current wordpress containers available right now on
Docker Index usually embed Apache, Wordpress and MySQL all in one single
container. The difference is that two containers will be deployed. One for
the MySQL server, another for Apache+Wordpress. The Database information (IP,
port and password) are injected in the environment of the Wordpress container.
So we can easily imagine a Wordpress container scaled accross different hosts
using the same database (the latter being scaled using a master/slave setup).

Let's try to run the example. First of all, let's fetch the 2 images needed:

```
docker pull samalba/wordpress
docker pull samalba/mysql
```

You will find the "source code" of those containers in the
"example/docker-containers" directory.

Then, the following command will provision the stack through Heat:

```
heat stack-create wordpress -f openstack-heat-docker/example/templates/wordpress_mysql.yml
```

If it went well, you should be able to see the stack with the status
"CREATION_COMPLETE".

```
heat stack-list
+--------------------------------------+------------+-----------------+----------------------+
| id                                   | stack_name | stack_status    | creation_time        |
+--------------------------------------+------------+-----------------+----------------------+
| 239cc009-00fe-4c6f-ac67-f8873df38f08 | wordpress  | CREATE_COMPLETE | 2013-10-15T23:23:08Z |
+--------------------------------------+------------+-----------------+----------------------+
```

And the according containers in Docker:

```
docker ps
ID            IMAGE                     COMMAND               CREATED        STATUS        PORTS
5513c532b4dc  samalba/wordpress:latest  /usr/sbin/apache2 -D  2 minutes ago  Up 2 minutes  49174->80
b98d764d109d  samalba/mysql:latest      /start_mysqld.sh      2 minutes ago  Up 2 minutes  49173->3306
```

In this example, connecting with a web browser on the port 49174 of host will
show the wordpress install page.

The Heat template also generated the Blog URL:

```
heat stack-show wordpress
```
