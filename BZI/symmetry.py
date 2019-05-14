"""Generate quantities reated to the symmetry of the lattice. This module
draws heavily from Setyawan, Wahyu, and Stefano Curtarolo. "High-throughput
electronic band structure calculations: Challenges and tools." Computational
Materials Science 49.2 (2010): 299-312.
"""

import numpy as np
from numpy.linalg import norm, inv, det
import math, itertools
from copy import deepcopy
import itertools as it
from itertools import islice, product

from phenum.grouptheory import SmithNormalForm
from phenum.vector_utils import _minkowski_reduce_basis
from phenum.symmetry import get_lattice_pointGroup, get_spaceGroup
from BZI.utilities import check_contained, find_point_indices, swap_rows_columns

class Lattice(object):
    """Create a lattice.

    Args:
        centering_type (str): identifies the position of lattice points in
            the conventional unit cell. Option include 'prim', 'base', 'body',
            and 'center'.
        lattice_constants (list): a list of constants that correspond to the
            lengths of the lattice vectors in the conventional unit cell ordered
            as [a,b,c].
        lattice_angles (list): a list of angles in radians that correspond to
            the angles between lattice vectors in the conventional unit cell
            ordered as [alpha, beta, gamma] where alpha is the angle between bc,
            beta is the angle between ac, and gamma is the angle between ab.
        convention (str): gives the convention of for finding the reciprocal lattice
            vectors. Options include 'ordinary' and 'angular'. Angular include a 
            factor of 2pi.

    Attributes:
        centering (str): the type of lattice point centering in the 
            conventional unit cell. Option include 'prim', 'base', 'body', and
            'center'.
        constants (list): a list of constants that correspond to the
            lengths of the lattice vectors in the conventional unit cell ordered
            as [a,b,c].
        angles (list): a list of angles in radians that correspond to
            the angles between lattice vectors in the conventional unit cell
            ordered as [alpha, beta, gamma] where alpha is the angle between bc,
            beta is the angle between ac, and gamma is the angle between ab.
        vectors (numpy.ndarray): an array of primitive lattice vectors
            as columns of a 3x3 matrix.
        reciprocal_vectors (numpy.ndarray): the reciprocal primitive 
            translation vectors as columns of a 3x3 matrix.
        symmetry_group (numpy.ndarray): the group of transformations under which
            the lattice in invariant.
        symmetry_points (dict): a dictionary of high symmetry points with the
            keys as letters and values as lattice coordinates.
        symmetry_paths (list): a list of symmetry point pairs used when creating
            a band structure plot.
        type (str): the Bravais lattice type.
        volume (float): the volume of the parallelepiped given by the three
            lattice vectors
        reciprocal_volume (float): the volume of the parallelepiped given by the three
            reciprocal lattice vectors
    """
    
    def __init__(self, centering_type, lattice_constants, lattice_angles,
                 convention="ordinary", rtol=1e-5, atol=1e-8, eps=1e-10):
        self.rtol = rtol
        self.atol = atol
        self.eps = eps
        self.centering = centering_type
        self.constants = lattice_constants
        self.angles = lattice_angles
        self.type = find_lattice_type(centering_type, lattice_constants,
                                      lattice_angles)
        self.vectors = make_lattice_vectors(self.type, lattice_constants,
                                            lattice_angles)
        self.reciprocal_vectors = make_rptvecs(self.vectors, convention)
        self.symmetry_group = get_point_group(self.vectors, rtol=self.rtol,
                                              atol=self.atol, eps=self.eps)
        # self.symmetry_group = find_point_group(self.vectors)
        self.symmetry_points = get_sympts(centering_type, lattice_constants,
                                          lattice_angles, convention=convention)
                                          
        self.symmetry_paths = get_sympaths(centering_type, lattice_constants,
                                           lattice_angles, convention=convention)
        self.volume = det(self.vectors)
        self.reciprocal_volume = det(self.reciprocal_vectors)

# Define the symmetry points for a simple-cubic lattice in lattice coordinates.
sc_sympts = {"$\Gamma$": [0. ,0., 0.],
              "R": [1./2, 1./2, 1./2],
              "X": [0., 1./2, 0.],
              "M": [1./2, 1./2, 0.]}


# Define the symmetry points for a fcc lattice in lattice coordinates.
# Coordinates are in lattice coordinates.
fcc_sympts = {"$\Gamma$": [0., 0., 0.], # G is the gamma point.
              "K": [3./8, 3./8, 3./4],
              "L": [1./2, 1./2, 1./2],
              "U": [5./8, 1./4, 5./8],              
              "W": [1./2, 1./4, 3./4],
              "X": [1./2, 0., 1./2]}

# One of the band plots needs the gamma point in the neighboring cell.
mod_fcc_sympts = {"$\Gamma$": [0., 0., 0.], # G is the gamma point.
                  "K": [3./8, 3./8, 3./4],
                  "L": [1./2, 1./2, 1./2],
                  "U": [5./8, 1./4, 5./8],              
                  "W": [1./2, 1./4, 3./4],
                  "X": [1./2, 0., 1./2],
                  "G2":[1., 1., 1.]}

# Define the symmetry points for a bcc lattice in lattice coordinates
bcc_sympts = {"$\Gamma$": [0., 0., 0.],
              "H": [1./2, -1./2, 1./2],
              "P": [1./4, 1./4, 1./4],
              "N": [0., 0., 1./2]}

# Tetragonal high symmetry points
tet_sympts = {"$\Gamma$": [0., 0., 0.],
              "A": [1./2, 1./2, 1./2],
              "M": [1./2, 1./2, 0.],
              "R": [0., 1./2, 1./2],
              "X": [0., 1./2, 0.],
              "Z": [0., 0., 1./2]}

def bct1_sympts(a, c):
    """Return the body-centered tetragonal high symmetry points for c < a as a 
    dictionary.
    """
    
    eta = (1. + c**2/a**2)/4.
    return {"$\Gamma$": [0., 0., 0.],
            "M": [-1./2, 1./2, 1./2],
            "N": [0., 1./2, 0.],
            "P": [1./4, 1./4, 1./4],
            "X": [0., 0., 1./2],
            "Z": [eta, eta, -eta],
            "Z1": [-eta, 1-eta, eta]}


def bct2_sympts(a, c):
    """Return the body-centered tetragonal high symmetry points for a < c
    as a dictionary.
    """
    
    eta = (1. + a**2/c**2)/4.
    zeta = a**2/(2*c**2)
    return {"$\Gamma$": [0., 0., 0.],
            "N": [0., 1./2, 0.],
            "P": [1./4, 1./4, 1./4],
            "S": [-eta, eta, eta], # Sigma
            "S1": [eta, 1-eta, -eta], # Sigma_1
            "X": [0., 0., 1./2],
            "Y": [-zeta, zeta, 1./2],
            "Y1": [1./2, 1./2, -zeta],
            "Z": [1./2, 1./2, -1./2]}


# Orthorhombic high symmetry points
orc_sympts = {"$\Gamma$": [0., 0., 0.],
              "R": [1./2, 1./2, 1./2],
              "S": [1./2, 1./2, 0.],
              "T": [0., 1./2, 1./2],
              "U": [1./2, 0., 1./2],
              "X": [1./2, 0., 0.],
              "Y": [0., 1./2, 0.],
              "Z": [0., 0., 1./2]}


def orcf13_sympts(a, b, c):
    """Return the face-centered orthorhombic high symmetry points for
     1/a**2 > 1/b**2 +1/c**2 and 1/a**2 = 1/b**2 +1/c**2 as a dictionary.
    """
    
    a = float(a)
    b = float(b)
    c = float(c)
    zeta = (1 + (a/b)**2 - (a/c)**2)/4.
    eta = (1 + (a/b)**2 + (a/c)**2)/4.
    
    return {"$\Gamma$": [0., 0., 0.],
            "A": [1./2, 1./2+zeta, zeta],
            "A1": [1./2, 1./2 - zeta, 1 - zeta],
            "L": [1./2, 1./2, 1./2],
            "T": [1., 1./2, 1./2],
            "X": [0., eta, eta],
            "X1": [1., 1-eta, 1-eta],
            "Y": [1./2, 0., 1./2],
            "Z": [1./2, 1./2, 0.]}


def orcf2_sympts(a, b, c):
    """Return the face-centered orthorhombic high symmetry points for
     1/a**2 < 1/b**2 +1/c**2 as a dictionary.
    """

    a = float(a)
    b = float(b)
    c = float(c)
    eta = (1 + a**2/b**2 - a**2/c**2)/4
    phi = (1 + c**2/b**2 - c**2/a**2)/4
    delta = (1 + b**2/a**2 - b**2/c**2)/4
    
    return {"$\Gamma$": [0., 0., 0.],
            "C": [1./2, 1./2 - eta, 1. - eta],
            "C1": [1./2, 1./2 + eta, eta],
            "D": [1./2 - delta, 1./2, 1. - delta],
            "D1": [1./2 + delta, 1./2, delta],
            "L": [1./2, 1./2, 1./2],
            "H": [1 - phi, 1./2 - phi, 1./2],
            "H1": [phi, 1./2 + phi, 1./2],
            "X": [0., 1./2, 1./2],
            "Y": [1./2, 0., 1./2],
            "Z": [1./2, 1./2, 0.]}

def orci_sympts(a, b, c):
    """Return the body-centered orthorhombic high symmetry points.
    """
    
    a = float(a)
    b = float(b)
    c = float(c)
    zeta = (1 + a**2/c**2)/4
    eta = (1 + b**2/c**2)/4
    delta = (b**2 - a**2)/(4*c**2)
    mu = (a**2 + b**2)/(4*c**2)
    
    return {"$\Gamma$": [0., 0., 0.],
            "L": [-mu, mu, 1./2 - delta],
            "L1": [mu, -mu, 1./2 + delta],
            "L2": [1./2 - delta, 1./2 + delta, -mu],
            "R": [0., 1./2, 0.],
            "S": [1./2, 0., 0.],
            "T": [0., 0., 1./2],
            "W": [1./4, 1./4, 1./4],
            "X": [-zeta, zeta, zeta],
            "X1": [zeta, 1-zeta, -zeta],
            "Y": [eta, -eta, eta],
            "Y1": [1-eta, eta, -eta],
            "Z": [1./2, 1./2, -1./2]}

def orcc_sympts(a, b):
    """Return the base-centered orthorhombic high symmetry points.
    """
    
    a = float(a)
    b = float(b)
    zeta = (1 + a**2/b**2)/4
    
    return {"$\Gamma$": [0., 0., 0.],
            "A": [zeta, zeta, 1./2],
            "A1": [-zeta, 1-zeta, 1./2],
            "R": [0., 1./2, 1./2],
            "S": [0., 1./2, 0.],
            "T": [-1./2, 1./2, 1./2],
            "X": [zeta, zeta, 0],
            "X1": [-zeta, 1-zeta, 0],
            "Y": [-1./2, 1./2, 0.],
            "Z": [0., 0., 1./2]}

# High symmetry points for a hexagonal lattice.
hex_sympts = {"$\Gamma$": [0., 0., 0.],
              "A": [0., 0., 1./2],
              "H": [1./3, 1./3, 1./2],
              "K": [1./3, 1./3, 0.],
              "L": [1./2, 0., 1./2],
              "M": [1./2, 0., 0.]}

def rhl1_sympts(alpha):
    """Return the rhombohedral lattice points for alpha < pi/2 radians.
    """
    alpha = float(alpha)
    eta = (1 + 4*np.cos(alpha))/(2 + 4*np.cos(alpha))
    nu = 3./4 - eta/2
    
    return {"$\Gamma$": [0., 0., 0.],
            "B": [eta, 1./2, 1-eta],
            "B1": [1./2, 1-eta, eta-1],
            "F": [1./2, 1./2, 0.],
            "L": [1./2, 0.,  0.],
            "L1": [0., 0., -1./2],
            "P": [eta, nu, nu],
            "P1": [1-nu, 1-nu, 1-eta],
            "P2": [nu, nu, eta-1],
            "Q": [1-nu, nu, 0],
            "X": [nu, 0, -nu],
            "Z": [1./2, 1./2, 1./2]}

def rhl2_sympts(alpha):
    """Return the rhombohedral lattice points for alpha > pi/2 radians.
    """
    
    alpha = float(alpha)
    eta = 1/(2*np.tan(alpha/2)**2)
    nu = 3./4 - eta/2
    return {"$\Gamma$": [0., 0., 0.],
            "F": [1./2, -1./2, 0.],
            "L": [1./2, 0., 0.],
            "P": [1-nu, -nu, 1-nu],
            "P1": [nu, nu-1, nu-1],
            "Q": [eta, eta, eta],
            "Q1": [1-eta, -eta, -eta],
            "Z": [1./2, -1./2, 1./2]}

def mcl_sympts(b, c, alpha):
    """Return the high symmetry points for the monoclinic lattice as a 
    dictionary where the keys are strings the values are the lattice coordinates
    of the high symmetry points.
    """

    b = float(b)
    c = float(c)
    alpha = float(alpha)
    
    eta = (1 - b*np.cos(alpha)/c)/(2*np.sin(alpha)**2)
    nu = 1./2 - eta*c*np.cos(alpha)/b
    return {"$\Gamma$": [0., 0., 0.],
            "A": [1./2, 1./2, 0.],
            "C": [0., 1./2, 1./2],
            "D": [1./2, 0., 1./2],
            "D1": [1./2, 0., -1./2],
            "E": [1./2, 1./2, 1./2],
            "H": [0., eta, 1-nu],
            "H1": [0., 1-eta, nu],
            "H2": [0, eta, -nu],
            "M": [1./2, eta, 1-nu],
            "M1": [1./2, 1-eta, nu],
            "M2": [1./2, eta, -nu],
            "X": [0., 1./2, 0.],
            "Y": [0., 0., 1./2],
            "Y1": [0., 0., -1./2],
            "Z": [1./2, 0., 0.]}

def mclc12_sympts(a, b, c, alpha):
    """Return the high symmetry points for a base-centered monoclinic lattice 
    with kgamma > pi/2 and kgamma = pi/2 as a dictionary where the keys are 
    strings the values are the lattice coordinates of the high symmetry points.
    """
    
    a = float(a)
    b = float(b)
    c = float(c)
    alpha = float(alpha)
    
    zeta = (2 - b*np.cos(alpha)/c)/(4*np.sin(alpha)**2)
    eta = 1./2 + 2*zeta*c*np.cos(alpha)/b
    psi = 3./4 - a**2/(4*b**2*np.sin(alpha)**2)
    phi = psi + (3./4 - psi)*b*np.cos(alpha)/c

    return {"$\Gamma$": [0., 0., 0.],
            "N": [1./2, 0., 0.],
            "N1": [0., -1./2, 0.],
            "F": [1-zeta, 1-zeta, 1-eta],
            "F1": [zeta, zeta, eta],
            "F2": [-zeta, -zeta, 1-eta],
            "F3": [1-zeta, -zeta, 1-eta],
            "I": [phi, 1-phi, 1./2],
            "I1": [1-phi, phi-1, 1./2],
            "L": [1./2, 1./2, 1./2],
            "M": [1./2, 0., 1./2],
            "X": [1-psi, psi-1, 0.],
            "X1": [psi, 1-psi, 0.],
            "X2": [psi-1, -psi, 0.],
            "Y": [1./2, 1./2, 0.],
            "Y1": [-1./2, -1./2, 0.],
            "Z": [0., 0., 1./2]}

def mclc34_sympts(a, b, c, alpha):
    """Return the high symmetry points for a base-centered monoclinic lattice
    with gamma < pi/2 and b*cos(alpha/c) + b**2*sin(alpha/a**2)**2 <= 1 (3 is < 1, 4 = 1) as
    a dictionary where the keys are strings the values are the lattice
    coordinates of the high symmetry points. 
    """
    
    a = float(a)
    b = float(b)
    c = float(c)
    alpha = float(alpha)

    mu = (1 + b**2/a**2)/4
    delta = b*c*np.cos(alpha)/(2*a**2)
    zeta = mu - 1./4 + (1 - b*np.cos(alpha)/c)/(4*np.sin(alpha)**2)
    eta = 1./2 + 2*zeta*c*np.cos(alpha)/b
    phi = 1 + zeta - 2*mu
    psi = eta - 2*delta
                
    return {"$\Gamma$": [0., 0., 0.],
            "F": [1-phi, 1-phi, 1-psi],
            "F1": [phi, phi-1, psi],
            "F2": [1-phi, -phi, 1-psi],
            "H": [zeta, zeta, eta],
            "H1": [1-zeta, -zeta, 1-eta],
            "H2": [-zeta, -zeta, 1-eta],
            "I": [1./2, -1./2, 1./2],
            "M": [1./2, 0., 1./2],
            "N": [1./2, 0., 0.],
            "N1": [0., -1./2, 0.],
            "X": [1./2, -1./2, 0.],
            "Y": [mu, mu, delta],
            "Y1": [1-mu, -mu, -delta],
            "Y2": [-mu, -mu, -delta],
            "Y3": [mu, mu-1, delta],
            "Z": [0., 0., 1./2]}

