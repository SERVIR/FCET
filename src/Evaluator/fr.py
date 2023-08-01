from tables.models import CBSmeans
from tables.serializers import CBSmeansSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser





table = CBSmeans(name = 't_soc',
                  sample = 'Unmatched',
                  treated = 0.48805,
                  control = 0.63231,
                  bias = -29.4,
                  t = -18.67,
                  pt = 0.000
                  )
table.save()                  