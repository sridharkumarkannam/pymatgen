#!/usr/bin/python
import unittest
import os

import numpy as np

from pymatgen.io.cifio import CifParser, CifWriter
from pymatgen.io.vaspio import Poscar
from pymatgen.core.periodic_table import Element, Specie
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure

class  CifIOTest(unittest.TestCase):
    
    def setUp(self):
        self.module_dir = os.path.dirname(os.path.abspath(__file__))

    def test_CifParser(self):
        parser = CifParser(os.path.join(self.module_dir,'vasp_testfiles','LiFePO4.cif'))
        for s in parser.get_structures(True):
            self.assertEqual(s.formula, "Li4 Fe4 P4 O16", "Incorrectly parsed cif.")
            self.assertEqual(s[0].specie.oxi_state, 1, "Incorrectly parsed cif.")
        
        #test for disordered structures
        parser = CifParser(os.path.join(self.module_dir,'vasp_testfiles','Li10GeP2S12.cif'))
        for s in parser.get_structures(True):
            self.assertEqual(s.formula, "Li20.2 Ge2.06 P3.94 S24", "Incorrectly parsed cif.")
      
    def test_CifWriter(self):
        filepath = os.path.join(self.module_dir, 'vasp_testfiles','POSCAR.gz')
        poscar = Poscar.from_file(filepath)
        writer = CifWriter(poscar.struct)
        expected_cif_str = """#\#CIF1.1
##########################################################################
#               Crystallographic Information Format file 
#               Produced by PyCifRW module
# 
#  This is a CIF file.  CIF has been adopted by the International
#  Union of Crystallography as the standard for data archiving and 
#  transmission.
#
#  For information on this file format, follow the CIF links at
#  http://www.iucr.org
##########################################################################

data_FePO4
_symmetry_space_group_name_H-M          'P 1'
_cell_length_a                          10.4117668699
_cell_length_b                          6.06717187997
_cell_length_c                          4.75948953998
_cell_angle_alpha                       90.0
_cell_angle_beta                        90.0
_cell_angle_gamma                       90.0
_chemical_name_systematic               'Generated by pymatgen'
_symmetry_Int_Tables_number             1
_chemical_formula_structural            FePO4
_chemical_formula_sum                   'Fe4 P4 O16'
_cell_volume                            300.65685512
_cell_formula_units_Z                   4
loop_
  _symmetry_equiv_pos_site_id
  _symmetry_equiv_pos_as_xyz
   1  'x, y, z'
 
loop_
  _atom_site_type_symbol
  _atom_site_symmetry_multiplicity
  _atom_site_fract_x
  _atom_site_fract_y
  _atom_site_fract_z
  _atom_site_attached_hydrogens
  _atom_site_B_iso_or_equiv
  _atom_site_label
  _atom_site_occupancy
   Fe  1  0.21872822  0.75  0.47486711  0  .  Fe1  1
   Fe  1  0.28127178  0.25  0.97486711  0  .  Fe2  1
   Fe  1  0.71872822  0.75  0.02513289  0  .  Fe3  1
   Fe  1  0.78127178  0.25  0.52513289  0  .  Fe4  1
   P  1  0.09461309  0.25  0.41824327  0  .  P5  1
   P  1  0.40538691  0.75  0.91824327  0  .  P6  1
   P  1  0.59461309  0.25  0.08175673  0  .  P7  1
   P  1  0.90538691  0.75  0.58175673  0  .  P8  1
   O  1  0.04337231  0.75  0.70713767  0  .  O9  1
   O  1  0.09664244  0.25  0.74132035  0  .  O10  1
   O  1  0.16570974  0.04607233  0.28538394  0  .  O11  1
   O  1  0.16570974  0.45392767  0.28538394  0  .  O12  1
   O  1  0.33429026  0.54607233  0.78538394  0  .  O13  1
   O  1  0.33429026  0.95392767  0.78538394  0  .  O14  1
   O  1  0.40335756  0.75  0.24132035  0  .  O15  1
   O  1  0.45662769  0.25  0.20713767  0  .  O16  1
   O  1  0.54337231  0.75  0.79286233  0  .  O17  1
   O  1  0.59664244  0.25  0.75867965  0  .  O18  1
   O  1  0.66570974  0.04607233  0.21461606  0  .  O19  1
   O  1  0.66570974  0.45392767  0.21461606  0  .  O20  1
   O  1  0.83429026  0.54607233  0.71461606  0  .  O21  1
   O  1  0.83429026  0.95392767  0.71461606  0  .  O22  1
   O  1  0.90335756  0.75  0.25867965  0  .  O23  1
   O  1  0.95662769  0.25  0.29286233  0  .  O24  1
 
"""
        self.assertEqual(str(writer), expected_cif_str, "Incorrectly generated cif string")

    def test_disordered(self):
        si = Element("Si")
        n = Element("N")
        coords = list()
        coords.append(np.array([0,0,0]))
        coords.append(np.array([0.75,0.5,0.75]))
        lattice = Lattice(np.array([[ 3.8401979337, 0.00, 0.00],[1.9200989668, 3.3257101909, 0.00],[0.00,-2.2171384943,3.1355090603]]))
        struct = Structure(lattice,[si,{si:0.5, n:0.5}],coords)
        writer = CifWriter(struct)
        ans = """#\#CIF1.1
##########################################################################
#               Crystallographic Information Format file 
#               Produced by PyCifRW module
# 
#  This is a CIF file.  CIF has been adopted by the International
#  Union of Crystallography as the standard for data archiving and 
#  transmission.
#
#  For information on this file format, follow the CIF links at
#  http://www.iucr.org
##########################################################################

data_Si3N
_symmetry_space_group_name_H-M          'P 1'
_cell_length_a                          3.8401979337
_cell_length_b                          3.84019899434
_cell_length_c                          3.84019793372
_cell_angle_alpha                       119.999990864
_cell_angle_beta                        90.0
_cell_angle_gamma                       60.0000091373
_chemical_name_systematic               'Generated by pymatgen'
_symmetry_Int_Tables_number             1
_chemical_formula_structural            Si3N
_chemical_formula_sum                   'Si1.5 N0.5'
_cell_volume                            40.0447946443
_cell_formula_units_Z                   0
loop_
  _symmetry_equiv_pos_site_id
  _symmetry_equiv_pos_as_xyz
   1  'x, y, z'
 
loop_
  _atom_site_type_symbol
  _atom_site_symmetry_multiplicity
  _atom_site_fract_x
  _atom_site_fract_y
  _atom_site_fract_z
  _atom_site_attached_hydrogens
  _atom_site_B_iso_or_equiv
  _atom_site_label
  _atom_site_occupancy
   Si  1  0  0  0  0  .  Si1  1
   Si  1  0.75  0.5  0.75  0  .  Si2  0.5
   N  1  0.75  0.5  0.75  0  .  N3  0.5
 
"""
        self.assertEqual(str(writer),ans)
    
    def test_specie_cifwriter(self):
        si4 = Specie("Si", 4)
        si3 = Specie("Si",3)
        n = Specie("N", -3)
        coords = list()
        coords.append(np.array([0,0,0]))
        coords.append(np.array([0.75,0.5,0.75]))
        coords.append(np.array([0.5,0.5,0.5]))
        lattice = Lattice(np.array([[ 3.8401979337, 0.00, 0.00],[1.9200989668, 3.3257101909, 0.00],[0.00,-2.2171384943,3.1355090603]]))
        struct = Structure(lattice,[si4,{si3:0.5, n:0.5}, n],coords)
        writer = CifWriter(struct)
        ans = """#\#CIF1.1
##########################################################################
#               Crystallographic Information Format file 
#               Produced by PyCifRW module
# 
#  This is a CIF file.  CIF has been adopted by the International
#  Union of Crystallography as the standard for data archiving and 
#  transmission.
#
#  For information on this file format, follow the CIF links at
#  http://www.iucr.org
##########################################################################

data_SiSi2N3
_symmetry_space_group_name_H-M          'P 1'
_cell_length_a                          3.8401979337
_cell_length_b                          3.84019899434
_cell_length_c                          3.84019793372
_cell_angle_alpha                       119.999990864
_cell_angle_beta                        90.0
_cell_angle_gamma                       60.0000091373
_chemical_name_systematic               'Generated by pymatgen'
_symmetry_Int_Tables_number             1
_chemical_formula_structural            SiN
_chemical_formula_sum                   'Si1.5 N1.5'
_cell_volume                            40.0447946443
_cell_formula_units_Z                   0
loop_
  _symmetry_equiv_pos_site_id
  _symmetry_equiv_pos_as_xyz
   1  'x, y, z'
 
loop_
  _atom_type_symbol
  _atom_type_oxidation_number
   Si4+  4
   N3-  -3
   Si3+  3
 
loop_
  _atom_site_type_symbol
  _atom_site_symmetry_multiplicity
  _atom_site_fract_x
  _atom_site_fract_y
  _atom_site_fract_z
  _atom_site_attached_hydrogens
  _atom_site_B_iso_or_equiv
  _atom_site_label
  _atom_site_occupancy
   Si4+  1  0  0  0  0  .  Si1  1
   N3-  1  0.75  0.5  0.75  0  .  N2  0.5
   Si3+  1  0.75  0.5  0.75  0  .  Si3  0.5
   N3-  1  0.5  0.5  0.5  0  .  N4  1
 
"""
        self.assertEqual(str(writer),ans)
        
if __name__ == '__main__':
    unittest.main()

