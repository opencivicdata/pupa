from django.db import models


class DivisionManager(models.Manager):

    def children_of(self, division_id, subtype=None, depth=1):
        pieces = [piece.split(':', 1) for piece in division_id.split('/')]
        query = {}

        # if they included the ocd-division bit, pop it off
        if pieces[0] == ['ocd-division']:
            pieces.pop(0)

        if pieces[0][0] != 'country':
            raise ValueError('OCD id must start with country')

        query['country'] = pieces[0][1]

        # add the remaining pieces
        n = 1
        for stype, subid in pieces[1:]:
            query['subtype{0}'.format(n)] = stype
            query['subid{0}'.format(n)] = subid
            n += 1

        # only get children
        if subtype:
            query['subtype{0}'.format(n)] = subtype
        else:
            query['subtype{0}__isnull'.format(n)] = False
        query['subid{0}__isnull'.format(n)] = False

        # allow for depth wildcards
        n += depth

        # ensure final field is null
        query['subtype{0}__isnull'.format(n)] = True
        query['subid{0}__isnull'.format(n)] = True

        return self.filter(**query)


class Division(models.Model):
    objects = DivisionManager()

    id = models.CharField(max_length=300, primary_key=True)
    display_name = models.CharField(max_length=300)
    country = models.CharField(max_length=2)
    redirect = models.ForeignKey('self', null=True)

    # up to 7 pieces of the id that are searchable
    subtype1 = models.CharField(max_length=50, null=True, blank=True)
    subid1 = models.CharField(max_length=100, null=True, blank=True)
    subtype2 = models.CharField(max_length=50, null=True, blank=True)
    subid2 = models.CharField(max_length=100, null=True, blank=True)
    subtype3 = models.CharField(max_length=50, null=True, blank=True)
    subid3 = models.CharField(max_length=100, null=True, blank=True)
    subtype4 = models.CharField(max_length=50, null=True, blank=True)
    subid4 = models.CharField(max_length=100, null=True, blank=True)
    subtype5 = models.CharField(max_length=50, null=True, blank=True)
    subid5 = models.CharField(max_length=100, null=True, blank=True)
    subtype6 = models.CharField(max_length=50, null=True, blank=True)
    subid6 = models.CharField(max_length=100, null=True, blank=True)
    subtype7 = models.CharField(max_length=50, null=True, blank=True)
    subid7 = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return '{0} ({1})'.format(self.display_name, self.id)

    def get_absolute_url(self):
        return reverse('division', args=(self.id,))
