from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from lxml import etree

from aristotle_mdr import models
from aristotle_ddi_utils import utils
from aristotle_mdr.contrib.slots.models import SlotDefinition, Slot

register = {}

def register_ddi_serializer(cls):
    cls()

def get_version(xml):
    return (0,1,2)

def fragment(*elems):
    xml = etree.Element("{ddi:instance:3_2}fragment")
    for elem in elems:
        xml.append( elem )
    return xml


class DDI_conceptSerializer(object):
    app_label = None
    model_name = None
    model = None
    ddi_namespace = ""
    ddi_elementname = ""

    def __init__(self, *args, **kwargs):
        super(DDI_conceptSerializer, self).__init__(*args, **kwargs)
        register.update({self.model: self})
        self.app_label = self.model._meta.app_label
        self.model_name = self.model._meta.model_name

    @classmethod
    def to_aristotle(cls, xml):
        agency, identifier, version = get_version()
        concept_model = ContentType.objects.get(app_label=cls.app_label, model=cls.model_name).model_class().objects.all
        ddi_agency = SlotDefinition.object.get_or_create(name="DDI Agency", **model)
        ddi_identifier = SlotDefinition.object.get_or_create(name="DDI Identifier", **model)
        ddi_version = SlotDefinition.object.get_or_create(name="DDI Version", **model)
        try:
            concept_model = concept_model.filter(slot__type=ddi_agency, slot__value=agency)
            concept_model = concept_model.filter(slot__type=ddi_identifier, slot__value=identifier)
            concept_model = concept_model.filter(slot__type=ddi_version, slot__value=version)
            concept = concept_model.first()
        except:
            pass


    @classmethod
    def to_ddi_urn(cls, obj):
        ddi_urn = SlotDefinition.objects.get(slot_name="DDI URN")

        urn = Slot.objects.filter(concept=obj.concept, type=ddi_urn).first()
        if urn:
            ddi_urn = urn.value
        else:
            agency = getattr(settings, 'ARISTOTLE_DDI_AGENCY', "example.com")
            _id = str(obj.id)
            version = str(obj.version) or '0.0.1'
            ddi_urn = "urn:ddi:%s:%s:%s"%(agency,_id,version)

        urn = etree.Element("{ddi:reusable:3_2}URN")
        urn.text = ddi_urn
        return urn

    @classmethod
    def to_ddi_userid(cls, obj):
        user_id = etree.Element("{ddi:reusable:3_2}UserID")
        user_id.text = str(obj.pk)
        user_id.attrib['typeOfUserID'] = 'aristotle_mdr'
        return user_id

    @classmethod
    def to_xml(cls, obj, inline=False):
        xml = etree.Element("{%s}%s"%(cls.ddi_namespace,cls.ddi_elementname))

        xml.append(cls.to_ddi_urn(obj))
        name = etree.SubElement(xml, "{%s}%sName"%(cls.ddi_namespace,cls.ddi_elementname))
        etree.SubElement(name, "{ddi:reusable:3_2}String").text = obj.name

        desc = etree.SubElement(xml, "{ddi:reusable:3_2}Description")
        etree.SubElement(desc, "{ddi:reusable:3_2}Content").text = obj.definition

        xml.append(cls.to_ddi_userid(obj))

        return xml

    def get_ddi_id(obj):
        pass

    @classmethod
    def build_xml_reference(cls, obj):
        ref = etree.Element("{ddi:reusable:3_2}%sReference"%(cls.ddi_elementname))

        ref.append(cls.to_ddi_urn(obj))
        ref.append(cls.to_ddi_userid(obj))

        return ref

class DDI_32_DataElement(DDI_conceptSerializer):
    model = models.DataElement
    ddi_namespace = "ddi:logicalproduct:3_2"
    ddi_elementname = "RepresentedVariable"

    def to_aristotle(self):
        pass

    @classmethod
    def to_xml(cls, obj, *args, **kwargs):
        xml = super(DDI_32_DataElement, cls).to_xml(obj, *args, **kwargs)

        if obj.dataElementConcept:
            xml.append(DDI_32_DataElementConcept().build_xml_reference(obj.dataElementConcept))
        if obj.valueDomain:
            xml.append(DDI_32_ValueDomain().build_xml_reference(obj.valueDomain))

        return xml        

register_ddi_serializer(DDI_32_DataElement)


class DDI_32_DataElementConcept(DDI_conceptSerializer):
    model = models.DataElementConcept
    ddi_namespace = "ddi:logicalproduct:3_2"
    ddi_elementname = "ConceptualVariable"

    def to_aristotle(self):
        pass


class DDI_32_ObjectClass(DDI_conceptSerializer):
    model = models.ObjectClass
    ddi_namespace = "ddi:conceptualcomponent:3_2"
    ddi_elementname = "Universe"

    def to_aristotle(self):
        pass


register_ddi_serializer(DDI_32_ObjectClass)


class DDI_32_ValueDomain(DDI_conceptSerializer):
    model = models.ValueDomain
    ddi_namespace = "ddi:reusable:3_2"
    ddi_elementname = None

    def to_aristotle(self):
        pass

    @classmethod
    def to_xml(cls, obj, *args, **kwargs):
        cls.ddi_elementname = utils.valuedomain_dditype(obj)
        return super(DDI_32_ValueDomain, cls).to_xml(obj, *args, **kwargs)

    @classmethod
    def build_xml_reference(cls, obj, *args, **kwargs):
        cls.ddi_elementname = utils.valuedomain_dditype(obj)
        return super(DDI_32_ValueDomain, cls).build_xml_reference(obj, *args, **kwargs)

	
register_ddi_serializer(DDI_32_ValueDomain)
