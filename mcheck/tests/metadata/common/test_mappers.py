"""
Copyright (C) 2016  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of meta-check

meta-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on Apr 08, 2016.
"""
import unittest
from mcheck.metadata.common.mappers import IdentifierMapper

class TestIdentifierMapper(unittest.TestCase):

    def test_seqsc2irods(self):
        id_type = 'internal_id'
        entity_type = 'sample'
        result = IdentifierMapper.seqsc2irods(id_type, entity_type)
        expected = 'sample_id'
        self.assertEqual(result, expected)

    def test_seqsc2irods_acc_nr(self):
        id_type = 'accession_number'
        entity_type = 'sample'
        result = IdentifierMapper.seqsc2irods(id_type, entity_type)
        expected = 'sample_accession_number'
        self.assertEqual(result, expected)

    def test_seq2irods_name(self):
        id_type = 'name'
        entity_type = 'library'
        result = IdentifierMapper.seqsc2irods(id_type, entity_type)
        expected = 'library'
        self.assertEqual(result, expected)