def mclc5_sympts(a, b, c, alpha):
    """Return the high symmetry points for a base-centered monoclinic lattice
    with gamma < pi/2 and b*cos(alpha/c) + b**2*sin(alpha/a**2)**2 > 1 as
    a dictionary where the keys are strings the values are the lattice
    coordinates of the high symmetry points. 
    """

    a = float(a)
    b = float(b)
    c = float(c)
    alpha = float(alpha)

    zeta = (b**2/a**2 + (1 - b*np.cos(alpha)/c)/np.sin(alpha)**2)/4
    eta = 1./2 + 2*zeta*c*np.cos(alpha)/b
    mu = eta/2 + b**2/(4*a**2) - b*c*np.cos(alpha)/(2*a**2)
    nu = 2*mu - zeta
    omega = (4*nu - 1 - b**2*np.sin(alpha)**2/a**2)*c/(2*b*np.cos(alpha))
    delta = zeta*c*np.cos(alpha)/b + omega/2 - 1./4
    rho = 1 - zeta*a**2/b**2

    return {"$\Gamma$": [0., 0., 0.],
            "F": [nu, nu, omega],
            "F1": [1-nu, 1-nu, 1-omega],
            "F2": [nu, nu-1, omega],
            "H": [zeta, zeta, eta],
            "H1": [1-zeta, -zeta, 1-eta],
            "H2": [-zeta, -zeta, 1-eta],
            "I": [rho, 1-rho, 1./2],
            "I1": [1-rho, rho-1, 1./2],
            "L": [1./2, 1./2, 1./2],
            "M": [1./2, 0., 1./2],
            "N": [1./2, 0., 0.],
            "N1": [0., -1./2, 0.],
            "X": [1./2, -1./2, 0.],
            "Y": [mu, mu, delta],
            "Y1": [1-mu, -mu, -delta],
            "Y2": [-mu, -mu, -delta],
            "Y3": [mu, mu-1, delta],
            "Z": [0., 0., 1./2]}

# Triclinic symmetry points with lattice parameters that satisfy

## tri1a ##
# k_alpha > pi/2
# k_beta > pi/2
# k_gamma > pi/2 where k_gamma = min(k_alpha, k_beta, k_gamma)

## tri2a ##
# k_alpha > pi/2
# k_beta > pi/2
# k_gamma = pi/2
tri1a2a_sympts = {"$\Gamma$": [0., 0., 0.],
                  "L": [1./2, 1./2, 0.],
                  "M": [0., 1./2, 1./2],
                  "N": [1./2, 0., 1./2],
                  "R": [1./2, 1./2, 1./2],
                  "X": [1./2, 0., 0.],
                  "Y": [0., 1./2, 0.],
                  "Z": [0., 0., 1./2]}

# Triclinic symmatry points with lattice parameters that satisfy

## tri1b ##
# k_alpha < pi/2
# k_beta < pi/2
# k_gamma < pi/2 where k_gamma = max(k_alpha, k_beta, k_gamma)

## tri2b ##
# k_alpha < pi/2
# k_beta < pi/2
# k_gamma = pi/2
tr1b2b_sympts = {"$\Gamma$": [0., 0., 0.],
                 "L": [1./2, -1./2, 0.],
                 "M": [0., 0., 1./2],
                 "N": [-1./2, -1./2, 1./2],
                 "R": [0., -1./2, 1./2],
                 "X": [0., -1./2, 0.],
                 "Y": [1./2, 0., 0.],
                 "Z": [-1./2, 0., 1./2]}

def get_sympts(centering_type, lattice_constants, lattice_angles,
               convention="ordinary"):
    """Find the symmetry points for the provided lattice.

    Args:
        centering_type (str): the centering type for the lattice. Vaild
            options include 'prim', 'base', 'body', and 'face'.
        lattice_constants (list): a list of lattice constants [a, b, c].
        lattice_angles (list): a list of lattice angles [alpha, beta, gamma].
        convention (str): indicates the convention used in defining the reciprocal
            lattice vectors. Options include 'ordinary' and 'angular'.

    Returns:
        (dict): a dictionary with a string of letters as the keys and lattice 
            coordinates of the symmetry points ase values.

    Example:
        >>> lattice_constants = [4.05]*3
        >>> lattice_angles = [numpy.pi/2]*3
        >>> symmetry_points = get_sympts(lattice_constants, lattice_angles)
    """
    
    a = float(lattice_constants[0])
    b = float(lattice_constants[1])
    c = float(lattice_constants[2])
    
    alpha = float(lattice_angles[0])
    beta = float(lattice_angles[1])
    gamma = float(lattice_angles[2])
    
    lattice_vectors = make_ptvecs(centering_type, lattice_constants,
                                  lattice_angles)
    reciprocal_lattice_vectors = make_rptvecs(lattice_vectors, convention=convention)
    
    rlat_veca = reciprocal_lattice_vectors[:,0] # individual reciprocal lattice vectors
    rlat_vecb = reciprocal_lattice_vectors[:,1]
    rlat_vecc = reciprocal_lattice_vectors[:,2]
    
    ka = norm(rlat_veca) # lengths of primitive reciprocal lattice vectors
    kb = norm(rlat_vecb)
    kc = norm(rlat_vecc)

    # These are the angles between reciprocal lattice vectors.
    kalpha = np.arccos(np.dot(rlat_vecb, rlat_vecc)/(kb*kc))
    kbeta = np.arccos(np.dot(rlat_veca, rlat_vecc)/(ka*kc))
    kgamma = np.arccos(np.dot(rlat_veca, rlat_vecb)/(ka*kb))
    
    # Start with the cubic lattices, which have all angles equal to pi/2 radians.
    if (np.isclose(alpha, np.pi/2) and
        np.isclose(beta, np.pi/2) and
        np.isclose(gamma, np.pi/2)):
        if (np.isclose(a, b) and
            np.isclose(b, c)):
            if centering_type == "prim":
                return sc_sympts
            elif centering_type == "body":
                return bcc_sympts
            elif centering_type == "face":
                return fcc_sympts
            else:
                msg = ("Valid lattice centerings for cubic latices include "
                       "'prim', 'body', and 'face'.")
                raise ValueError(msg.format(centering_type))
            
        # Tetragonal.
        elif (np.isclose(a,b) and not np.isclose(b,c)):
            if centering_type == "prim":
                return tet_sympts
            elif centering_type == "body":
                if c < a:
                    return bct1_sympts(a, c)
                else:
                    return bct2_sympts(a, c)
            else:
                msg = ("Valid lattice centerings for tetragonal lattices "
                       "include 'prim' and 'body'.")
                raise ValueError(msg.format(centering_type))
            
        # Last of the lattices with all angles equal to pi/2 is orthorhombic.
        else:
            if centering_type == "prim":
                return orc_sympts
            
            elif centering_type == "base":
                return orcc_sympts(a, b)
            
            elif centering_type == "body":
                return orci_sympts(a, b, c)
            
            elif centering_type == "face":
                if  (1/a**2 >= 1/b**2 +1/c**2):
                    return orcf13_sympts(a, b, c)
                else:
                    return orcf2_sympts(a, b, c)
                
            else:
                msg = ("Valid lattice centerings for orthorhombic lattices "
                       "include 'prim', 'base', 'body', and 'face'.")
                raise ValueError(msg.format(centering_type))
            
    # Hexagonal has alpha = beta = pi/2, gamma = 2pi/3, a = b != c.
    if (np.isclose(alpha, beta) and np.isclose(beta, np.pi/2) and
        np.isclose(gamma, 2*np.pi/3) and np.isclose(a, b) and not
        np.isclose(b, c)):
        return hex_sympts

    # Rhombohedral has equal angles and constants.
    elif (np.isclose(alpha, beta) and np.isclose(beta, gamma) and 
          np.isclose(a, b) and np.isclose(b, c)):
            if alpha < np.pi/2:
                return rhl1_sympts(alpha)
            else:
                return rhl2_sympts(alpha)

    # Monoclinic a,b <= c, alpha < pi/2, beta = gamma = pi/2, a != b != c
    elif (not (a > c or b > c) and np.isclose(beta, gamma) and
          np.isclose(beta, np.pi/2) and alpha < np.pi/2):
        if centering_type == "prim":
            return mcl_sympts(b, c, alpha)
        elif centering_type == "base":
            if kgamma > np.pi/2 or np.isclose(kgamma, np.pi/2):
                return mclc12_sympts(a, b, c, alpha)
            
            elif (kgamma < np.pi/2
                  and ((b*np.cos(alpha)/c + (b*np.sin(alpha)/a)**2) < 1.
                       or np.isclose(b*np.cos(alpha)/c + (b*np.sin(alpha)/a)**2, 1))):
                return mclc34_sympts(a, b, c, alpha)
            
            elif (kgamma < np.pi/2 and
                  (b*np.cos(alpha)/c + (b*np.sin(alpha)/a)**2) > 1.):
                return mclc5_sympts(a, b, c, alpha)
            
            else:
                msg = "Something is wrong with the monoclinic lattice provided."
                raise ValueError(msg.format(reciprocal_lattice_vectors))
        else:
            msg = ("Valid lattice centerings for monoclinic lattices "
                   "include 'prim' and 'base'")
            raise ValueError(msg.format(centering_type))
        
    # Triclinic a != b != c, alpha != beta != gamma
    elif not (np.isclose(a,b) and np.isclose(b,c) and np.isclose(alpha,beta) and
              np.isclose(beta, gamma)):
        if ((kalpha > np.pi/2 and kbeta > np.pi/2 and kgamma > np.pi/2) or
            (kalpha > np.pi/2 and kbeta > np.pi/2 and np.isclose(kgamma, np.pi/2))):
            return tri1a2a_sympts
        elif ((kalpha < np.pi/2 and kbeta < np.pi/2 and kgamma < np.pi/2) or
              (kalpha < np.pi/2 and kbeta < np.pi/2 and np.isclose(kgamma, np.pi/2))):
            return tr1b2b_sympts
        else:
            msg = "Something is wrong with the triclinic lattice provided."
            raise ValueError(msg.format(reciprocal_lattice_vectors))
    else:
        msg = ("The lattice parameters provided don't correspond to a valid "
               "3D Bravais lattice.")
        raise ValueError(msg.format())
    
def get_sympaths(centering_type, lattice_constants, lattice_angles,
                 convention="ordinary"):
    """Find the symmetry paths for the provided lattice.

    Args:
        centering_type (str): the centering type for the lattice. Vaild
            options include 'prim', 'base', 'body', and 'face'.
        lattice_constants (list): a list of lattice constants [a, b, c].
        lattice_angles (list): a list of lattice angles [alpha, beta, gamma].
        convention (str): indicates the convention used in defining the reciprocal
            lattice vectors. Options include 'ordinary' and 'angular'.

    Returns:
        (dict): a dictionary with a string of letters as the keys and lattice 
            coordinates of the symmetry points as values.

    Example:
        >>> lattice_constants = [4.05]*3
        >>> lattice_angles = [numpy.pi/2]*3
        >>> symmetry_points = get_sympts(lattice_constants, lattice_angles)
    """
        
    a = float(lattice_constants[0])
    b = float(lattice_constants[1])
    c = float(lattice_constants[2])
    
    alpha = float(lattice_angles[0])
    beta = float(lattice_angles[1])
    gamma = float(lattice_angles[2])
    
    lattice_vectors = make_ptvecs(centering_type, lattice_constants,
                                  lattice_angles)
    reciprocal_lattice_vectors = make_rptvecs(lattice_vectors, convention=convention)
    
    rlat_veca = reciprocal_lattice_vectors[:,0] # individual reciprocal lattice vectors
    rlat_vecb = reciprocal_lattice_vectors[:,1]
    rlat_vecc = reciprocal_lattice_vectors[:,2]
    
    ka = norm(rlat_veca) # lengths of primitive reciprocal lattice vectors
    kb = norm(rlat_vecb)
    kc = norm(rlat_vecc)

    # These are the angles between reciprocal lattice vectors.
    kalpha = np.arccos(np.dot(rlat_vecb, rlat_vecc)/(kb*kc))
    kbeta = np.arccos(np.dot(rlat_veca, rlat_vecc)/(ka*kc))
    kgamma = np.arccos(np.dot(rlat_veca, rlat_vecb)/(ka*kb))

    # Start with the cubic lattices, which have all angles equal to pi/2 radians.
    if (np.isclose(alpha, np.pi/2) and
        np.isclose(beta, np.pi/2) and
        np.isclose(gamma, np.pi/2)):
        if (np.isclose(a, b) and
            np.isclose(b, c)):
            if centering_type == "prim":
                return [["$\Gamma$", "X"], ["X", "M"], ["M", "$\Gamma$"], ["$\Gamma$", "R"],
                        ["R", "X"], ["M", "R"]]
            elif centering_type == "body":
                return [["$\Gamma$", "H"], ["H", "N"], ["N", "$\Gamma$"], ["$\Gamma$", "P"],
                        ["P", "H"], ["P", "N"]]
            elif centering_type == "face":
                return [["$\Gamma$", "X"], ["X", "W"], ["W", "K"], ["K", "$\Gamma$"],
                        ["$\Gamma$", "L"], ["L", "U"], ["U", "W"], ["W", "L"],
                        ["L", "K"], ["U", "X"]]
            else:
                msg = ("Valid lattice centerings for cubic latices include "
                       "'prim', 'body', and 'face'.")
                raise ValueError(msg.format(centering_type))
            
        # Tetragonal.
        elif (np.isclose(a,b) and not np.isclose(b,c)):
            if centering_type == "prim":
                return [["$\Gamma$", "X"], ["X", "M"], ["M", "$\Gamma$"], ["$\Gamma$", "Z"],
                        ["Z", "R"], ["R", "A"], ["A", "Z"], ["X", "R"],
                        ["M", "A"]]
            elif centering_type == "body":
                if c < a:
                    return [["$\Gamma$", "X"], ["X", "M"], ["M", "$\Gamma$"], ["$\Gamma$", "Z"],
                            ["Z", "P"], ["P", "N"], ["N", "Z1"], ["Z1", "M"],
                            ["X", "P"]]
                else:
                    return [["$\Gamma$", "X"], ["X", "Y"], ["Y", "S"], ["S", "$\Gamma$"],
                            ["$\Gamma$", "Z"], ["Z", "S1"], ["S1", "N"], ["N", "P"],
                            ["P", "Y1"], ["Y1", "Z"], ["X", "P"]]
            else:
                msg = ("Valid lattice centerings for tetragonal lattices "
                       "include 'prim' and 'body'.")
                raise ValueError(msg.format(centering_type))
            
        # Last of the lattices with all angles equal to pi/2 is orthorhombic.
        else:
            if centering_type == "prim": # orc
                return [["$\Gamma$", "X"], ["X", "S"], ["S", "Y"], ["Y", "$\Gamma$"],
                        ["$\Gamma$", "Z"], ["Z", "U"], ["U", "R"], ["R", "T"],
                        ["T", "Z"], ["Y", "T"], ["U", "X"], ["S", "R"]]
            elif centering_type == "base": # orcc
                return [["$\Gamma$", "X"], ["X", "S"], ["S", "R"], ["R", "A"],
                        ["A", "Z"], ["Z", "$\Gamma$"], ["$\Gamma$", "Y"], ["Y", "X1"],
                        ["X1", "A1"], ["A1", "T"], ["T", "Y"], ["Z", "T"]]
            elif centering_type == "body": # orci
                return [["$\Gamma$", "X"], ["X", "L"], ["L", "T"], ["T", "W"],
                        ["W", "R"], ["R", "X1"], ["X1", "Z"], ["Z", "$\Gamma$"],
                        ["$\Gamma$", "Y"], ["Y", "S"], ["S", "W"], ["L1", "Y"],
                        ["Y1", "Z"]]
            elif centering_type == "face":
                if (1/a**2 > 1/b**2 +1/c**2): # orcf1
                    return[["$\Gamma$", "Y"], ["Y", "T"], ["T", "Z"], ["Z", "$\Gamma$"],
                           ["$\Gamma$", "X"], ["X", "A1"], ["A1", "Y"], ["T", "X1"],
                           ["X", "A"], ["A", "Z"], ["L", "$\Gamma$"]]
                elif np.isclose(1/a**2, 1/b**2 +1/c**2): # orcf3
                    return [["$\Gamma$", "Y"], ["Y", "T"], ["T", "Z"], ["Z", "$\Gamma$"],
                            ["$\Gamma$", "X"], ["X", "A1"], ["A1", "Y"], ["X", "A"],
                            ["A", "Z"], ["L", "$\Gamma$"]]                    
                else: #orcf2
                    return [["$\Gamma$", "Y"], ["Y", "C"], ["C", "D"], ["D", "X"],
                            ["X", "$\Gamma$"], ["$\Gamma$", "Z"], ["Z", "D1"], ["D1", "H"],
                            ["H", "C"], ["C1", "Z"], ["X", "H1"], ["H", "Y"],
                            ["L", "$\Gamma$"]]            
            else:
                msg = ("Valid lattice centerings for orthorhombic lattices "
                       "include 'prim', 'base', 'body', and 'face'.")
                raise ValueError(msg.format(centering_type))
            
    # Hexagonal has alpha = beta = pi/2, gamma = 2pi/3, a = b != c.
    if (np.isclose(alpha, beta) and np.isclose(beta, np.pi/2) and
        np.isclose(gamma, 2*np.pi/3) and np.isclose(a, b) and not
        np.isclose(b, c)):
        return [["$\Gamma$", "M"], ["M", "K"], ["K", "$\Gamma$"], ["$\Gamma$", "A"], ["A", "L"],
                ["L", "H"], ["H", "A"], ["L", "M"], ["K", "H"]]

    # Rhombohedral has equal angles and constants.
    elif (np.isclose(alpha, beta) and np.isclose(beta, gamma) and 
          np.isclose(a, b) and np.isclose(b, c)):
            if alpha < np.pi/2: # RHL1
                return [["$\Gamma$", "L"], ["L", "B1"], ["B", "Z"], ["Z", "$\Gamma$"],
                        ["$\Gamma$", "X"], ["Q", "F"], ["F", "P1"], ["P1", "Z"],
                        ["L", "P"]]
            else: #RHL2
                return [["$\Gamma$", "P"], ["P", "Z"], ["Z", "Q"], ["Q", "$\Gamma$"],
                        ["$\Gamma$", "F"], ["F", "P1"], ["P1", "Q1"], ["Q1", "L"],
                        ["L", "Z"]]

    # Monoclinic a,b <= c, alpha < pi/2, beta = gamma = pi/2, a != b != c
    elif (not (a > c or b > c) and np.isclose(beta, gamma) and
          np.isclose(beta, np.pi/2) and alpha < np.pi/2):
        if centering_type == "prim":
            return [["$\Gamma$", "Y"], ["Y", "H"], ["H", "C"], ["C", "E"],
                    ["E", "M1"], ["M1", "A"], ["A", "X"], ["X", "H1"],
                    ["M", "D"], ["D", "Z"], ["Y", "D"]]
        elif centering_type == "base": # MCLC1
            if np.isclose(kgamma, np.pi/2): # MCLC2
                return [["$\Gamma$", "Y"], ["Y", "F"], ["F", "L"], ["L", "I"],
                        ["I1", "Z"], ["Z", "F1"], ["N", "$\Gamma$"], ["$\Gamma$", "M"]]        
            elif kgamma > np.pi/2:
                return [["$\Gamma$", "Y"], ["Y", "F"], ["F", "L"], ["L", "I"],
                        ["I1", "Z"], ["Z", "F1"], ["Y", "X1"], ["X", "$\Gamma$"],
                        ["$\Gamma$", "N"], ["M", "$\Gamma$"]]
            elif (kgamma < np.pi/2 # MCLC3
                  and ((b*np.cos(alpha)/c + (b*np.sin(alpha)/a)**2) < 1)):
                return [["$\Gamma$", "Y"], ["Y", "F"], ["F", "H"], ["H", "Z"],
                        ["Z", "I"], ["I", "F1"], ["H1", "Y1"], ["Y1", "X"],
                        ["X", "$\Gamma$"], ["$\Gamma$", "N"], ["M", "$\Gamma$"]]
            elif (kgamma < np.pi/2 and # MCLC4
                  np.isclose(b*np.cos(alpha)/c + (b*np.sin(alpha)/a)**2, 1)):
                return [["$\Gamma$", "Y"], ["Y", "F"], ["F", "H"], ["H", "Z"], 
                        ["Z", "I"], ["H1", "Y1"], ["Y1", "X"], ["X", "$\Gamma$"],
                        ["$\Gamma$", "N"], ["M", "$\Gamma$"]]
            elif (kgamma < np.pi/2 and # MCLC5
                  (b*np.cos(alpha)/c + (b*np.sin(alpha)/a)**2) > 1.):
                return [["$\Gamma$", "Y"], ["Y", "F"], ["F", "L"], ["L", "I"],
                        ["I1", "Z"], ["Z", "H"], ["H", "F1"], ["H1", "Y1"],
                        ["Y1", "X"], ["X", "$\Gamma$"], ["$\Gamma$", "N"], ["M", "$\Gamma$"]]
            else:
                msg = "Something is wrong with the monoclinic lattice provided."
                raise ValueError(msg.format(reciprocal_lattice_vectors))
        else:
            msg = ("Valid lattice centerings for monoclinic lattices "
                   "include 'prim' and 'base'")
            raise ValueError(msg.format(centering_type))
        
    # Triclinic a != b != c, alpha != beta != gamma
    elif not (np.isclose(a,b) and np.isclose(b,c) and np.isclose(a,c) and 
              np.isclose(alpha,beta) and np.isclose(beta, gamma) and
              np.isclose(alpha, gamma)):
        kangles = np.sort([kalpha, kbeta, kgamma])
        if kangles[0] > np.pi/2: # TRI1a
            return [["X", "$\Gamma$"], ["$\Gamma$", "Y"], ["L", "$\Gamma$"], ["$\Gamma$", "Z"], ["N", "$\Gamma$"],
                    ["$\Gamma$", "M"], ["R", "$\Gamma$"]]
        elif kangles[2] < np.pi/2: #TRI1b
            return [["X", "$\Gamma$"], ["$\Gamma$", "Y"], ["L", "$\Gamma$"], ["$\Gamma$", "Z"],
                    ["N", "$\Gamma$"], ["$\Gamma$", "M"], ["R", "$\Gamma$"]]
        elif (np.isclose(kangles[0], np.pi/2) and (kangles[1] > np.pi/2) and
              (kangles[2] > np.pi/2)): #TRI2a
            return [["X", "$\Gamma$"], ["$\Gamma$", "Y"], ["L", "$\Gamma$"], ["$\Gamma$", "Z"], ["N", "$\Gamma$"],
                    ["$\Gamma$", "M"], ["R", "$\Gamma$"]]
        elif (np.isclose(kangles[2], np.pi/2) and (kangles[0] < np.pi/2) and
              (kangles[1] < np.pi/2)): #TRI2b
            return [["X", "$\Gamma$"], ["$\Gamma$", "Y"], ["L", "$\Gamma$"], ["$\Gamma$", "Z"],
                    ["N", "$\Gamma$"], ["$\Gamma$", "M"], ["R", "$\Gamma$"]]
        else:
            msg = "Something is wrong with the triclinic lattice provided."
            raise ValueError(msg.format(reciprocal_lattice_vectors))
    else:
        msg = ("The lattice parameters provided don't correspond to a valid "
               "3D Bravais lattice.")
        raise ValueError(msg.format())
    
