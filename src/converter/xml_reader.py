import logging
import os
from typing import Optional, List

from pedantic import pedantic_class
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET

from src.converter.bpmn_models.bpmn_enum import BPMNEnum

@pedantic_class
class XMLReader:
    """
    A XMLReader gets a path to a *.xml-file and parses it. It saves the XML-DOM
    to be queried and searched.
    There a additional functionalities:
    1. makes a copy of the file and only works on the copy
    2. modifies (copied) file to make it parsable (workaround to a bug)
    """
    def __init__(self,
                 xml_dom: Optional[Element] = None,
                 abs_path: Optional[str] = None,
                 rel_path: Optional[str] = None) -> None:
        self.xml_dom = xml_dom
        self.abs_path = abs_path
        self.rel_path = rel_path
        self.temp_name = 'temp_' # all copied files start with this string

    def prepare_dom(self,abs_file_path: str) -> str:
        """
        Prepares the *.xml-file to make it parsable.
        1.The bpmn-xml of demo.bpmn.io contains wrong
        xmlns-definitions (tag: <definitions>)that prevent the python xml
        parser to read the xml. We need to kick them out.

        2. The *.xml-file contains diagram-position-attributes
        (X-Y-Coordinates) of the elements. At first glance this is
        not a problem but when deleting the surrounding <definitions> tag
        we got a not-well formed xml:
        before:
         <definitions ....> # prevent parsing
            <process>
                # our process description. Contains all the BPMNs
            </process>
            <bpmndi>
                # X-Y-Coordinates of all the BPMNs
            </bpmndi>
        </definitions>

        When deleting <definitions>, the xml is not well-formed, because
        the surrounding brackets are missing.
            <process>
                ...
            </process>
            <bpmndi>
                ...
            </bpmndi>
        So we delete bpmndi and all sub-tags too.

        Alternative:
        You may think it would be easier to query the <process> tag and work
        with it instead of deleting half of the document. Well yes but actually
        no. We cannot parse/read the original document, because the parser dies.
        Therefore we cannot query <process>.
        """

        # We open (r = read) the file and save all lines in file in a
        # list of strings.
        with open(abs_file_path, 'r') as f:
            lines = f.readlines()

        # lines to delete start with those tags
        block_line_tags = ['<definitions', '</definitions',
                            '<bpmndi', '</bpmndi',
                            '<omgdi', '<omgdc']

        # sometimes some of the block_line_tags start with 'bpmn:'
        # e.g 'bpmn:omgdi' or 'bpmn:bpmndi'
        # so we add all those tags to the existing list
        # @python implementation: we cannot simply traverse the list and
        # add the new element at the end, we would get an infinite loop.
        # So we use a temporary list and later extend the existing list.
        added_tags = []
        for tag in block_line_tags:
            added_tags.append('bpmn:' + tag)
        block_line_tags.extend(added_tags)

        # Make the new file content by copying line by line except those lines
        # that begin with a tag that is in block_line_tags
        new_file_content = [line for line in lines
                    if not any(map(line.__contains__, block_line_tags))]

        # We write a new file and change the self.abs_path so
        # every function calling this XMLReader will work on the new file.
        new_file_path = self.make_temp_file_path(abs_file_path=abs_file_path)
        self.abs_path = new_file_path

        # Write (=w) the new file
        try:
            with open(new_file_path, 'w') as f:
                for line in new_file_content:
                    f.write(line)
        except FileExistsError:
            pass

        return new_file_path

    def parse_to_dom(self, abs_file_path: str) -> Element:
        """
        Opens the XML-file and parses to a DOM you can then query.
        """
        if not os.path.isabs(abs_file_path):
            abs_file_path = os.path.abspath(abs_file_path)

        if not os.path.isfile(abs_file_path):
            logging.error(f'File not found: {abs_file_path}')
            raise FileNotFoundError(abs_file_path)

        self.prepare_dom(abs_file_path=abs_file_path)

        self.xml_dom = ET.parse(self.abs_path).getroot()

        # temp files now useless. clean them
        self.clean_temp_file_path()

        return self.xml_dom

    def query(self, element_type: BPMNEnum) -> List[Element]:
        """
        Returns all elements in the XML-file of the given type.
        Example:
            <hello>
              <world id_=123\>
              <world id_=456\>
            <\hello>
            element_type: 'world'
        Returns: [<world id_=456>] with 'world' being an object (not a string!)
        """

        if self.xml_dom is None:
            logging.debug('XML-DOM of XML-Reader is None. Used parse_to_dom() to initiate.')
            self.xml_dom = self.parse_to_dom(abs_file_path=self.abs_path)

        # build the XPath-Query here. XPath-Documentation:
        # https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath
        # With .// we search the whole document.

        # What is bpmn_tag? Well I forgot. In one version of the camunda frontEnd
        # the queries work without the bpmn_tag. And in one version we need to
        # add this bpmn_tag. Would be a nice thing to recheck and refactor this
        # in future.
        elements_in_file = []
        bpmn_tag = '{http://www.omg.org/spec/BPMN/20100524/MODEL}'
        for element in self.xml_dom.findall(
                './/' + bpmn_tag + element_type.value):
            elements_in_file.append(element)

        # in older tests, the 'bpmn:' tag (which resolves} is not present.
        # So it doesnt find anything.
        # so we query without the bpmn-tag
        if len(elements_in_file) == 0:
            for element in self.xml_dom.findall(
                    './/' + element_type.value):
                elements_in_file.append(element)

        return elements_in_file


    def make_temp_file_path(self, abs_file_path: str) -> str:
        """
        Adds self.temp_name in front of filename in a absolute path.
        Example:
            C:/.../src/my_home.xml
            --> C:/.../src/temp_my_home.xml
        """
        new_file_name = os.path.join(self.temp_name + os.path.basename(abs_file_path))
        original_folder_path = os.path.dirname(abs_file_path)
        return os.path.join(original_folder_path, new_file_name)


    def clean_temp_file_path(self) -> None:
        """
        reverting the temp to original file:
        delete temp_ file and set self.abs_path back to original file
        """
        temp_file_path = self.abs_path

        filename = os.path.basename(temp_file_path)
        if self.temp_name in filename:
            # delete file_path
            os.remove(path=temp_file_path)
            # setting back
            self.abs_path.replace(self.temp_name, '')
