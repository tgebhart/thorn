KAFKA = {
    'consumer_config' : {'bootstrap.servers': '0',
                  'default.topic.config': {'auto.offset.reset': 'smallest'}}
}

CASSANDRA = {
    'nodes': ['127.0.0.1'],
    'second_update_keyspace': {
        'name':'second_update',
        'query': "CREATE KEYSPACE second_update WITH replication = {'class':'SimpleStrategy','replication_factor':1};"}
}