def make_ptvecs(center_type, lat_consts, lat_angles):
    """Provided the center type, lattice constants and angles of the conventional unit
    cell, return the primitive translation vectors.
    
    Args:
        center_type (str): identifies the location of the atoms in the cell.
        lat_consts (float or int): the characteristic spacing of atoms in the
            material with 'a' first, 'b' second, and 'c' third in the list. These
            are typically ordered such that a < b < c.
        angles (list): a list of angles between the primitive translation vectors,
            in radians, with 'alpha' the first entry, 'beta' the second, and 'gamma' the
            third in the list.

    Returns:
        lattice_vectors (numpy.ndarray): returns the primitive translation vectors as
            the columns of a matrix.

    Example:
        >>> center_type = "prim"
        >>> lat_consts = [1.2]*3
        >>> angles = [np.pi/2]*3
        >>> vectors = make_ptvecs(lattice_type, lat_consts, angles)
    """

    if type(lat_consts) not in (list, np.ndarray):
        raise ValueError("The lattice constants must be in a list or numpy "
                         "array.")
    if type(lat_angles) not in (list, np.ndarray):
        raise ValueError("The lattice angles must be in a list or numpy array.")

    if (np.sum(np.sort(lat_angles)[:2]) < max(lat_angles) or
        np.isclose(np.sum(np.sort(lat_angles)[:2]), max(lat_angles))):
        msg = ("The sum of the two smallest lattice angles must be greater than "
               "the largest lattice angle for the lattice vectors to be "
               "linearly independent.")
        raise ValueError(msg.format(lat_angles))

    # Extract the angles
    alpha = float(lat_angles[0])
    beta = float(lat_angles[1])
    gamma = float(lat_angles[2])

    if (np.isclose(alpha, beta) and np.isclose(beta, gamma) and
        np.isclose(beta, 2*np.pi/3)):
        msg = ("The lattice vectors are linearly dependent with all angles "
               "equal to 2pi/3.")
        raise ValueError(msg.format(lat_angles))
    
    # Extract the lattice constants for the conventional lattice.
    a = float(lat_consts[0])
    b = float(lat_consts[1])
    c = float(lat_consts[2])
    
    # avec is chosen to lie along the x-direction.
    avec = np.array([a, 0., 0.])
    # bvec is chosen to lie in the xy-plane.
    bvec = np.array([b*np.cos(gamma), b*np.sin(gamma), 0])
    # I had to round the argument of the sqrt function in order to avoid
    # numerical errors in cvec.
    cvec = np.array([c*np.cos(beta),
                c/np.sin(gamma)*(np.cos(alpha) -
                                 np.cos(beta)*np.cos(gamma)),
                np.sqrt(np.round(c**2 - (c*np.cos(beta))**2 -
                                 (c/np.sin(gamma)*(np.cos(alpha) -
                                                   np.cos(beta)*np.cos(gamma)))**2, 15))])
    
    if center_type == "prim":
        # I have to take care that a hexagonal grid is rotated 60 degrees so
        # it matches what was obtained in Stefano's paper.
        if ((np.isclose(a, b) and not np.isclose(b,c)) and
            np.isclose(alpha, beta) and np.isclose(beta, np.pi/2) and
            np.isclose(gamma, 2*np.pi/3)):
            rotate = [[np.cos(gamma/2), np.sin(gamma/2), 0],
                        [-np.sin(gamma/2), np.cos(gamma/2), 0],
                        [0, 0, 1]]
            av = np.dot(rotate, avec)
            bv = np.dot(rotate, bvec)
            cv = np.dot(rotate, cvec)
            pt_vecs = np.transpose(np.array([av, bv, cv], dtype=float))
            return pt_vecs
        
        # The rhombohedral lattice vectors also need to be rotated to match
        # those of Stefano.
        elif (np.isclose(alpha, beta) and np.isclose(beta, gamma) and
              not np.isclose(beta, np.pi/2) and np.isclose(a, b) and
              np.isclose(b,c)):
            
            # The vectors in Stefano's paper are mine rotated 60 degrees.
            rotate = [[np.cos(gamma/2), np.sin(gamma/2), 0],
                      [-np.sin(gamma/2), np.cos(gamma/2), 0],
                      [0, 0, 1]]
            av = np.dot(rotate, avec)
            bv = np.dot(rotate, bvec)
            cv = np.dot(rotate, cvec)
            pt_vecs = np.transpose(np.array([av, bv, cv], dtype=float))
            return pt_vecs
        else:
            pt_vecs = np.transpose(np.array([avec, bvec, cvec], dtype=float))
            return pt_vecs
    
    elif center_type == "base":
        av = .5*(avec - bvec)
        bv = .5*(avec + bvec)
        cv = cvec
        
        # The vectors defined in Stefano's paper are defined
        # differently for base-centered, monoclinic lattices.
        if (alpha < np.pi/2 and np.isclose(beta, np.pi/2)
            and np.isclose(gamma, np.pi/2) and a <= c and b <= c
            and not (np.isclose(a,b) or np.isclose(b,c) or np.isclose(a,c))):            
            av = .5*(avec + bvec)
            bv = .5*(-avec + bvec)
            cv = cvec
        pt_vecs  = np.transpose(np.array([av, bv, cv], dtype=float))
        return pt_vecs
        
    elif (not (a > c or b > c) and np.isclose(beta, gamma) and
          np.isclose(beta, np.pi/2) and alpha < np.pi/2):
        av = .5*(avec + bvec)
        bv = .5*(-avec + bvec)
        cv = cvec
        pt_vecs  = np.transpose(np.array([av, bv, cv], dtype=float))
        return pt_vecs
    
    elif center_type == "body":
        av = .5*(-avec + bvec + cvec)
        bv = .5*(avec - bvec + cvec)
        cv = .5*(avec + bvec - cvec)
        pt_vecs = np.transpose(np.array([av, bv, cv], dtype=float))
        return pt_vecs

    elif center_type == "face":
        av = .5*(bvec + cvec)
        bv = .5*(avec + cvec)
        cv = .5*(avec + bvec)
        pt_vecs = np.transpose(np.array([av, bv, cv], dtype=float))
        return pt_vecs
    
    else:
        msg = "Please provide a valid centering type."
        raise ValueError(msg.format(center_type))


def make_rptvecs(A, convention="ordinary"):
    """Return the reciprocal primitive translation vectors of the provided
    vectors.

    Args:
        A (list or numpy.ndarray): the primitive translation vectors in real space 
            as the columns of a nested list or numpy array.
        convention (str): gives the convention that defines the reciprocal lattice vectors.
            This is really the difference between using ordinary frequency and angular
            frequency, and whether the transformation between real and reciprocal space is
            unitary.
    Return:
        B (numpy.ndarray): return the primitive translation vectors in 
            reciprocal space as the columns of a matrix.    
    """
    if convention == "ordinary":
        return np.transpose(np.linalg.inv(A))
    elif convention == "angular":
        return np.transpose(np.linalg.inv(A))*2*np.pi
    else:
        msg = "The two allowed conventions are 'ordinary' and 'angular'."
        raise ValueError(msg.format(convention))


