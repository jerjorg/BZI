"""Test the Brillouin zone sampling methods.
"""
import os
import pytest
import numpy as np
from itertools import product
import csv

from BZI.symmetry import (get_minmax_indices, swap_column, swap_row,
                          HermiteNormalForm, UpperHermiteNormalForm)

from BZI.sampling import (make_grid, make_large_grid, sphere_pts,
                          large_sphere_pts, make_cell_points)
from BZI.utilities import check_contained


from BZI.symmetry import make_ptvecs, make_rptvecs
from conftest import run

tests = run("all sampling")

@pytest.mark.skipif("test_make_grid" not in tests, reason="different tests")
def test_make_grid():
    grid_centering = "prim"
    grid_consts = [1,1,1]
    grid_angles = [np.pi/2]*3
    grid_vecs = make_ptvecs(grid_centering, grid_consts, grid_angles)

    lat_centering = "prim"
    lat_consts = [2]*3
    lat_angles = [np.pi/2]*3
    lat_vecs = make_ptvecs(lat_centering, lat_consts, lat_angles)

    offset = [0]*3
    grid0 = [[0,0,0], [0,0,1], [0,1,0], [0,1,1],
             [1,0,0], [1,0,1], [1,1,0], [1,1,1]]
    grid1 = make_grid(lat_vecs, grid_vecs, offset)

    assert len(grid0) == len(grid1)
    
    for g0 in grid0:
        contained = False
        for g1 in grid1:
            if np.allclose(g0,g1):
                contained = True
        assert contained == True


    grid_centering = "body"
    grid_consts = [1.]*3
    grid_angles = [np.pi/2]*3
    grid_vecs = make_ptvecs(grid_centering, grid_consts, grid_angles)

    lat_centering = "body"
    lat_consts = [2.]*3
    lat_angles = [np.pi/2]*3
    lat_vecs = make_ptvecs(lat_centering, lat_consts, lat_angles)

    offset = [0]*3

    a = 0.5
    grid0 = [[0,0,0], [-a,a,a], [a,-a,a], [0,0,2*a], [a,a,-a],
             [0,2*a,0], [2*a,0,0],[a,a,a]]
    grid1 = make_grid(lat_vecs, grid_vecs, offset)

    assert len(grid0) == len(grid1)

    for g0 in grid0:
        contained = False
        for g1 in grid1:
            if np.allclose(g0,g1):
                contained = True
        assert contained == True
        
        
@pytest.mark.skipif("test_make_cell_points" not in tests, reason="different tests")
def test_make_cell_points():
    """Verify the grid satisfies various properties, such as verifying
    the neighbors of each point are withing the grid as long as the 
    neighbors lie within the unit cell. Also verify none of the points
    lie outside the unit cell.
    """

    # At the moment it only tests the cubic lattices.
    grid_center_list = ["prim", "face"]
    grid_constants = np.array([1./2, 1./4])*2*np.sqrt(2)
    grid_consts_list = [[m]*3 for m in grid_constants]
    grid_angles = [np.pi/2]*3
    cell_center_list = ["prim", "body"]
    cell_constants = [2*np.sqrt(2)]
    cell_consts_list = [[c]*3 for c in cell_constants]
    cell_angles = [np.pi/2]*3
    offsets = [[0., 0., 0.], [1./2, 1./2, 1./2]]
    
    # for grid_constant in grid_constants:
    for grid_consts in grid_consts_list:
        for grid_center in grid_center_list:
            grid_vectors = make_ptvecs(grid_center, grid_consts, grid_angles)
            grid_lengths = [np.linalg.norm(lv) for lv in grid_vectors]
            for cell_consts in cell_consts_list:
                for cell_center in cell_center_list:
                    cell_vectors = make_ptvecs(cell_center,
                                               cell_consts, cell_angles)
                    cell_lengths = [np.linalg.norm(cv) for cv in
                                        cell_vectors]
                    for offset in offsets:
                        grid = make_cell_points(cell_vectors, grid_vectors, offset)
                        grid2, null_grid = make_large_grid(cell_vectors,
                                                  grid_vectors, offset)
                        
                        # Verify all the points in the cell for the large grid
                        # are contained in grid.
                        assert check_contained(grid, grid2)
                            
