"""
Copyright (C) 2015  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of metadata-check

metadata-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on Feb 11, 2015.
"""

from main import metadata_utils
from com import utils
from irods import icommands_wrapper as irods_wrapper

import error_types

# TODO: hardcoded that a fle should have 1 md5 attribute
def check_md5_metadata(irods_fpath, irods_metadata):
    md5_metadata = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(irods_metadata, 'md5')
    if not md5_metadata:
        raise error_types.IrodsMetadataAttributeFrequencyError(fpath=irods_fpath, attribute='md5', desired_occurances=1, actual_occurances=0)

    md5_chksum = irods_wrapper.iRODSChecksumOperations.get_checksum(irods_fpath)
    if md5_chksum:
        if not md5_metadata[0] == md5_chksum.md5:
            return error_types.WrongMD5Error(imeta_value=md5_metadata[0], ichksum_value=md5_chksum.md5, fpath=irods_fpath)


def check_run_id(irods_fpath, irods_metadata):
    """
    This test assumes that all the files in iRODS have exactly 1 run (=LANELETS)
    """
    irods_run_ids = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(irods_metadata, 'id_run')
    path_run_id = metadata_utils.iRODSUtils.get_run_from_irods_path(irods_fpath)
    if len(irods_run_ids) > 1:
        raise error_types.TestImpossibleToRunError(fpath=irods_fpath, test_name="check run id", reason="too many run ids in iRODS metadata("+str(len(irods_metadata))+"), don't know which one to compare against file name")
    elif len(irods_run_ids) < 1:
        raise error_types.TestImpossibleToRunError(fpath=irods_fpath, test_name="check run id", reason="no run id found in iRODS metadata")
    else:
        irods_run_id = irods_run_ids[0]
        if irods_run_id != path_run_id:
            raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=irods_fpath, attribute='id_run', irods_value=irods_run_id, filename_value=path_run_id)


def check_lane_metadata(irods_fpath, irods_metadata):
    lane_id = metadata_utils.iRODSUtils.get_lane_from_irods_path(irods_fpath)
    irods_lane_ids = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(irods_metadata, 'lane')
    if len(irods_lane_ids) < 1:
        raise error_types.TestImpossibleToRunError(fpath=irods_fpath, test_name="check lane id", reason="no lane ids found in iRODS metadata")
    elif len(irods_lane_ids) > 1:
        raise error_types.TestImpossibleToRunError(fpath=irods_fpath, test_name="check lane id", reason="too many lane ids("+ str(len(irods_lane_ids))+"), don't know against which one to check")
    else:
        irods_lane_id = irods_lane_ids[0]
        if not irods_lane_id == lane_id:
            raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=irods_fpath, attribute='lane', irods_value=irods_lane_ids, filename_value=lane_id)


def check_lanelet_name(irods_fpath, header_lanelets):
    if len(header_lanelets) < 1:
        raise error_types.TestImpossibleToRunError(fpath=irods_fpath, test_name="check lanelet name irods vs. header", reason="no header lanelets extracted from header")
    elif len(header_lanelets) > 1:
        raise error_types.TestImpossibleToRunError(fpath=irods_fpath, test_name="check lanelet name irods vs. header", reason="too many lanelets in header("+ str(len(header_lanelets))+ ")")
    irods_lanelet_name = metadata_utils.iRODSUtils.extract_lanelet_name_from_irods_fpath(irods_fpath)
    fname = utils.extract_basename(irods_lanelet_name)
    if fname != header_lanelets[0]:
        raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=irods_fpath, attribute='lanelet name', irods_value=irods_lanelet_name, filename_value=fname)


def check_reference(irods_fpath, irods_metadata, desired_ref):
    ref_paths = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(irods_metadata, 'reference')
    if len(ref_paths) > 1:
        raise error_types.TestImpossibleToRunError(fpath=irods_fpath, test_name="check reference", reason="too many references in iRODS metadata")
    elif len(ref_paths) < 1:
        raise error_types.TestImpossibleToRunError(fpath=irods_fpath, test_name="check reference", reason="no reference in iRODS metadata")
    else:
        ref_path = ref_paths[0]
    ref_name = metadata_utils.iRODSUtils.extract_reference_name_from_path(ref_path)
    if ref_name != desired_ref:
        raise error_types.WrongReferenceError(fpath=irods_fpath, desired_ref=desired_ref, header_ref='not implemented', irods_ref=ref_name)


# TODO: separate between the case in which the test is impossible to be run and the test is run and throws and error
def run_irods_seq_specific_tests(irods_path, irods_metadata, header_metadata, desired_ref=None):
    issues = []
    try:
        check_md5_metadata(irods_path, irods_metadata)
    except error_types.WrongMD5Error as e:
        issues.append(str(e))
    except error_types.IrodsMetadataAttributeFrequencyError as e:
        issues.append(error_types.TestImpossibleToRunError(fpath=e.fpath, test_name='Compare MD5 ichksum vs. iRODS metadata md5', reason=str(e)))

    try:
        check_run_id(irods_path, irods_metadata)
    except (error_types.IrodsMetadataAttributeVsFileNameError, error_types.TestImpossibleToRunError) as e:
        issues.append(str(e))

    try:
        check_lane_metadata(irods_path, irods_metadata)
    except (error_types.TestImpossibleToRunError, error_types.IrodsMetadataAttributeVsFileNameError) as e:
        issues.append(str(e))

    try:
        check_lanelet_name(irods_path, header_metadata.lanelets)
    except (error_types.TestImpossibleToRunError, error_types.IrodsMetadataAttributeVsFileNameError) as e:
        issues.append(str(e))

    if desired_ref:
        try:
            check_reference(irods_path, irods_metadata, desired_ref)
        except (error_types.WrongReferenceError, error_types.TestImpossibleToRunError) as e:
            issues.append(str(e))
    return issues