def make_lattice_vectors(lattice_type, lattice_constants, lattice_angles):
    """Create the vectors that generate a lattice.

    Args:
        lattice_type (str): the lattice type.
        lattice_constants (list or numpy.ndarray): the axial lengths of the
            conventional lattice vectors.
        lattice_angles (list or numpy.ndarray): the interaxial angles of the
            conventional lattice vectors.

    Returns:
        lattice_vectors (numpy.ndarray): the vectors that generate the lattice
            as columns of an array [a1, a2, a3] where a1, a2, and a3 are column
            vectors.

    Example:
        >>> lattice_type = "face-centered cubic"
        >>> lattice_constants = [1]*3
        >>> lattice_angles = [numpy.pi/2]*3
        >>> lattice_vectors = make_lattice_vectors(lattice_type, 
                                                   lattice_constants, 
                                                   lattice_angles)
    """
    
    # Extract parameters.
    a = float(lattice_constants[0])
    b = float(lattice_constants[1])
    c = float(lattice_constants[2])
    alpha = float(lattice_angles[0])
    beta = float(lattice_angles[1])
    gamma = float(lattice_angles[2])
    
    if lattice_type == "simple cubic":
        if not ((np.isclose(a, b) and np.isclose(b, c))):
            msg = ("The lattice constants should all be the same for a simple-"
                    "cubic lattice")
            raise ValueError(msg.format(lattice_constants))
        
        if not (np.isclose(alpha, np.pi/2) and np.isclose(beta, np.pi/2)
                and np.isclose(gamma, np.pi/2)):
            msg = ("The lattice angles should all be the same and equal to pi/2"
                    " for a simple-cubic lattice.")
            raise ValueError(msg.format(lattice_angles))
        
        a1 = [a, 0, 0]
        a2 = [0, a, 0]
        a3 = [0, 0, a]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors
    
    elif lattice_type == "face-centered cubic":
        if not ((np.isclose(a, b) and np.isclose(b, c))):
            msg = ("The lattice constants should all be the same for a face-"
                   "centered, cubic lattice.")
            raise ValueError(msg.format(lattice_constants))
        if not (np.isclose(alpha, np.pi/2) and np.isclose(beta, np.pi/2)
                and np.isclose(gamma, np.pi/2)):
            msg = ("The lattice angles should all be the same and equal to pi/2"
                   " for a face-centered, cubic lattice.")
            raise ValueError(msg.format(lattice_angles))

        a1 = [  0, a/2, a/2]
        a2 = [a/2,   0, a/2]
        a3 = [a/2, a/2,   0]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors
    
    elif lattice_type == "body-centered cubic":
        if not ((np.isclose(a, b) and np.isclose(b, c))):
            msg = ("The lattice constants should all be the same for a body-"
                   "centered, cubic lattice.")
            raise ValueError(msg.format(lattice_constants))

        if not (np.isclose(alpha, np.pi/2) and np.isclose(beta, np.pi/2)
                and np.isclose(gamma, np.pi/2)):
            msg = ("The lattice angles should all be the same and equal to pi/2"
                   " for a body-centered, cubic lattice.")
            raise ValueError(msg.format(lattice_angles))
        
        a1 = [-a/2,  a/2,  a/2]
        a2 = [ a/2, -a/2,  a/2]
        a3 = [ a/2,  a/2, -a/2]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors
    
    elif lattice_type == "tetragonal":
        if not (np.isclose(a, b) and
                not np.isclose(b, c)):
            msg = ("For tetragonal lattice, a = b != c where a, b, and c are "
                   "the first, second, and third entries in lattice_constants, "
                   "respectively.")
            raise ValueError(msg.format(lattice_constants))
        if not (np.isclose(alpha, np.pi/2) and np.isclose(beta, np.pi/2)
                and np.isclose(gamma, np.pi/2)):
            msg = ("The lattice angles should all be the same and equal to pi/2"
                   " for a tetragonal lattice.")
            raise ValueError(msg.format(lattice_angles))
        
        a1 = [a, 0, 0]
        a2 = [0, a, 0]
        a3 = [0, 0, c]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors
    
    elif lattice_type == "body-centered tetragonal":
        if not (np.isclose(a, b) and
                not np.isclose(b, c)):
            msg = ("For a body-centered, tetragonal lattice, a = b != c where "
                   "a, b, and c are the first, second, and third entries in "
                   "lattice_constants, respectively.")
            raise ValueError(msg.format(lattice_constants))
        if not (np.isclose(alpha, np.pi/2) and np.isclose(beta, np.pi/2)
                and np.isclose(gamma, np.pi/2)):
            msg = ("The lattice angles should all be the same and equal to pi/2"
                   " for a body-centered, tetragonal lattice.")
            raise ValueError(msg.format(lattice_angles))

        a1 = [-a/2,  a/2,  c/2]
        a2 = [ a/2, -a/2,  c/2]
        a3 = [ a/2,  a/2, -c/2]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors

    elif lattice_type == "orthorhombic":
        if (np.isclose(a, b) or np.isclose(b, c) or np.isclose(a, c)):
            msg = ("The lattice constants should all be different for an "
                   "orthorhombic lattice.")
            raise ValueError(msg.format(lattice_constants))
        if not (np.isclose(alpha, np.pi/2) and np.isclose(beta, np.pi/2)
                and np.isclose(gamma, np.pi/2)):
            msg = ("The lattice angles should all be the same and equal to pi/2 "
                   "for an orthorhombic lattice.")
            raise ValueError(msg.format(lattice_angles))
        if (b < a) or (c < b):
            msg = ("The lattice constants should in ascending order for an "
                   "orthorhombic lattice.")
            raise ValueError(msg.format(lattice_constants))

        a1 = [a, 0, 0]
        a2 = [0, b, 0]
        a3 = [0, 0, c]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors

    elif lattice_type == "face-centered orthorhombic":
        if (np.isclose(a, b) or np.isclose(b, c) or np.isclose(a, c)):
            msg = ("The lattice constants should all be different for a "
                   "face-centered, orthorhombic lattice.")
            raise ValueError(msg.format(lattice_constants))
        if not (np.isclose(alpha, np.pi/2) and np.isclose(beta, np.pi/2)
                and np.isclose(gamma, np.pi/2)):
            msg = ("The lattice angles should all be the same and equal to pi/2"
                   " for a face-centered, orthorhombic lattice.")
            raise ValueError(msg.format(lattice_angles))
        if not (a < b < c):
            msg = ("The lattice constants should in ascending order for a ."
                   "face-centered, orthorhombic lattice.")
            raise ValueError(msg.format(lattice_constants))

        a1 = [  0, b/2, c/2]
        a2 = [a/2,   0, c/2]
        a3 = [a/2, b/2,   0]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors

    elif lattice_type == "body-centered orthorhombic":
        if (np.isclose(a, b) or np.isclose(b, c) or np.isclose(a, c)):
            msg = ("The lattice constants should all be different for a "
                   "body-centered, orthorhombic lattice.")
            raise ValueError(msg.format(lattice_constants))
        if not (np.isclose(alpha, np.pi/2) and np.isclose(beta, np.pi/2)
                and np.isclose(gamma, np.pi/2)):
            msg = ("The lattice angles should all be the same and equal to pi/2"
                   " for a body-centered, orthorhombic lattice.")
            raise ValueError(msg.format(lattice_angles))
        if not (a < b < c):
            msg = ("The lattice constants should in ascending order for a ."
                   "body-centered, orthorhombic lattice.")
            raise ValueError(msg.format(lattice_constants))

        a1 = [-a/2,  b/2,  c/2]
        a2 = [ a/2, -b/2,  c/2]
        a3 = [ a/2,  b/2, -c/2]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors
 
    elif lattice_type == "base-centered orthorhombic":
        if (np.isclose(a, b) or np.isclose(b, c) or np.isclose(a, c)):
            msg = ("The lattice constants should all be different for a "
                   "base-centered, orthorhombic lattice.")
            raise ValueError(msg.format(lattice_constants))
        if not (np.isclose(alpha, np.pi/2) and np.isclose(beta, np.pi/2)
                and np.isclose(gamma, np.pi/2)):
            msg = ("The lattice angles should all be the same and equal to pi/2"
                   " for a base-centered, orthorhombic lattice.")
            raise ValueError(msg.format(lattice_angles))
        if not (a < b < c):
            msg = ("The lattice constants should in ascending order for a ."
                   "base-centered, orthorhombic lattice.")
            raise ValueError(msg.format(lattice_constants))

        a1 = [a/2, -b/2, 0]
        a2 = [a/2,  b/2, 0]
        a3 = [  0,    0, c]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors

    elif lattice_type == "hexagonal":
        if not (np.isclose(a, b) and
                not np.isclose(b, c)):
            msg = ("For a hexagonal lattice, a = b != c where "
                   "a, b, and c are the first, second, and third entries in "
                   "lattice_constants, respectively.")
            raise ValueError(msg.format(lattice_constants))
        if not (np.isclose(alpha, beta) and np.isclose(beta, np.pi/2) and
                np.isclose(gamma, 2*np.pi/3)):
            msg = ("The first two lattice angles, alpha and beta, should be the "
                   "same and equal to pi/2 while the third gamma should be "
                   "2pi/3 radians for a hexagonal lattice.")
            raise ValueError(msg.format(lattice_angles))
        
        a1 = [a/2, -a*np.sqrt(3)/2, 0]
        a2 = [a/2, a*np.sqrt(3)/2, 0]
        a3 = [0, 0, c]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors

    elif lattice_type == "rhombohedral":
        if not (np.isclose(a, b) and np.isclose(b,c) and np.isclose(a, c)):
            msg = ("For a rhombohedral lattice, a = b = c where "
                   "a, b, and c are the first, second, and third entries in "
                   "lattice_constants, respectively.")
            raise ValueError(msg.format(lattice_constants))
        if not (np.isclose(alpha, beta) and np.isclose(beta, gamma) and
                np.isclose(alpha, gamma)):
            msg = ("All lattice angles should be the same for a rhombohedral "
                   "lattice.")
            raise ValueError(msg.format(lattice_angles))
        if (np.isclose(alpha, np.pi/2) or np.isclose(beta, np.pi/2) or
            np.isclose(gamma, np.pi/2)):
            msg = ("No lattice angle should be equal to pi/2 radians for a "
                   "rhombohedral lattice.")
            raise ValueError(msg.format(lattice_angles))
        if (np.isclose(alpha, np.pi/3) or np.isclose(beta, np.pi/3) or
            np.isclose(gamma, np.pi/3)):
            msg = ("No lattice angle should be equal to pi/3 radians for a "
                   "rhombohedral lattice.")
            raise ValueError(msg.format(lattice_angles))
        if (np.isclose(alpha, np.arccos(-1/3)) or np.isclose(beta, np.arccos(-1/3)) or
            np.isclose(gamma, np.arccos(-1/3))):
            msg = ("No lattice angle should be equal to arccos(-1/3) radians for a "
                   "rhombohedral lattice.")
            raise ValueError(msg.format(lattice_angles))                
        if (alpha > 2*np.pi/3):
            msg = ("The lattice angle should be less than 2*pi/3 radians for a "
                   "rhombohedral lattice.")
            raise ValueError(msg.format(lattice_angles))

        a1 = [a*np.cos(alpha/2), -a*np.sin(alpha/2), 0]
        a2 = [a*np.cos(alpha/2),  a*np.sin(alpha/2), 0]
        a3x = a*np.cos(alpha)/abs(np.cos(alpha/2))
        a3 = [a3x, 0, np.sqrt(a**2 - a3x**2)]
        
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors

    elif lattice_type == "monoclinic":
        if (a > c or b > c):
            msg = ("The first and second lattice constants, a and b, should "
                   "both be less than or equal to the last lattice constant, c,"
                   " for a monoclinic lattice.")
            raise ValueError(msg.format(lattice_constants))
        if (np.isclose(a,b) or np.isclose(b,c) or np.isclose(a,c)):
            msg = ("No two lattice constants are the same for a monoclinic "
                   "lattice.")
            raise ValueError(msg.format(lattice_constants))
        if alpha >= np.pi/2:
            msg = ("The first lattice angle, alpha, should be less than pi/2 "
                   "radians for a monoclinic lattice.")
            raise ValueError(msg.format(lattice_angles))
        if not (np.isclose(beta, np.pi/2) and np.isclose(gamma, np.pi/2)):
            msg = ("The second and third lattice angles, beta and gamma, "
                   "should both be pi/2 radians for a monoclinic lattice.")
            raise ValueError(msg.format(lattice_angles))
        
        a1 = [a, 0, 0]
        a2 = [0, b, 0]
        a3 = [0, c*np.cos(alpha), c*np.sin(alpha)]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors

    elif lattice_type == "base-centered monoclinic":
        if (a > c or b > c):
            msg = ("The first and second lattice constants, a and b, should "
                   "both be less than or equal to the last lattice constant c. "
                   " for a monoclinic lattice.")
            raise ValueError(msg.format(lattice_constants))
        if alpha >= np.pi/2:
            msg = ("The first lattice angle, alpha, should be less than pi/2 "
                   "radians for a monoclinic lattice.")
            raise ValueError(msg.format(lattice_angles))
        if not (np.isclose(beta, np.pi/2) and np.isclose(gamma, np.pi/2)):
            msg = ("The second and third lattice angles, beta and gamma, "
                   "should both be pi/2 radians for a monoclinic lattice.")
            raise ValueError(msg.format(lattice_angles))
        
        a1 = [ a/2, b/2, 0]
        a2 = [-a/2, b/2, 0]
        a3 = [0, c*np.cos(alpha), c*np.sin(alpha)]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors
                
    elif lattice_type == "triclinic":
        if (np.isclose(a, b) or np.isclose(b, c) or np.isclose(a, c)):
            msg = ("The lattice constants should all be different for a "
                   "triclinic lattice.")
            raise ValueError(msg.format(lattice_constants))
        if (np.isclose(alpha, beta) or np.isclose(beta, gamma) or
            np.isclose(alpha, gamma)):
            msg = ("The lattice angles should all be different for a "
                   "triclinic lattice.")
            raise ValueError(msg.format(lattice_angles))
        
        a1 = [a, 0, 0]
        a2 = [b*np.cos(gamma), b*np.sin(gamma), 0]
        a3 = [c*np.cos(beta), c/np.sin(gamma)*(np.cos(alpha) -
                                               np.cos(beta)*np.cos(gamma)),
              c/np.sin(gamma)*np.sqrt(np.sin(gamma)**2 - np.cos(alpha)**2 - 
                                       np.cos(beta)**2 + 2*np.cos(alpha)*
                                       np.cos(beta)*np.cos(gamma))]
        lattice_vectors = np.transpose(np.array([a1, a2, a3], dtype=float))
        return lattice_vectors
    else:
        msg = "Please provide a valid lattice type."
        raise ValueError(msg.format(lattice_type))

def sym_path(lattice, npts, cart=False):
    """Create an array of lattice coordinates along the symmetry paths of 
    the lattice.

    Args:
        lattice (:py:obj:`BZI.symmetry.Lattice`): an instance of the Lattice
            class.
        npts (int): the number of points on each symmetry path.
        cart (bool): if true, return the k-points in Cartesian coordinates. The 
            reciprocal lattice vectors will be used in the conversion.
    Return:
        (numpy.array): an array of lattice coordinates along the symmetry
            paths.
    """    
    
    paths = []
    for i,sym_pair in enumerate(lattice.symmetry_paths):
        sym_pti = lattice.symmetry_points[sym_pair[0]]
        sym_ptf = lattice.symmetry_points[sym_pair[1]]

        pxi = sym_pti[0]
        pxf = sym_ptf[0]
        pyi = sym_pti[1]
        pyf = sym_ptf[1]
        pzi = sym_pti[2]
        pzf = sym_ptf[2]
        px = np.linspace(pxi,pxf,npts)
        py = np.linspace(pyi,pyf,npts)
        pz = np.linspace(pzi,pzf,npts)
        ipath = [[px[j],py[j],pz[j]] for j in range(len(px))]
        if i == 0:
            paths += ipath
        else:
            del ipath[-1]
            paths += ipath
    
    if cart:
        return [np.dot(lattice.reciprocal_vectors, k) for k in paths]
    else:
        return paths    


def find_point_group(lat_vecs, eps=1e-9):
    """Return the point group of a lattice.

    Args:
        lat_vecs (numpy.ndarray or list): the vectors as the columns of a matrix.

    Returns
        pg (list): A list of the operators in the point group.
    """
    # _get_lattice_pointGroup has the vectors as rows instead of columns.
    lat_vecs = np.transpose(lat_vecs)
    return get_lattice_pointGroup(lat_vecs, eps)


def find_space_group(lattice_vectors, atom_labels, atomic_basis, coords="Cart", eps=1e-6):
    """Get the point group and fractional translations of a crystal using phonon-
    enumeration's `get_spaceGroup`.

    Args:
        lattice_vectors (list or numpy.ndarray): the lattice vectors, in Cartesian 
            coordinates, as columns of a 3x3 array.
        atom_labels (list): a list of atoms labels. Each label should be distince for each
            atomic species. The labels must start at zero and should be in the same order 
            as atomic basis.
        atomic_basis (list or numpy.ndarray): a list of atomic positions in Cartesian 
            (default) or lattice coordinates.
        coords (bool): specifies the coordinate system of the atomic basis.
        eps (float): finite precision parameter.

    Returns:
        point_group (list): a list of point group operations.
        translations (list): a list of translations
    """

    if coords == "Cart":
        point_group, translations = get_spaceGroup(np.transpose(lattice_vectors),
                                                   atom_labels, atomic_basis,
                                                   lattcoords=False, eps=1e-6)
    else:
        point_group, translations = get_spaceGroup(np.transpose(lattice_vectors),
                                                   atom_labels, atomic_basis,
                                                   lattcoords=True, eps=1e-6)
    return point_group, translations


def shells(vector, lat_vecs):
    """Find the vectors that are equivalent to another vector by symmetry
    
    Args:
        vector (list or numpy.ndarray): a vector in cartesian coordinates.
        lat_vecs (numpy.ndarray or list): a matrix with the lattice vectors as columns.
    
    Returns:
        unique_shells (list): a list of vectors expressed as numpy arrays.    
    """

    pointgroup = find_point_group(lat_vecs)
    all_shells = (np.dot(pointgroup, vector)).tolist()
    unique_shells = []
    for sh in all_shells:  
        if any([np.allclose(sh, us) for us in unique_shells]) == True:
            continue
        else:
            unique_shells.append(np.array(sh))
                
    tol = 1.e-10
    for (i,us) in enumerate(unique_shells):
        for (j,elem) in enumerate(us):
            if np.abs(elem) < tol:
                unique_shells[i][j] = 0.
    return unique_shells

def shells_list(vectors, lat_vecs):
    """Returns a list of several shells useful for constructing pseudopotentials.

    Args:
        vector (list or numpy.ndarray): a vector in cartesian coordinates.
    
    Returns:
        unique_shells (list): a list of vectors expressed as numpy arrays.
    
    Example:
        >>> from bzi.symmetry import sc_shells
        >>> vectors = [[0.,0.,0.], [1.,0.,0.]]
        >>> sc_shells_list(vector)
    """
    nested_shells = [shells(i, lat_vecs) for i in vectors]
    return np.array(list(itertools.chain(*nested_shells)))
            
