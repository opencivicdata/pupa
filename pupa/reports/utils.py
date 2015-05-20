from pupa.models import DataQualityTypes


def percentage(numerator, denominator):
    if denominator == 0:
        return 0
    else:
        share = numerator / denominator
        percentage = share * 100
        return percentage


def assert_data_quality_types_exist(ocd_type, report):
    for type_ in report.keys():
        matches = DataQualityTypes.objects.filter(object_type=ocd_type, name=type_)
        assert len(matches) == 1, "{} data quality type does not exist for {} report".format(type_, ocd_type)


def get_or_create_type_and_modify(ocd_type, name, bad_range, is_percentage):
    data_quality_type, created = DataQualityTypes.objects.get_or_create(
        object_type=ocd_type, name=name,
        defaults={'bad_range': 1, 'is_percentage': is_percentage})
        # object_type=ocd_type, name=name, defaults={'bad_range': (None, None)})
    if not created:
        # data_quality_type.bad_range = bad_range
        data_quality_type.is_percentage = is_percentage
        data_quality_type.save()
