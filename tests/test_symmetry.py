"""Unit tests for symmetry.py module
"""

import pytest
import numpy as np
from numpy.linalg import det
from copy import deepcopy
from numpy.linalg import norm, inv
from itertools import product
from itertools import combinations
from phenum.vector_utils import *
from phenum.vector_utils import (_minkowski_reduce_basis, _reduce_C_in_ABC,
                                 _gaussian_reduce_two_vectors)
from phenum.symmetry import get_lattice_pointGroup

from BZI.sampling import make_cell_points

from BZI.symmetry import *
from conftest import run

tests = run("all symmetry")

# @pytest.mark.skipif("test_make_ptvecs" not in tests, reason="different tests")            
# def test_make_ptvecs():
#     """Verify the primitive translation vectors are correct.
#     """
#     center_list = ["prim", "base", "body", "face"]# , "hex", "rhom"]
#     consts_list = [[1]*3, [1.2]*3, [np.pi]*3, [1, 1, 2],
#                    [1, 2, 3],[1.2, 1.5, 3], [np.pi, np.pi, 4],
#                    [100,110.3,210.3]]
#     angles_list = [[np.pi/2]*3, [1]*3,
#                    [np.pi/3, np.pi/3, np.pi/4],
#                    [2, 2, 1], [1, 2, 2.1],
#                    [np.pi/2, np.pi/3, np.pi/3],
#                    [np.pi/2, np.pi/2, np.pi/4]]

#     for center_type in center_list:
#         for lat_consts in consts_list:
#             for lat_angles in angles_list:
#                 vecs = make_ptvecs(center_type,
#                                    lat_consts,
#                                    lat_angles)
#                 a = float(lat_consts[0])
#                 b = float(lat_consts[1])
#                 c = float(lat_consts[2])
                
#                 alpha = float(lat_angles[0])
#                 beta = float(lat_angles[1])
#                 gamma = float(lat_angles[2])
                
#                 v0 = vecs[:,0]
#                 v1 = vecs[:,1]
#                 v2 = vecs[:,2]
                
#                 # Primitive centering type
#                 if center_type == "prim":
#                     # Verify the vectors have the correct lengths.
#                     assert np.isclose(norm(v0), a)
#                     assert np.isclose(norm(v1), b)
#                     assert np.isclose(norm(v2), c)                                        
                    
#                     # Verify the angles between the vectors are correct.
#                     assert np.isclose(np.dot(v0,v1), a*b*np.cos(gamma))
#                     assert np.isclose(np.dot(v1,v2), b*c*np.cos(alpha))
#                     assert np.isclose(np.dot(v2,v0), a*c*np.cos(beta))
#                 # Base centering type
#                 elif center_type == "base":
#                     # Verify the vectors have the correct lengths.
#                     assert np.isclose(norm(v0),
#                                       1./2*np.sqrt(a**2 + b**2 -
#                                                   2*a*b*np.cos(gamma)))
#                     assert np.isclose(norm(v1),
#                                       1./2*np.sqrt(a**2 + b**2 +
#                                                   2*a*b*np.cos(gamma)))
#                     assert np.isclose(norm(v2), c)

#                     # Verify the angles between the vectors are correct.
#                     assert np.isclose(np.dot(v0, v1), 1./4*(a**2 - b**2))
#                     assert np.isclose(np.dot(v1, v2), 1./2*a*c*np.cos(beta)
#                                       + 1./2*b*c*np.cos(alpha))
#                     assert np.isclose(np.dot(v0, v2), 1./2*a*c*np.cos(beta)
#                                       - 1./2*b*c*np.cos(alpha))

#                 # Body centering type
#                 elif center_type == "body":
#                     # Verify the vectors have the correct lengths.
#                     assert np.isclose(norm(v0), 1./2*np.sqrt(
#                         a**2 + b**2 + c**2
#                         - 2*a*b*np.cos(gamma)
#                         + 2*b*c*np.cos(alpha)
#                         - 2*a*c*np.cos(beta)))                    
#                     assert np.isclose(norm(v1), 1./2*np.sqrt(
#                         a**2 + b**2 + c**2
#                         - 2*a*b*np.cos(gamma)
#                         - 2*b*c*np.cos(alpha)
#                         + 2*a*c*np.cos(beta)))
#                     assert np.isclose(norm(v2), 1./2*np.sqrt(
#                         a**2 + b**2 + c**2
#                         + 2*a*b*np.cos(gamma)
#                         - 2*b*c*np.cos(alpha)
#                         - 2*a*c*np.cos(beta)))
                    
#                     # Verify the angles between the vectors are correct.
#                     assert np.isclose(gamma, (np.arccos((4*np.dot(v0,v1)
#                                               + a**2 + b**2 - c**2)/(2*a*b))))
#                     assert np.isclose(beta, (np.arccos((4*np.dot(v0,v2)
#                                               + a**2 - b**2 + c**2)/(2*a*c))))
#                     assert np.isclose(alpha, (np.arccos((4*np.dot(v1,v2)
#                                               - a**2 + b**2 + c**2)/(2*b*c))))
#                 # Face centering type
#                 elif center_type == "face":
#                     # Verify the vectors have the correct lengths.
#                     assert np.isclose(norm(v0), 1./2*np.sqrt(b**2 + c**2 +
#                                                         2*b*c*np.cos(alpha)))
#                     assert np.isclose(norm(v1), 1./2*np.sqrt(a**2 + c**2 +
#                                                         2*a*c*np.cos(beta)))
#                     assert np.isclose(norm(v2), 1./2*np.sqrt(a**2 + b**2 +
#                                                         2*a*b*np.cos(gamma)))

#                     # Verify the angles between the vectors are correct.
#                     common = (a*b*np.cos(gamma) + a*c*np.cos(beta) +
#                               b*c*np.cos(alpha))
#                     assert np.isclose(np.dot(v0,v1), 1./4*(common + c**2))
#                     assert np.isclose(np.dot(v0,v2), 1./4*(common + b**2))
#                     assert np.isclose(np.dot(v1,v2), 1./4*(common + a**2))

#                 # Primitive centering type
#                 if center_type == "hex":
#                     # Verify the vectors have the correct lengths.
#                     assert np.isclose(norm(v0), a)
#                     assert np.isclose(norm(v1), b)
#                     assert np.isclose(norm(v2), c)                                        
                    
#                     # Verify the angles between the vectors are correct.
#                     assert np.isclose(np.dot(v0,v1), a*b*np.cos(gamma))
#                     assert np.isclose(np.dot(v1,v2), b*c*np.cos(alpha))
#                     assert np.isclose(np.dot(v2,v0), a*c*np.cos(beta))                    
                    
#                 # Rhombohedral centering type
#                 elif center_type == "rhom":
#                     # Verify the vectors have the correct lengths.
#                     assert np.isclose(norm(v0), a)
#                     assert np.isclose(norm(v1), b)
#                     assert np.isclose(norm(v2), c)                                        
                    
#                     # Verify the angles between the vectors are correct.
#                     assert np.isclose(np.dot(v0,v1), a*b*np.cos(gamma))
#                     assert np.isclose(np.dot(v1,v2), b*c*np.cos(alpha))
#                     assert np.isclose(np.dot(v2,v0), a*c*np.cos(beta))


# @pytest.mark.skipif("test_make_lattice_vectors" not in tests, reason="different tests")
# def test_make_lattice_vectors():
#     """Check that make_lattice_vectors agrees with what is obtained with
#     make_ptvecs."""
    
#     lat_type = "simple cubic"
#     lat_consts = [1]*3
#     lat_angles = [np.pi/2]*3
#     lat_centering = "prim"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "body-centered cubic"
#     lat_consts = [1]*3
#     lat_angles = [np.pi/2]*3
#     lat_centering = "body"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "face-centered cubic"
#     lat_consts = [1]*3
#     lat_angles = [np.pi/2]*3
#     lat_centering = "face"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "tetragonal"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "prim"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "body-centered tetragonal"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "body"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "prim"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "face-centered orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "face"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "body-centered orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "body"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "base-centered orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "base"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "hexagonal"
#     lat_consts = [1., 1., 3.]
#     lat_angles = [np.pi/2, np.pi/2, 2*np.pi/3]
#     lat_centering = "prim"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "rhombohedral"
#     lat_consts = [1., 1., 1.]
#     lat_angles1 = [.3*np.pi]*3
#     lat_angles2 = [.3*np.pi]*3
#     lat_centering = "prim"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles1)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles2)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "monoclinic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/3, np.pi/2, np.pi/2]
#     lat_centering = "prim"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "base-centered monoclinic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/4, np.pi/2, np.pi/2]
#     lat_centering = "base"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     assert np.allclose(lat_vecs1, lat_vecs2)