def get_orbits(grid_car, lat_vecs, rlat_vecs, atom_labels, atom_positions,
               kpt_coords = "Cart", atom_coords="lat", duplicates=False, pointgroup=None,
               complete_orbit=False, unit_cell=True, pg_coords="lat", eps=1e-10, rtol=1e-4,
               atol=1e-6):
    """Find the partial orbitals of the points in a grid, including only the
    points that are in the grid. This symmetry reduction routine doesn't scale
    linearly. It is highly recommended that you use find_orbits instead.
    
    Args:
        grid_car (numpy.ndarray): a list of grid point positions in Cartesian
            coordinates.
        lat_vecs (numpy.ndarray): the lattice vectors as the columns of a 3x3 array
            in Cartesian coordinates.
        rlat_vecs (numpy.ndarray): the reciprocal lattice vectors as the columns of a 3x3
            array in Cartesian coordinates.
        atom_labels (list): a list of atoms labels. Each label should be distince for each
            atomic species. The labels must start at zero and should be in the same order 
            as atomic basis.
        atom_positions (list or numpy.ndarray): a list of atom positions in Cartesian 
            (default) or lattice coordinates.
        kpt_coords (str): a string that indicates coordinate system of the returned
            k-points. It can be in Cartesian ("cart") or lattice ("lat").
        atom_coords (str): a string that indicates coordinate system of the atom positions
            It can be in Cartesian ("cart") or lattice ("lat").
        duplicates (bool): if there are points in the grid outside the first
            unit cell, duplicates should be true.
        pointgroup (list): a list of point group symmetry operators in lattice
            coordinates.
        complete_orbit (bool): if true, the complete orbit of each k-point is returned.
        unit_cell (bool): if true, return the points of the orbits in the first unit cell.
            Has no effect unless complete_orbit = True.
        pg_coords (string): the coordinates of the point group: "lat" stands for lattice
            and "Cart" for Cartesian.
        eps (float): finite precision parameter used when finding points within a sphere.
        rtol (float): a relative tolerance used when finding if two k-points are 
            equivalent.
        atol (float): an absolute tolerance used when finding if two k-points are 
            equivalent.

    Returns:
        gp_orbits (dict): the orbits of the grid points in a nested list. 
        orbit_wts (list): the number of k-points in each orbit.
    """
    
    if type(grid_car) == list:
        if type(grid_car[0]) == list:
            grid_car = np.array(grid_car)
        else:
            grid_car = np.array([g.tolist() for g in grid_car])
    else:
        if type(grid_car[0]) == list:
            grid_car = np.array([g.tolist() for g in grid_car])
        else:
            pass
        
    # Put the grid in lattice coordinates and move it into the first unit cell.
    grid_lat = bring_into_cell(grid_car, rlat_vecs, atol=atol, rtol=rtol, coords="lat")
    
    # Remove duplicates if necessary.    
    if duplicates:
        grid_copy = list(deepcopy(grid_lat))
        grid_lat = []
        while len(grid_copy) != 0:
            gp = grid_copy.pop()
            if any([np.allclose(gp, gc, rtol=rtol, atol=atol) for gc in grid_copy]):
                continue
            else:
                grid_lat.append(gp)
    
    gp_orbits = []
    grid_copy = list(deepcopy(grid_lat))
    
    if pointgroup is None:
        pointgroup, translations = get_space_group(lat_vecs, atom_labels, atom_positions,
                                                   coords=atom_coords, rtol=rtol,
                                                   atol=atol, eps=eps)
    else:
        if pg_coords != "lat":
            pointgroup = np.matmul(np.matmul(inv(lat_vecs), pointgroup), lat_vecs)

    while len(grid_copy) != 0:
        g = grid_copy.pop()
        
        # Start a new orbit.
        gp_orbits.append([g])
        
        for pg in pointgroup:
            
            # Check both the k-point that is moved back into the unit cell and one that
            # isn't.
            new_grid_point = np.dot(pg, g)
            new_grid_point_car = np.dot(rlat_vecs, new_grid_point)
            new_grid_point_cell = bring_into_cell(new_grid_point, rlat_vecs, rtol=rtol,
                                                  atol=atol, coords="lat")
            new_gps = [new_grid_point_cell, new_grid_point]            

            # Add all unique k-points traversed by the orbit regardless of them
            # belonging to the k-point grid.
            if complete_orbit:
                if unit_cell:
                    # Only include this point in the orbit if it is unique.
                    if not check_contained(new_kps[0], gp_orbits[-1], rtol=rtol,
                                           atol=atol):
                        gp_orbits[-1].append(new_gps[0])
                else:
                    # Add points to the orbit without translating them back into the first
                    # unit cell
                    if not check_contained(new_kps[1], gp_orbits[-1], rtol=rtol,
                                           atol=atol):
                        gp_orbits[-1].append(new_gps[1])
            else:                
                # If the new grid point is in the grid, remove it and add it to the
                # orbit of grid point (g).
                for new_gp in new_gps:
                    indices = find_point_indices(new_gp, grid_copy, rtol=rtol, atol=atol)
                    if len(indices) > 1:
                        msg = "There are duplicate points in the grid."
                        raise ValueError(msg)
                    elif len(indices) == 0:
                        continue
                    else:
                        
                        gp_orbits[-1].append(new_gp)
                        del grid_copy[indices[0]]


    orbit_wts = [len(orb) for orb in gp_orbits]

    if kpt_coords == "Cart":
        for i in range(len(gp_orbits)):
            gp_orbits[i] = np.dot(rlat_vecs, np.array(gp_orbits[i]).T).T        
        return gp_orbits, orbit_wts
    
    elif kpt_coords == "lat":
        return gp_orbits, orbit_wts
    else:
        raise ValueError("Coordinate options are 'Cart' and 'lat'.")

# def find_full_orbitals(grid_car, lat_vecs, coord = "Cart", unitcell=False):
#     """ Find the complete orbitals of the points in a grid, including points
#     not contained in the grid.

#     Args:
#         grid_car (list): a list of grid point positions in cartesian coordinates.
#         lat_vecs (numpy.ndarray): the vectors that define the integration cell
#         coord (string): tell it to return the orbits in Cartesian ("cart",
#             default) or lattice ("lat") coordinates.
#         unitcell (string): return the points in the orbits in the first unit
#             cell when true.

#     Returns:
#         gp_orbits (dict): the orbitals of the grid points in a dictionary. 
#             The keys of the dictionary are integer labels and the values are the
#             grid points in the orbital.
#     """

#     grid_car = np.array(grid_car)
#     grid_lat = (np.dot(inv(lat_vecs), grid_car.T).T).tolist()
#     gp_orbits = {}
#     nirr_kpts = 0
#     grid_copy = deepcopy(grid_lat)
#     pointgroup = find_point_group(lat_vecs)

#     # To move an operator into lattice coordinates you have to take the product
#     # L^(-1) O L where L is the lattice vectors and O is the operator.
#     pointgroup = np.matmul(np.matmul(inv(lat_vecs), pointgroup), lat_vecs)
#     while grid_copy != []:
#         # Grap a point and build its orbit but only include points from the grid.
#         gp = grid_copy.pop()
#         nirr_kpts += 1
#         gp_orbits[nirr_kpts] = []
#         for pg in pointgroup:
#             # If the group operation moves the point outside the cell, %1 moves
#             # it back in.
#             # I ran into floating point precision problems the last time I ran
#             # %1. Just to be safe it's included here.
#             # Move the k-point into the first unit cell is requested.
#             if unitcell:
#                 new_gp = np.round(np.dot(pg, gp), 15)%1
#             else:
#                 new_gp = np.round(np.dot(pg, gp), 15)
                
#             if any([np.allclose(new_gp, gc) for gc in grid_copy]):
#                 ind = np.where(np.array([np.allclose(new_gp, gc) for gc in grid_copy]) == True)[0][0]
#                 del grid_copy[ind]
#                 gp_orbits[nirr_kpts].append(new_gp)
#             else:
#                 gp_orbits[nirr_kpts].append(new_gp)                
#                 continue

#     if coord == "cart":
#         for i in range(1, len(gp_orbits.keys()) + 1):
#             for j in range(len(gp_orbits[i])):
#                 gp_orbits[i][j] = np.dot(lat_vecs, gp_orbits[i][j])
#         return gp_orbits
#     elif coord == "lat":
#         return gp_orbits
#     else:
#         raise ValueError("Coordinate options are 'cell' and 'lat'.")

def find_lattice_type(centering_type, lattice_constants, lattice_angles):
    """Find the Bravais lattice type of the lattice.

    Args:
        centering_type (str): how points are centered in the conventional
            unit cell of the lattice. Options include 'prim', 'base', 'body',
            and 'face'.
        lattice_constants (list or numpy.ndarray): the axial lengths
            of the conventional lattice vectors.  
        lattice_angles (list or numpy.ndarray): the interaxial angles of the
            conventional lattice vectors.

    Returns:
        (str): the Bravais lattice type.
    Example:
        >>> centering_type = "prim
        >>> lattice_constants = [1]*3
        >>> lattice_angles = [numpy.pi/2]*3
        >>> lattice_type = find_lattice_type(centering_type,
                                             lattice_constants,
                                             lattice_angles)
    """

    
    # Extract parameters.
    a = float(lattice_constants[0])
    b = float(lattice_constants[1])
    c = float(lattice_constants[2])
    alpha = float(lattice_angles[0])
    beta = float(lattice_angles[1])
    gamma = float(lattice_angles[2])

    # Lattices with all angles = pi/2.
    if (np.isclose(alpha, beta) and np.isclose(beta, gamma) and
        np.isclose(gamma, np.pi/2)):
        # Check if it is a cubic lattice.
        if (np.isclose(a,b) and np.isclose(b,c)):
            if centering_type == "body":
                return "body-centered cubic"
            elif centering_type == "prim":
                return "simple cubic"
            elif centering_type == "face":
                return "face-centered cubic"
            else:
                msg = ("Valid centering types for cubic lattices include "
                       "'prim', 'body', and 'face'.")
                raise ValueError(msg.format(centering_type))
                
        # Check if it is tetragonal.
        elif (np.isclose(a,b) and not np.isclose(b,c)):
            if centering_type == "prim":
                return "tetragonal"
            elif centering_type == "body":
                return "body-centered tetragonal"
            else:
                msg = ("Valid centering types for tetragonal lattices include "
                       "'prim' and 'body'.")
                raise ValueError(msg.format(centering_type))
            
        # Check if it is orthorhombic
        elif not (np.isclose(a,b) and np.isclose(b,c) and np.isclose(a,c)):
            if centering_type == "body":
                return "body-centered orthorhombic"
            elif centering_type == "prim":
                return "orthorhombic"
            elif centering_type == "face":
                return "face-centered orthorhombic"
            elif centering_type == "base":
                return "base-centered orthorhombic"
            else:
                msg = ("Valid centering types for orthorhombic lattices include "
                       "'prim', 'base', 'body', and 'face'.")
                raise ValueError(msg.format(centering_type))
        else:
            msg = ("The lattice constants provided do not appear to correspond "
                   "to a Bravais lattice. They almost represent a cubic, "
                   "tetragonal, or orthorhombic lattice.")
            raise ValueError(msg.format(lattice_constants))
        
    # Check if it is rhombohedral.
    elif (np.isclose(alpha, beta) and np.isclose(beta, gamma)):
        if (np.isclose(a, b) and np.isclose(b,c)):
            if centering_type == "prim":
                return "rhombohedral"
            else:
                msg = ("The only valid centering type for rhombohedral lattices "
                       "is 'prim'.")
                raise ValueError(msg.format(centering_type))
        else:
            msg = ("All of the lattice constants should have the same value "
                   "for a rhombohedral lattice")
            raise ValueError(msg.format(lattice_constants))
        
    # Check if it is hexagonal.
    elif (np.isclose(alpha, beta) and np.isclose(beta, np.pi/2) and
          np.isclose(gamma, 2*np.pi/3)):
          if (np.isclose(a, b) and not np.isclose(b, c)):
            if centering_type == "prim":
                return "hexagonal"
            else:
                msg = ("The only valid centering type for hexagonal lattices "
                       "is 'prim'.")
                raise ValueError(msg.format(centering_type))
          else:
              msg = ("For a hexagonal lattice, a = b != c.")
              raise ValueError(msg.format(lattice_constants))
          
    # Check if it is monoclinic
    # Monoclinic a,b <= c, alpha < pi/2, beta = gamma = pi/2, a != b != c
    elif (np.isclose(beta, gamma) and np.isclose(beta, np.pi/2) and
          (alpha < np.pi/2)):
        if ((a < c or np.isclose(a, c)) and (b < c or np.isclose(b,c))):
            if centering_type == "prim":
                return "monoclinic"
            elif centering_type == "base":
                return "base-centered monoclinic"
            else:
                msg = ("Valid centering types for monoclinic lattices include "
                       "'prim' and 'base'.")
                raise ValueError(msg.format(centering_type))
        else:
            msg = ("The lattice constants of a monoclinic lattice should be "
                   "arranged such that a, b <= c.")
            raise ValueError(msg.format(lattice_constants))
            
    # Check if the lattice is triclinic.
    elif not (np.isclose(alpha, beta) and np.isclose(beta, gamma) and
          np.isclose(alpha, gamma)):
        if not (np.isclose(a, b) and np.isclose(b, c) and np.isclose(a, c)):
            if centering_type == "prim":
                return "triclinic"
            else:
                msg = ("The onld valid centering type for triclinic "
                       "lattices is 'prim'.")
                raise ValueError(msg.format(centering_type))
        else:
            msg = ("None of the lattice constants are equivalent for a "
                   "triclinic lattice.")
            raise ValueError(msg.format(lattice_constants))
    else:
        msg = ("The lattice angles provided do not correspond to any Bravais "
               "lattice type.")
        raise ValueError(msg.format(lattice_angles))

# Find transformation to create HNF from integer matrix.
def get_minmax_indices(a):
    """Find the maximum and minimum elements of a list that aren't zero.

    Args:
        a (numpy.ndarray): a three element numpy array.

    Returns:
        minmax (list): the minimum and maximum values of array a with the
            minimum first and maximum second.
    """
    a = np.abs(a)
    maxi = 2 - np.argmax(a[::-1])
    min = 0
    i = 0
    while min == 0:
        min = a[i]
        i += 1
    mini = i-1
    for i,ai in enumerate(a):
        if ai > 0 and ai < min:
            min = ai
            mini = i
    return np.asarray([mini, maxi])

def swap_column(M, B, k):
    """Swap the column k with whichever column has the highest value (out of
    the columns to the right of k in row k). The swap is performed for both
    matrices M and B. 

    Args:
        M (numpy.ndarray): the matrix being transformed
        B (numpy.ndarray): a matrix to keep track of the transformation steps 
            on M. 
        k (int): the column to swap, as described in summary.
    """
    
    Ms = deepcopy(M)
    Bs = deepcopy(B)
    
    # Find the index of the non-zero element in row k.
    maxidx = np.argmax(np.abs(Ms[k,k:])) + k
    tmpCol = deepcopy(Bs[:,k]);
    Bs[:,k] = Bs[:,maxidx]
    Bs[:,maxidx] = tmpCol

    tmpCol = deepcopy(Ms[:,k])
    Ms[:,k] = Ms[:, maxidx]
    Ms[:,maxidx] = tmpCol

    return Ms, Bs

def swap_row(M, B, k):
    """Swap the row k with whichever row has the highest value (out of
    the rows below k in column k). The swap is performed for both matrices M and B.

    Args:
        M (numpy.ndarray): the matrix being transformed
        B (numpy.ndarray): a matrix to keep track of the transformation steps 
            on M. 
        k (int): the column to swap, as described in summary.
    """
    
    Ms = deepcopy(M)
    Bs = deepcopy(B)
    
    # Find the index of the non-zero element in row k.
    maxidx = np.argmax(np.abs(Ms[k:,k])) + k

    tmpCol = deepcopy(Bs[k,:]);
    Bs[k,:] = Bs[maxidx,:]
    Bs[maxidx,:] = tmpCol
    
    tmpRow = deepcopy(Ms[k,:])
    Ms[k,:] = Ms[maxidx,:]
    Ms[maxidx,:] = tmpRow

    return Ms, Bs    