@pytest.mark.skipif("test_get_minmax_indices" not in tests, reason="different tests")
def test_get_minmax_indices():
    """Various tests taxen from symlib."""
    ntests =50
    
    vecs = []
    mins = []
    maxs = []
    for n in range(1,ntests+1):
        vec_filename = os.path.join(os.path.dirname(__file__), "sampling_testfiles/get_minmax_indices_invec.in.%s" %n)
        max_filename = os.path.join(os.path.dirname(__file__), "./sampling_testfiles/get_minmax_indices_max.out.%s" %n)
        min_filename = os.path.join(os.path.dirname(__file__), "./sampling_testfiles/get_minmax_indices_min.out.%s" %n)

        print("file ", vec_filename)
        
        with open(vec_filename,'r') as f:
            next(f) # skip headings
            vec = np.asarray([int(elem) for elem in next(f).strip().split()])
        
        with open(max_filename,'r') as f:
            next(f) # skip headings
            max = int(next(f).strip())

        with open(min_filename,'r') as f:
            next(f) # skip headings
            min = int(next(f).strip())

        assert np.allclose(get_minmax_indices(np.array(vec)), np.asarray([min-1, max-1])) == True

@pytest.mark.skipif("test_swap_columns" not in tests, reason="different tests")
def test_swap_columns():
    """Various tests taxen from symlib."""    
    import csv
    ntests =50

    vecs = []
    mins = []
    maxs = []
    for n in range(1,ntests+1):
        Bin_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_B.in.%s" %n))
        Bout_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_B.out.%s" %n))
        Min_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_M.in.%s" %n))
        Mout_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_M.out.%s" %n))
        kin_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_k.in.%s" %n))

        Bin = []
        Bin_file.readline() # skip headings 
        for line in Bin_file.readlines():
            Bin.append([int(x) for x in line.split()])
        Bin = np.asarray(Bin)
        Bout = []
        Bout_file.readline() # skip headings 
        for line in Bout_file.readlines():
            Bout.append([int(x) for x in line.split()])
        Bout = np.asarray(Bout)
        Min = []
        Min_file.readline() # skip headings 
        for line in Min_file.readlines():
            Min.append([int(x) for x in line.split()])
        Min = np.asarray(Min)

        Mout = []
        Mout_file.readline() # skip headings 
        for line in Mout_file.readlines():
            Mout.append([int(x) for x in line.split()])
        Mout = np.asarray(Mout)
        
        kin = 0
        kin_file.readline() # skip headings
        for line in kin_file.readlines():
            kin = int(line)
                
        assert np.allclose(swap_column(Min,Bin,kin-1), (Mout, Bout)) == True

@pytest.mark.skipif("test_swap_rows" not in tests, reason="different tests")
def test_swap_rows():
    """Various tests taxen from symlib."""    
    import csv
    ntests =50

    vecs = []
    mins = []
    maxs = []
    for n in range(1,ntests+1):
        Bin_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_B.in.%s" %n))
        Bout_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_B.out.%s" %n))
        Min_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_M.in.%s" %n))
        Mout_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_M.out.%s" %n))
        kin_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/swap_column_k.in.%s" %n))
        
        Bin = []
        Bin_file.readline() # skip headings 
        for line in Bin_file.readlines():
            Bin.append([int(x) for x in line.split()])
        Bin = np.asarray(Bin)
        Bout = []
        Bout_file.readline() # skip headings 
        for line in Bout_file.readlines():
            Bout.append([int(x) for x in line.split()])
        Bout = np.asarray(Bout)
        Min = []
        Min_file.readline() # skip headings 
        for line in Min_file.readlines():
            Min.append([int(x) for x in line.split()])
        Min = np.asarray(Min)

        Mout = []
        Mout_file.readline() # skip headings 
        for line in Mout_file.readlines():
            Mout.append([int(x) for x in line.split()])
        Mout = np.asarray(Mout)
        
        kin = 0
        kin_file.readline() # skip headings
        for line in kin_file.readlines():
            kin = int(line)
            
        Min = np.transpose(Min)
        Bin = np.transpose(Bin)
        Min, Bin = swap_row(Min,Bin,kin-1)
        Min = np.transpose(Min)
        Bin = np.transpose(Bin)
        
        assert np.allclose((Min, Bin), (Mout, Bout)) == True

        
