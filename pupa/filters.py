import re


_bill_id_re = re.compile(r'([A-Z]*)\s*0*([-\d]+)')
_mi_bill_id_re = re.compile(r'(SJR|HJR)\s*([A-Z]+)')


def fix_bill_id(bill_id):
    # special case for MI Joint Resolutions
    if _mi_bill_id_re.match(bill_id):
        return _mi_bill_id_re.sub(r'\1 \2', bill_id, 1).strip()
    return _bill_id_re.sub(r'\1 \2', bill_id, 1).strip()


def apply_filters(filters, data):
    for key, key_filters in filters.items():
        if isinstance(key_filters, list):
            for filter in key_filters:
                data[key] = filter(data[key])
        elif isinstance(key_filters, dict):
            apply_filters(key_filters, data[key])
        else:
            data[key] = key_filters(data[key])


BILL_FILTERS = {
    'identifier': fix_bill_id
}