def HermiteNormalForm(S, eps=10):
    """Find the Hermite normal form (HNF) of a given integer matrix and the
    matrix that mediates the transformation.

    Args:
        S (numpy.ndarray): The 3x3 integer matrix describing the relationship 
            between two commensurate lattices.
        eps (int): finite precision parameter that determines number of decimals
            kept when rounding.
    Returns:
        H (numpy.ndarray): The resulting HNF matrix.
        B (numpy.ndarray): The transformation matrix such that H = SB.
    """
    if np.linalg.det(S) == 0:
        raise ValueError("Singular matrix passed to HNF routine")
    B = np.identity(np.shape(S)[0]).astype(int)
    H = deepcopy(S)
    
    # Keep doing column operations until all elements in the first row are zero
    # except for the one on the diagonal.
    while np.count_nonzero(H[0,:]) > 1:
        
        # Divide the column with the smallest value into the largest.
        minidx, maxidx = get_minmax_indices(H[0,:])
        minm = H[0,minidx]
        
        # Subtract a multiple of the column containing the smallest element from
        # the column containing the largest element.
        multiple = int(H[0, maxidx]/minm)
        H[:, maxidx] = H[:, maxidx] - multiple*H[:, minidx]
        B[:, maxidx] = B[:, maxidx] - multiple*B[:, minidx]
        if np.allclose(np.dot(S, B), H) == False:
            raise ValueError("COLS: Transformation matrices didn't work.")
    if H[0,0] == 0:
        H, B = swap_column(H, B, 0) # Swap columns if (0,0) is zero.
    if H[0,0] < 0:
        H[:,0] = -H[:,0]
        B[:,0] = -B[:,0]

    if np.count_nonzero(H[0,:]) > 1:
        raise ValueError("Didn't zero out the rest of the row.")
    if np.allclose(np.dot(S, B), H) == False:
        raise ValueError("COLSWAP: Transformation matrices didn't work.")
    
    # Now work on element H[1,2].
    while H[1,2] != 0:
        if H[1,1] == 0:
            tempcol = deepcopy(H[:,1])
            H[:,1] = H[:,2]
            H[:,2] = tempcol

            tempcol = deepcopy(B[:,1])
            B[:,1] = B[:,2]
            B[:,2] = tempcol
            if H[1,2] == 0:
                break
            
        if np.abs(H[1,2]) < np.abs(H[1,1]):
            maxidx = 1
            minidx = 2
        else:
            maxidx = 2
            minidx = 1

        multiple = int(H[1, maxidx]/H[1,minidx])
        H[:,maxidx] = H[:, maxidx] - multiple*H[:,minidx]
        B[:,maxidx] = B[:, maxidx] - multiple*B[:,minidx]
        
        if np.allclose(np.dot(S, B), H) == False:
            raise ValueError("COLS: Transformation matrices didn't work.")

    if H[1,1] == 0:
        tempcol = deepcopy(H[:,1])
        H[:,1] = H[:,2]
        H[:,2] = tempcol
        
    if H[1,1] < 0: # change signs
        H[:,1] = -H[:,1]
        B[:,1] = -B[:,1]
        
    if H[1,2] != 0:
        raise ValueError("Didn't zero out last element.")
    
    if np.allclose(np.dot(S,B), H) == False:
        raise ValueError("COLSWAP: Transformation matrices didn't work.")
    
    if H[2,2] < 0: # change signs
        H[:,2] = -H[:,2]
        B[:,2] = -B[:,2]
        
    check1 = (np.array([0,0,1]), np.array([1,2,2]))
    
    if np.count_nonzero(H[check1]) != 0:
        raise ValueError("Not lower triangular")
    
    if np.allclose(np.dot(S, B), H) == False:
        raise ValueError("End Part1: Transformation matrices didn't work.")
    
    # Now that the matrix is in lower triangular form, make sure the lower
    # off-diagonal elements are non-negative but less than the diagonal
    # elements.
    while H[1,1] <= H[1,0] or H[1,0] < 0:
        if H[1,1] <= H[1,0]:
            multiple = 1
        else:
            multiple = -1
            
        H[:,0] = H[:,0] - multiple*H[:,1]
        B[:,0] = B[:,0] - multiple*B[:,1]
        
    for j in [0,1]:
        while H[2,2] <= H[2,j] or H[2,j] < 0:
            
            if H[2,2] <= H[2,j]:
                multiple = 1
            else:
                multiple = -1
                
            H[:,j] = H[:,j] - multiple*H[:,2]
            B[:,j] = B[:,j] - multiple*B[:,2]

    if np.allclose(np.dot(S, B), H) == False:
        raise ValueError("End Part1: Transformation matrices didn't work.")
    
    if np.count_nonzero(H[check1]) != 0:
        raise ValueError("Not lower triangular")
    
    check2 = (np.asarray([0, 1, 1, 2, 2, 2]), np.asarray([0, 0, 1, 0, 1, 2]))
    if any(H[check2] < 0) == True:
        raise ValueError("Negative elements in lower triangle.")

    if H[1,0] > H[1,1] or H[2,0] > H[2,2] or H[2,1] > H[2,2]:
        raise ValueError("Lower triangular elements bigger than diagonal.")
    
    H = np.round(H, eps).astype(int)
    return H, B

def UpperHermiteNormalForm(S):
    """Find the Hermite normal form (HNF) of a given integer matrix and the
    matrix that mediates the transformation.

    Args:
        S (numpy.ndarray): The 3x3 integer matrix describing the relationship 
            between two commensurate lattices.
    Returns:
        H (numpy.ndarray): The resulting HNF matrix.
        B (numpy.ndarray): The transformation matrix such that H = SB.
    """
    if np.linalg.det(S) == 0:
        raise ValueError("Singular matrix passed to HNF routine")
    B = np.identity(np.shape(S)[0]).astype(int)
    H = deepcopy(S)

    #    Keep doing row operations until all elements in the first column are zero
    #    except for the one on the diagonal.
    while np.count_nonzero(H[:,0]) > 1:
        # Divide the row with the smallest value into the largest.
        minidx, maxidx = get_minmax_indices(H[:,0])
        minm = H[minidx,0]
        # Subtract a multiple of the row containing the smallest element from
        # the row containing the largest element.
        multiple = int(H[maxidx,0]/minm)
        H[maxidx,:] = H[maxidx,:] - multiple*H[minidx,:]
        B[maxidx,:] = B[maxidx,:] - multiple*B[minidx,:]
        if np.allclose(np.dot(B, S), H) == False:
            raise ValueError("ROWS: Transformation matrices didn't work.")
    if H[0,0] == 0:
        H, B = swap_row(H, B, 0) # Swap rows if (0,0) is zero.
    if H[0,0] < 0:
        H[0,:] = -H[0,:]
        B[0,:] = -B[0,:]
    if np.count_nonzero(H[:,0]) > 1:
        raise ValueError("Didn't zero out the rest of the row.")
    if np.allclose(np.dot(B,S), H) == False:
        raise ValueError("ROWSWAP: Transformation matrices didn't work.")
    # Now work on element H[2,1].
    while H[2,1] != 0:
        if H[1,1] == 0:
            temprow = deepcopy(H[1,:])
            H[1,:] = H[2,:]
            H[2,:] = temprow

            temprow = deepcopy(B[1,:])
            B[1,:] = B[2,:]
            B[2,:] = temprow
            break         
        if np.abs(H[2,1]) < np.abs(H[1,1]):
            maxidx = 1
            minidx = 2
        else:
            maxidx = 2
            minidx = 1
        
        multiple = int(H[maxidx,1]/H[minidx,1])
        H[maxidx,:] = H[maxidx,:] - multiple*H[minidx,:]
        B[maxidx,:] = B[maxidx,:] - multiple*B[minidx,:]

        if np.allclose(np.dot(B,S), H) == False:
            raise ValueError("COLS: Transformation matrices didn't work.")

    if H[1,1] == 0:
        temprow = deepcopy(H[1,:])
        H[1,:] = H[0,:]
        H[0,:] = temprow
    if H[1,1] < 0: # change signs
        H[1,:] = -H[1,:]
        B[1,:] = -B[1,:]
    if H[1,0] != 0:
        raise ValueError("Didn't zero out last element.")
    if np.allclose(np.dot(B,S), H) == False:
        raise ValueError("COLSWAP: Transformation matrices didn't work.")
    if H[2,2] < 0: # change signs
        H[2,:] = -H[2,:]
        B[2,:] = -B[2,:]
    check1 = (np.array([2,2,1]), np.array([1,0,0]))

    if np.count_nonzero(H[check1]) != 0:
        raise ValueError("Not lower triangular")
    if np.allclose(np.dot(B,S), H) == False:
        raise ValueError("End Part1: Transformation matrices didn't work.")

    # Now that the matrix is in lower triangular form, make sure the lower
    # off-diagonal elements are non-negative but less than the diagonal
    # elements.    
    while H[1,1] <= H[0,1] or H[0,1] < 0:
        if H[1,1] <= H[0,1]:
            multiple = 1
        else:
            multiple = -1
        H[0,:] = H[0,:] - multiple*H[1,:]
        B[0,:] = B[0,:] - multiple*B[1,:]
    for j in [0,1]:
        while H[2,2] <= H[j,2] or H[j,2] < 0:
            if H[2,2] <= H[j,2]:
                multiple = 1
            else:
                multiple = -1
            H[j,:] = H[j,:] - multiple*H[2,:]
            B[j,:] = B[j,:] - multiple*B[2,:]

    if np.allclose(np.dot(B, S), H) == False:
        raise ValueError("End Part1: Transformation matrices didn't work.")
    if np.count_nonzero(H[check1]) != 0:
        raise ValueError("Not lower triangular")
    check2 = (np.asarray([0, 0, 0, 1, 1, 2]), np.asarray([0, 1, 2, 1, 2, 2]))
    if any(H[check2] < 0) == True:
        raise ValueError("Negative elements in lower triangle.")
    if H[0,1] > H[1,1] or H[0,2] > H[2,2] or H[1,2] > H[2,2]:
        raise ValueError("Lower triangular elements bigger than diagonal.")
    return H, B


def find_kpt_index(kpt, invK, L, D, eps=4):
    """This function takes a k-point in Cartesian coordinates and "hashes" it 
    into a single number, corresponding to its place in the k-point list.

    Args:
    kpt (list or numpy.ndarray): the k-point in Cartesian coordinates
    invK(list or numpy.ndarray): the inverse of the k-point grid generating
        vectors
    L (list or numpy.ndarray): the left transform for the SNF conversion
    D (list or numpy.ndarray): the diagonal of the SNF
    eps (float): a finite-precision parameter that corresponds to the decimal
        rounded when converting k-points from Cartesian to grid coordinates.

    Returns:
        _ (int): the unique index of the k-point in the first unit cell
    """

    # Put the k-point in grid coordinates.
    gpt = np.round(np.dot(invK, kpt), eps)
    
    gpt = np.dot(L, gpt).astype(int)%D
        
    # Convert from group coordinates to a single, base-10 number between 1 and
    # the number of k-points in the unreduced grid.
    # return gpt[0]*D[1]*D[2] + gpt[1]*D[2] + gpt[2]
    return gpt[0]*D[1]*D[2] + gpt[1]*D[2] + gpt[2]

def bring_into_cell(points, rlat_vecs, rtol=1e-5, atol=1e-8, coords="Cart",
                    centered=False):
    """Bring a point or list of points into the first unit cell.

    Args:
        point (list or numpy.ndarray): a point or list of points in three space in
            Cartesian coordinates.
        rlat_vecs (numpy.ndarray): the lattice generating vectors as columns of a 3x3
            array.

    Returns:
        _ (numpy.ndarray): a point or list of points in three space inside the first
            unit cell in Cartesian (default) or lattice coordinates.
    """

    # Convert to lattice coordinates and move points into the first unit cell.
    points = np.array(points)
    lat_points = np.dot(inv(rlat_vecs), points.T).T%1
    
    # Special care has to be taken for points near 1.
    lat_points[np.isclose(lat_points, 1, rtol=rtol, atol=atol)] = 0

    # Shift points again if the unit cell is centered at the origin.
    if centered:
        lat_points[lat_points > 0.5] = lat_points[lat_points > 0.5] - 1

        # Special care has to be taken for points near 1/2.
        lat_points[np.isclose(lat_points, 0.5, rtol=rtol, atol=atol)] = -0.5

    
    # Convert back to Cartesian coordinates.
    if coords == "Cart":
        return np.dot(rlat_vecs, lat_points.T).T
    elif coords == "lat":
        return lat_points
    else:
        msg = "Coordinate options include 'Cart' and 'lat'."
        raise ValueError(msg)

    
def reduce_kpoint_list(kpoint_list, lattice_vectors, grid_vectors, shift,
                       eps=9, rtol=1e-5, atol=1e-8):
    """Use the point group symmetry of the lattice vectors to reduce a list of
    k-points.
    
    Args:
        kpoint_list (list or numpy.ndarray): a list of k-point positions in
            Cartesian coordinates.
        lattice_vectors (list or numpy.ndarray): the vectors that generate the
            reciprocal lattice in a 3x3 array with the vectors as columns.
        grid_vectors (list or numpy.ndarray): the vectors that generate the
            k-point grid in a 3x3 array with the vectors as columns in 
            Cartesian coordinates.
        shift (list or numpy.ndarray): the offset of the k-point grid in grid
            coordinates.
        

    Returns:
        reduced_kpoints (list): an ordered list of irreducible k-points
        kpoint_weights (list): an ordered list of irreducible k-point weights.
    """
    
    try:
        inv(lattice_vectors)
    except np.linalg.linalg.LinAlgError:
        msg = "The lattice generating vectors are linearly dependent."
        raise ValueError(msg.format(lattice_vectors))
    
    try:
        inv(grid_vectors)
    except np.linalg.linalg.LinAlgError:
        msg = "The grid generating vectors are linearly dependent."
        raise ValueError(msg.format(lattice_vectors))
        
    if abs(det(lattice_vectors)) < abs(det(grid_vectors)):
        msg = """The k-point generating vectors define a grid with a unit cell 
        larger than the reciprocal lattice unit cell."""
        raise ValueError(msg.format(grid_vectors))

    # Put the shift in Cartesian coordinates.
    shift = np.dot(grid_vectors, shift)

    # Check that the lattice and grid vectors are commensurate.
    check, N = check_commensurate(grid_vectors, lattice_vectors, rtol=rtol, atol=atol)
    if not check:
        msg = "The lattice and grid vectors are incommensurate."
        raise ValueError(msg.format(grid_vectors))
        
    # Find the HNF of N. B is the transformation matrix (BN = H).
    H,B = HermiteNormalForm(N)
    H = [list(H[i]) for i in range(3)]
    
    # Find the SNF of H. L and R are the left and right transformation matrices
    # (LHR = S).
    S,L,R = SmithNormalForm(H)

    # Get the diagonal of SNF.
    D = np.round(np.diag(S), eps).astype(int)
    
    cOrbit = 0 # unique orbit counter
    pointgroup = find_point_group(lattice_vectors) # a list of point group operators
    nSymOps = len(pointgroup) # the number of symmetry operations
    nUR = len(kpoint_list) # the number of unreduced k-points
    
    # A dictionary to keep track of the number of symmetrically-equivalent
    # k-points.
    hashtable = dict.fromkeys(range(nUR))

    # A dictionary to keep track of the k-points that represent each orbital.
    iFirst = {}

    # A dictionary to keep track of the number of symmetrically-equivalent
    # k-points in each orbit.
    iWt = {}
    invK = inv(grid_vectors)

    # Loop over unreduced k-points.
    for i in range(nUR):
        ur_kpt = kpoint_list[i]
        idx = find_kpt_index(ur_kpt - shift, invK, L, D, eps)
        
        if hashtable[idx] != None:
            continue
        cOrbit += 1        
        hashtable[idx] = cOrbit
        iFirst[cOrbit] = i
        iWt[cOrbit] = 1
        for pg in pointgroup:
            # Rotate the k-point.
            rot_kpt = np.dot(pg, ur_kpt)
            # Bring it back into the first unit cell.
            rot_kpt = bring_into_cell(rot_kpt, lattice_vectors)
            if not np.allclose(np.dot(invK, rot_kpt-shift),
                               np.round(np.dot(invK, rot_kpt-shift))):
                continue
            
            idx = find_kpt_index(rot_kpt - shift, invK, L, D, eps)            
            if hashtable[idx] == None:
                hashtable[idx] = cOrbit
                iWt[cOrbit] += 1
    sum = 0
    kpoint_weights = list(iWt.values())
    reduced_kpoints = []
    for i in range(cOrbit):
        sum += kpoint_weights[i]
        reduced_kpoints.append(kpoint_list[iFirst[i+1]])
    
    if sum != nUR:
        msg = "There are more or less k-points after the symmetry reduction."
        raise ValueError(msg)
    
    return reduced_kpoints, kpoint_weights


