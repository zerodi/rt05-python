from typing import TypedDict

from tesmart import utils


class Param(TypedDict):
    addr: str
    size: int
    type: type


###
# T Текущая высчитывается, как (temp_11 + temp_2) / 2
# T Задание высчитывается, как (temp_o + temp_p) / 2 - temp_const
###
current = dict(
    {
        # Секунда
        't_ss': Param(addr='000', size=1, type=int),
        # Минута
        't_mm': Param(addr='001', size=1, type=int),
        # Час
        't_hh': Param(addr='002', size=1, type=int),
        # День недели
        't_dey': Param(addr='003', size=1, type=int),
        # День месяца
        't_dm': Param(addr='004', size=1, type=int),
        # Месяц
        't_my': Param(addr='005', size=1, type=int),
        # Год
        't_yy': Param(addr='006', size=1, type=int),
        # Время наработки
        'Tall': Param(addr='00E', size=4, type=int),
        # Версия ПО
        'Version': Param(addr='04A', size=2, type=int),
        # Серийный номер
        'SerialN': Param(addr='04C', size=4, type=int),
        # T11
        'temp_11': Param(addr='069', size=2, type=int),
        # T2
        'temp_2': Param(addr='06B', size=2, type=int),
        # Tк
        'temp_k': Param(addr='06D', size=2, type=int),
        # Тн (если < 0, то инвертировать int(value, 16) - int('FFFF', 16))
        'temp_n': Param(addr='06F', size=2, type=int),
        'temp_21': Param(addr='071', size=2, type=int),
        # dTцрк
        'temp_d_crk': Param(addr='073', size=2, type=int),
        'temp_ts': Param(addr='078', size=2, type=int),
        # Tо(расч)
        'temp_o': Param(addr='07A', size=2, type=int),
        # Tп(расч)
        'temp_p': Param(addr='07C', size=2, type=int),
        # TConst
        'temp_const': Param(addr='0E6', size=2, type=int),
    },
)


def read_int(body: bytearray, address: int, size: int) -> int:
    return utils.bytes_to_int(body[address : address + size])


def transform_current_response(body: bytearray) -> dict:
    result = dict()
    if body:
        for key, value in current.items():
            if value['type'] == int:
                result[key] = read_int(body, int(value['addr'], 16), value['size'])
    return result