#     lat_type = "triclinic"
#     lat_consts = [1.1, 2.8, 4.3]
#     lat_angles = [np.pi/6, np.pi/4, np.pi/3]
#     lat_centering = "prim"
#     lat_vecs1 = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     lat_vecs2 = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     assert np.allclose(lat_vecs1, lat_vecs2)    

#     # Verify that an error gets raised for poor input parameters.
    
#     # Simple cubic
#     lat_type = "simple cubic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "simple cubic"
#     lat_consts = [1, 1, 1]
#     lat_angles = [np.pi/2, np.pi/2, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "simple cubic"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi/3, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Body-centered cubic
#     lat_type = "body-centered cubic"
#     lat_consts = [1, 2, 1]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "body-centered cubic"
#     lat_consts = [1, 1, 1]
#     lat_angles = [np.pi/2, np.pi/3, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "body-centered cubic"
#     lat_consts = [2, 1, 1]
#     lat_angles = [np.pi/2, np.pi/3, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Face-centered cubic
#     lat_type = "face-centered cubic"
#     lat_consts = [3.3, 1, 1]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "face-centered cubic"
#     lat_consts = [np.pi, np.pi, np.pi]
#     lat_angles = [np.pi/2, np.pi/2, np.pi/5]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "face-centered cubic"
#     lat_consts = [np.pi, np.pi, np.pi]
#     lat_angles = [np.pi/2, np.pi/5, np.pi/5]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Tetragonal

#     lat_type = "tetragonal"
#     lat_consts = [1, 1, 1]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "tetragonal"
#     lat_consts = [1, 1, 3]
#     lat_angles = [np.pi/2, np.pi/2, np.pi/8]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "tetragonal"
#     lat_consts = [1, 1, 3]
#     lat_angles = [np.pi/8, np.pi/8, np.pi/8]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Body-centered tetragonal
#     lat_type = "body-centered tetragonal"
#     lat_consts = [np.pi/3, np.pi/3, np.pi/3]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "body-centered tetragonal"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi/2, np.pi/3, np.pi/4]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "body-centered tetragonal"
#     lat_consts = [1.1, 1.1, 2.2]
#     lat_angles = [np.pi/2, 1, 1]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Orthorhombic        
#     lat_type = "orthorhombic"
#     lat_consts = [2, 2, 3]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "orthorhombic"
#     lat_consts = [2.2, 2.2, 2.2]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2, np.pi/2, np.pi/10]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/10, np.pi/10, np.pi/10]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/3, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Face-centered orthorhombic
#     lat_type = "face-centered orthorhombic"
#     lat_consts = [1, 1, 3]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "face-centered orthorhombic"
#     lat_consts = [1, 1, 1]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "face-centered orthorhombic"
#     lat_consts = [1, 1, 1]
#     lat_angles = [np.pi/2, np.pi/2, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "face-centered orthorhombic"
#     lat_consts = [1, 1, 1]
#     lat_angles = [np.pi/2, np.pi/4, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "face-centered orthorhombic"
#     lat_consts = [1, 1, 1]
#     lat_angles = [np.pi/5, np.pi/4, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Body-centered orthorhombic    
#     lat_type = "body-centered orthorhombic"
#     lat_consts = [2.2, 2.2, 5.5]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "body-centered orthorhombic"
#     lat_consts = [2.2, 5.5, 5.5]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "body-centered orthorhombic"
#     lat_consts = [5.5, 5.5, 5.5]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
    
#     lat_type = "body-centered orthorhombic"
#     lat_consts = [1.1, 1.2, 1.3]
#     lat_angles = [np.pi/2, np.pi/2, np.pi/7]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "body-centered orthorhombic"
#     lat_consts = [1.1, 1.2, 1.3]
#     lat_angles = [np.pi/2, np.pi/7, np.pi/7]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "body-centered orthorhombic"
#     lat_consts = [1.1, 1.2, 1.3]
#     lat_angles = [np.pi/7, np.pi/7, np.pi/7]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Base-centered orthorhombic    
#     lat_type = "base-centered orthorhombic"
#     lat_consts = [1, 2, 2]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "base-centered orthorhombic"
#     lat_consts = [2, 2, 2]
#     lat_angles = [np.pi/2]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "base-centered orthorhombic"
#     lat_consts = [2, 2, 2]
#     lat_angles = [np.pi/2, np.pi/2, 1]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "base-centered orthorhombic"
#     lat_consts = [2, 2, 2]
#     lat_angles = [np.pi/2, 1, 1]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "base-centered orthorhombic"
#     lat_consts = [2, 2, 2]
#     lat_angles = [1, 1, 1]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     # Hexagonal        
#     lat_type = "hexagonal"
#     lat_consts = [1., 1., 3.]
#     lat_angles = [np.pi/2, np.pi/2, 2*np.pi/4]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "hexagonal"
#     lat_consts = [1., 1., 3.]
#     lat_angles = [np.pi/2, np.pi/3, 2*np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "hexagonal"
#     lat_consts = [1., 1., 3.]
#     lat_angles = [np.pi/3, np.pi/2, 2*np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "hexagonal"
#     lat_consts = [1., 1., 3.]
#     lat_angles = [np.pi/3, np.pi/3, 2*np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "hexagonal"
#     lat_consts = [1., 2., 3.]
#     lat_angles = [np.pi/2, np.pi/2, 2*np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "hexagonal"
#     lat_consts = [1., 3., 3.]
#     lat_angles = [np.pi/2, np.pi/2, 2*np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "hexagonal"
#     lat_consts = [3., 2., 3.]
#     lat_angles = [np.pi/2, np.pi/2, 2*np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "hexagonal"
#     lat_consts = [3.1, 3.1, 3.1]
#     lat_angles = [np.pi/2, np.pi/2, 2*np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     # Rhombohedral    
#     lat_type = "rhombohedral"
#     lat_consts = [1., 1., 2.]
#     lat_angles = [np.pi/3]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "rhombohedral"
#     lat_consts = [1., 1.1, 1.]
#     lat_angles = [np.pi/3]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "rhombohedral"
#     lat_consts = [np.pi/3, 1., 1.]
#     lat_angles = [np.pi/3]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "rhombohedral"
#     lat_consts = [np.pi/3, np.pi/3, 1.]
#     lat_angles = [np.pi/3]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "rhombohedral"
#     lat_consts = [np.pi/3, np.pi/2, np.pi/3]
#     lat_angles = [np.pi/3]*3
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "rhombohedral"
#     lat_consts = [np.pi/3, np.pi/3, np.pi/3]
#     lat_angles = [1, 1, 2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "rhombohedral"
#     lat_consts = [np.pi/3, np.pi/3, np.pi/3]
#     lat_angles = [1, 2, 2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "rhombohedral"
#     lat_consts = [np.pi/3, np.pi/3, np.pi/3]
#     lat_angles = [2, 1, 2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Monoclinic
#     lat_type = "monoclinic"
#     lat_consts = [1, 3, 2]
#     lat_angles = [np.pi/3, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "monoclinic"
#     lat_consts = [3, 1, 2]
#     lat_angles = [np.pi/3, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "monoclinic"
#     lat_consts = [1, 2.00001, 2]
#     lat_angles = [np.pi/3, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "monoclinic"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi/3, np.pi/2, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "monoclinic"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi/3, np.pi/3, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "monoclinic"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi, np.pi/3, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "monoclinic"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi, np.pi, np.pi]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "monoclinic"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     # Base-centered monoclinic        
#     lat_type = "base-centered monoclinic"
#     lat_consts = [1, 3.1, 3]
#     lat_angles = [np.pi/4, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "base-centered monoclinic"
#     lat_consts = [3+1e-6, 3, 3]
#     lat_angles = [np.pi/4, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "base-centered monoclinic"
#     lat_consts = [3+1e-6, 3+1e-6, 3]
#     lat_angles = [np.pi/4, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "base-centered monoclinic"
#     lat_consts = [1, 1, 3]
#     lat_angles = [np.pi, np.pi/2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
    
#     lat_type = "base-centered monoclinic"
#     lat_consts = [3, 3, 3]
#     lat_angles = [np.pi, np.pi, np.pi]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "base-centered monoclinic"
#     lat_consts = [3, 2, 3]
#     lat_angles = [np.pi/3, np.pi, np.pi]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "base-centered monoclinic"
#     lat_consts = [2, 2, 3]
#     lat_angles = [np.pi/3, np.pi/2+1e-2, np.pi/2]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     # Triclinic    
#     lat_type = "triclinic"
#     lat_consts = [1, 2, 2+1e-14]
#     lat_angles = [np.pi/6, np.pi/4, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "triclinic"
#     lat_consts = [1, 2, 2]
#     lat_angles = [np.pi/6, np.pi/4, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "triclinic"
#     lat_consts = [2, 2, 2]
#     lat_angles = [np.pi/6, np.pi/4, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "triclinic"
#     lat_consts = [8, 2, 2]
#     lat_angles = [np.pi/6, np.pi/4, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "triclinic"
#     lat_consts = [8, 2, 2]
#     lat_angles = [np.pi/4, np.pi/4, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
        
