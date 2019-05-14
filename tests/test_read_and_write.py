"""Unit tests for read_and_write module."""

import numpy as np
import pytest
from BZI.read_and_write import read_QE, read_vasp, read_vasp_input
from BZI.utilities import check_contained
from conftest import run
import os

tests = run("all read_and_write")

@pytest.mark.skipif("test_read_qe" not in tests, reason="different tests")
def test_read_qe():
    location = os.path.join(os.getcwd(), "tests")
    QE_data_Al = read_QE(location, "Al")

    assert QE_data_Al["bravais-lattice index"] == 2.0
    assert QE_data_Al["lattice parameter"] == "4.0460 a.u."
    assert QE_data_Al["unit-cell volume"] == "16.5584 (a.u.)^3"
    assert QE_data_Al["number of atoms/cell"] == 4.0
    assert QE_data_Al["number of atomic types"] == 1.0
    assert QE_data_Al["number of electrons"] == 12.0
    assert QE_data_Al["number of Kohn-Sham states"] == 10.0
    assert QE_data_Al["kinetic-energy cutoff"] == "40.0000 Ry"
    assert QE_data_Al["charge density cutoff"] == "160.0000 Ry"
    assert QE_data_Al["convergence threshold"] == 1.0E-08
    assert QE_data_Al["mixing beta"] == 0.7
    assert QE_data_Al["number of iterations used"] == ["8 plain", "0 mixing"]
    assert QE_data_Al["Exchange-correlation"] == "SLA-PW-PBX-PBC ( 1  4  3  4 0 0)"
    assert QE_data_Al["crystallographic constants"] == [4.046, 0.0, 0.0, 0.0, 0.0, 0.0]
    assert (QE_data_Al["crystal axes"] ==
            np.transpose([[-0.500000, 0.000000, 0.500000],
                          [0.000000, 0.500000, 0.500000],
                          [-0.500000, 0.500000, 0.000000]])).all()
    assert (QE_data_Al["reciprocal axes"]
            == np.transpose([[-1.000000, -1.000000, 1.000000],
                             [1.000000, 1.000000, 1.000000],
                             [-1.000000, 1.000000, -1.000000]])).all()
    assert QE_data_Al["Sym. Ops."] == 6.0
    assert QE_data_Al["number of reduced k-points"] == 4.0
    assert QE_data_Al["k-points"] == [[0.0, 0.0, 0.0],
                                   [0.5, -0.5, 0.5],
                                   [0.0, -1.0, 0.0],
                                   [0.5, 0.5, 0.5]]
    assert QE_data_Al["k-point weights"] == [0.25, 0.75, 0.75, 0.25]
    assert QE_data_Al["Dense grid"] == "537 G-vectors"
    assert QE_data_Al["FFT dimensions"] == (12.0, 12.0, 12.0)
    assert QE_data_Al["self-consistent calculation time"] == ["0.2 secs"]*4 + ["0.3 secs"]*7
    assert QE_data_Al["k-point plane waves"] == [65.0, 70.0, 64.0, 70.0]
    assert QE_data_Al["k-point energies"] == [[8.4972, 13.4207, 13.6719,
                                               13.6719, 37.6953, 37.6953,
                                               37.7436, 43.5118, 43.5118, 84.4353],
                                              [-6.3826, 4.6733, 7.5091,
                                               7.7205, 35.8214, 35.9668,
                                               39.5326, 48.0515, 48.1570, 80.9232],
                                              [3.2720, 12.9556, 13.1129,
                                               15.8590, 27.2614, 31.5269,
                                               56.3308, 56.7839, 56.7942, 117.8606],
                                              [-6.6101, 4.7046, 7.7376,
                                               7.7376, 35.9858, 35.9858,
                                               39.5725, 47.9988, 47.9988, 81.0608]]
    assert QE_data_Al["Fermi energy"] == "37.6961 ev"
    assert QE_data_Al["total energy"] == "172.57397669 Ry"
    assert QE_data_Al["one-electron contribution"] == "-13.72740223 Ry"
    assert QE_data_Al["hartree contribution"] == "29.48566464 Ry"
    assert QE_data_Al["xc contribution"] == "-23.69388655 Ry"
    assert QE_data_Al["ewald contribution"] == "180.50960083 Ry"
    assert QE_data_Al["number of self-consistent iterations"] == 10.0
    assert QE_data_Al["number of unreduced k-points"] == 8.0


    QE_data_Si = read_QE(location, "Si")

    assert QE_data_Si["bravais-lattice index"] == 2.0
    assert QE_data_Si["lattice parameter"] == "10.2600 a.u."
    assert QE_data_Si["unit-cell volume"] == "270.0114 (a.u.)^3"
    assert QE_data_Si["number of atoms/cell"] == 2.0
    assert QE_data_Si["number of atomic types"] == 1.0
    assert QE_data_Si["number of electrons"] == 8.0
    assert QE_data_Si["number of Kohn-Sham states"] == 16.0
    assert QE_data_Si["kinetic-energy cutoff"] == "20.0000 Ry"
    assert QE_data_Si["charge density cutoff"] == "80.0000 Ry"
    assert QE_data_Si["convergence threshold"] == 1.0E-08
    assert QE_data_Si["mixing beta"] == 0.7
    assert QE_data_Si["number of iterations used"] == ["8 plain", "0 mixing"]
    assert QE_data_Si["Exchange-correlation"] == "PBE ( 1  4  3  4 0 0)"
    assert QE_data_Si["crystallographic constants"] == [10.26, 0.0, 0.0, 0.0, 0.0, 0.0]
    assert (QE_data_Si["crystal axes"] ==
            np.transpose([[-0.500000, 0.000000, 0.500000],
                          [0.000000, 0.500000, 0.500000],
                          [-0.500000, 0.500000, 0.000000]])).all()
    assert (QE_data_Si["reciprocal axes"]
            == np.transpose([[-1.000000, -1.000000,  1.000000],
                             [1.000000,  1.000000,  1.000000],
                             [-1.000000,  1.000000, -1.000000]])).all()
    assert QE_data_Si["Sym. Ops."] == 48.0
    assert QE_data_Si["number of reduced k-points"] == 28.0
    assert QE_data_Si["k-points"] == [[-0.0833333,   0.0833333,   0.0833333],
                                      [-0.2500000,   0.2500000,  -0.0833333],
                                      [-0.4166667,   0.4166667,  -0.2500000],
                                      [ 0.4166667,  -0.4166667,   0.5833333],
                                      [ 0.2500000,  -0.2500000,   0.4166667],
                                      [ 0.0833333,  -0.0833333,   0.2500000],
                                      [-0.0833333,   0.4166667,   0.0833333],
                                      [-0.2500000,   0.5833333,  -0.0833333],
                                      [ 0.5833333,  -0.2500000,   0.7500000],
                                      [ 0.4166667,  -0.0833333,   0.5833333],
                                      [ 0.2500000,   0.0833333,   0.4166667],
                                      [-0.0833333,   0.7500000,   0.0833333],
                                      [ 0.7500000,  -0.0833333,   0.9166667],
                                      [ 0.5833333,   0.0833333,   0.7500000],
                                      [ 0.4166667,   0.2500000,   0.5833333],
                                      [-0.0833333,  -0.9166667,   0.0833333],
                                      [-0.2500000,  -0.7500000,  -0.0833333],
                                      [-0.0833333,  -0.5833333,   0.0833333],
                                      [-0.2500000,   0.2500000,   0.2500000],
                                      [-0.4166667,   0.4166667,   0.0833333],
                                      [ 0.4166667,  -0.4166667,   0.9166667],
                                      [ 0.2500000,  -0.2500000,   0.7500000],
                                      [-0.2500000,   0.5833333,   0.2500000],
                                      [ 0.5833333,  -0.2500000,   1.0833333],
                                      [ 0.4166667,  -0.0833333,   0.9166667],
                                      [-0.2500000,  -1.0833333,   0.2500000],
                                      [-0.4166667,   0.4166667,   0.4166667],
                                      [0.4166667 , -0.4166667 ,  1.2500000 ]]    
    assert QE_data_Si["k-point weights"] == [0.0092593,
                                             0.0277778,
                                             0.0277778,
                                             0.0277778,
                                             0.0277778,
                                             0.0277778,
                                             0.0277778,
                                             0.0555556,
                                             0.0555556,
                                             0.0555556,
                                             0.0555556,
                                             0.0277778,
                                             0.0555556,
                                             0.0555556,
                                             0.0555556,
                                             0.0277778,
                                             0.0555556,
                                             0.0277778,
                                             0.0092593,
                                             0.0277778,
                                             0.0277778,
                                             0.0277778,
                                             0.0277778,
                                             0.0555556,
                                             0.0555556,
                                             0.0277778,
                                             0.0092593,
                                             0.0277778]    
    assert QE_data_Si["Dense grid"] == "3287 G-vectors"
    assert QE_data_Si["FFT dimensions"] == (24.0, 24.0, 24.0)
    assert QE_data_Si["self-consistent calculation time"] == ["1.8 secs", "4.9 secs",
                                                              "5.9 secs", "6.9 secs",
                                                              "8.1 secs", "9.4 secs",
                                                              "10.5 secs"]
    assert QE_data_Si["k-point plane waves"] == [405.0,
                                                 399.0,             
                                                 409.0,
                                                 407.0,
                                                 405.0,
                                                 401.0,
                                                 404.0,
                                                 409.0,
                                                 409.0,
                                                 411.0,
                                                 404.0,
                                                 413.0,
                                                 411.0,
                                                 405.0,
                                                 407.0,
                                                 413.0,
                                                 410.0,
                                                 413.0,
                                                 401.0,
                                                 404.0,
                                                 406.0,
                                                 412.0,
                                                 412.0,
                                                 409.0,
                                                 405.0,
                                                 410.0,
                                                 413.0,
                                                 406.0]
    assert QE_data_Si["k-point energies"] == [[-5.6605,  -5.6605,   5.3661,   5.3661,
                                               6.0681,   6.0681,   6.0995,   6.0995,
                                               8.8350,   8.8350,   8.9953,   8.9953,
                                               9.0182,   9.0182,  10.2406,  10.2406],
                                              [-5.1815,  -5.1815,   3.2771,   3.2771,
                                               4.8357,   4.8357,   5.8719,   5.8719,
                                               8.9453,   8.9453,   9.4044,   9.4044,
                                               9.7677,   9.7677,  11.9663,  11.9663],
                                              [-4.0830,  -4.0830,   0.4992,   0.4992,
                                               4.3700,   4.3700,   5.2281,   5.2281,
                                               8.4364,   8.4364,   9.7904,   9.7904,
                                               9.8333,   9.8333,  13.7227,  13.7227],
                                              [-3.3787,  -3.3787,  -0.6530,  -0.6530,
                                               4.4378,   4.4378,   4.8442,   4.8442,
                                               8.2785,   8.2785,   9.5055,   9.5055,
                                               9.9355,   9.9355,  14.1539,  14.1539],
                                              [-4.4974,  -4.4974,   1.3507,   1.3507,
                                               4.8992,   4.8992,   4.9459,   4.9459,
                                               8.5224,   8.5224,   9.5331,   9.5331,
                                               10.3314,  10.3314,  12.2212,  12.2212],
                                              [-5.4187,  -5.4187,   4.2945,   4.2945,
                                               5.4292,   5.4292,   5.6225,   5.6225,
                                               8.5420,   8.5420,   9.4551,   9.4551,
                                               9.9176,   9.9176,  11.1241,  11.1241],
                                              [-4.9392,  -4.9392,   3.0947,   3.0947,
                                               4.6763,   4.6763,   4.6974,   4.6974,
                                               7.9550,   7.9550,  10.1309,  10.1309,
                                               10.9287,  10.9287,  11.1519,  11.1519],
                                              [-4.0241,  -4.0241,   1.2470,   1.2470,
                                               3.3506,   3.3506,   4.3035,   4.3035,
                                               8.3569,   8.3569,   9.9889,   9.9889,
                                               10.8014,  10.8014,  12.2697,  12.2697],
                                              [-2.8995,  -2.8995,  -0.5176,  -0.5176,
                                               2.7481,   2.7481,   4.0738,   4.0738,
                                               8.6070,   8.6070,  10.1768,  10.1768,
                                               12.1452,  12.1452,  12.5239,  12.5239],
                                              [-3.6270,  -3.6270,   0.5489,   0.5489,
                                               2.7031,   2.7031,   4.5651,   4.5651,
                                               9.2154,   9.2154,   9.8443,   9.8443,
                                               11.5329,  11.5329,  12.0166,  12.0166],
                                              [-4.7125,  -4.7125,   2.2501,   2.2501,
                                               4.0530,   4.0530,   5.2409,   5.2409,
                                               8.8521,   8.8521,   9.7457,   9.7457,
                                               10.8044,  10.8044,  11.1450,  11.1450],
                                              [-3.3093,  -3.3093,   0.4207,   0.4207,
                                               3.3128,   3.3128,   3.6562,   3.6562,
                                               7.1201,   7.1201,   8.0991,   8.0991,
                                               13.8354,  13.8354,  13.8858,  13.8858],
                                              [-2.1063,  -2.1063,  -0.9255,  -0.9255,
                                               2.4633,   2.4633,   3.2456,   3.2456,
                                               7.7481,   7.7481,   8.8794,   8.8794,
                                               13.3672,  13.3672,  14.8470,  14.8470],
                                              [-2.4774,  -2.4774,  -0.5920,  -0.5920,
                                               1.9779,   1.9779,   3.7956,   3.7956,
                                               8.3730,   8.3730,  11.3050,  11.3050,
                                               12.2999,  12.2999,  12.9768,  12.9768],
                                              [-3.5134,  -3.5134,  -0.1459,  -0.1459,
                                               3.6560,   3.6560,   4.6641,   4.6641,
                                               8.8363,   8.8363,   9.4405,   9.4405,
                                               10.7834,  10.7834,  13.0097,  13.0097],
                                              [-2.1995,  -2.1995,  -0.9339,  -0.9339,
                                               3.0411,   3.0411,   3.4394,   3.4394,
                                               7.0053,   7.0053,   7.5772,   7.5772,
                                               15.3237,  15.3237,  15.4212,  15.4212],
                                              [-3.1393,  -3.1393,   0.1953,   0.1953,
                                               2.7890,   2.7890,   3.5883,   3.5883,
                                               7.9606,   7.9606,   9.2491,   9.2491,
                                               12.0055,  12.0055,  13.8328,  13.8328],
                                              [-4.2310,  -4.2310,   1.7917,   1.7917,
                                               3.8625,   3.8625,   4.0815,   4.0815,
                                               7.4443,   7.4443,   9.0175,   9.0175,
                                               12.2888,  12.2888,  12.4863,  12.4863],
                                              [-4.9508,  -4.9508,   2.2912,   2.2912,
                                               5.4474,   5.4474,   5.4788,   5.4788,
                                               8.2541,   8.2541,   9.7311,   9.7311,
                                               9.7529,   9.7529,  13.1357,  13.1357],
                                              [-4.2680,  -4.2680,   1.3580,   1.3580,
                                               3.3148,   3.3148,   5.2931,   5.2931,
                                               9.0155,   9.0155,  10.2401,  10.2401,
                                               10.4188,  10.4188,  12.3661,  12.3661],
                                              [-3.0816,  -3.0816,  -0.0873,  -0.0873,
                                               2.1993,   2.1993,   4.4988,   4.4988,
                                               8.2576,   8.2576,  11.5661,  11.5661,
                                               11.6851,  11.6851,  13.4208,  13.4208],
                                              [-3.0296,  -3.0296,  -0.1669,  -0.1669,
                                               2.6825,   2.6825,   4.0125,   4.0125,
                                               7.7539,   7.7539,  10.6924,  10.6924,
                                               11.9806,  11.9806,  12.1692,  12.1692],
                                              [-3.8415,  -3.8415,   0.5447,   0.5447,
                                               3.7865,    3.7865,   4.3888,   4.3888,
                                               8.2437,   8.2437,  10.4944,  10.4944,
                                               11.1416,  11.1416,  11.2952,  11.2952],
                                              [-2.8337,  -2.8337,  -0.1977,  -0.1977,
                                               2.2993,   2.2993,   3.5858,   3.5858,
                                               9.4663,   9.4663,  10.0073,  10.0073,
                                               10.9959,  10.9959,  13.7491,  13.7491],
                                              [-1.9976,  -1.9976,  -0.9333,  -0.9333,
                                               2.1313,   2.1313,   2.9126,   2.9126,
                                               9.2635,   9.2635,  10.5329,  10.5329,
                                               11.3481,  11.3481,  12.7404,  12.7404],
                                              [-2.2092,  -2.2092,  -0.8409,  -0.8409,
                                               2.0042,   2.0042,   3.8166,   3.8166,
                                               7.4736,   7.4736,  10.4065,  10.4065,
                                               13.3480,  13.3480,  13.5566,  13.5566],
                                              [-3.7511,  -3.7511,  -0.2501,  -0.2501,
                                               5.0551,   5.0551,   5.0868,   5.0868,
                                               7.8210,   7.8210,   9.6283,   9.6283,
                                               9.6439,   9.6439,  14.0372,  14.0372],
                                              [-3.1421,  -3.1421,  -0.5514,  -0.5514,
                                               3.2271,   3.2271,   4.6271,   4.6271,
                                               8.4203,   8.4203,  10.3070,  10.3070,
                                               10.6416,  10.6416,  14.2247,  14.2247]]
    assert QE_data_Si["Fermi energy"] == "6.1979 ev"
    assert QE_data_Si["total energy"] == "-22.83557223 Ry"
    assert QE_data_Si["one-electron contribution"] == "5.12540110 Ry"
    assert QE_data_Si["hartree contribution"] == "1.09647549 Ry"
    assert QE_data_Si["xc contribution"] == "-12.25651922 Ry"
    assert QE_data_Si["ewald contribution"] == "-16.80092959 Ry"
    assert QE_data_Si["number of self-consistent iterations"] == 6.0
    assert QE_data_Si["number of unreduced k-points"] == 216.0
    

