import codecs


def prep_bytes(byte_str):
    byte_str.reverse()
    return ''.join(byte_str)


def calc_checksum(packet):
    return bytes([(~sum(packet) & 0xFF)])


def prepare_response(resp):
    response = _decode(resp)
    return '%s' % (_format_data(response.upper()))


def _decode(resp):
    return str(codecs.encode(resp, 'hex').decode('ascii'))


def _format_data(data):
    fmt_data = ''
    for i in range(0, len(data), 2):
        fmt_data += (data[i:i+2] + ' ')
    return fmt_data