#     lat_type = "triclinic"
#     lat_consts = [8, 2, 2]
#     lat_angles = [np.pi/3, np.pi/4, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
    
#     lat_type = "triclinic"
#     lat_consts = [8, 2, 2]
#     lat_angles = [np.pi/3, np.pi/3, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)

#     lat_type = "triclinic"
#     lat_consts = [8.1, 8.1, 8.1]
#     lat_angles = [np.pi/3, np.pi/3, np.pi/3]
#     with pytest.raises(ValueError) as error:
#         lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
                              
# @pytest.mark.skipif("test_sympts_sympaths" not in tests, reason="different tests")     
# def test_sympts_sympaths():
#     """Verify the symmetry points for the various Brillouin zones are at the
#     correct positions. and that the symmetry paths are correct.
#     """
#     z = 0.
#     a = 1./2
#     b = 1./4
#     c = 1./8
    
#     # Simple cubic
#     sympts1 = {"$\Gamma$": [z, z, z],
#               "M": [a, a, z],
#               "R": [a, a, a],
#               "X": [z, a, z]}    
    
#     lattice_centering = "prim"
#     lattice_constants = [1,1,1]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "X"], ["X", "M"], ["M", "$\Gamma$"], ["$\Gamma$", "R"], ["R", "X"],
#                 ["M", "R"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)        
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2

#     # Face-centered cubic
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "K": [3./8, 3./8, 3./4],
#                "L": [a, a, a],
#                "U": [5./8, b, 5./8],
#                "W": [a, b, 3./4],
#                "X": [a, z, a]}
#     lattice_centering = "face"
#     lattice_constants = [1.3,1.3,1.3]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "X"], ["X", "W"], ["W", "K"], ["K", "$\Gamma$"], ["$\Gamma$", "L"],
#                 ["L", "U"], ["U", "W"], ["W", "L"], ["L", "K"], ["U", "X"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)        
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2
    
#     # Body-centered cubic
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "H": [a, -a, a],
#                "P": [b, b, b],
#                "N": [z, z, a]}
    
#     lattice_centering = "body"
#     lattice_constants = [1.3,1.3,1.3]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "H"], ["H", "N"], ["N", "$\Gamma$"], ["$\Gamma$", "P"], ["P", "H"],
#                 ["P", "N"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)        
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2
    
#     # Tetragonal
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "A": [a, a, a],
#                "M": [a, a, z],
#                "R": [z, a, a],
#                "X": [z, a, z],
#                "Z": [z, z, a]}
                  
#     lattice_centering = "prim"
#     lattice_constants = [1.3, 1.3, 4.9]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "X"], ["X", "M"], ["M", "$\Gamma$"], ["$\Gamma$", "Z"], ["Z", "R"],
#                 ["R", "A"], ["A", "Z"], ["X", "R"], ["M", "A"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)        
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2
        
#     # Body-centered tetragonal 1 (c < a)
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "M": [-a, a, a],
#                "N": [z, a, z],
#                "P": [b, b, b],
#                "X": [z, z, a],
#                "Z": [5./16, 5./16, -5./16],
#                "Z1": [-5./16, 11./16., 5./16]}
                  
#     lattice_centering = "body"
#     lattice_constants = [2., 2., 1.]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "X"], ["X", "M"], ["M", "$\Gamma$"], ["$\Gamma$", "Z"], ["Z", "P"],
#                 ["P", "N"], ["N", "Z1"], ["Z1", "M"], ["X", "P"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)        
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2        
        
#     # Body-centered tetragonal 2 (a < c)
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "N": [z, a, z],
#                "P": [b, b, b],
#                "S": [-5./16, 5./16, 5./16],
#                "S1": [5./16, 11./16, -5./16],
#                "X": [z, z, a],
#                "Y": [-1./8, 1./8, a],
#                "Y1": [a, a, -1./8],
#                "Z": [a, a, -a]}
    
#     lattice_centering = "body"
#     lattice_constants = [1., 1., 2.]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "X"], ["X", "Y"], ["Y", "S"], ["S", "$\Gamma$"], ["$\Gamma$", "Z"],
#                 ["Z", "S1"], ["S1", "N"], ["N", "P"], ["P", "Y1"],
#                 ["Y1", "Z"], ["X", "P"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2

#     # Orthorhombic
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "R": [a, a, a],
#                "S": [a, a, z],
#                "T": [z, a, a],
#                "U": [a, z, a],
#                "X": [a, z, z],
#                "Y": [z, a, z],
#                "Z": [z, z, a]}
    
#     lattice_centering = "prim"
#     lattice_constants = [1., 2., 3.]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "X"], ["X", "S"], ["S", "Y"], ["Y", "$\Gamma$"], ["$\Gamma$", "Z"],
#                 ["Z", "U"], ["U", "R"], ["R", "T"], ["T", "Z"], ["Y", "T"],
#                 ["U", "X"], ["S", "R"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2        

#     # Face-centered orthorhombic 1
#     zeta = 19./64
#     eta = 21./64
#     sympts1 = {"$\Gamma$": [z, z, z,],
#                "A": [a, a+zeta, zeta],
#                "A1": [a, a-zeta, 1-zeta],
#                "L": [a, a, a],
#                "T": [1., a, a],
#                "X": [z, eta, eta],
#                "X1": [1., 1.-eta, 1.-eta],
#                "Y": [a, 0, a],
#                "Z": [a, a, 0]}

#     lattice_centering = "face"
#     lattice_constants = [1./2, 1., 2.]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "Y"], ["Y", "T"], ["T", "Z"], ["Z", "$\Gamma$"], ["$\Gamma$", "X"],
#                 ["X", "A1"], ["A1", "Y"], ["T", "X1"], ["X", "A"], ["A", "Z"],
#                 ["L", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                

#     # Face-centered orthorhombic 3
#     zeta = 2./5
#     eta = 1./2
#     sympts1 = {"$\Gamma$": [z, z, z,],
#                "A": [a, a+zeta, zeta],
#                "A1": [a, a-zeta, 1-zeta],
#                "L": [a, a, a],
#                "T": [1., a, a],
#                "X": [z, eta, eta],
#                "X1": [1., 1.-eta, 1.-eta],
#                "Y": [a, 0, a],
#                "Z": [a, a, 0]}

#     lattice_centering = "face"
#     lattice_constants = [2./np.sqrt(5), 1., 2.]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "Y"], ["Y", "T"], ["T", "Z"], ["Z", "$\Gamma$"], ["$\Gamma$", "X"],
#                 ["X", "A1"], ["A1", "Y"], ["X", "A"], ["A", "Z"], ["L", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                        

#     # Face-centered orthorhombic 2
#     eta = -19./36
#     phi = 91./256
#     delta = -19./144
#     sympts1 = {"$\Gamma$": [z, z, z,],
#                "C": [a, a-eta, 1-eta],
#                "C1": [a, a+eta, eta],
#                "D": [a-delta, a, 1-delta],
#                "D1": [a+delta, a, delta],
#                "L": [a, a, a],
#                "H": [1-phi, a-phi, a],
#                "H1": [phi, a+phi, a],
#                "X": [z, a, a],
#                "Y": [a, z, a],
#                "Z": [a, a, z]}

#     lattice_centering = "face"
#     # With a = 1/2, eta was greater than 1.
#     # It might be possible to avoid this by adding %1 to the symmetry point
#     # components but I haven't checked this.
#     lattice_constants = [2., 1., 3./4]
#     lattice_angles = [np.pi/2, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "Y"], ["Y", "C"], ["C", "D"], ["D", "X"], ["X", "$\Gamma$"],
#                 ["$\Gamma$", "Z"], ["Z", "D1"], ["D1", "H"], ["H", "C"], ["C1", "Z"],
#                 ["X", "H1"], ["H", "Y"], ["L", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                        
        
#     # Body-centered orthorhombic
#     zeta = 5./18
#     eta = 13./36
#     delta = 1./12
#     mu = 5./36

#     sympts1 = {"$\Gamma$": [z, z, z],
#                "L": [-mu, mu, a-delta],
#                "L1": [mu, -mu, a+delta],
#                "L2": [a-delta, a+delta, -mu],
#                "R": [z, a, z],
#                "S": [a, z, z],
#                "T": [z, z, a],
#                "W": [b, b, b],
#                "X": [-zeta, zeta, zeta],
#                "X1": [zeta, 1-zeta, -zeta],
#                "Y": [eta, -eta, eta],
#                "Y1": [1-eta, eta, -eta],
#                "Z": [a, a, -a]}
    
