import pulumi
from pulumi_aws import ec2, get_availability_zones
from pulumi_tls import PrivateKey
import pulumi_azure_native as azure_native

class AwsInfrastructure(pulumi.ComponentResource):
    def __init__(self, name, aws_vpc_cidr, subnets, instance_type, key_pair_name, user_data_path, opts=None):
        super().__init__('custom:module:AwsInfrastructure', name, None, opts)
         

        # Properly handle opts for get_ami
        ami_opts = pulumi.InvokeOptions(provider=opts.provider) if opts else pulumi.InvokeOptions()
        az_opts = pulumi.InvokeOptions(provider=opts.provider) if opts else pulumi.InvokeOptions()
        #ami_opts = pulumi.InvokeOptions(providers=opts.providers) if opts else pulumi.InvokeOptions() 
        # Fetch the latest Amazon Linux 2 AMI using the provided opts
        ami = ec2.get_ami(most_recent=True,
                          owners=["amazon"],
                          filters=[{"name": "name", "values": ["amzn2-ami-kernel-5*"]}],
                          opts=ami_opts)

        # Load user data script
        with open(user_data_path, 'r') as user_data_file:
            user_data = user_data_file.read()

        # Create a VPC
        self.vpc = ec2.Vpc(f'{name}-vpc',
                           cidr_block=aws_vpc_cidr,
                           tags={'Name': f'{name}-vpc'},
                           opts=opts)

        # Get availability zones
        azs = get_availability_zones(opts=az_opts).names

        # Create subnets
        self.subnets = [ec2.Subnet(f'{name}-subnet-{i}',
                                   vpc_id=self.vpc.id,
                                   cidr_block=subnet['subnet_cidr'],
                                   availability_zone=azs[0],
                                   tags={'Name': subnet['subnet_name']},
                                   opts=opts)
                        for i, subnet in enumerate(subnets)]

        # Create an Internet Gateway
        self.igw = ec2.InternetGateway(f'{name}-igw',
                                       vpc_id=self.vpc.id,
                                       tags={'Name': f'{name}-igw'},
                                       opts=opts)

        # Create a Route Table
        self.route_table = ec2.RouteTable(f'{name}-rt',
                                          vpc_id=self.vpc.id,
                                          tags={'Name': f'{name}-rt'},
                                          opts=opts)

        # Associate Route Table with each subnet
        self.route_table_associations = [ec2.RouteTableAssociation(f'{name}-rta-{i}',
                                                                   route_table_id=self.route_table.id,
                                                                   subnet_id=subnet.id,
                                                                   opts=opts)
                                         for i, subnet in enumerate(self.subnets)]

        # Create a default route
        self.route = ec2.Route(f'{name}-route-igw',
                               destination_cidr_block='0.0.0.0/0',
                               gateway_id=self.igw.id,
                               route_table_id=self.route_table.id,
                               opts=opts)

        # Create a Security Group
        self.sg = ec2.SecurityGroup(f'{name}-security-group',
                                    vpc_id=self.vpc.id,
                                    ingress=[
                                        ec2.SecurityGroupIngressArgs(
                                            description='SSH',
                                            from_port=22,
                                            to_port=22,
                                            protocol='tcp',
                                            cidr_blocks=['0.0.0.0/0']
                                        ),
                                        # ... other ingress rules ...
                                    ],
                                    egress=[
                                        ec2.SecurityGroupEgressArgs(
                                            from_port=0,
                                            to_port=0,
                                            protocol='-1',
                                            cidr_blocks=['0.0.0.0/0']
                                        )
                                    ],
                                    tags={'Name': f'{name}-security-group'},
                                    opts=opts)

        # Create SSH Key Pair
        rsa_key = PrivateKey(f'{name}-rsa-key', algorithm='RSA', rsa_bits=4096, opts=opts)
        self.key_pair = ec2.KeyPair(key_pair_name,
                                    public_key=rsa_key.public_key_openssh,
                                    opts=opts)


        pulumi.export('sshPublicKey', rsa_key.public_key_openssh)
        #with open(f'{name}-public.key', 'w') as public_key_file:
        #     public_key_file.write(rsa_key.public_key_openssh)
        #rsa_key.public_key_openssh.apply(lambda pub_key: write_to_file(f'{name}-public.key', pub_key))
        rsa_key.private_key_pem.apply(lambda priv_key: write_to_file(f'{name}-private.pem', priv_key))
        def write_to_file(filename, content):
            """ Helper function to write content to a file """
            with open(filename, 'w') as file:
                 file.write(content)
        # Create EC2 Instances
        self.instances = [ec2.Instance(f'{name}-instance-{i}',
                                       ami=ami.id,
                                       instance_type=instance_type,
                                       key_name=self.key_pair.key_name,
                                       subnet_id=subnet.id,
                                       user_data=user_data,
                                       vpc_security_group_ids=[self.sg.id],
                                       tags={'Name': f'{name}-instance-{i}'},
                                       opts=opts)
                          for i, subnet in enumerate(self.subnets)]

        # Create Elastic IPs for each EC2 instance
        self.eips = [ec2.Eip(f'{name}-eip-{i}',
                             domain='vpc',
                             instance=self.instances[i].id,
                             opts=opts)
                     for i in range(len(self.instances))]

        self.register_outputs({})