@pytest.mark.skipif("test_HermiteNormalForm" not in tests, reason="different tests")
def test_HermiteNormalForm():
    """Various tests taxen from symlib."""
    import csv
    ntests =50

    vecs = []
    mins = []
    maxs = []
    for n in range(1,ntests+1):
        Sin_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/HermiteNormalForm_S.in.%s" %n))
        Bout_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/HermiteNormalForm_B.out.%s" %n))
        Hout_file = open(os.path.join(os.path.dirname(__file__),
                        "sampling_testfiles/HermiteNormalForm_H.out.%s" %n))
        
        Sin = []
        Sin_file.readline() # skip headings 
        for line in Sin_file.readlines():
            Sin.append([int(x) for x in line.split()])
        Sin = np.asarray(Sin)
        
        Bout = []
        Bout_file.readline() # skip headings 
        for line in Bout_file.readlines():
            Bout.append([int(x) for x in line.split()])
        Bout = np.asarray(Bout)
        
        Hout = []
        Hout_file.readline() # skip headings 
        for line in Hout_file.readlines():
            Hout.append([int(x) for x in line.split()])
        Hout = np.asarray(Hout)

        assert np.allclose(HermiteNormalForm(Sin), (Hout, Bout)) == True

@pytest.mark.skipif("test_UpperHermiteNormalForm" not in tests, reason="different tests")
def test_UpperHermiteNormalForm():
    """Various tests taxen from symlib."""
    import csv
    ntests =100

    vecs = []
    mins = []
    maxs = []
    for n in range(1,ntests+1):
        S = np.random.randint(-100,100, size=(3,3))
        H, B = UpperHermiteNormalForm(S)

        assert np.isclose(abs(np.linalg.det(B)), 1) == True
        assert np.allclose(np.dot(B, S), H) == True
        check1 = (np.array([2,2,1]), np.array([1,0,0]))
        assert np.count_nonzero(H[check1]) == 0
        check2 = (np.asarray([0, 0, 0, 1, 1, 2]), np.asarray([0, 1, 2, 1, 2, 2]))
        assert any(H[check2] < 0) == False
        assert (H[0,1] < H[1,1]) == True
        assert (H[0,2] < H[2,2]) == True
        assert (H[1,2] < H[2,2]) == True


@pytest.mark.skipif("test_make_grid2" not in tests, reason="different tests")
def test_make_grid2():
    # This unit test doesn't pass because the primitive translation vectors
    # changed when I updated the code (I think).

    grid_pts1 = [[0,0,0],
                 [1,1,1],
                 [0,0,2],
                 [0,2,0],
                 [0,2,2],
                 [2,0,0],
                 [0,2,2],
                 [2,0,2],
                 [2,2,0],
                 [2,2,2],
                 [1,3,3],
                 [3,1,3],
                 [3,1,1],
                 [1,1,3],
                 [1,3,1],
                 [3,1,1]]
    grid_pts1 = np.asarray(grid_pts1)*1./4

    cell_centering = "prim"
    cell_const = 1.
    cell_const_list = [cell_const]*3
    cell_angles = [np.pi/2]*3
    cell_vecs = make_ptvecs(cell_centering, cell_const_list, cell_angles)
    
    grid_centering = "body"
    grid_const = cell_const/2
    grid_const_list = [grid_const]*3
    grid_angles = [np.pi/2]*3
    grid_vecs = make_ptvecs(grid_centering, grid_const_list, grid_angles)
    offset = np.asarray([0.,0.,0.])
    grid = make_grid(cell_vecs, grid_vecs, offset, coords="lat")
    
    for g1 in grid_pts1:
        assert check_contained(g1, grid)
        
    lat_type_list = ["fcc"]
    lat_centering_list = ["face"]
    lat_const_list = [3*np.pi]
    lat_consts_list = [[l]*3 for l in lat_const_list]
    lat_angles =[np.pi/2]*3
    offset_list = [[1.3, 1.1,1.7]]
    r_list = [np.pi]

    for lat_centering in lat_centering_list:
        for lat_consts in lat_consts_list:
            lat_vecs = make_ptvecs(lat_centering, lat_consts, lat_angles)
            rlat_vecs = make_rptvecs(lat_vecs)
            for offset in offset_list:
                offset = np.asarray(offset)
                for r in r_list:
                    total_grid = large_sphere_pts(lat_vecs,r,offset)
                    grid = sphere_pts(lat_vecs,r,offset)
                    contained = False
                    for tg in total_grid:
                        if np.dot(tg-offset,tg-offset) <= r:
                            assert check_contained(tg, grid)
