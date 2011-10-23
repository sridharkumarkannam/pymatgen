#!/usr/bin/env python

from __future__ import division

"""
This module provides classes for calculating the ewald sum of a structure.
"""

__author__="Shyue Ping Ong"
__copyright__ = "Copyright 2011, The Materials Project"
__credits__ = "Christopher Fischer"
__version__ = "1.0"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__status__ = "Production"
__date__ ="$Sep 23, 2011M$"

import numpy as np
from math import pi, sqrt, log, exp, cos, sin, erfc
import scipy.constants as sc
from pymatgen.core.structure import Structure

def compute_average_oxidation_state(site):
    """
    Calculates the average oxidation state of a site
    """
    return sum([sp.oxi_state * occu for sp, occu in site.species_and_occu.items() if sp != None])

class EwaldSummation:
    """
    Calculates the electrostatic energy of a periodic array of charges using the Ewald technique. 
    References : http://www.ee.duke.edu/~ayt/ewaldpaper/ewaldpaper.html
    E = E_recip + E_real + E_point
    Atomic units used in the code, then converted to eV
    """

    # taken from convasp. converts unit of q*q/r into eV 
    CONV_FACT = 1e10 * sc.e / (4 * pi * sc.epsilon_0)
    
    def __init__(self, structure, real_space_cut = -1.0, recip_space_cut = -1.0, eta = -1.0, acc_factor = 8.0):
        """
        Initializes and calculates the Ewald sum. Default convergence parameters have been
        specified, but you can override them if you wish.
        Arguments:
            structure - input structure that must have proper Specie on all sites, i.e.
                        Element with oxidation state. Use OxidationStateDecorator in 
                        pymatgen.core.structure_modifier for example.
            real_space_cut - Real space cutoff radius dictating how many terms are used in the 
                             real space sum. negative means determine automagically using the
                             formula given in gulp 3.1 documentation
            recip_space_cut - Reciprocal space cutoff radius. negative means determine automagically using
                              formula given in gulp 3.1 documentation
            eta - The screening parameter. negative means determine automatically.
            calculate_forces - Set to true if forces are desired
            acc_factor - No. of significant figures each sum is converged to. See the gulp manual. 
        """
        self._s = structure
        self._vol = structure.volume
        
        self._acc_factor = acc_factor

        # set screening length
        self._eta = eta if eta > 0 else (len(structure) * 0.01 / self._vol) ** (1/3) * pi        
        self._sqrt_eta = sqrt(self._eta)
        
        # acc factor used to automatically determine the optimal real and 
        # reciprocal space cutoff radii
        self._accf = sqrt(log(10 ** acc_factor))  
        
        self._rmax = real_space_cut if real_space_cut  > 0 else self._accf/self._sqrt_eta 
        self._gmax = recip_space_cut if recip_space_cut > 0 else 2* self._sqrt_eta * self._accf
        self._oxi_states = [compute_average_oxidation_state(site) for site in structure]
        self._total_q = sum(self._oxi_states)        
        self._forces = np.zeros((len(structure),3))
        self._calc_recip()
        self._calc_real_and_point()
        
    @property
    def reciprocal_space_energy(self):
        return self._recip
    
    @property
    def real_space_energy(self):
        return self._real
    
    @property
    def point_energy(self):
        return self._point
    
    @property
    def total_energy(self):
        return self._recip + self._real + self._point
    
    @property
    def forces(self):
        return self._forces
    
    def _calc_recip(self):
        """
        Perform the reciprocal space summation. Calculates the quantity
        E_recip = 1/(2PiV) sum_{G < Gmax} exp(-(G.G/4/eta))/(G.G) S(G)S(-G) where
        S(G) = sum_{k=1,N} q_k exp(-i G.r_k)
        S(G)S(-G) = |S(G)|**2
        """
        
        prefactor = 2 * pi / self._vol
        erecip = 0.0 
                
        recip = Structure(self._s.lattice.reciprocal_lattice, ["H"], [np.array([0,0,0])])
        nn = recip.get_neighbors(recip[0], self._gmax)
        for (n,dist) in nn:
            gvect = n.coords
            gsquare = np.linalg.norm(gvect) ** 2
            expval = exp(-1.0 * gsquare / (4.0 * self._eta))
                        
            #calculate the structure factor
            sreal = 0.0
            simag = 0.0
            for i in range(self._s.num_sites):
                site = self._s[i]
                exparg = np.dot(gvect, site.coords) 
                qj = self._oxi_states[i] 
                sreal += qj * cos(exparg)
                simag += qj * sin(exparg)
                pref = 2 * expval / gsquare * qj

            erecip += expval/gsquare*(sreal*sreal + simag*simag)
            #do forces if necessary
            for i in range(self._s.num_sites):
                site = self._s[i]
                exparg = np.dot(gvect, site.coords) 
                qj = self._oxi_states[i]  
                pref = 2 * expval / gsquare * qj
                self._forces[i] += prefactor * pref * gvect * (sreal * sin(exparg) - simag * cos(exparg)) * EwaldSummation.CONV_FACT
    
        #self._forces = forces
        self._recip = erecip * prefactor * EwaldSummation.CONV_FACT 
    

    def _calc_real_and_point(self):
        """
         * determines the self energy
         * 
         * -(eta/pi)**(1/2) * sum_{i=1}^{N} q_i**2
         * 
         * if cell is charged a compensating background is added (i.e. a G=0 term)
         *  
         * @return
         */
        """

        ereal = 0.0
        epoint = 0.0
        forcepf = 2.0 * self._sqrt_eta/sqrt(pi) 
        all_nn = self._s.get_all_neighbors(self._rmax)
        for i in range(self._s.num_sites):
            site = self._s[i]
            nn = all_nn[i] #self._s.get_neighbors(site, self._rmax)
            qi = self._oxi_states[i]
            epoint += qi*qi
            for (nsite, rij)  in nn:
                qj = compute_average_oxidation_state(nsite) 
                erfcval = erfc(self._sqrt_eta*rij)
                ereal += erfcval * qi * qj / rij
                fijpf = qj / rij / rij / rij* (erfcval + forcepf * rij * exp(-self._eta * rij * rij)) 
                self._forces[i] += fijpf * (site.coords - nsite.coords) * qi * EwaldSummation.CONV_FACT
                    
        self._real = ereal * 0.5 * EwaldSummation.CONV_FACT
        
        epoint *= -1.0 * sqrt(self._eta/pi)
        #add compensating jellium term
        epoint += self._total_q * pi / (2.0 * self._vol * self._eta)
        self._point = epoint * EwaldSummation.CONV_FACT 
    
    @property
    def eta(self):
        return self._eta
    
    def __str__(self):
        output = ["Real = " + str(self.real_space_energy)]
        output.append("Reciprocal = " + str(self.reciprocal_space_energy))
        output.append("Point = " + str(self.point_energy))
        output.append("Total = " + str(self.total_energy))
        output.append("Forces:\n" + str(self.forces))
        return "\n".join(output)
