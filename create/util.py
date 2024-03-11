
def leave_dict_diff(dict1: dict, dict2: dict) -> dict:
    """
    dict1's leave type minus dict2's leave type

    Return
    ========
    If succeed: {'statue': 'valid', content: {leaveID: hours}}
    if leave hour not enough: {'status': 'invalid, {leave_id} not enough'}
    """
    return_dict = {'status': None}
    if dict2:
        for key in dict2:
            try:
                if dict1[key] >= dict2[key]:
                    return_dict['status'] = 'valid'
                    dict1[key] = dict1[key] - dict2[key]
                    return_dict['content'] = dict1
                else:
                    return_dict['status'] = 'invalid'
                    return_dict['content'] = f'{key} not enough'
            except:
                return_dict['status'] = f'invalid, {key} leave type not in dict1'
            finally:
                return return_dict
    else:
        return_dict['status'] = 'valid'
        return_dict['content'] = dict1
        return return_dict
