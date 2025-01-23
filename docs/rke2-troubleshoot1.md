#RKE2 Hangs Resolution:

<https://forum.uipath.com/t/rke2-stuck-in-activating/570680>

First, activating can take some time. It is normal for it to take 2-5 minutes.
Usually, the logs RKE2 logs need to be checked to diagnose the issue. However, in some cases, this can be caused if there are orphaned RKE2 processes stuck in a running state. Usually, this will not cause an issue, however, if there was a misconfiguration in RKE2 and the process was restarted after the configuration was corrected, these orphaned processes may need to be killed. To take care of this, try running the drain command and then kill all orphaned processes.
First, try to drain the node. This command should fail but should be attempted in case any processes need to be terminated.
/opt/node-drain.sh
(NOTE: It will take around 1.5 minutes to timeout and will end with hostname cannot be found).
If the above command does succeed, most likely the service was simply taking a long time to start. In such a case, recheck the status of the RKE2 service.
For servers: systemctl restart rke2-server
For agents: systemctl restart rke2-agent.
If the service is now running, there was no issue but activation took a long time. Run the following command to uncordon the node.
/opt/node-drain.sh uncordon
If the drain command failed, or the service is not in a running state, then run the following command to kill stop RKE2 and kill any orphaned processes.
rke2-killlall.sh
Once the above steps are done, try restarting the service.
For servers: systemctl restart rke2-server
For agents: systemctl restart rke2-agent.
Check the status of the service to see if it was able to start.
For servers: systemctl restart rke2-server
For agents: systemctl restart rke2-agent.
If it was still not able to start, then we need to take a look at the logs.
For servers: systemctl status rke2-server
For agents: systemctl status rke2-agent.
If it remains active, something else is wrong and the logs need to be analyzed.
First, check to see if the service keeps restarting.
journalctl | grep 'Started Rancher Kubernetes Engine'
If there are multiple restarts present around the current time, that probably means that the service keeps getting restarted. If this is the case, then the issue is the RKE2 is not starting and is not that the service is stuck in activating.
In this scenario see KB article RKE2 Fails To Start.
Next, check the journal logs of the machine. To do this run the following command:
For a server: journalctl -r -u rke2-server
For an agent: journalctl -r -u rke2-agent
Analyzing the RKE2 logs in depth is beyond the scope of this article. However here are some simple tips:
Look for error messages. Sometimes they explain the exact issue.
Failed to test data store connection: this server is not a member of the etcd cluster
If this message is encountered, it most likely means the node IP has changed.
For multinodes, delete the node and rejoin it. See: Removing A Node From The Cluster
For single-node, contact UiPath Support, providing the logs mentioned at the bottom of this article. The etcd store uses the node ip for registration. If that IP changes, then the instance will be seen as unregistered, causing issues.
Failed to test the data store connection: connection refused/etcd is not ready
Check for the etcd pod logs using crictl to see the errors and that could help find the possible cause.
export CRI_CONFIG_FILE=/var/lib/rancher/rke2/agent/etc/crictl.yaml
crictl ps -a


check the logs for the etcd pod

crictl logs 

Look for the following string to find fatal errors 'level=warning'
If none of the above helps identify the issue, generate an RKE2 bundle and open a ticket with UiPath.
To generate an RKE2 bundle, follow the steps here: The Rancher v2.x Linux Log Collector Script
Also check our docs, in case our troubleshooting guide has been updated for the installation-specific support bundle. If it has, use that instead of the Suse tool. (the RKE2 bundle will be incorporated into our tool in the future). Using Support Bundle Tool.
In the ticket opened with UiPath please include the support bundle, the steps taken so for and any details discovered going through this KB article.
