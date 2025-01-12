import copy

import numpy as np
import pytest
import qcelemental as qcel
from qcelemental.testing import compare_recursive
from qcengine.testing import using_molpro

import qcengine as qcng

# qcenginerecords not required, skips whole file
qcer = pytest.importorskip("qcenginerecords")

# Prep globals
molpro_info = qcer.get_info('molpro')


@pytest.mark.parametrize('test_case', molpro_info.list_test_cases())
def test_molpro_output_parser(test_case):

    # Get output file data
    data = molpro_info.get_test_data(test_case)
    inp = qcel.models.ResultInput.parse_raw(data["input.json"])

    output = qcng.get_program('molpro', check=False).parse_output(data, inp).dict()
    output.pop("provenance", None)

    output_ref = qcel.models.Result.parse_raw(data["output.json"]).dict()
    output_ref.pop("provenance", None)

    # TODO add `skip` to compare_recursive
    check = compare_recursive(output_ref, output, forgive={"stdout"})
    assert check, check


@pytest.mark.parametrize('test_case', molpro_info.list_test_cases())
def test_molpro_input_formatter(test_case):

    # Get input file data
    data = molpro_info.get_test_data(test_case)
    inp = qcel.models.ResultInput.parse_raw(data["input.json"])

    # TODO add actual comparison of generated input file
    input_file = qcng.get_program('molpro', check=False).build_input(inp, qcng.get_config())
    assert input_file.keys() >= {"commands", "infiles"}


@using_molpro
@pytest.mark.parametrize('test_case', molpro_info.list_test_cases())
def test_molpro_executor(test_case):
    # Get input file data
    data = molpro_info.get_test_data(test_case)
    inp = qcel.models.ResultInput.parse_raw(data["input.json"])

    # Run Molpro
    result = qcng.compute(inp, 'molpro', local_options={"ncores": 4})
    assert result.success is True

    # Get output file data
    output_ref = qcel.models.Result.parse_raw(data["output.json"])

    atol = 1e-6
    assert compare_recursive(output_ref.return_result, result.return_result, atol=atol)
