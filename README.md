Pulumi code

Usage:
Before running pulumi up, set the configuration for the desired cloud provider:
* For AWS: 
pulumi config set cloud-provider AWS pulumi up   
* For Azure:
pulumi config set cloud-provider AZURE pulumi up   
* For both or defaulting to AWS (if no configuration is set):
  Simply run pulumi up without setting the cloud-provider configuration.

This structure allows for clear separation of cloud-specific initialization logic and can be easily extended or modified for additional cloud providers or configurations in the future.
