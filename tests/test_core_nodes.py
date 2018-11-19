from datetime import datetime, timezone

from freezegun import freeze_time

from corrente import core


def test_node_transaction_simple():
    
    # connect producer node with transporter node
    node_producer = core.DataNode(2743, {'product': 'corn', 'ammount': 1500})
    node_transporter_source = core.DataNode(8364, {
        'service':'transport',
        'vehicle':{'type': 'truck', 'registry': 'ABC1234567890'}})
    with freeze_time(datetime(2018,6,1,9,1, tzinfo=timezone.utc)):
        node_producer.process_hash_chain()
    with freeze_time(datetime(2018,6,1,9,2, tzinfo=timezone.utc)):
        node_transporter_source.process_hash_chain()
    transaction_transport_source = core.TransactionNode(
        'TRANSPORT-SOURCE',
        node_producer.hash_chain__object.make_playload(),
        node_transporter_source.hash_chain__object.make_playload(),
    )
    with freeze_time(datetime(2018,6,1,9,3, tzinfo=timezone.utc)): # todo: use timestamp, maybe
        transaction_transport_source.process_source_signature() # todo: source key
    with freeze_time(datetime(2018,6,1,9,4, tzinfo=timezone.utc)): # todo: use timestamp, maybe
        transaction_transport_source.process_target_signature() # todo: target key
    with freeze_time(datetime(2018,6,1,9,5, tzinfo=timezone.utc)):
        transaction_transport_source.process_hash_chain()
    
    # connect transporter node with consumer node
    node_transporter_target = core.DataNode(8364, {
        'service':'transport',
        'vehicle':{'type': 'truck', 'registry': 'ABC1234567890'},
        'route': [(1,1),(2,4),(3,5)]})
    node_consumer = core.DataNode(7463, {'product': 'corn', 'ammount': 1500})
    with freeze_time(datetime(2018,6,1,14,1, tzinfo=timezone.utc)):
        node_transporter_target.process_hash_chain()
    with freeze_time(datetime(2018,6,1,14,2, tzinfo=timezone.utc)):
        node_consumer.process_hash_chain()
    transaction_transport_target = core.TransactionNode(
        'TRANSPORT-TARGET',
        node_transporter_target.hash_chain__object.make_playload(),
        node_consumer.hash_chain__object.make_playload(),
    )
    with freeze_time(datetime(2018,6,1,14,3, tzinfo=timezone.utc)): # todo: use timestamp, maybe
        transaction_transport_target.process_source_signature() # todo: source key
    with freeze_time(datetime(2018,6,1,14,4, tzinfo=timezone.utc)): # todo: use timestamp, maybe
        transaction_transport_target.process_target_signature() # todo: target key
    with freeze_time(datetime(2018,6,1,14,5, tzinfo=timezone.utc)):
        transaction_transport_target.process_hash_chain()
    
    # connect source transport node with target transport node
    
    
    # connect consumer node with producer node by sale Transaction node
    
    
    # connect consumer node with producer node by payment Transaction node
