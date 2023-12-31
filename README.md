# Pulumi Code Usage Guide

This guide outlines how to use the Pulumi code for different cloud providers. The structure allows for clear separation of cloud-specific initialization logic and can be easily extended or modified for additional cloud providers or configurations.

## Usage

Before running `pulumi up`, set the configuration for the desired cloud provider.

### For AWS

To configure and deploy to AWS, use the following commands:

```bash
pulumi config set cloud-provider AWS
pulumi up
