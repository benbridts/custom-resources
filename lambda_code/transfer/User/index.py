from cfn_custom_resource import CloudFormationCustomResource
from _metadata import CUSTOM_RESOURCE_NAME


class User(CloudFormationCustomResource):
    """
    Properties:
        Role: str: role for user, should include permissions to access a bucket
        Policy: str: policy for limiting access of user
        ServerId: str: the transfer server id
        SshPublicKeyBody: str: base64 encoded public key for user
        UserName: str: name of user
        HomeDirectory: str: home directory folder in bucket
    """
    RESOURCE_TYPE_SPEC = CUSTOM_RESOURCE_NAME
    DISABLE_PHYSICAL_RESOURCE_ID_GENERATION = True  # Use User Name instead

    def validate(self):
        self.role = self.resource_properties['Role']
        self.policy = self.resource_properties.get('Policy')
        self.server_id = self.resource_properties['ServerId']
        self.ssh_key = self.resource_properties['SshPublicKeyBody']
        self.username = self.resource_properties['UserName']
        self.home_dir = self.resource_properties.get('HomeDirectory', f'/{self.username}')

    @staticmethod
    def add_if_not_none(params, key, value):
        if value is not None:
            params[key] = value

    def build_params(self):
        required = {
            'HomeDirectory': self.home_dir,
            'Role': self.role,
            'ServerId': self.server_id,
            'UserName': self.username
        }
        self.add_if_not_none(required, 'Policy', self.policy)

        return required

    def create(self):
        transfer_client = self.get_boto3_client('transfer')

        params = self.build_params()
        params['SshPublicKeyBody'] = self.ssh_key
        transfer_client.create_user(**params)
        self.physical_resource_id = self.username

        return {'ServerId': self.server_id, 'UserName': self.username}

    def update(self):
        transfer_client = self.get_boto3_client('transfer')

        params = self.build_params()
        transfer_client.update_user(**params)

        return {'ServerId': self.server_id, 'UserName': self.username}

    def delete(self):
        transfer_client = self.get_boto3_client('transfer')

        transfer_client.delete_user(ServerId=self.server_id, UserName=self.username)

        return {'ServerId': self.server_id, 'UserName': self.username}


handler = User.get_handler()
