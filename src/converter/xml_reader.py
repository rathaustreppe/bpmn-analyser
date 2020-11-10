import logging
import os
from typing import Optional, List, Tuple

from pedantic import pedantic_class
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET

from src.converter.bpmn_models.bpmn_enum import BPMNEnum

@pedantic_class
class XMLReader:
    def __init__(self,
                 xml_dom: Optional[Element] = None,
                 abs_path: Optional[str] = None,
                 rel_path: Optional[str] = None) -> None:
        self.xml_dom = xml_dom
        self.abs_path = abs_path
        self.rel_path = rel_path

    def prepare_dom(self,abs_file_path: str) -> str:
        """
        The bpmn-xml of demo.bpmn.io contains wrong
        xmlns-definitions that prevent the python xml
        parser to read the xml.
        We kick them out.
        It also creates alot of diagram-position-attributes.
        When kicking out <definitions>, the xml is still not
        well-formed:
        before:
        <definitions ....> # prevent parsing
            <process>
                # our process discription
            </process>
            <bpmndi>
                # information where to put diagrams in a gui
            </bpmndi>
        </definitions>
        So we delete bpmndi and all sub-tags too.
        """

        # we need those sadistic low-level commands, because
        # we cannot parse the xml, modify it with xpath and
        # write it back, because the parser dies.
        with open(abs_file_path, 'r') as f:
            lines = f.readlines()

        # lines to delete containing:
        # make sure to have opening and closing tags
        block_line_tags = ['<definitions', '</definitions',
                            '<bpmndi', '</bpmndi',
                            '<omgdi', '<omgdc']

        # sometimes 'bpmn:' is put in front of every line
        # update block_line_tags:
        added_tags = []
        for tag in block_line_tags:
            added_tags.append('bpmn:' + tag)

        block_line_tags.extend(added_tags)

        new_file = [line for line in lines
                    if not any(map(line.__contains__, block_line_tags))]

        # write the new file in a new file. Change the self.abs_path so every
        # function calling this XMLReader will work on the new file.
        new_file_path = self.make_temp_file_path(abs_file_path=abs_file_path)
        self.abs_path = new_file_path

        # access file with x: create when not existing, leave it when existing
        try:
            with open(new_file_path, 'w') as f:
                for line in new_file:
                    f.write(line)
        except FileExistsError:
            pass

        return new_file_path

    def parse_to_dom(self, abs_file_path: str) -> Element:
        if not os.path.isabs(abs_file_path):
            abs_file_path = os.path.abspath(abs_file_path)

        if not os.path.isfile(abs_file_path):
            logging.error(f'File not found: {abs_file_path}')
            raise FileNotFoundError(abs_file_path)

        # always prepare_dom(). Why? When malicious lines are in the document,
        # the parser may parse everything or may die. If he parses, then the
        # query cannot execute and returns None ==> dies at this point.
        # When something dies, we could run prepare_dom() and retest everything
        # again. This check is confusing when put in code.
        # So to keep things simple, we run the prepare_dom() method
        # every time at first.
        # It is fast as well!
        self.prepare_dom(abs_file_path=abs_file_path)

        self.xml_dom = ET.parse(self.abs_path).getroot()

        return self.xml_dom

    def query(self, element_type: BPMNEnum) -> List[Element]:
        """
        access all <elementnames> of xml file with XPath syntax
        .// means: in whole xml text (doesnt care about depth)
        https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath
        optional, you can specifiy a list of elements
        that are ignored
        return a list containing all elements in the xml with
        the <elementname> tag
        Example with exclude_ids: 123
        <hello>
          <world id_=123\>
          <world id_=456\>
        <\hello>
        elementname: 'world'
        Returns: [<world id_=456>] with 'world' beeing an object
        Args:
            element_type (BPMNEnum): elementname of bpmn-specification

        Returns:
        """
        if self.xml_dom is None:
            logging.debug('XML-DOM of XML-Reader is None. Used parse_to_dom() to initiate.')
            self.xml_dom = self.parse_to_dom(abs_file_path=self.abs_path)

        elements_in_file = []
        bpmn_tag = '{http://www.omg.org/spec/BPMN/20100524/MODEL}'
        for element in self.xml_dom.findall(
                './/' + bpmn_tag + element_type.value):

            # We dont need to preserve which sequence flow is
            # incomming and outgoing. This is stored in
            # sourceRef and targetRef of each sequenceFlow.
            elements_in_file.append(element)

        # in older tests, the 'bpmn:' tag (which resolves} is not present.
        # So it doesnt find anything.
        # so we query without the tag
        if len(elements_in_file) == 0:
            for element in self.xml_dom.findall(
                    './/' + element_type.value):
                elements_in_file.append(element)

        return elements_in_file

    @staticmethod
    def rel_to_abs_path(rel_path: str) -> str:
        if not os.path.isabs(rel_path):
            abs_path = os.path.abspath(rel_path)
            return abs_path
        else:
            abs_path = rel_path
            return abs_path

    def make_temp_file_path(self, abs_file_path: str) -> str:
        new_file_name = os.path.join('temp_' + os.path.basename(abs_file_path))
        original_folder_path = os.path.dirname(abs_file_path)
        return os.path.join(original_folder_path, new_file_name)


    def clean_temp_file_path(self) -> None:
        # reverting the temp to original file:
        # delete temp_ file and set self.abs_path back to original file
        temp_file_path = self.abs_path

        filename = os.path.basename(temp_file_path)
        if 'temp_' in filename:
            # delete file_path
            os.remove(path=temp_file_path)
            # setting back
            self.abs_path.replace('temp_', '')
