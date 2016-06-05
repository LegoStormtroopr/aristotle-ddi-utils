from django.db.models import signals
import aristotle_dse
import aristotle_mdr
from django.conf import settings

def load_ddi_slots(**kwargs):
    print "Loading DDI Slots"
    signals.post_save.disconnect(aristotle_mdr.models.concept_saved)

    from aristotle_mdr.contrib.slots.models import SlotDefinition
    model = {'concept_type': '_concept', 'app_label': 'aristotle_mdr'}
    ddi_urn = SlotDefinition.objects.get_or_create(slot_name="DDI URN", **model)
    signals.post_save.connect(aristotle_mdr.models.concept_saved)

signals.post_syncdb.connect(load_ddi_slots, sender=aristotle_mdr.models)