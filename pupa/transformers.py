import re


_bill_id_re = re.compile(r'([A-Z]*)\s*0*([-\d]+)')
_mi_bill_id_re = re.compile(r'(SJR|HJR)\s*([A-Z]+)')


def fix_bill_id(bill_id):
    # special case for MI Joint Resolutions
    if _mi_bill_id_re.match(bill_id):
        return _mi_bill_id_re.sub(r'\1 \2', bill_id, 1).strip()
    return _bill_id_re.sub(r'\1 \2', bill_id, 1).strip()
