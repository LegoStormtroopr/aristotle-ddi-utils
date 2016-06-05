from django.http import HttpResponse
from django.shortcuts import render

from lxml import etree

from aristotle_mdr.utils import get_download_template_path_for_item
from aristotle_mdr.downloader import items_for_bulk_download
from aristotle_ddi_utils.serializers import register, fragment

item_register = {
    'ddi3.2': {
        'aristotle_mdr': ['dataelement', 'dataelementconcept', 'objectclass'],
    }
}

def download(request,downloadType,item):

    template = get_download_template_path_for_item(item,downloadType)


    serializer = register.get(item.item.__class__)
    xml = fragment(serializer.to_xml(item.item))
    
    response = HttpResponse(etree.tostring(xml, pretty_print=True), content_type='application/xml')
    #response['Content-Disposition'] = 'attachment; filename=%s.ddi.xml'%item.id

    return response


def bulk_download(request, download_type, items, title=None, subtitle=None):

    item_querysets = items_for_bulk_download(items, request)
    print item_querysets
    base_frag = fragment()
    for item_set in item_querysets.values():
        items = item_set['qs']
        for item in items:
            if item:
                serializer = register.get(item.item.__class__)
                if serializer:
                    base_frag.append(serializer.to_xml(item.item))
    
    response = HttpResponse(etree.tostring(base_frag, pretty_print=True), content_type='application/xml')
    return response
