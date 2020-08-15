




'''
temp main to test converter
'''
from src.converter.converter import Converter

'''
XML Laden
traversen und jedes Element in ein Python Object schmeißen
'''

if __name__ == '__main__':
    #path_to_xml = r'..\bpmn-files\AB_unmodified.xml'
    #path_to_xml = r'..\bpmn-files\2.xml'
    path_to_xml = r'..\bpmn-files\1.xml'

    converter = Converter()
    converter.convert(path_to_bpmn=path_to_xml)


# # Test wegen Objekterstellung
# sequence_flow = BPMNSequenceFlow(id='Flow_0b8jwpw', source=None, target=None)
# start_event = BPMNStartEvent(id='Event_08oupc5', name='Eingang Rechnung Zittau', sequenceFlow=sequence_flow)
# activity = BPMNActivity(id='Activity_00dopgn', name='ML Unterschrift', sequenceFlowIn=sequence_flow)
#