#     lattice_centering = "body"
#     lattice_constants = [1,2,3]
#     lattice_angles = [np.pi/2]*3
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "X"], ["X", "L"], ["L", "T"], ["T", "W"], ["W", "R"],
#                 ["R", "X1"], ["X1", "Z"], ["Z", "$\Gamma$"], ["$\Gamma$", "Y"], ["Y", "S"],
#                 ["S", "W"], ["L1", "Y"], ["Y1", "Z"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                                

#     # Base-centered orthorhombic
#     zeta = 5./16
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "A": [zeta, zeta, a],
#                "A1": [-zeta, 1-zeta, a],
#                "R": [z, a, a],
#                "S": [z, a, z],
#                "T": [-a, a, a],
#                "X": [zeta, zeta, z],
#                "X1": [-zeta, 1-zeta, z],
#                "Y": [-a, a, z],
#                "Z": [z, z, a]}
    
#     lattice_centering = "base"
#     lattice_constants = [1,2,3]
#     lattice_angles = [np.pi/2]*3
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])
        
#     sympath1 = [["$\Gamma$", "X"], ["X", "S"], ["S", "R"], ["R", "A"], ["A", "Z"],
#                 ["Z", "$\Gamma$"], ["$\Gamma$", "Y"], ["Y", "X1"], ["X1", "A1"], ["A1", "T"],
#                 ["T", "Y"], ["Z", "T"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                                        
        
#     # Hexagonal
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "A": [z, z, a],
#                "H": [1./3, 1./3, a],
#                "K": [1./3, 1./3, z],
#                "L": [a, z, a],
#                "M": [a, z, z]}
    
#     lattice_centering = "prim"
#     lattice_constants = [1,1,3]
#     lattice_angles = [np.pi/2, np.pi/2, 2*np.pi/3]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)    
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])
        
#     sympath1 = [["$\Gamma$", "M"], ["M", "K"], ["K", "$\Gamma$"], ["$\Gamma$", "A"], ["A", "L"],
#                 ["L", "H"], ["H", "A"], ["L", "M"], ["K", "H"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                                        
    
#     # Rhombohedral 1
#     eta = 3./4
#     nu = 3./8
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "B": [eta, a, 1-eta],
#                "B1": [a, 1-eta, eta-1],
#                "F": [a, a, z],
#                "L": [a, z, z],
#                "L1": [z, z, -a],
#                "P": [eta, nu, nu],
#                "P1": [1-nu, 1-nu, 1-eta],
#                "P2": [nu, nu, eta-1],
#                "Q": [1-nu, nu, z],
#                "X": [nu, z, -nu],
#                "Z": [a, a, a]}
    
#     lattice_centering = "prim"
#     lattice_constants = [1.]*3
#     lattice_angles = [np.pi/3]*3
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "L"], ["L", "B1"], ["B", "Z"], ["Z", "$\Gamma$"], ["$\Gamma$", "X"],
#                 ["Q", "F"], ["F", "P1"], ["P1", "Z"], ["L", "P"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                                        
        
#     # Rhombohedral 2
#     eta = 0.263932022500210
#     nu = 0.618033988749895
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "F": [a, -a, z],
#                "L": [a, z, z],
#                "P": [1-nu, -nu, 1-nu],
#                "P1": [nu, nu-1, nu-1],
#                "Q": [eta, eta, eta],
#                "Q1": [1-eta, -eta, -eta],
#                "Z": [a, -a, a]}
    
#     lattice_centering = "prim"
#     lattice_constants = [1.]*3
#     lattice_angles = [6*np.pi/10]*3
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "P"], ["P", "Z"], ["Z", "Q"], ["Q", "$\Gamma$"], ["$\Gamma$", "F"], 
#                 ["F", "P1"], ["P1", "Q1"], ["Q1", "L"], ["L", "Z"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                                        
                
#     # Verify that an error gets raised for all of the angles equal to 2pi/3 radians.
#     lattice_centering = "prim"
#     lattice_constants = [1.]*3
#     lattice_angles = [2*np.pi/3]*3
#     with pytest.raises(ValueError):
#         get_sympts(lattice_centering, lattice_constants, lattice_angles)

#     # Monoclinic
#     eta = 4./9
#     nu = 1./6
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "A": [a, a, z],
#                "C": [z, a, a],
#                "D": [a, z, a],
#                "D1": [a, z, -a],
#                "E": [a, a, a],
#                "H": [z, eta, 1-nu],
#                "H1": [z, 1-eta, nu],
#                "H2": [z, eta, -nu],
#                "M": [a, eta, 1-nu],
#                "M1": [a, 1-eta, nu],
#                "M2": [a, eta, -nu],
#                "X": [z, a, z],
#                "Y": [z, z, a],
#                "Y1": [z, z, -a],
#                "Z": [a, z, z]}

#     lattice_centering = "prim"
#     lattice_constants = [1, 2, 3]
#     lattice_angles = [np.pi/3, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)        
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "Y"], ["Y", "H"], ["H", "C"], ["C", "E"], ["E", "M1"],
#                 ["M1", "A"], ["A", "X"], ["X", "H1"], ["M", "D"], ["D", "Z"],
#                 ["Y", "D"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                                        
        
#     # Base-centered Monoclinic 1 (kgamma > pi/2)
#     zeta = 5./9
#     eta = 4./3
#     psi = 2./3
#     phi = 25./36

#     sympts1 = {"$\Gamma$": [z, z, z],
#                "N": [a, z, z],
#                "N1": [0, -a, z],
#                "F": [1-zeta, 1-zeta, 1-eta],
#                "F1": [zeta, zeta, eta],
#                "F2": [-zeta, -zeta, 1-eta],
#                "F3": [1-zeta, -zeta, 1-eta],
#                "I": [phi, 1-phi, a],
#                "I1": [1-phi, phi-1, a],
#                "L": [a, a, a],
#                "M": [a, z, a],
#                "X": [1-psi, psi-1, z],
#                "X1": [psi, 1-psi, z],
#                "X2": [psi-1, -psi, z],
#                "Y": [a, a, z],
#                "Y1": [-a, -a, z],
#                "Z": [z, z, a]}

#     lattice_centering = "base"
#     lattice_constants = [1, 2, 3]
#     lattice_angles = [np.pi/3, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "Y"], ["Y", "F"], ["F", "L"], ["L", "I"], ["I1", "Z"],
#                 ["Z", "F1"], ["Y", "X1"], ["X", "$\Gamma$"], ["$\Gamma$", "N"], ["M", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                                                

#     # Base-centered Monoclinic 2 (kgamma = pi/2)
#     zeta = 2. - 1/np.sqrt(3)
#     eta = 1./2 +3./2*np.sqrt(3)*(2. - 1./np.sqrt(3))
#     psi = 1./2
#     phi = 1./2 + 1./(4*np.sqrt(3))

#     sympts1 = {"$\Gamma$": [z, z, z],
#                "N": [a, z, z],
#                "N1": [0, -a, z],
#                "F": [1-zeta, 1-zeta, 1-eta],
#                "F1": [zeta, zeta, eta],
#                "F2": [-zeta, -zeta, 1-eta],
#                "F3": [1-zeta, -zeta, 1-eta],
#                "I": [phi, 1-phi, a],
#                "I1": [1-phi, phi-1, a],
#                "L": [a, a, a],
#                "M": [a, z, a],
#                "X": [1-psi, psi-1, z],
#                "X1": [psi, 1-psi, z],
#                "X2": [psi-1, -psi, z],
#                "Y": [a, a, z],
#                "Y1": [-a, -a, z],
#                "Z": [z, z, a]}

#     lattice_centering = "base"
#     lattice_constants = [1, 2, 3]
#     lattice_angles = [np.pi/6, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "Y"], ["Y", "F"], ["F", "L"], ["L", "I"], ["I1", "Z"],
#                 ["Z", "F1"], ["N", "$\Gamma$"], ["$\Gamma$", "M"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2
        
#     # Base-centered Monoclinic 3 (kgamma < pi/2, other condition < 1)
#     mu = 5./4
#     delta = 3.80422606518061
#     zeta = 2.37308484630850
#     eta = 9.52775122721195
#     phi = 0.87308484630850
#     psi = 1.9192990968507
    
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "F": [1-phi, 1-phi, 1-psi],
#                "F1": [phi, phi-1, psi],
#                "F2": [1-phi, -phi, 1-psi],
#                "H": [zeta, zeta, eta],
#                "H1": [1-zeta, -zeta, 1-eta],
#                "H2": [-zeta, -zeta, 1-eta],
#                "I": [a, -a, a],
#                "M": [a, z, a],
#                "N": [a, z, z],
#                "N1": [z, -a, z],
#                "X": [a, -a, z],
#                "Y": [mu, mu, delta],
#                "Y1": [1-mu, -mu, -delta],
#                "Y2": [-mu, -mu, -delta],
#                "Y3": [mu, mu-1, delta],
#                "Z": [z, z, a]}