def find_orbits(kpoint_list, lattice_vectors, rlattice_vectors, grid_vectors, shift,
                atom_labels, atom_positions, full_orbit=False, kpt_coords="cart",
                atom_coords="lat", eps=1e-10, rounding_eps=4, rtol=1e-4, atol=1e-6):
    """Use the point group symmetry of the lattice vectors to reduce a list of
    k-points.
    
    Args:
        kpoint_list (list or numpy.ndarray): a list of k-point positions in
            Cartesian coordinates.
        lattice_vectors (list or numpy.ndarray): the vectors that generate the
            lattice in a 3x3 array with the vectors as columns in Cartesian coordinates.
        rlattice_vectors (list or numpy.ndarray): the vectors that generate the
            reciprocal lattice in a 3x3 array with the vectors as columns in Cartesian 
            coordinates.
        grid_vectors (list or numpy.ndarray): the vectors that generate the
            k-point grid in a 3x3 array with the vectors as columns in 
            Cartesian coordinates.
        shift (list or numpy.ndarray): the offset of the k-point grid in grid
            coordinates.
        atom_labels (list): a list of atoms labels. Each label should be distince for each
            atomic species. The labels must start at zero and should be in the same order 
            as atomic basis.
        atom_positions (list or numpy.ndarray): a list of atomic positions in Cartesian 
            (default) or lattice coordinates.
        full_orbit (bool): if true, return the orbits with the list of k-points from
            `kpoint_list`.
        kpt_coords (str): a string that indicates coordinate system of the returned
            k-points. It can be in Cartesian ("cart") or lattice ("lat").
        atom_coords (str): a string that indicates coordinate system of the atom positions
            It can be in Cartesian ("cart") or lattice ("lat").
        eps (float): a finite precision parameter that is added to the norms of points in
            `search_sphere`.
        rounding_eps (int): a finite precision parameter that determines the number of
            decimals kept when rounding.
        rtol (float): a relative tolerance used when finding if two k-points are 
            equivalent.
        atol (float): an absolute tolerance used when finding if two k-points are 
            equivalent.

    Returns:
        reduced_kpoints (list): an ordered list of irreducible k-points. If full_orbit
            is True, return `orbits_list`, a list of all k-points in each orbit.
        orbit_weights (list): an ordered list of the number of k-points in each orbit.
    """

    try:
        inv(lattice_vectors)
    except np.linalg.linalg.LinAlgError:
        msg = "The lattice generating vectors are linearly dependent."
        raise ValueError(msg.format(lattice_vectors))
    
    try:
        inv(rlattice_vectors)
    except np.linalg.linalg.LinAlgError:
        msg = "The reciprocal lattice generating vectors are linearly dependent."
        raise ValueError(msg.format(rlattice_vectors))
    
    try:
        inv(grid_vectors)
    except np.linalg.linalg.LinAlgError:
        msg = "The grid generating vectors are linearly dependent."
        raise ValueError(msg.format(rlattice_vectors))
        
    if abs(det(rlattice_vectors) + atol) < abs(det(grid_vectors)):
        msg = """The k-point generating vectors define a grid with a unit cell 
        larger than the reciprocal lattice unit cell."""
        raise ValueError(msg.format(grid_vectors))
    
    # Put the shift in Cartesian coordinates.
    shift = np.dot(grid_vectors, shift)
    
    # Verify the grid and lattice are commensurate.
    check, N = check_commensurate(grid_vectors, rlattice_vectors, rtol=rtol, atol=atol)
    if not check:
        msg = "The lattice and grid vectors are incommensurate."
        raise ValueError(msg.format(grid_vectors))
    
    # Find the HNF of N. B is the transformation matrix (BN = H).
    H,B = HermiteNormalForm(N)
    H = [list(H[i]) for i in range(3)]
    
    # Find the SNF of H. L and R are the left and right transformation matrices
    # (LHR = S).
    S,L,R = SmithNormalForm(H)

    # Get the diagonal of SNF.
    D = np.round(np.diag(S), rounding_eps).astype(int)

    # Unique orbit counter
    cOrbit = 0

    # A list of point group operators
    pointgroup, translations = get_space_group(lattice_vectors, atom_labels,
                                               atom_positions, coords=atom_coords,
                                               rtol=rtol, atol=atol, eps=eps)
    
    # The number of symmetry operations
    nSymOps = len(pointgroup)
    
    # The number of unreduced k-points
    nUR = len(kpoint_list)
    
    # A dictionary to keep track of the number of symmetrically-equivalent
    # k-points. It goes from the k-point index (the one not associated with the k-point's
    # position in `kpoint_list`) to the label of that k-point's orbit.
    hashtable = dict.fromkeys(range(nUR))
    
    # A dictionary to keep track of the k-points that represent each orbital.
    # It goes from orbit label to the index of the k-point that represents
    # the orbit.
    iFirst = {}

    # A dictionary to keep track of the number of symmetrically-equivalent
    # k-points in each orbit.
    iWt = {}

    # A dictionary for converting between k-point indices. The keys are the k-point
    # indices associated with the k-point's components. The values are the k-point
    # indices associated with the k-point's location in `kpoint_list`.
    kpt_index_conv = {}
    
    invK = inv(grid_vectors)

    # Loop over unreduced k-points.
    for i in range(nUR):
        
        # Grab an unreduced k-point.
        ur_kpt = kpoint_list[i]
        
        # Find the unreduced k-point's index.
        kpt_hash = find_kpt_index(ur_kpt - shift, invK, L, D, rounding_eps)

        kpt_index_conv[kpt_hash] = i
        
        # If it has already been looked at because it was part of the orbit of a
        # previous k-point, skip it.
        if hashtable[kpt_hash] != None:
            continue
        
        # If this k-point hasn't already been looked at, increment the orbit counter.
        cOrbit += 1
        
        # Add this k-point to the hashtable.
        hashtable[kpt_hash] = cOrbit
        
        # Make it the representative k-point for this orbit.
        iFirst[cOrbit] = i
        
        # Initialize the weight of this orbit.
        iWt[cOrbit] = 1
        
        # Loop through the point group operators.
        for pg in pointgroup:
            
            # Rotate the k-point.
            rot_kpt = np.dot(pg, ur_kpt)
            
            # Bring it back into the first unit cell.
            rot_kpt = bring_into_cell(rot_kpt, rlattice_vectors)
            
            # Verify that this point is part of the grid. If not, discard it.
            if not np.allclose(np.dot(invK, rot_kpt-shift),
                               np.round(np.dot(invK, rot_kpt-shift)), rtol=rtol):
                continue

            # Find the index of the rotated k-point.
            kpt_hash = find_kpt_index(rot_kpt - shift, invK, L, D, rounding_eps)

            # If this k-point hasn't been hit during the traversal of the orbit,
            # add the rotated k-point to this orbit and increment the orbit's weight.
            if hashtable[kpt_hash] == None:
                hashtable[kpt_hash] = cOrbit
                iWt[cOrbit] += 1
    
    # Remove empty entries from hashtable.
    hashtable = dict((k, v) for k, v in hashtable.items() if v)
    
    # Find the reduced k-points from the indices of the representative k-points in
    # iFirst.
    kpoint_list = np.array(kpoint_list)

    # test_indices = [kpt_index_conv[i] for i in list(iFirst.values())]    
    
    # reduced_kpoints = kpoint_list[test_indices]
    reduced_kpoints = kpoint_list[list(iFirst.values())]

    orbit_weights = list(iWt.values())

    if full_orbit:
        # A nested list that will eventually contain the k-points in each orbit.
        orbit_list = [[] for _ in range(max(list(hashtable.values())))]

        kpoint_index_list = list(hashtable.keys())

        # Put the index of the k-points in orbit_list.
        for kpt_i in kpoint_index_list:
            orbit_list[hashtable[kpt_i]-1].append(kpt_i)

        # Replace the indices by the actual k-points.
        for i,orbit in enumerate(orbit_list):
            for j,kpt_index in enumerate(orbit):
                
                kpt = kpoint_list[kpt_index_conv[kpt_index]]
                
                # Put points in lattice coordinates if option provided.
                if kpt_coords == "lat":
                    kpt = np.dot(inv(rlattice_vectors), kpt)
                orbit_list[i][j] = kpt

        return orbit_list, orbit_weights
    else:
        if kpt_coords == "lat":
            reduced_kpoints = np.dot(inv(rlattice_vectors), reduced_kpoints.T).T
        return reduced_kpoints, orbit_weights


# def minkowski_reduce_basis(basis, eps):
#     """Find the Minkowski representation of a basis.

#     Args:
#         basis(numpy.ndarray): a matrix with the generating vectors as columns.
#         eps (int): a finite precision parameter in 10**(-eps).
#     """

#     if type(eps) != int:
#         msg = ("eps must be an integer, cooresponds to 10**-eps")
#         raise ValueError(msg.format(eps))

#     return _minkowski_reduce_basis(basis.T, 10**(-eps)).T


def just_map_to_bz(grid, rlattice_vectors, coords="Cart", rtol=1e-4, atol=1e-6, eps=1e-10):
    """Map a grid into the first Brillouin zone in the Minkowski basis.

    Args:
        grid (list): a list of k-points in Cartesian coordinates.
        rlattice_vectors (numpy.ndarray): a matrix whose columes are the
            reciprocal lattice generating vectors.
        coords (string): the coordinates of the returned k-points. Options include
            "Cart" for Cartesian and "lat" for lattice.
        eps (int): finite precision parameter that determines decimal rounded.

    Returns:
        reduced_grid (numpy.ndarray): a numpy array of grid points in the first 
            Brillouin zone in Minkowski space.
        weights (numpy.ndarray): the k-point weights
    """

    # Find the Minkowski basis.
    mink_basis = minkowski_reduce_basis(rlattice_vectors, rtol=rtol, atol=atol, eps=eps)

    # Initialize the grid that will be mapped to the BZ.
    new_grid = []

    # Loop over all points in the grid.
    for i, pt in enumerate(grid):

        # Move each point into the first unit cell.
        pt = bring_into_cell(pt, mink_basis, rtol=rtol, atol=atol)

        # Put the point in lattice coordinates.
        pt_lat = np.dot(inv(rlattice_vectors), pt)

        # Find the translationally equivalent points in the eight unit cells that
        # share a vertex at the origin in lattice coordinates.
        pts_lat = np.array([pt_lat + shift for shift in product([-1,0], repeat=3)])

        # Put the translationally equivalent points in Cartesian coordinates.
        pts = np.dot(rlattice_vectors, pts_lat.T).T
        
        # Keep the point that is the closest to the origin.
        new_grid.append(pts[np.argmin(norm(pts, axis=1))])

    new_grid = np.array(new_grid)
    if coords == "lat":
        new_grid = np.dot(inv(rlattice_vectors), new_grid.T).T
        return new_grid
    
    elif coords == "Cart":
        return new_grid
    
    else:
        msg = "Coordinate options include 'Cart' and 'lat'."
        raise ValueError(msg)


def map_to_bz(grid, lattice_vectors, rlattice_vectors, grid_vectors, shift, atom_labels,
              atom_positions, rtol=1e-5, atol=1e-8, eps=1e-10):
    """Map a grid into the first Brillouin zone in Minkowski space.
    
    Args:
        grid (list): a list of grid points in Cartesian coordinates.
        rlattice_vectors (numpy.ndarray): a matrix whose columes are the
            reciprocal lattice generating vectors.
        grid_vectors (numpy.ndarray): the grid generating vectors.
        shift (list or numpy.ndarray): the offset of the k-point grid in grid
            coordinates.
        eps (int): finite precision parameter that is the integer exponent in
            10**(-eps).
    Returns:
        reduced_grid (numpy.ndarray): a numpy array of grid points in the first 
            Brillouin zone in Minkowski space.
        weights (numpy.ndarray): the k-point weights
    """

    # Reduce the grid and move into the unit cell.
    # reduced_grid, weights = reduce_kpoint_list(grid, rlattice_vectors, grid_vectors,
    #                                   shift, eps)

    # Uncomment this when symmetry reduction is fixed.
    reduced_grid, weights = find_orbits(grid, lattice_vectors, rlattice_vectors,
                                        grid_vectors, shift, atom_labels, atom_positions)
    reduced_grid = np.array(reduced_grid)
    
    # Find the Minkowski basis.
    mink_basis = minkowski_reduce_basis(rlattice_vectors, rtol=rtol, atol=atol, eps=eps)
    
    reduced_grid_copy = deepcopy(reduced_grid)
    for i, pt1 in enumerate(reduced_grid_copy):
        pt1 = bring_into_cell(pt1, mink_basis)
        norm_pt1 = np.dot(pt1, pt1)
        reduced_grid[i] = pt1
        for n in product([-1,0], repeat=3):
            pt2 = pt1 + np.dot(mink_basis, n)
            norm_pt2 = np.dot(pt2, pt2)
            if (norm_pt2 + eps) < norm_pt1:
                norm_pt1 = norm_pt2
                reduced_grid[i] = pt2

    return reduced_grid, weights


def number_of_point_operators(lattice_type):
    """Return the number of point group operators for the provided lattice type.

    Args:
        lattice_type (str): the Bravais lattice.

    Returns:
        (int): the number of point group symmetry operators for the Bravais lattice.
    """

    num_operators = [2, 4, 8, 12, 16, 24, 48]
    lat_types = ['triclinic', 'monoclinic', 'orthorhombic', 'rhombohedral', 'tetragonal',
             'hexagonal', 'cubic']
    lat_dict = {i:j for i,j in zip(lat_types, num_operators)}

    try:        
        return lat_dict[lattice_type]
    except:
        msg = ("Please provide a Bravais lattice, excluding atom centering, such as "
               "'cubic' or 'hexagonal'.")
        raise ValueError(msg.format(lattice_type))


def search_sphere(lat_vecs, eps=1e-9):
    """Find all the lattice points within a sphere whose radius is the same
    as the length of the longest lattice vector.
    
    Args:
        lat_vecs (numpy.ndarray): the lattice vectors as columns of a 3x3 array.
        eps (float): finite precision tolerance used when comparing norms of points.
        
    Returns:
        sphere_points (numpy.ndarray): a 1D array of points within the sphere.
    """
    
    a0 = lat_vecs[:,0]
    a1 = lat_vecs[:,1]
    a2 = lat_vecs[:,2]

    # Let's orthogonalize the lattice vectors be removing parallel components.
    a0_hat = a0/norm(a0)
    a1_hat = a1/norm(a1)

    a1p = a1 - np.dot(a1, a0_hat)*a0_hat
    a1p_hat = a1p/norm(a1p)

    a2p = a2 - np.dot(a2, a1p_hat)*a1p_hat - np.dot(a2, a0_hat)*a0_hat

    max_norm = max(norm(lat_vecs, axis=0))
    max_indices = [int(np.ceil(max_norm/norm(a0) + eps)), int(np.ceil(max_norm/norm(a1p) + eps)),
                   int(np.ceil(max_norm/norm(a2p) + eps))]
    imin = -max_indices[0]
    imax =  max_indices[0] + 1
    jmin = -max_indices[1]
    jmax =  max_indices[1] + 1
    kmin = -max_indices[2]
    kmax =  max_indices[2] + 1
    
    sphere_pts = []
    for i,j,k in it.product(range(imin, imax), range(jmin, jmax), range(kmin, kmax)):        
        pt = np.dot(lat_vecs, [i,j,k])
        if (np.dot(pt, pt) - eps) < max_norm**2:
            sphere_pts.append(pt)

    return np.array(sphere_pts)


def get_point_group(lat_vecs, rtol = 1e-4, atol=1e-6, eps=1e-9):
    """Get the point group of a lattice.

    Args:
        lat_vecs (numpy.ndarray): a 3x3 array with the lattice vectors as columns.
        rtol (float): relative tolerance for floating point comparisons.
        atol (float): absolute tolerance for floating point comparisions.
        eps (float): finite precision parameter for identifying points within a sphere.

    Returns:
        point_group (numpy.ndarray): a list of rotations, reflections and improper
            rotations.
    """
    

    pts = search_sphere(lat_vecs, eps)
    a1 = lat_vecs[:,0]
    a2 = lat_vecs[:,1]
    a3 = lat_vecs[:,2]

    inv_lat_vecs = inv(lat_vecs)
    point_group = []
    i = 0
    for p1,p2,p3 in it.permutations(pts, 3):
        # In a unitary transformation, the length of the vectors will be
        # preserved.
        if (np.isclose(np.dot(p1,p1), np.dot(a1,a1), rtol=rtol, atol=atol) and
            np.isclose(np.dot(p2,p2), np.dot(a2,a2), rtol=rtol, atol=atol) and
            np.isclose(np.dot(p3,p3), np.dot(a3,a3), rtol=rtol, atol=atol)):
            
            new_lat_vecs = np.transpose([p1,p2,p3])
            
            # The volume of a parallelepiped given by the new basis should
            # be the same.
            if np.isclose(abs(det(new_lat_vecs)), abs(det(lat_vecs)), rtol=rtol,
                          atol=atol):
                
                op = np.dot(new_lat_vecs, inv_lat_vecs)
                
                # Check that the rotation, reflection, or improper rotation 
                # is an orthogonal matrix.
                if np.allclose(np.eye(3), np.dot(op, op.T), rtol=rtol, atol=atol):
                    
                    # Make sure this operator is unique.
                    if not check_contained([op], point_group, rtol=rtol, atol=atol):
                        point_group.append(op)
    return point_group


