"""
T Текущая высчитывается, как (temp_11 + temp_2) / 2
T Задание высчитывается, как (temp_o + temp_p) / 2 - temp_const
"""
current = dict({
    # Секунда
    't_ss': {'addr': '000', 'size': 1, 'type': int},
    # Минута
    't_mm': {'addr': '001', 'size': 1, 'type': int},
    # Час
    't_hh': {'addr': '002', 'size': 1, 'type': int},
    # День недели
    't_dey': {'addr': '003', 'size': 1, 'type': int},
    # День месяца
    't_dm': {'addr': '004', 'size': 1, 'type': int},
    # Месяц
    't_my': {'addr': '005', 'size': 1, 'type': int},
    # Год
    't_yy': {'addr': '006', 'size': 1, 'type': int},
    # Время наработки
    'Tall': {'addr': '00E', 'size': 4, 'type': int},
    # Версия ПО
    'Version': {'addr': '04A', 'size': 2, 'type': int},
    # Серийный номер
    'SerialN': {'addr': '04C', 'size': 4, 'type': int},
    # T11
    'temp_11': {'addr': '069', 'size': 2, 'type': int},
    # T2
    'temp_2': {'addr': '06B', 'size': 2, 'type': int},
    # Tк
    'temp_k': {'addr': '06D', 'size': 2, 'type': int},
    # Тн (если < 0, то инвертировать int(value, 16) - int('FFFF', 16))
    'temp_n': {'addr': '06F', 'size': 2, 'type': int},
    'temp_21': {'addr': '071', 'size': 2, 'type': int},
    # dTцрк
    'temp_d_crk': {'addr': '073', 'size': 2, 'type': int},
    'temp_ts': {'addr': '078', 'size': 2, 'type': int},
    # Tо(расч)
    'temp_o': {'addr': '07A', 'size': 2, 'type': int},
    # Tп(расч)
    'temp_p': {'addr': '07C', 'size': 2, 'type': int},
    # TConst
    'temp_const': {'addr': '0E6', 'size': 2, 'type': int},

})