#     lattice_centering = "base"
#     lattice_constants = [2,4,8]
#     lattice_angles = [np.pi/10, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)    
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "Y"], ["Y", "F"], ["F", "H"], ["H", "Z"], ["Z", "I"],
#                 ["I", "F1"], ["H1", "Y1"], ["Y1", "X"], ["X", "$\Gamma$"], ["$\Gamma$", "N"],
#                 ["M", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2
        
#     # Base-centered Monoclinic 4 (kgamma < pi/2, other condition = 1)
#     mu = 5./4
#     delta = 2.92705
#     zeta = 2.
#     eta = 6.3541
#     phi = 1./2
#     psi = 1./2
    
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "F": [1-phi, 1-phi, 1-psi],
#                "F1": [phi, phi-1, psi],
#                "F2": [1-phi, -phi, 1-psi],
#                "H": [zeta, zeta, eta],
#                "H1": [1-zeta, -zeta, 1-eta],
#                "H2": [-zeta, -zeta, 1-eta],
#                "I": [a, -a, a],
#                "M": [a, z, a],
#                "N": [a, z, z],
#                "N1": [z, -a, z],
#                "X": [a, -a, z],
#                "Y": [mu, mu, delta],
#                "Y1": [1-mu, -mu, -delta],
#                "Y2": [-mu, -mu, -delta],
#                "Y3": [mu, mu-1, delta],
#                "Z": [z, z, a]}

#     lattice_centering = "base"
#     lattice_constants = [2,4,6.15536707431]
#     lattice_angles = [np.pi/10, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "Y"], ["Y", "F"], ["F", "H"], ["H", "Z"], ["Z", "I"],
#                 ["H1", "Y1"], ["Y1", "X"], ["X", "$\Gamma$"], ["$\Gamma$", "N"], ["M", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2

#     # Base-centered Monoclinic 5 (kgamma < pi/2, other condition > 1)
#     zeta = 1.65567
#     eta = 5.08891
#     mu = 0.772815
#     rho = 0.586083
#     nu = -0.110035
#     omega = -1.64464
#     delta = 1.22214

#     sympts1 = {"$\Gamma$": [z, z, z],
#                "F": [nu, nu, omega],
#                "F1": [1-nu, 1-nu, 1-omega],
#                "F2": [nu, nu-1, omega],
#                "H": [zeta, zeta, eta],
#                "H1": [1-zeta, -zeta, 1-eta],
#                "H2": [-zeta, -zeta, 1-eta],
#                "I": [rho, 1-rho, a],
#                "I1": [1-rho, rho-1, a],
#                "L": [a, a, a],
#                "M": [a, z, a],
#                "N": [a, z, z],
#                "N1": [z, -a, z],
#                "X": [a, -a, z],
#                "Y": [mu, mu, delta],
#                "Y1": [1-mu, -mu, -delta],
#                "Y2": [-mu, -mu, -delta],
#                "Y2": [-mu, -mu, -delta],
#                "Y3": [mu, mu-1, delta],
#                "Z": [z, z, a]}

#     lattice_centering = "base"
#     lattice_constants = [1, 2, 3]
#     lattice_angles = [np.pi/8, np.pi/2, np.pi/2]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)    

#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["$\Gamma$", "Y"], ["Y", "F"], ["F", "L"], ["L", "I"], ["I1", "Z"],
#                 ["Z", "H"], ["H", "F1"], ["H1", "Y1"], ["Y1", "X"], ["X", "$\Gamma$"],
#                 ["$\Gamma$", "N"], ["M", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)

#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2
        
#     # Triclinic 1a (kalpha, kbeta, kgamma > pi/2)
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "L": [a, a, z],
#                "M": [z, a, a],
#                "N": [a, z, a],
#                "R": [a, a, a],
#                "X": [a, z, z],
#                "Y": [z, a, z],
#                "Z": [z, z, a]}

#     lattice_centering = "prim"
#     lattice_constants = [1, 2, 3]
#     lattice_angles = [np.pi/7, np.pi/6, np.pi/5]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)    
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["X", "$\Gamma$"], ["$\Gamma$", "Y"], ["L", "$\Gamma$"], ["$\Gamma$", "Z"], ["N", "$\Gamma$"],
#                 ["$\Gamma$", "M"], ["R", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2        

#     # Triclinic 2a (kgamma = pi/2)
#     # I just make one of the angles pi/2.
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "L": [a, a, z],
#                "M": [z, a, a],
#                "N": [a, z, a],
#                "R": [a, a, a],
#                "X": [a, z, z],
#                "Y": [z, a, z],
#                "Z": [z, z, a]}
    
#     lattice_centering = "prim"
#     lattice_constants = [1, 2, 3]
#     lattice_angles = [np.pi/5.104299312111, np.pi/6,np.pi/4]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["X", "$\Gamma$"], ["$\Gamma$", "Y"], ["L", "$\Gamma$"], ["$\Gamma$", "Z"], ["N", "$\Gamma$"],
#                 ["$\Gamma$", "M"], ["R", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                

#     # Triclinic 1b (kalpha, kbeta, kgamma, < pi/2)
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "L": [a, -a, z],
#                "M": [z, z, a],
#                "N": [-a, -a, a],
#                "R": [z, -a, a],
#                "X": [z, -a, z],
#                "Y": [a, z, z],
#                "Z": [-a, z, a]}

#     lattice_centering = "prim"
#     lattice_constants = [1, 2, 3]
#     lattice_angles = [2*np.pi/3, 7*np.pi/6, 8*np.pi/5]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)
#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["X", "$\Gamma$"], ["$\Gamma$", "Y"], ["L", "$\Gamma$"], ["$\Gamma$", "Z"], ["N", "$\Gamma$"],
#                 ["$\Gamma$", "M"], ["R", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)
#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2                        

#     # Triclinic 2b (kgamma = pi/2)
#     sympts1 = {"$\Gamma$": [z, z, z],
#                "L": [a, -a, z],
#                "M": [z, z, a],
#                "N": [-a, -a, a],
#                "R": [z, -a, a],
#                "X": [z, -a, z],
#                "Y": [a, z, z],
#                "Z": [-a, z, a]}

#     lattice_centering = "prim"
#     lattice_constants = [1, 2, 3]
#     lattice_angles = [2*np.pi/3, 7*np.pi/6, 8*np.pi/4.87047732859]
#     sympts2 = get_sympts(lattice_centering, lattice_constants, lattice_angles)    

#     for k in sympts1.keys():
#         assert np.allclose(sympts1[k], sympts2[k])

#     sympath1 = [["X", "$\Gamma$"], ["$\Gamma$", "Y"], ["L", "$\Gamma$"], ["$\Gamma$", "Z"], ["N", "$\Gamma$"],
#                 ["$\Gamma$", "M"], ["R", "$\Gamma$"]]
#     sympath2 = get_sympaths(lattice_centering, lattice_constants,
#                             lattice_angles)

#     for p1, p2 in zip(sympath1, sympath2):
#         assert p1 == p2


# @pytest.mark.skipif("test_get_orbits" not in tests, reason="different tests")     
# def test_get_orbits():

#     lat_angles = [np.pi/2]*3
#     lat_consts = [2]*3
#     lat_centering = "body"

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]    

#     lat_vecs = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)

#     grid = [[0,.5,.5], [.5,.5,0], [.5,0,.5], 
#             [0,-.5,.5], [-.5,.5,0], [-.5,0,.5],
#             [0,.5,-.5], [.5,-.5,0], [.5,0,-.5], 
#             [0,-.5,-.5], [-.5,-.5,0], [-.5, 0,-.5]]

#     orbits, weight = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions,
#                           duplicates=True)
    
#     # There should only be one orbit.
#     assert len(orbits) == 1

#     # The origin, which wasn't part of the grid to begin with, should now be part of the
#     # orbit.
#     assert check_contained([0,0,0], orbits[0])

#     # There should only be one point in the orbit
#     assert len(orbits[0]) == 1


#     lat_angles = [np.pi/2]*3
#     lat_consts = [2]*3
#     lat_centering = "face"

#     lat_vecs = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)

#     grid = [[-.5,.5,.5], [.5,-.5,.5], [-.5,-.5,.5], 
#             [.5,.5,-.5], [-.5,.5,-.5], [.5,-.5,-.5],
#             [-.5,-.5,-.5], [0,0,0]]

#     orbits, weight = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions,
#                           duplicates=True)

#     # There should only be one orbit.
#     assert len(orbits) == 1

#     # There should be one k-points in this orbit.
#     assert len(orbits[0]) == 1

#     # The origin should still be in the orbit.
#     assert check_contained([0,0,0], orbits[0])


