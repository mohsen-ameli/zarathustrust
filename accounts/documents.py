# from django_elasticsearch_dsl import Document
# from django_elasticsearch_dsl.registries import registry
# from users.models import CustomUser

# @registry.register_document
# class CustomeUserDocment(Document):
#     class Index:
#         name = 'CustomUser'

#     settings = {
#         'number_of_shards': 1,
#         'number_of_replicas': 0
#     }

#     class Django:
#         model = CustomUser
        
#         fields = [
#             'username',
#             'phone_number',
#             'email'
#         ]