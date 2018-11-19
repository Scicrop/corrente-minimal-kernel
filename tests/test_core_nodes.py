from datetime import datetime, timezone

from freezegun import freeze_time

from corrente import core


def test_node_transction_simple():
    # create 3 nodes
    node_producer = core.DataNode(2743, {'product': 'corn', 'ammount': 1500})
    node_transporter = core.DataNode(8364, {
        'service':'transport',
        'vehicle':{'type': 'truck', 'registry': 'ABC1234567890'}})
    node_consumer = core.DataNode(7463, {'product': 'corn', 'ammount': 1500})
    # connect producer node with transporter node
    with freeze_time(datetime(2018,6,1,9,1, tzinfo=timezone.utc)):
        node_producer.process_hash_chain()
    with freeze_time(datetime(2018,6,1,9,2, tzinfo=timezone.utc)):
        node_transporter.process_hash_chain()
    transaction_transport = core.TransactionNode(
        'TRANSPORT',
        node_producer.hash_chain__object.make_playload(),
        node_transporter.hash_chain__object.make_playload(),
    )
    with freeze_time(datetime(2018,6,1,9,3, tzinfo=timezone.utc)): # todo: use timestamp, maybe
        transaction_transport.process_source_signature() # todo: source key
    with freeze_time(datetime(2018,6,1,9,4, tzinfo=timezone.utc)): # todo: use timestamp, maybe
        transaction_transport.process_target_signature() # todo: target key
    with freeze_time(datetime(2018,6,1,9,5, tzinfo=timezone.utc)):
        transaction_transport.process_hash_chain()
    # connect transporter node with consumer node
    
    # connect producer node with consumer node by transport Transaction Node
    
    # connect consumer node with producer node by sale
    