#     lat_angles = [np.pi/2]*3
#     lat_consts = [1]*3
#     lat_centering = "prim"
#     lat_vecs = make_ptvecs(lat_centering, lat_consts, lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)
    
#     grid = [[-1,1,1], [1,-1,1], [-1,-1,1], [1,1,-1], [-1,1,-1], [1,-1,-1],
#             [-1,-1,-1], [0,0,0], [0,1,1], [1,0,1], [0,0,1], [1,1,0], [0,1,0],
#             [1,0,0], [0,-1,0]]

#     orbits, weight = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions,
#                           duplicates=True)

#     # There should be one orbit.
#     assert len(orbits) == 1

#     # The origin should be in the orbit.
#     assert check_contained([0,0,0], orbits[0])

#     # There should be one unique points in the orbit.
#     assert len(orbits[0]) == 1


# @pytest.mark.skipif("test_reduce_simple_cubic" not in tests, reason="different tests")     
# def test_reduce_simple_cubic():

#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.

#     ### Simple Cubic ###
#     lat_consts = [2.8272]*3
#     lat_angles = [np.pi/2]*3
#     centering = 'prim'

#     lat_vecs = make_ptvecs(centering, lat_consts, lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)

#     H = np.array([[40,0,0],
#                   [0,40,0],
#                   [0,0,40]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2, 1./2, 1./2])

#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid, rlat_vecs, grid_vecs,
#                                           offset)
#     assert len(weights) == 1540
#     assert len(red_grid) == 1540
#     assert np.sum(weights) == 40**3

#     H = np.array([[41,0,0],
#                   [0,41,0],
#                   [0,0,41]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)

#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid, rlat_vecs, grid_vecs,
#                                           offset)
#     assert len(weights) == 1771
#     assert len(red_grid) == 1771
#     assert np.sum(weights) == 41**3

#     H = np.array([[42,0,0],
#                   [0,42,0],
#                   [0,0,42]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)

#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 2024
#     assert len(red_grid) == 2024
#     assert np.sum(weights) == 42**3

#     H = np.array([[40,0,0],
#                   [0,40,0],
#                   [0,0,20]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2, 1./2, 1./2])

#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 2100
#     assert len(red_grid) == 2100
#     assert np.sum(weights) == 40*40*20


#     H = np.array([[41,0,0],
#                   [0,21,0],
#                   [0,0,41]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.0]*3)

#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 2541
#     assert len(red_grid) == 2541
#     assert np.sum(weights) == 41*41*21

#     H = np.array([[22,0,0],
#                   [0,42,0],
#                   [0,0,42]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.0]*3)

#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3014
#     assert len(red_grid) == 3014
#     assert np.sum(weights) == 42*42*22
    
#     H = np.array([[3,0,0],
#                   [0,3,0],
#                   [0,0,3]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.0]*3)    

#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)

    
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)
    
#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
#     assert irrkpts == []

# @pytest.mark.skipif("test_reduce_body_centered_cubic" not in tests,
#                     reason="different tests")     
# def test_reduce_body_centered_cubic():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.

#     ### Body-centered cubic ###
#     lat_consts = [2*1.580307]*3
#     lat_angles = [np.pi/2]*3
#     centering = 'body'
#     lat_vecs = make_ptvecs(centering, lat_consts,
#                            lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)

#     H = np.array([[40,0,0],
#                   [0,40,0],
#                   [0,0,40]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 1650
#     assert len(red_grid) == 1650
#     assert np.sum(weights) == 40**3

#     H = np.array([[41,0,0],
#                   [0,41,0],
#                   [0,0,41]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 1771
#     assert len(red_grid) == 1771
#     assert np.sum(weights) == 41**3

#     H = np.array([[42,0,0],
#                   [0,42,0],
#                   [0,0,42]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 1903
#     assert len(red_grid) == 1903
#     assert np.sum(weights) == 42**3

#     H = np.array([[20,0,0],
#                   [0,40,0],
#                   [0,0,40]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 1411
#     assert len(red_grid) == 1411
#     assert np.sum(weights) == 20*40*40

#     H = np.array([[41,0,0],
#                   [0,21,0],
#                   [0,0,41]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 8771
#     assert len(red_grid) == 8771
#     assert np.sum(weights) == 41*21*41

#     H = np.array([[18,0,0],
#                   [0,38,0],
#                   [0,0,38]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 6108
#     assert len(red_grid) == 6108
#     assert np.sum(weights) == 18*38*38

#     H = np.array([[3,0,0],
#                   [0,3,0],
#                   [0,0,3]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
#     assert irrkpts == []
    

# @pytest.mark.skipif("test_reduce_face_centered_cubic" not in tests,
#                     reason="different tests")     
# def test_reduce_face_centered_cubic():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.
    
#     ### Face-centered cubic ###
#     lat_consts = [3.248231]*3
#     lat_angles = [np.pi/2]*3
#     centering = 'face'
#     lat_vecs = make_ptvecs(centering, lat_consts, lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)
    
#     H = np.array([[20,0,0],
#                   [0,20,0],
#                   [0,0,20]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 770
#     assert len(red_grid) == 770
#     assert np.sum(weights) == 20**3

#     H = np.array([[41,0,0],
#                   [0,41,0],
#                   [0,0,41]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 1771
#     assert len(red_grid) == 1771
#     assert np.sum(weights) == 41**3

#     H = np.array([[40,0,0],
#                   [0,40,0],
#                   [0,0,40]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 1661
#     assert len(red_grid) == 1661
#     assert np.sum(weights) == 40**3

#     H = np.array([[40,0,0],
#                   [0,20,0],
#                   [0,0,20]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 1026
#     assert len(red_grid) == 1026
#     assert np.sum(weights) == 40*20**2

#     H = np.array([[21,0,0],
#                   [0,41,0],
#                   [0,0,21]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 4741
#     assert len(red_grid) == 4741
#     assert np.sum(weights) == 41*21**2

#     H = np.array([[18,0,0],
#                   [0,18,0],
#                   [0,0,38]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3043
#     assert len(red_grid) == 3043
#     assert np.sum(weights) == 38*18**2

#     H = np.array([[3,0,0],
#                   [0,3,0],
#                   [0,0,3]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
#     assert irrkpts == []
    
# @pytest.mark.skipif("test_reduce_orthorhombic" not in tests,
#                     reason="different tests")     
# def test_reduce_orthorhombic():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.

#     ### Orthorhombic ###

#     lat_consts = [2.95, 3.92, 8.55]
#     lat_angles = [np.pi/2]*3
#     centering = 'prim'

#     lat_vecs = make_ptvecs(centering, lat_consts,
#                            lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)
#     H = np.array([[40,0,0],
#                   [0,40,0],
#                   [0,0,40]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 8000
#     assert len(red_grid) == 8000
#     assert np.sum(weights) == 40**3

#     H = np.array([[40,0,0],
#                   [0,40,0],
#                   [0,0,40]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)

#     assert len(weights) == 9261
#     assert len(red_grid) == 9261
#     assert np.sum(weights) == 40**3

#     H = np.array([[41,0,0],
#                   [0,41,0],
#                   [0,0,41]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 9261
#     assert len(red_grid) == 9261
#     assert np.sum(weights) == 41**3

#     H = np.array([[21,0,0],
#                   [0,41,0],
#                   [0,0,41]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 4851
#     assert len(red_grid) == 4851
#     assert np.sum(weights) == 21*41**2

#     H = np.array([[40,0,0],
#                   [0,20,0],
#                   [0,0,40]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 4000
#     assert len(red_grid) == 4000
#     assert np.sum(weights) == 20*40**2

#     H = np.array([[40,0,0],
#                   [0,41,0],
#                   [0,0,20]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 4851
#     assert len(red_grid) == 4851
#     assert np.sum(weights) == 40*41*20

#     H = np.array([[3,0,0],
#                   [0,3,0],
#                   [0,0,3]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
#     assert irrkpts == []
    
# @pytest.mark.skipif("test_reduce_base_centered_orthorhombic" not in tests,
#                     reason="different tests")     
# def test_reduce_base_centered_orthorhombic():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.

#     ### Base-centered orthorhombic ###
#     lat_consts = [2.95, 3.92, 8.55]
#     lat_angles = [np.pi/2]*3
#     centering = 'base'
    
#     lat_vecs = make_ptvecs(centering, lat_consts,
#                            lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)

#     H = np.array([[30,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3856
#     assert len(red_grid) == 3856
#     assert np.sum(weights) == 30**3
    
#     H = np.array([[31,0,0],
#                   [0,31,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 4096
#     assert len(red_grid) == 4096
#     assert np.sum(weights) == 31**3

#     H = np.array([[14,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3376
#     assert len(red_grid) == 3376
#     assert np.sum(weights) == 14*30*30