# Example usage is in the MainProgram
class AzureInfrastructure(pulumi.ComponentResource):
    def __init__(self, name,  resource_group_name, location, vnet_name, vnet_cidr, subnets, nsg_name, vm_size, vm_name, ssh_key_name, user_data_path, opts=None):
        super().__init__('custom:module:AzureInfrastructure', name, None, opts)

        # Create a Resource Group
        self.resource_group = azure_native.resources.ResourceGroup(f'{name}-rg',
                                                                   resource_group_name=resource_group_name,
                                                                   location=location)

        # Create a Virtual Network
        self.vnet = azure_native.network.VirtualNetwork(f'{name}-vnet',
                                                        resource_group_name=self.resource_group.name,
                                                        location=self.resource_group.location,
                                                        address_space=azure_native.network.AddressSpaceArgs(address_prefixes=[vnet_cidr]))

        # Create Subnets
        self.subnets = []
        for idx, subnet in enumerate(subnets):
       	    for cidr_idx, cidr in enumerate(subnet['azure_subnet_cidr']):
                subnet_name = f"{subnet['azure_subnet_name']}-cidr-{cidr_idx}"
                subnet_resource = azure_native.network.Subnet(f'{name}-subnet-{idx}',
                                                          resource_group_name=self.resource_group.name,
                                                          virtual_network_name=self.vnet.name,
                                                          address_prefix=cidr)
                self.subnets.append(subnet_resource)

        # Create a Network Security Group
        self.nsg = azure_native.network.NetworkSecurityGroup(f'{name}-nsg',
                                                             resource_group_name=self.resource_group.name,
                                                             location=self.resource_group.location,
                                                             security_rules=[
                                                                 azure_native.network.SecurityRuleArgs(
                                                                     name="allow_ssh",
                                                                     priority=100,
                                                                     direction="Inbound",
                                                                     access="Allow",
                                                                     protocol="Tcp",
                                                                     source_port_range="*",
                                                                     destination_port_range="22",
                                                                     source_address_prefix="*",
                                                                     destination_address_prefix="*"
                                                                 ),
                                                                 # Add other security rules as needed
                                                             ])

        # TLS for SSH Key
        rsa_key = PrivateKey(f'{name}-rsa-key', algorithm='RSA', rsa_bits=4096)
        
        # Save SSH Public Key
        self.ssh_public_key = azure_native.compute.SshPublicKey(f'{name}-ssh-key',
                                                                resource_group_name=self.resource_group.name,
                                                                location=self.resource_group.location,
                                                                public_key=rsa_key.public_key_openssh)

        # Create Network Interfaces
        """
        self.nics = []
        for idx, subnet in enumerate(self.subnets):
            nic = azure_native.network.NetworkInterface(f'{name}-nic-{idx}',
                                                        resource_group_name=self.resource_group.name,
                                                        location=self.resource_group.location,
                                                        ip_configurations=[
                                                            azure_native.network.NetworkInterfaceIPConfigurationArgs(
                                                                name="nic-ip",
                                                                subnet=azure_native.network.SubnetArgs(
                                                                    id=subnet.id
                                                                ),
                                                                private_ip_address_allocation="Static",
                                                                private_ip_address=subnets[idx]['azure_private_ip']
                                                            )
                                                        ])
            self.nics.append(nic)
        """
        self.nics = []
        for subnet_info in subnets:
    # Find the corresponding subnet resource created earlier
            corresponding_subnet = next((s for s in self.subnets if s.name == subnet_info['azure_subnet_name']), None)
            if corresponding_subnet:
               nic = azure_native.network.NetworkInterface(subnet_info['azure_nic'],
                                                    resource_group_name=self.resource_group.name,
                                                    location=self.resource_group.location,
                                                    ip_configurations=[
                                                        azure_native.network.NetworkInterfaceIPConfigurationArgs(
                                                            name=f"{subnet_info['azure_nic']}-ip-config",
                                                            subnet=azure_native.network.SubnetArgs(
                                                                id=corresponding_subnet.id
                                                            ),
                                                            private_ip_address_allocation="Static",
                                                            private_ip_address=subnet_info['azure_private_ip']
                                                        )
                                                    ])
               self.nics.append(nic)

        # Create Azure Linux Virtual Machines
        self.vms = []
        for idx, nic in enumerate(self.nics):
            vm = azure_native.compute.VirtualMachine(f'{name}-vm-{idx}',
                                                     resource_group_name=self.resource_group.name,
                                                     location=self.resource_group.location,
                                                     network_profile=azure_native.compute.NetworkProfileArgs(
                                                         network_interfaces=[
                                                             azure_native.compute.NetworkInterfaceReferenceArgs(
                                                                 id=nic.id
                                                             )
                                                         ]
                                                     ),
                                                     hardware_profile=azure_native.compute.HardwareProfileArgs(
                                                         vm_size=vm_size
                                                     ),
                                                     os_profile=azure_native.compute.OSProfileArgs(
                                                         computer_name=f'{vm_name}-{idx}',
                                                         admin_username="adminuser",
                                                         admin_password="password",
                                                         linux_configuration=azure_native.compute.LinuxConfigurationArgs(
                                                             disable_password_authentication=True,
                                                             ssh=azure_native.compute.SshConfigurationArgs(
                                                                 public_keys=[
                                                                     azure_native.compute.SshPublicKeyArgs(
                                                                         path=f"/home/adminuser/.ssh/authorized_keys",
                                                                         key_data=rsa_key.public_key_openssh
                                                                     )
                                                                 ]
                                                             )
                                                         )
                                                     ),
                                                     storage_profile=azure_native.compute.StorageProfileArgs(
                                                         os_disk=azure_native.compute.OSDiskArgs(
                                                             create_option="FromImage",
                                                             caching="ReadWrite",
                                                             managed_disk=azure_native.compute.ManagedDiskParametersArgs(
                                                                 storage_account_type="Standard_LRS"
                                                             )
                                                         ),
                                                         image_reference=azure_native.compute.ImageReferenceArgs(
                                                             publisher="Canonical",
                                                             offer="UbuntuServer",
                                                             sku="18.04-LTS",
                                                             version="latest"
                                                         )
                                                     ))
            self.vms.append(vm)

        self.register_outputs({})
