## RebootD - Automagically reboot your clusters

This tool is pretty simple. To use it, you only need two things:

* A redis server
* A cluster of n+1 machines

### What can it do for me?

This script will reboot your system! But only if all of the conditions are met:

* you system has reached the maximum uptime (configurable)
* the redis server is reachable
* no other machine of the same cluster (configurable) is currently rebooting

### Why the hell should I use that?

This will bring the following improvements:

* No more uptime bugs
* Fixes memory leaks :p
* You know that your cluster nodes can recover after a reboot
* automated updates of libraries used by running services take effect
* even automated kernel updates take effect

And all of that without your manual work!

### Ok, my second name is "danger". How to get it working?

Even if it's called RebootD, it's not a daemon (sorry for that. Maybe in one of the next versions?).
So you need a cronjob, running in your desired intervall, just calling ```rebootd.py --config /your/config/file.json``` as root.
If the preconditions in the config file are met, your cluster will register at the redis server as currently rebooting, preventing all other nodes form the same cluster to do the same.
After a successfull reboot (and the next run of the cronjob) it will remove itself from the redis server, so another machine from the cluster can reboot. Thats it!

#### Configuration options

```json
{
    "group": "mygroup",
    "week": "1",
    "redis": "my.redis.server"
}
```

**group**: The cluster this node is a member of
**week**: If your node is up for more than *n* weeks, it will reboot
**redis**: Hostname/IP of your redis server