#     H = np.array([[31,0,0],
#                   [0,15,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3728
#     assert len(red_grid) == 3728
#     assert np.sum(weights) == 15*31**2

#     H = np.array([[30,0,0],
#                   [0,31,0],
#                   [0,0,15]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3728
#     assert len(red_grid) == 3728
#     assert np.sum(weights) == 30*31*15

#     H = np.array([[3,0,0],
#                   [0,3,0],
#                   [0,0,3]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
                
# @pytest.mark.skipif("test_reduce_body_centered_orthorhombic" not in tests,
#                     reason="different tests")     
# def test_reduce_body_centered_orthorhombic():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.

#     ### Body-centered orthorhombic ###
#     lat_consts = [2.95, 3.92, 8.55]
#     lat_angles = [np.pi/2]*3
#     centering = 'body'

#     lat_vecs = make_ptvecs(centering, lat_consts,
#                            lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)    
#     H = np.array([[30,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3736
#     assert len(red_grid) == 3736
#     assert np.sum(weights) == 30**3

#     H = np.array([[31,0,0],
#                   [0,31,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 4096
#     assert len(red_grid) == 4096
#     assert np.sum(weights) == 31**3

#     H = np.array([[14,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 6169
#     assert len(red_grid) == 6169
#     assert np.sum(weights) == 14*30**2

#     H = np.array([[30,0,0],
#                   [0,14,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 6169
#     assert len(red_grid) == 6169
#     assert np.sum(weights) == 14*30**2

#     H = np.array([[30,0,0],
#                   [0,31,0],
#                   [0,0,14]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 6512
#     assert len(red_grid) == 6512
#     assert np.sum(weights) == 14*30*31

#     H = np.array([[3,0,0],
#                   [0,3,0],
#                   [0,0,3]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:    
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
#     assert irrkpts == []

# @pytest.mark.skipif("test_reduce_face_centered_orthorhombic" not in tests,
#                     reason="different tests")     
# def test_reduce_face_centered_orthorhombic():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.
    
#     ### Face-centered orthorhombic ###
#     lat_consts = [2.95, 3.92, 8.55]
#     lat_angles = [np.pi/2]*3
#     centering = 'face'

#     lat_vecs = make_ptvecs(centering, lat_consts,
#                            lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)

#     H = np.array([[30,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3736
#     assert len(red_grid) == 3736
#     assert np.sum(weights) == 30**3

#     H = np.array([[31,0,0],
#                   [0,31,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 4096
#     assert len(red_grid) == 4096
#     assert np.sum(weights) == 31**3

#     H = np.array([[14,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 5874
#     assert len(red_grid) == 5874
#     assert np.sum(weights) == 14*30**2

#     H = np.array([[32,0,0],
#                   [0,16,0],
#                   [0,0,32]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3281
#     assert len(red_grid) == 3281
#     assert np.sum(weights) == 16*32**2

#     H = np.array([[34,0,0],
#                   [0,35,0],
#                   [0,0,13]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 7736
#     assert len(red_grid) == 7736
#     assert np.sum(weights) == 34*35*13

#     H = np.array([[3,0,0],
#                   [0,3,0],
#                   [0,0,3]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)

#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:        
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
# @pytest.mark.skipif("test_reduce_monoclinic" not in tests,
#                     reason="different tests")                     
# def test_reduce_monoclinic():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.

#     ### Monoclinic ###
#     lat_consts = [5.596, 3.533, 4.274]
#     lat_angles = [np.pi/2, 119.069*np.pi/180, np.pi/2]
#     centering = 'prim'

#     lat_vecs = make_ptvecs(centering, lat_consts,
#                            lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)
    
#     H = np.array([[30,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 7232
#     assert len(red_grid) == 7232
#     assert np.sum(weights) == 30**3

#     H = np.array([[31,0,0],
#                   [0,31,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)                
#     assert len(weights) == 7696
#     assert len(red_grid) == 7696
#     assert np.sum(weights) == 31**3
#     H = np.array([[14,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                        rlat_vecs, grid_vecs,
#                        offset)
#     assert len(weights) == 3392
#     assert len(red_grid) == 3392
#     assert np.sum(weights) == 14*30**2

#     H = np.array([[31,0,0],
#                   [0,15,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3848
#     assert len(red_grid) == 3848
#     assert np.sum(weights) == 15*31**2

#     H = np.array([[31,0,0],
#                   [0,15,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3848
#     assert len(red_grid) == 3848
#     assert np.sum(weights) == 15*31**2

#     H = np.array([[30,0,0],
#                   [0,31,0],
#                   [0,0,14]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)

#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 3360
#     assert len(red_grid) == 3360
#     assert np.sum(weights) == 30*31*14

#     H = np.array([[3,0,0],
#                   [0,3,0],
#                   [0,0,3]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:        
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
#     assert irrkpts == []

# @pytest.mark.skipif("test_reduce_base_centered_monoclinic" not in tests,
#                     reason="different tests")                     
# def test_reduce_base_centered_monoclinic():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.
    
#     ### Base-centered monoclinic ###
#     lat_consts = [5.596, 3.533, 4.274]
#     lat_angles = [np.pi/2, 119.069*np.pi/180, np.pi/2]
#     centering = 'base'

#     lat_vecs = make_ptvecs(centering, lat_consts,
#                            lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)    

#     H = np.array([[30,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 6992
#     assert len(red_grid) == 6992
#     assert np.sum(weights) == 30**3

#     H = np.array([[31,0,0],
#                   [0,31,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 7696
#     assert len(red_grid) == 7696
#     assert np.sum(weights) == 31**3

#     H = np.array([[14,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 6288
#     assert len(red_grid) == 6288
#     assert np.sum(weights) == 14*30**2
                
#     H = np.array([[31,0,0],
#                   [0,15,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 7208
#     assert len(red_grid) == 7208
#     assert np.sum(weights) == 15*31**2

#     H = np.array([[31,0,0],
#                   [0,15,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 7208
#     assert len(red_grid) == 7208
#     assert np.sum(weights) == 15*31**2

#     H = np.array([[31,0,0],
#                   [0,20,0],
#                   [0,0,15]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = [0.0, 0.5, 0.5]
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 4650
#     assert len(red_grid) == 4650
#     assert np.sum(weights) == 31*20*15

#     H = np.array([[4,0,0],
#                   [0,4,0],
#                   [0,2,3]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = [0.0, 0.5, 0.5]
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:        
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
#     assert irrkpts == []
                
# @pytest.mark.skipif("test_reduce_tetragonal" not in tests,
#                     reason="different tests")                     
# def test_reduce_tetragonal():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.
    
#     ### Tetragonal ###
#     lat_consts = [4.93777, 4.93777, 7.461038]
#     lat_angles = [np.pi/2]*3
#     centering = 'prim'

#     lat_vecs = make_ptvecs(centering, lat_consts,
#                            lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)

#     H = np.array([[30,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 2176
#     assert len(red_grid) == 2176
#     assert np.sum(weights) == 30**3
    
#     H = np.array([[31,0,0],
#                   [0,31,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 2176
#     assert len(red_grid) == 2176
#     assert np.sum(weights) == 31**3

#     H = np.array([[14,0,0],
#                   [0,30,0],
#                   [0,0,30]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 1575
#     assert len(red_grid) == 1575
#     assert np.sum(weights) == 14*30**2

#     H = np.array([[31,0,0],
#                   [0,15,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 2048
#     assert len(red_grid) == 2048
#     assert np.sum(weights) == 15*31**2

#     H = np.array([[33,0,0],
#                   [0,31,0],
#                   [0,0,17]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 2448
#     assert len(red_grid) == 2448
#     assert np.sum(weights) == 33*31*17

#     H = np.array([[5,0,0],
#                   [3,4,0],
#                   [1,2,7]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:        
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
#     assert irrkpts == []
    
# @pytest.mark.skipif("test_reduce_body_centered_tetragonal" not in tests,
#                     reason="different tests")                     
# def test_reduce_body_centered_tetragonal():
#     # Compare our symmetry reduction to the symmetry reduction obtained in VASP.
#     ### Body-centered tetragonal ###
#     lat_consts = [4.93777, 4.93777, 7.461038]
#     lat_angles = [np.pi/2]*3
#     centering = 'body'

#     lat_vecs = make_ptvecs(centering, lat_consts,
#                            lat_angles)
#     rlat_vecs = make_rptvecs(lat_vecs)
    
#     H = np.array([[32,0,0],
#                   [0,32,0],
#                   [0,0,32]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 2393
#     assert len(red_grid) == 2393
#     assert np.sum(weights) == 32**3

#     H = np.array([[33,0,0],
#                   [0,33,0],
#                   [0,0,33]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([1./2]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 2601
#     assert len(red_grid) == 2601
#     assert np.sum(weights) == 33**3