def get_space_group(lattice_vectors, atom_labels, atom_positions, coords="lat",
                    rtol=1e-4, atol=1e-6, eps=1e-10):
    """Get the space group (point group and fractional translations) of a crystal.
    
    Args:
        lattice_vectors (list or numpy.ndarray): the lattice vectors, in Cartesian
            coordinates, as columns of a 3x3 array.
        atom_labels (list): a list of atom labels. Each label should be distince for each
            atomic species. The labels can be of type string or integer but must be in the
            same order as atomic_basis.
        atom_positions (list or numpy.ndarray): a list of atom positions in Cartesian
            (default) or lattice coordinates.
        coords (bool): specifies the coordinate system of the atomic basis. Anything other
            than "lat", for lattice coordinates, will default to Cartesian.
        rtol (float): relative tolerance for finding point group.
        atol (float): absolute tolerance for finding point group.
        eps (float): finite precision parameter used when finding points within a sphere.

    Returns:
        point_group (list): a list of point group operations.
        translations (list): a list of translations.
    """
    
    
    def check_atom_equivalency(atom_label_i, atom_position_i, atom_labels, atom_positions):
        """Check if an atom is equivalent to another atom in a list of atoms. Two atoms
        are equivalent if they have the same label and are located at the same position.
        
        Args:
            atom_label_i (int): the label of the atom being compared.
            atom_position_i (list or numpy.ndarray): the position of the atom being
                compared in 3-space.
            atom_labels (list or numpy.ndarray): a list of atom labels.
            atom_positions (list or numpy.ndarray): a list of atom positions in 3-space.
        
        Returns:
            _ (bool): return `True` if the atom is equivalent to an atom in the list of
                atoms.
        """

        # Check to see if this atom that was rotated, translated, and brought
        # into the unit cell is equivalent to one of the other atoms in the atomic
        # basis.

        # Find the location of the atom 
        label_index = find_point_indices([atom_label_i], atom_labels)
        position_index = find_point_indices(atom_position_i, atom_positions)

        if check_contained(position_index, label_index):    
            return True
        else:
            return False
                          
    # Initialize the point group and fractional translations subgroup.
    point_group = []
    translations = []

    atomic_basis = deepcopy(np.array(atom_positions))

    # Put atomic positions in Cartesian coordinates if necessary.
    if coords == "lat":
        atomic_basis = np.dot(lattice_vectors, atomic_basis.T).T

    # Bring the atom's positions into the first unit cell.
    atomic_basis = np.array([bring_into_cell(ab, lattice_vectors, rtol=rtol, atol=atol)
                             for ab in atomic_basis])

    # Get the point group of the lattice.
    lattice_pointgroup = get_point_group(lattice_vectors, rtol=rtol, atol=atol, eps=eps)
    
    # The possible translations are between atoms of the same type. The translations
    # between atoms of *one* type will be, in every case, a *superset* of all translations
    # that may be in the spacegroup. We'll generate this superset of translations and keep
    # only those that are valid for all atom types.
    
    # Grab the type and position of the first atom.
    first_atom_type = atom_labels[0]
    first_atom_pos = atomic_basis[0]
    
    # Loop through the point group operators of the parent lattice.
    for lpg in lattice_pointgroup:
        
        # Rotate the first atom.
        rot_first_atom_pos = np.dot(lpg, first_atom_pos)
        
        # Loop over all the atoms.
        for atom_type_i,atom_pos_i in zip(atom_labels, atomic_basis):
            
            # If the atoms are diffent types, move on to the next atom.
            if first_atom_type != atom_type_i:
                continue
            
            # Calculate the vector that points from the first atom's rotated position to
            # this atom's position and then move it into the first unit cell. This is one
            # of the translations in the superset of fractional translations for the first
            # atom type.
            frac_trans = bring_into_cell(atom_pos_i - rot_first_atom_pos, lattice_vectors,
                                         rtol=rtol, atol=atol)

            # Verify that this rotation and fractional translation map each atom onto
            # another atom of its the same type.
            for atom_type_j,atom_pos_j in zip(atom_labels, atomic_basis):
                
                # Rotate, translate, and then bring this atom into the unit cell in the
                # first unit cell.
                rot_atom_pos_j = bring_into_cell(np.dot(lpg, atom_pos_j) + frac_trans,
                                                 lattice_vectors, rtol=rtol, atol=atol)
                
                # Check to see if this atom that was rotated, translated, and brought
                # into the unit cell is equivalent to one of the other atoms in the atomic
                # basis.
                equivalent = check_atom_equivalency(atom_type_j, rot_atom_pos_j,
                                                    atom_labels, atomic_basis)
                                        
                # If this atom isn't equivalent to one of the others, it isn't a valid
                # rotation + translation.
                if not equivalent:
                    break
                
            # If all the atoms get mapped onto atoms of their same type, add this
            # translation and rotation to the space group.
            # print(equivalent)            
            if equivalent:
                point_group.append(lpg)
                translations.append(frac_trans)
                
    return point_group, translations

def equivalent_orbits(orbits_list0, orbits_list1, rtol=1e-4, atol=1e-6):
    """Check that two orbits are equivalent.

    Args:
        orbit_list0 (list or numpy.ndarray): a list of k-points in orbits.
        orbit_list1 (list or numpy.ndarray): a list of k-points in orbits.
        rtol (float): the relative tolerance
        atol (float): the absolute tolerance

    Returns:
        _ (bool): true if the two lists of orbits are equivalent

    """

    def check_orbits(orbits_list0, orbits_list1):
        """Check that the orbits of one list of orbits are a subset of another
        list of orbits.

        Args:
            orbit_list0 (list or numpy.ndarray): a list of k-points in orbits.
            orbit_list1 (list or numpy.ndarray): a list of k-points in orbits.
        """
        
        orbit_lists_equal = []

        # Grab an orbit from the first list.
        for orbit0 in orbits_list0:
            orbit_equal = []

            # Grab an orbit from the second list.
            for orbit1 in orbits_list1:
                orbit_equal.append([])

                # See if all the k-points in the first orbit are in the second orbit.
                for kpt in orbit0:
                    orbit_equal[-1].append(check_contained([kpt], orbit1, rtol=rtol, atol=atol))
                    
                # An orbit is equivalent to another if all it's k-points are in another.
                orbit_equal[-1] = all(orbit_equal[-1])
                
            orbit_lists_equal.append(any(orbit_equal))
            
        return all(orbit_lists_equal)

    # If the two lists of orbits are subsets of each other, they are equivalent.
    return all([check_orbits(orbits_list0, orbits_list1),
                check_orbits(orbits_list1, orbits_list0)])


def gaussian_reduction(v1, v2, eps=1e-10):
    """Gaussian reduced two vectors by subtracting multiples of the shorter
    vector from the longer. Repeat this process on both vectors until the 
    shortest set is obtained.
    
    Args:
        v1 (list or numpy.ndarray): a vector in three space in Cartesian
            coordinates.
        v2 (list or numpy.ndarray): a vector in three space in Cartesian
            coordinates.            
        eps (float): a finite precision tolerance used for comparing lengths
            of of vectors.
        
    Returns:
        v1 (list or numpy.ndarray): a Gaussian reduced vector in three 
            space in Cartesian coordinates.
        v2 (list or numpy.ndarray): a Gaussian reduced vector in three
            space in Cartesian coordinates.
    """

    # Make sure the norm of v1 is smaller than v2.
    vecs = np.array([v1, v2])
    v1,v2 = vecs[np.argsort(norm(vecs, axis=1))]
    
    reduced = False    
    it = 0
    while not reduced:
        it += 1
        if it > 10:
            msg = "Failed to Gaussian reduce the vectors after {} iterations".format(it-1)
            raise ValueError(msg)
            
        # Subtract an integer multiple of v1 from v2.
        v2 -= np.round(np.dot(v1, v2)/np.dot(v1, v1))*v1
        
        # If v2 is still longer than v1, the vectors have been reduced.
        if (norm(v1) - eps) < norm(v2):
            reduced = True
        
        # Make sure the norm of v1 is smaller than v2.
        vecs = np.array([v1, v2])
        v1,v2 = vecs[np.argsort(norm(vecs, axis=1))]
        
    return v1, v2


def reduce_lattice_vector(lattice_vectors, rtol=1e-4, atol=1e-6, eps=1e-10):
    """Make last lattice vector as short as possible while remaining in an
    affine plane that passes through the end of the last lattice vector.
    
    Args:
        lattice_vectors (numpy.ndarray): the lattice generating vectors as columns
            of a 3x3 array. The first two columns define a plane which is parallel
            to the affine plane the third vector passes through. The third column
            is the lattice vector being reduced.        
        rtol (float): a relative tolerance used when verifying the lattice vectors 
            are linearly independent and when verifying the input lattice vectors
            are lattice points of the reduced lattice vectors.
        atol (float): an absolute tolerance used when verifying the lattice vectors
            are linearly independent and when verifying the input lattice vectors
            are lattice points of the reduced lattice vectors.
        eps (int): a finite precision tolerance that is added to the norms of vectors
            when comparing lengths and to a point converted into lattice coordinates
            before finding a nearby lattice point.
     
    Returns:
        reduced_lattice_vectors (numpy.ndarray): the generating vectors with the two in 
            the first two columns unchanged and the third reduced.
    """
        
    # Assign a variable for each of the lattice vectors.
    v1,v2,v3 = lattice_vectors.T
        
    # Gaussian reduce the first two lattice vectors, v1 and v2.
    # After reduction, the lattice point closest to the projection of v3
    # in v1-v2 plane is guaranteed to be one of the corners of the unit
    # cell enclosing the projection of v3.    
    v1r,v2r = gaussian_reduction(v1, v2, eps)
        
    # Replace the first two lattice vectors with the Gaussian reduced ones.
    temp_lattice_vectors = np.array([v1r, v2r, v3]).T
        
    # Verify the new basis is linearly independent.
    if np.isclose(det(temp_lattice_vectors), 0, rtol=rtol, atol=atol):
        msg = ("After Gaussian reduction of the first two lattice vectors, "
               "the lattice generating vectors are linearly dependent.")
        raise ValueError(msg)
                
    # Find the point in the v1-v2 affine plane that is closest
    # to the origin
    
    # Find a vector orthogonal and normal to the v1-v2 plane
    v_on = np.cross(v1r, v2r)/norm(np.cross(v1r, v2r))
    
    # Find the point on the plane closest to the origin
    closest_pt = v3 - v_on*np.dot(v_on, v3)
    
    # Put this point in lattice coordinates and then round down to the nearest
    # integer
    closest_lat_pt = np.floor(np.dot(inv(temp_lattice_vectors), 
                                     closest_pt) + eps).astype(int)    
    
    # Make sure this point isn't parallel to the v1-v2 plane.
    if not np.isclose(np.dot(closest_pt, v_on), 0, rtol=rtol, atol=atol):
        msg = ("After Gaussian reduction, the latttice vectors are "
               "linearly dependent.")
        raise ValueError(msg)

    # Find the four lattice points that enclose this point in lattice and Cartesian 
    # coordinates.
    corners_lat = np.array([list(i) + [0] for i in itertools.product([0,1], repeat=2)]) + (
                  closest_lat_pt)
    
    corners_cart = np.dot(temp_lattice_vectors, corners_lat.T).T
    
    # Calculate distances from the corners to `closest_pt`.
    corner_distances = norm(corners_cart - closest_pt, axis=1)
    
    # Find corner with the shortest distance.
    corner_index = np.argmin(corner_distances)
        
    # Calculate the reduced vector.
    try:
        v3r = v3 - corners_cart[corner_index]
    except:
        msg = "Failed to reduce the lattice vector."
        raise ValueError(msg)
        
    reduced_lattice_vectors = np.array([v1r, v2r, v3r]).T
    
    # Verify that the old lattice vectors are an integer combination of the new
    # lattice vectors.
    check, N = check_commensurate(reduced_lattice_vectors, lattice_vectors,
                                  rtol=rtol, atol=atol)
    if not check:
        msg = ("The reduced lattice generates a different lattice than the input"
               " lattice.")        
        raise ValueError(msg.format(grid_vectors))
    else:
        return reduced_lattice_vectors


def check_minkowski_conditions(lattice_basis, eps=1e-10):
    """Verify a lattice basis satisfies the Minkowski conditions. 
    
    Args:
        lattice_basis (numpy.ndarray): the lattice generating vectors as columns
            of a 3x3 array.
        eps (int): a finite precision parameter that is added to the norm of vectors
            when comparing lengths.
            
    Returns:
        minkowski_check (bool): A boolean whose value is `True` if the Minkowski 
            conditions are satisfied.
    """
        
    minkowski_check = True
    b1, b2, b3 = lattice_basis.T
    
    if (norm(b2) + eps) < norm(b1):
        print("Minkowski condition |b1| < |b2| failed.")
        minkowski_check = False
    
    if (norm(b3) + eps) < norm(b2):
        print("Minkowski condition |b2| < |b3| failed.")
        minkowski_check = False
        
    if (norm(b1 + b2) + eps) < norm(b2):
        print("Minkowski condition |b2| < |b1 + b2| failed.")
        minkowski_check = False
        
    if (norm(b1 - b2) + eps) < norm(b2):
        print("Minkowski condition |b1 - b2| < |b2| failed.")
        minkowski_check = False
    
    if (norm(b1 + b3) + eps) < norm(b3):
        print("Minkowski condition |b3| < |b1 + b3| failed.")
        minkowski_check = False
        
    if (norm(b3 - b1) + eps) < norm(b3):
        print("Minkowski condition |b3 - b1| < |b3| failed. ")
        minkowski_check = False        
        
    if (norm(b2 + b3) + eps) < norm(b3):
        print("Minkowski condition |b3| < |b2 + b3| failed. ")
        minkowski_check = False
        
    if (norm(b3 - b2) + eps) < norm(b3):
        print("Minkowski condition |b3| < |b3 - b2| failed.")
        minkowski_check = False
    
    if (norm(b1 + b2 + b3) + eps) < norm(b3):
        print("Minkowski condition |b3| < |b1 + b2 + b3| failed.")
        minkowski_check = False
        
    if (norm(b1 - b2 + b3) + eps) < norm(b3):
        print("Minkowski condition |b3| < |b1 - b2 + b3| failed.")
        minkowski_check = False
        
    if (norm(b1 + b2 - b3) + eps) < norm(b3):        
        print("Minkowski condition |b3| < |b1 + b2 - b3| failed.")
        minkowski_check = False
        
    if (norm(b1 - b2 - b3) + eps) < norm(b3):        
        print("Minkowski condition |b3| < |b1 - b2 - b3| failed.")
        minkowski_check = False

    return minkowski_check        


def minkowski_reduce_basis(lattice_basis, rtol=1e-4, atol=1e-6, eps=1e-10):
    """Minkowski reduce the basis of a lattice.
    
    Args:
        lattice_basis (numpy.ndarray): the lattice generating vectors as columns
            of a 3x3 array.
        rtol (float): a relative tolerance used when comparing determinates to zero, and
            used as an input to `reduce_lattice_vector`.
        atol (float): an absolute tolerance used when comparing determinates to zero, and
            used as an input to `reduce_lattice_vector`.
        eps (int): a finite precision tolerance that is added to the norms of vectors
            when comparing lengths.
            
    Returns:
        lat_vecs (numpy.ndarray): the Minkowski reduced lattice vectors as columns
            of a 3x3 array.
    """
    
    if np.isclose(det(lattice_basis), 0, rtol=rtol, atol=atol):
        msg = "Lattice basis is linearly dependent."
        raise ValueError(msg)

    limit = 10
    lat_vecs = deepcopy(lattice_basis)
    
    for _ in range(limit):
        
        # Sort the lattice vectors by their norms in ascending order.
        lat_vecs = lat_vecs.T[np.argsort(norm(lat_vecs, axis=0))].T
        
        # Reduce the lattice vector in the last column.
        lat_vecs = reduce_lattice_vector(lat_vecs, rtol=rtol, atol=atol, eps=eps)
        
        if norm( lat_vecs[:,2] ) >= (norm( lat_vecs[:,1] ) - eps):
            break
            
    # Check that the Minkowski conditions are satisfied.
    if not check_minkowski_conditions(lat_vecs, eps):
        msg = "Failed to meet Minkowski reduction conditions after {} iterations".format(limit)
        raise ValueError(msg)
    
    # Sort the lattice vectors by their norms in ascending order.
    lat_vecs = lat_vecs.T[np.argsort(norm(lat_vecs, axis=0))].T
    
    # We want the determinant to be positive. Technically, this is no longer a
    # Minkowski reduced basis but it shouldn't physically affect anything and the
    # basis is still as orthogonal as possible.
    if (det(lat_vecs) + eps) < 0:
        lat_vecs = swap_rows_columns(lat_vecs, 1, 2, rows=False)
        # lat_vecs[:, 1], lat_vecs[:, 2] = lat_vecs[:, 2], lat_vecs[:, 1].copy()
                
    return lat_vecs


def check_commensurate(lattice, sublattice, rtol=1e-5, atol=1e-8):
    """Check if a lattice is commensurate with a sublattice.

    Args:
        lattice (numpy.ndarray): lattice generating vectors as columns of a 3x3 array.
        sublattice (numpy.ndarray): sublattice generating vectors as columns of a 3x3
            array.
    Returns:
        _ (bool): if the lattice and sublattice are commensurate, return `True`.
        N (numpy.ndarray): if the lattice and sublattice are commensurate, return an array
            of ints. Otherwise, return an array of floats.
    """

    N = np.dot(inv(lattice), sublattice)
    
    if np.allclose(N, np.round(N), atol=atol, rtol=rtol):        
        N = np.round(N).astype(int)
        return True, N
    else:
        return False, N


def get_space_group_size(file_loc, coords="lat", rtol=1e-4, atol=1e-6, eps=1e-10):
    """Get the size of the point group.
    
    Args:
        file_loc (str): the location of the VASP POSCAR file.
        
    Returns:
        _ (int): the number of operations in the space group.
    """
    
    data = read_poscar(file_loc)
    lat_vecs = data["lattice vectors"]
    atom_labels = data["atomic basis"]["atom labels"]
    atom_positions = data["atomic basis"]["atom positions"]
    translations, point_group = get_space_group(lat_vecs, atom_labels, atom_positions, coords=coords,
                                                rtol=rtol, atol=atol, eps=eps)
    
    return len(point_group)
            
    
