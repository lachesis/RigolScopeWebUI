import socket

class ScopeError(Exception):
    pass
class OperationInProgressError(ScopeError):
    pass
class OperationTimeoutError(ScopeError):
    pass

class Scope(object):
    def __init__(self, ip, port=5555):
        self.ip = ip
        self.port = port
        self.sock = None

    def connect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        self.sock = socket.socket()
        self.sock.settimeout(5)
        self.sock.connect((self.ip, self.port))

    def shutdown(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def _send_command(self, cmd, check_complete=True, expect_output=True):
        if check_complete:
            res = self.opc()
            if res != '1':
                raise OperationInProgressError()

        if self.sock is None:
            self.connect()
        self.sock.send(cmd + '\n')
        if not expect_output:
            return ''
        buf = ''
        while len(buf) < 64*1024*1024:  # never read more than 64MB
            try:
                x = self.sock.recv(1024)
            except socket.timeout:
                raise OperationTimeoutError()
            buf += x
            if x.endswith('\n'):
                break

        if check_complete:
            for i in xrange(50):
                res = self.opc()
                if res == '1':
                    break
                time.sleep(0.1)
            else:
                raise OperationInProgressError()

        return buf.strip()

    def idn(self):
        return self._send_command('*IDN?', check_complete=False)

    def opc(self):
        return self._send_command('*OPC?', check_complete=False)

    def get_screen_image(self):
        res = self._send_command(':DISP:DATA?', check_complete=True)

        # Strip the headers
        header_size = 2 + int(res[1])
        data_bytes = int(res[2:header_size])
        print header_size, data_bytes, len(res)
        data = res[header_size:header_size+data_bytes]

        return data
