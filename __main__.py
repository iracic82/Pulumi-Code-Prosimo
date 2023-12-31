import pulumi
import json
from pulumi_aws import Provider as AWSProvider
from pulumi_azure_native import Provider as AzureProvider
from infrastructure_module import AwsInfrastructure, AzureInfrastructure

class MainProgram:
    def __init__(self):
        config = pulumi.Config()
        cloud_provider = config.get('cloud-provider')  # Retrieves the configuration value for 'cloud-provider'

        if cloud_provider == 'AWS' or cloud_provider is None:
            # Load AWS configuration
            with open('config.json', 'r') as aws_config_file:
                aws_config_data = json.load(aws_config_file)

            # Initialize AWS Infrastructure
            for region, vpcs in aws_config_data.items():
                aws_provider = AWSProvider('aws-provider', region=region)
                for vpc_name, vpc_config in vpcs.items():
                    AwsInfrastructure(f'aws-infra-{region}-{vpc_name}',
                                      aws_vpc_cidr=vpc_config['aws_vpc_cidr'],
                                      subnets=vpc_config['subnets'],
                                      key_pair_name=vpc_config['aws_ec2_key_pair_name'],
                                      instance_type='t2.micro',
                                      user_data_path='./aws.sh',
                                      opts=pulumi.ResourceOptions(provider=aws_provider))

        if cloud_provider == 'AZURE':
            # Load Azure configuration
            with open('azure_config.json', 'r') as azure_config_file:
                azure_config_data = json.load(azure_config_file)

            # Initialize Azure Infrastructure
            for region, vnets in azure_config_data.items():
                azure_provider = AzureProvider('azure-provider')
                for vnet_name, vnet_config in vnets.items():
                    AzureInfrastructure(
                        name=vnet_name,
                        resource_group_name=vnet_config['azure_resource_group'],
                        location="northeurope",
                        vnet_name=vnet_config['azure_vnet_name'],
                        vnet_cidr=vnet_config['azure_vnet_cidr'],
                        subnets=vnet_config['subnets'],
                        nsg_name=vnet_config['nsg_name'],
                        vm_size=vnet_config['azure_vm_size'],
                        vm_name=vnet_config['azure_instance_name'],
                        ssh_key_name=vnet_config['azure_server_key_pair_name'],
                        user_data_path="path_to_your_user_data_script",
                        opts=pulumi.ResourceOptions(provider=azure_provider))

# Instantiate the main program
main_program = MainProgram()
