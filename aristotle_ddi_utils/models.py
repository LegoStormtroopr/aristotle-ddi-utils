from django.db import models
from aristotle_mdr import models as MDR

class DDI32Object(MDR._concept):
    namespace = models.CharField(max_length=256)
    element_name = models.CharField(max_length=256)
