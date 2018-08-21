

class PackageParser:

    def __init__(self, packet_length):
        self._buffer = b""
        self.invalid_count = 0
        self._packet_length = packet_length


    def feed(self, data):
        self._buffer += data
        while len(self._buffer) >= self._packet_length:
            if self._buffer[0] != ord('#'):
                self.invalid_count += 1
                # try & forward the buffer to
                # the beginning of a potential message
                pos = self._buffer.find(b'#')
                if pos != -1:
                    self._buffer = self._buffer[pos:]
                    continue
            yield self._buffer[:self._packet_length]
            self._buffer = self._buffer[self._packet_length:]