@pytest.mark.skipif("test_read_vasp" not in tests, reason="different tests")
def test_read_vasp():

    location = os.path.join(os.getcwd(), "tests", "Al_VASP")
    vasp_input_data = read_vasp_input(location)
    vasp_data = read_vasp(location)

    assert np.allclose(vasp_input_data["ZVAL list"], [11.0])
    assert np.allclose(vasp_input_data["EAUG list"], [586.98])
    assert np.allclose(vasp_input_data["ENMAX list"], [295.446])
    assert vasp_input_data["number of unreduced k-points"] == 512
    assert np.allclose(vasp_input_data["offset"], [0.5]*3)
    assert vasp_input_data["name of system"] == "Cu4"
    assert np.isclose(vasp_input_data["scaling factor"], 1)
    assert np.allclose(vasp_input_data["lattice vectors"],
                       np.transpose([[3.616407, 0.000000, 0.000000],
                                     [0.000000, 3.616407, 0.000000],
                                     [0.000000, 0.000000, 3.616407]]))
    assert np.allclose(vasp_input_data["atomic basis"]["atom positions"],
                       [[0.000000, 0.000000, 0.000000],
                        [0.000000, 0.500000, 0.500000],
                        [0.500000, 0.000000, 0.500000],
                        [0.500000, 0.500000, 0.000000]])
     
    assert vasp_input_data["atomic basis"]["coordinates"] == "direct"
    
    assert vasp_input_data["atomic basis"]["number of atoms"] == 4
    assert vasp_input_data["atomic basis"]["number of atoms per atomic species"] == [4]
    assert vasp_data['number of unreduced k-points'] == 512
    assert vasp_data['offset'] == [0.5, 0.5, 0.5]
    assert vasp_data['name of system'] == "Cu4"
    assert vasp_data['scaling factor'] == 1.0
    assert (vasp_data['lattice vectors'] == np.transpose([[3.616407, 0.000000, 0.000000],
                                                          [0.000000, 3.616407, 0.000000],
                                                          [0.000000, 0.000000, 3.616407]])).all()

    assert vasp_data["number of electronic iterations"] == 26
    assert vasp_data["number of reduced k-points"] == 20
    assert np.allclose(vasp_data["k-point weights"],
                       [0.015625,
                        0.046875,
                        0.046875,
                        0.046875,
                        0.046875,
                        0.09375,
                        0.09375,
                        0.046875,
                        0.09375,
                        0.046875,
                        0.015625,
                        0.046875,
                        0.046875,
                        0.046875,
                        0.09375,
                        0.046875,
                        0.015625,
                        0.046875,
                        0.046875,
                        0.015625])
    assert np.isclose(np.sum(vasp_data["k-point weights"]), 1)
    assert np.allclose(vasp_data["reduced k-points"],
                       [[0.0625, 0.0625, 0.0625],
                        [0.1875, 0.0625, 0.0625],
                        [0.3125, 0.0625, 0.0625],
                        [0.4375, 0.0625, 0.0625],
                        [0.1875, 0.1875, 0.0625],
                        [0.3125, 0.1875, 0.0625],
                        [0.4375, 0.1875, 0.0625],
                        [0.3125, 0.3125, 0.0625],
                        [0.4375, 0.3125, 0.0625],
                        [0.4375, 0.4375, 0.0625],
                        [0.1875, 0.1875, 0.1875],
                        [0.3125, 0.1875, 0.1875],
                        [0.4375, 0.1875, 0.1875],
                        [0.3125, 0.3125, 0.1875],
                        [0.4375, 0.3125, 0.1875],
                        [0.4375, 0.4375, 0.1875],
                        [0.3125, 0.3125, 0.3125],
                        [0.4375, 0.3125, 0.3125],
                        [0.4375, 0.4375, 0.3125],
                        [0.4375, 0.4375, 0.4375]])
    assert np.sum(vasp_data["k-point degeneracy"]) == vasp_data["number of unreduced k-points"]
    assert vasp_data["NBANDS"] == 26
    assert vasp_data["alpha Z"] == 242.15273653
    assert vasp_data["Ewald energy"] == -4386.48630246
    assert vasp_data["-1/2 Hartree"] == -1372.67615408
    assert vasp_data["-exchange"] == 0.0
    assert vasp_data["-V(xc)+E(xc)"] == 178.50223159
    assert vasp_data["PAW double counting"] == 5237.15909487
    assert vasp_data["entropy T*S"] == 0.0
    assert vasp_data["eigenvalues"] == 190.83068261
    assert vasp_data["atomic energy"] == 5563.90821598
    assert vasp_data["free energy"] == -14.91203703
    assert vasp_data["energy without entropy"] == -14.91203703
    assert vasp_data["energy(sigma->0)"] == -14.91203703
    assert vasp_data["Fermi level"] == 7.3341
    assert vasp_data["total wrapped soft charge"] == [0,0,0]
    assert vasp_data["total wrapped charge"] == [0.0001]*3
    assert np.allclose(vasp_data["Final lattice vectors"],
                       [[ 3.64234384, -0.        , -0.        ],
                        [-0.        ,  3.64234384,  0.        ],
                        [ 0.        , -0.        ,  3.64234384]])
    assert np.allclose(vasp_data["Final reciprocal lattice vectors"], 
                       [[ 0.27454849,  0.        , -0.        ],
                        [ 0.        ,  0.27454849,  0.        ],
                        [ 0.        , -0.        ,  0.27454849]])

    assert vasp_data["Net forces acting on ions"] == [{'Electron-ion force': [6.5e-13, 1.42e-12, 1.35e-12]},
                                                      {'Ewald-force': [-2.75e-16, 6.81e-16, 2.43e-16]},
                                                      {'Non-local-force': [-8.62e-19, 8.67e-19, 0.0]},
                                                      {'Convergence-correction-force': [-2.64e-13,
                                                                                        -3.85e-13,
                                                                                        -2.96e-13]}]
    assert vasp_data["Electron-ion force"] == (
        np.linalg.norm(vasp_data["Net forces acting on ions"][0]["Electron-ion force"]))
    assert vasp_data["Ewald force"] == (
        np.linalg.norm(vasp_data["Net forces acting on ions"][1]["Ewald-force"]))
    assert vasp_data["Non-local force"] == (
        np.linalg.norm(vasp_data["Net forces acting on ions"][2]["Non-local-force"]))
    assert vasp_data["Convergence-correction force"] == (
        np.linalg.norm(vasp_data["Net forces acting on ions"][3]["Convergence-correction-force"]))
    assert vasp_data["Drift force"] == 0.0
    assert vasp_data["Elapsed time"] == 137.826
    assert vasp_data["number of plane waves"] == [1288,
                                                  1278,
                                                  1273,
                                                  1268,
                                                  1280,
                                                  1272,
                                                  1267,
                                                  1280,
                                                  1274,
                                                  1272,
                                                  1277,
                                                  1271,
                                                  1275,
                                                  1264,
                                                  1275,
                                                  1273,
                                                  1265,
                                                  1272,
                                                  1275,
                                                  1283]
    
    ops = [np.array([[1,   0,   0], # 1
                     [0,   1,   0],
                     [0,   0,   1]]),

           np.array([[-1,   0,   0], # 2
                     [0,  -1,   0],
                     [0,   0,  -1]]),

           np.array([[0,   0,   1], # 3
                     [1,   0,   0],
                     [0,   1,   0]]),

           np.array([[0,   0,  -1], # 4
                     [-1,   0,   0],
                     [0,  -1,   0]]),

           np.array([[0,   1,   0], # 5
                     [0,   0,   1],
                     [1,   0,   0]]),

           np.array([[0,  -1,   0], # 6
                     [0,   0,  -1],
                     [-1,   0,   0]]),
                        
           np.array([[0,  -1,   0], # 7
                     [1,   0,   0],
                     [0,   0,   1]]),

           np.array([[0,   1,   0], # 8
                     [-1,   0,   0],
                     [0,   0,  -1]]),

           np.array([[-1,   0,   0], # 9
                     [0,   0,   1],
                     [0,   1,   0]]),

           np.array([[1,   0,   0], # 10
                     [0,   0,  -1],
                     [0,  -1,   0]]),

           np.array([[0,   0,  -1], # 11
                     [0,   1,   0],
                     [1,   0,   0]]),

           np.array([[0,   0,   1], # 12
                     [0,  -1,   0],
                     [-1,   0,   0]]),

           np.array([[-1,   0,   0], # 13
                     [0,  -1,   0],
                     [0,   0,   1]]),

           np.array([[1,   0,   0], # 14
                     [0,   1,   0],
                     [0,   0,  -1]]),

           np.array([[0,   0,  -1], # 15
                     [-1,   0,   0],
                     [0,   1,   0]]),

           np.array([[0,   0,   1], # 16
                     [1,   0,   0],
                     [0,  -1,   0]]),

           np.array([[0,  -1,   0], # 17
                     [0,   0,  -1],
                     [1,   0,   0]]),

           np.array([[0,   1,   0], # 18
                     [0,   0,   1],
                     [-1,   0,   0]]),

           np.array([[0,   1,   0], # 19
                    [-1,   0,   0],
                    [0,   0,   1]]),

           np.array([[0,  -1,   0], # 20
                     [1,   0,   0],
                     [0,   0,  -1]]),

           np.array([[1,   0,   0], # 21
                     [0,   0,  -1],
                     [0,   1,   0]]),

           np.array([[-1,   0,   0], # 22
                     [0,   0,   1],
                     [0,  -1,   0]]),

           np.array([[0,   0,   1], # 23
                     [0,  -1,   0],
                     [1,   0,   0]]),

           np.array([[0,   0,  -1], # 24
                     [0,   1,   0],
                     [-1,   0,   0]]),

           np.array([[0,   0,   1], # 25
                     [-1,   0,   0],
                     [0,  -1,   0]]),

           np.array([[0,   0,  -1], # 26
                     [1,   0,   0],
                     [0,   1,   0]]),

           np.array([[0,   1,   0], # 27
                     [0,   0,  -1],
                     [-1,   0,   0]]),

           np.array([[0,  -1,   0], # 28
                     [0,   0,   1],
                     [1,   0,   0]]),

           np.array([[1,   0,   0], # 29
                     [0,  -1,   0],
                     [0,   0,  -1]]),

           np.array([[-1,   0,   0], # 30
                     [0,   1,   0],
                     [0,   0,   1]]),

           np.array([[0,   0,   1], # 31
                     [0,   1,   0],
                     [-1,   0,   0]]),

           np.array([[0,   0,  -1], # 32
                     [0,  -1,   0],
                     [1,   0,   0]]),

           np.array([[0,   1,   0], # 33
                     [1,   0,   0],
                     [0,   0,  -1]]),

           np.array([[0,  -1,   0], # 34
                     [-1,   0,   0],
                     [0,   0,   1]]),

           np.array([[1,   0,   0], # 35
                     [0,   0,   1],
                     [0,  -1,   0]]),

           np.array([[-1,   0,   0], # 36
                     [0,   0,  -1],
                     [0,   1,   0]]),

           np.array([[0,  -1,   0], # 37
                     [0,   0,   1],
                     [-1,   0,   0]]),

           np.array([[0,   1,   0], # 38
                     [0,   0,  -1],
                     [1,   0,   0]]),

           np.array([[-1,   0,   0], # 39
                     [0,   1,   0],
                     [0,   0,  -1]]),

           np.array([[1,   0,   0], # 40
                     [0,  -1,   0],
                     [0,   0,   1]]),

           np.array([[0,   0,  -1], # 41
                     [1,   0,   0],
                     [0,  -1,   0]]),

           np.array([[0,   0,   1], #42
                     [-1,   0,   0],
                     [0,   1,   0]]),

           np.array([[-1,   0,   0], # 43
                     [0,   0,  -1],
                     [0,  -1,   0]]),

           np.array([[1,   0,   0], # 44
                     [0,   0,   1],
                     [0,   1,   0]]),

           np.array([[0,  -1,   0], # 45
                     [-1,   0,   0],
                     [0,   0,  -1]]),

           np.array([[0,   1,   0], #46
                     [1,   0,   0],
                     [0,   0,   1]]),
                        
           np.array([[0,   0,  -1], # 47
                     [0,  -1,   0],
                     [-1,   0,   0]]),
                        
           np.array([[0,   0,   1], # 48
                     [0,   1,   0],
                     [1,   0,   0]])]

    assert check_contained(ops, vasp_data["symmetry operators"])    

    # for op in vasp_data["symmetry operators"]:
    #     assert check_contained(op, ops)
    
