# Pulumi Code Usage Guide

This guide outlines how to use the Pulumi code for different cloud providers. The structure allows for clear separation of cloud-specific initialization logic and can be easily extended or modified for additional cloud providers or configurations.

## Usage

Before running `pulumi up`, set the configuration for the desired cloud provider.

### For AWS

To configure and deploy to AWS, use the following commands:

```bash
pulumi config set cloud-provider AWS
pulumi up
```


### For Azure

To configure and deploy to Azure, use the following commands:

```bash
pulumi config set cloud-provider Azure
pulumi up

```


### For Both AWS and Azure

For both or defaulting to AWS (if no configuration is set):

Simply run pulumi up without setting the cloud-provider configuration.

```bash

pulumi up
```






### Pulumi Recap - brief


Pulumi offers a variety of commands that help you manage, monitor, and understand the resources you create. Here's a list of useful Pulumi CLI commands for these purposes:
1. pulumi up
* Usage: Deploys your stack, creating or updating resources as defined in your Pulumi program.
* Command:
  ```bash pulumi up  ``` 
2. pulumi preview
* Usage: Shows a preview of the changes that Pulumi plans to make to your infrastructure, without actually making them.
* Command:
  ```bash pulumi preview  ```  
3. pulumi refresh
* Usage: Refreshes the state of your stack to align it with the actual state of resources in the cloud. Useful if external changes were made to the cloud resources.
* Command:
   ```bash pulumi refresh   ``` 
4. pulumi stack
* Usage: Provides information about your Pulumi stack.
* Command:
   ```bash pulumi stack   ```
  
    * For detailed resource information: pulumi stack --show-urns
5. pulumi config
* Usage: Manages configuration for the current stack. You can view, set, or remove configuration values.
* Command:
   ```bash pulumi config ```  
6. pulumi destroy
* Usage: Destroys all resources managed by the current stack. Use with caution.
* Command:
   ```bash pulumi destroy ```  
7. pulumi logs
* Usage: Fetches logs for the resources in the current stack. This is useful for debugging and understanding the behavior of your resources.
* Command:
   ```bash pulumi logs  ``` 
    * For real-time logs: pulumi logs -f
8. pulumi history
* Usage: Displays the history of updates to the stack, including who performed each update and when.
* Command:
   ```bash pulumi history ```  
9. pulumi stack output
* Usage: Displays the outputs of the current stack. Outputs can include important data like IP addresses, DNS names, and other resource identifiers.
* Command:
   ```bash pulumi stack output ```  
10. pulumi whoami
* Usage: Displays the Pulumi username of the current user.
* Command:
   ```bash pulumi whoami   ```
11. pulumi policy
* Usage: Manages policy-as-code (if you're using Pulumi's CrossGuard feature). It's useful for enforcing certain rules and practices in your infrastructure.
* Command:
   ```bash pulumi policy  ``` 
12. pulumi plugin
* Usage: Manages plugins in your Pulumi environment. Plugins are used for interacting with various cloud providers.
* Command:
   ```bash pulumi plugin  ``` 
Notes for Using These Commands:
* Stack Context: Many of these commands operate within the context of a specific Pulumi stack. Ensure you're in the correct stack context or specify the stack name in the command.
* Project Directory: Run these commands in your Pulumi project directory, where your Pulumi.yaml file is located.
* Documentation: Consult the Pulumi documentation for more details and options for each command.
These commands cover most of the typical actions you'd perform in a development environment when working with Pulumi to manage cloud resources.



