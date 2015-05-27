from mock import patch
from ..src.emonhub_interfacer import EmonHubYunInterfacer

class MockBridgeClient():
    """Mock bridgeclient use for testing

    Interface based on: 
    https://github.com/arduino/YunBridge/blob/master/bridge/bridgeclient.py
    
    """
    def __init__(self):
        self._datastore = { } 
    
    def put(self, key, value):
        self._datastore[key] = value

    def get(self, key):
       return self._datastore[key] 

    def delete(self, key):
        if key in self._datastore:
            del self._datastore[key]


class TestEmonHubYunInterfacer:
    
    """Setup and teardown methods

    Instantiate EmonHubYunInterfacer and a mock BridgeClient
    before each test.

    """

    @patch('emonhub.src.emonhub_interfacer.BridgeClient')
    def setup(self, mock_bridge):
        self._interface = EmonHubYunInterfacer("Test")
        self._interface._bridgeclient = MockBridgeClient()
        self._interface._bridgeclient.put('reading', '')

    def test_read_empty_mailbox(self):
        data = self._interface.read()
        assert data is None

    def test_invalid_nodeid(self):
        """Node ID must be between the values of > 0 and < 31 
        """
        client = self._interface._bridgeclient
        client.put('reading', '40 10 10')
        data = self._interface.read()
        assert data is None

    def test_invalid_frame(self):
        """Frame must only contain numerical data
        """
        client = self._interface._bridgeclient
        client.put('reading', '40 11.0 b')
        data = self._interface.read()
        assert data is None
        
    def test_read_message(self):
        # Insert key
        client = self._interface._bridgeclient
        client.put('reading', '11 1.1 224.27')
        data = self._interface.read()
        assert data is not None

        # Check format of list
        assert data[1] == 11
        assert data[2] == 1.1
        assert data[3] == 224.27

        # Check that reading has been reset after a read
        assert client.get('reading') == ''