#     H = np.array([[15,0,0],
#                   [0,31,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 6983
#     assert len(red_grid) == 6983
#     assert np.sum(weights) == 15*31**2

#     H = np.array([[31,0,0],
#                   [0,15,0],
#                   [0,0,31]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 6983
#     assert len(red_grid) == 6983
#     assert np.sum(weights) == 15*31**2

#     H = np.array([[31,0,0],
#                   [0,32,0],
#                   [0,0,15]])
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     offset = np.array([0.]*3)
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     assert len(weights) == 7441
#     assert len(red_grid) == 7441
#     assert np.sum(weights) == 31*32*15

#     H = np.array([[3,0,0],
#                   [0,4,0],
#                   [0,0,5]])
#     offset = np.array([1./2]*3)
#     grid_vecs = np.dot(rlat_vecs, np.linalg.inv(H))
#     grid = make_cell_points(rlat_vecs, grid_vecs, offset)
#     red_grid, weights = reduce_kpoint_list(grid,
#                         rlat_vecs, grid_vecs,
#                         offset)
#     irrkpts = list(range(len(weights)))
#     grid_copy = deepcopy(red_grid)

#     atom_labels = [0]
#     atom_positions = [[0,0,0]]                       
#     orbits, weights = get_orbits(grid, lat_vecs, rlat_vecs, atom_labels, atom_positions)
    
#     for v in orbits:        
#         for k1 in v:
#             for k2 in red_grid:
#                 if irrkpts == []:
#                     break
#                 ind = np.where([np.allclose(k2, k) for k in grid_copy])[0][0]
#                 del grid_copy[ind]
#                 del irrkpts[ind]
#     assert irrkpts == []


# @pytest.mark.skipif("test_get_point_group" not in tests,
#                     reason="different tests")
# def test_get_point_group():

#     lat_type = "simple cubic"
#     lat_consts = [1]*3
#     lat_angles = [np.pi/2]*3
#     lat_centering = "prim"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)
#     point_group = get_point_group(lat_vecs)
#     assert len(point_group) == 48
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))
        
#     lat_type = "body-centered cubic"
#     lat_consts = [1]*3
#     lat_angles = [np.pi/2]*3
#     lat_centering = "body"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == 48
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

        
#     lat_type = "face-centered cubic"
#     lat_consts = [1]*3
#     lat_angles = [np.pi/2]*3
#     lat_centering = "face"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == 48
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))
    
#     lat_type = "tetragonal"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "prim"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "body-centered tetragonal"
#     lat_consts = [1, 1, 2]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "body"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "prim"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "face-centered orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "face"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "body-centered orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "body"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "base-centered orthorhombic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/2]*3
#     lat_centering = "base"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "hexagonal"
#     lat_consts = [1., 1., 3.]
#     lat_angles = [np.pi/2, np.pi/2, 2*np.pi/3]
#     lat_centering = "prim"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "rhombohedral"
#     lat_consts = [1., 1., 1.]
#     lat_angles = [.55*np.pi]*3
#     lat_centering = "prim"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "monoclinic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/3, np.pi/2, np.pi/2]
#     lat_centering = "prim"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "base-centered monoclinic"
#     lat_consts = [1, 2, 3]
#     lat_angles = [np.pi/4, np.pi/2, np.pi/2]
#     lat_centering = "base"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))

#     lat_type = "triclinic"
#     lat_consts = [1.1, 2.8, 4.3]
#     lat_angles = [np.pi/6, np.pi/4, np.pi/3]
#     lat_centering = "prim"
#     lat_vecs = make_lattice_vectors(lat_type, lat_consts, lat_angles)
#     volume = det(lat_vecs)    
#     point_group = get_point_group(lat_vecs)    
#     assert len(point_group) == number_of_point_operators(lat_type.split()[-1])
#     for pg in point_group:
#         assert np.isclose(abs(det(pg)), 1)
#         assert np.isclose(abs(volume), abs(det(np.dot(pg, lat_vecs))))
#         assert np.allclose(np.dot(pg, pg.T), np.eye(3))


# @pytest.mark.skipif("test_gaussian_reduction" not in tests,
#                     reason="different tests")
# def test_gaussian_reduction():
    
#     passed = True
#     for _ in range(1000):
        
#         v1 = np.random.randint(low=1, high=20)*np.random.rand(3)
#         v2 = np.random.randint(low=1, high=20)*np.random.rand(3)

#         if not np.allclose(_gaussian_reduce_two_vectors(v1, v2, eps=1e-10),
#                            gaussian_reduction(v1, v2)):
#             passed = False
#             break
        
#     assert passed


# @pytest.mark.skipif("test_reduce_lattice_vector" not in tests,
#                     reason="different tests")
# def test_reduce_lattice_vector():

#     passed = True
#     for _ in range(1000):

#         random_lat_vecs = np.random.randint(low=1, high=20)*np.random.rand(3,3)
#         while np.isclose(det(random_lat_vecs), 0):
#             random_lat_vecs = np.random.randint(low=1, high=20)*np.random.rand(3,3)
            
#         test1 = reduce_lattice_vector(random_lat_vecs)
#         A,B,C = random_lat_vecs.T

#         A,B,C = _reduce_C_in_ABC(A, B, C, 1e-10)
#         test2 = np.array([A,B,C]).T

#         if not np.allclose(test1, test2):
#             passed = False
        
#     assert passed

# @pytest.mark.skipif("test_minkowski_reduce_basis" not in tests,
#                     reason="different tests")
# def test_minkowski_reduce_basis():

#     same = True
#     for _ in range(1000):
        
#         lattice_basis = np.random.randint(low=1, high=100)*np.random.rand(3,3)

#         while np.isclose(det(lattice_basis), 0):
#             lattice_basis = np.random.randint(low=1, high=100)*np.random.rand(3,3)

#         test1 = _minkowski_reduce_basis(lattice_basis.T, 1e-10)
#         test2 = minkowski_reduce_basis(lattice_basis)

#         if not np.allclose(test1.T, test2):
#             same = False
            
#     assert same


@pytest.mark.skipif("test_get_space_group" not in tests,
                    reason="different tests")
def test_get_space_group():

    # lattice vectors 
    lat_vecs = np.array([[ 2.986,  0.   ,  1.493],
                         [ 0.   ,  0.   , -4.479],
                         [ 0.   ,  2.986,  1.493]])
    
    # atom positions in lattice coordinates
    atom_positions = [[0.0, 0.0, 0.0],
                      [0.33333333, 0.33333333, 0.33333333],
                      [0.66666667, 0.66666667, 0.66666667]]
    
    # atom labels
    atom_labels = [0, 0, 1]

    point_group1, translations1 = get_space_group(lat_vecs, atom_labels, atom_positions,
                                                  coords="lat", rtol=1e-4, atol=1e-6,
                                                  eps=8)

    point_group2, translations2 = get_spaceGroup(np.transpose(lat_vecs),
                                                 atom_labels, atom_positions,
                                                 lattcoords=True, eps=1e-6)
    
    assert len(point_group1) == len(point_group2)
    assert check_contained(point_group1, point_group2)
    

# @pytest.mark.skipif("test_bring_into_cell" not in tests,
#                     reason="different tests")        
# def test_bring_into_cell():

#     lat_vecs = 3*np.array([[1,0,0],[0,1,0],[0,0,1]])

#     point = [3+1e-8, 2+1e-4, 8+1e-6]
#     assert np.allclose(bring_into_cell(point, lat_vecs, rtol=1e-4), [1e-8, 2+1e-4, 2+1e-6])
    
#     points = [[21+1e-8, 14+1e-2, 13+1e-5], [1e-8, 3+1e-5, 7+1e-4]]
#     assert np.allclose(bring_into_cell(points, lat_vecs, rtol=1e-4),
#                        [[1e-8, 2+1e-2, 1+1e-5], [0, 1e-5, 1+1e-4]])
    
#     with pytest.raises(ValueError, message="Coordinate options include 'Cart' and 'lat'."):
#         bring_into_cell(points, lat_vecs, rtol=1e-4, coords="cart")


# @pytest.mark.skipif("test_check_commensurate" not in tests,
#                     reason="different tests")        
# def test_check_commensurate():

#     lattice = 3*np.array([[1,0,0],[0,1,0],[0,0,1]])
#     sublattice = 9*np.array([[1,0,0],[0,1,0],[0,0,1]])

#     check, N = check_commensurate(lattice, sublattice)

#     assert check == True
#     assert np.allclose(N, np.eye(3)*3)
    
#     lattice = 3*np.array([[1,0,0],[0,1,0],[0,0,1]])
#     sublattice = 7.5*np.array([[1,0,0],[0,1,0],[0,0,1]])

#     check, N = check_commensurate(lattice, sublattice)

#     assert check == False
#     assert np.allclose(N, np.eye(3)*2.5)
