import os

import numpy as np

from tradssat import CULFile, ECOFile
from .mgr import get_dssat_subdir, PeriphFileMgr


class PeriphGenMgr(PeriphFileMgr):
    def __init__(self, crops, cultivars, treatments, model=None):
        self.crops = crops
        self.cultivars = cultivars

        self.files = {
            trt: GeneticMgr(get_model(crp, model), cult) for trt, crp, cult in zip(treatments, crops, cultivars)
        }

    def get_val(self, var, trt):
        return self.files[trt].get_val(var)

    def set_val(self, var, val, trt):
        return self.files[trt].set_val(var, val)

    def variables(self):
        return {str(vr) for f in self.files.values() for vr in f.variables()}


class GeneticMgr(object):
    def __init__(self, crop, cult):
        self.crop = crop
        self.cult = cult

        geno_dir = get_dssat_subdir('Genotype')

        self.eco_file = self.cult_file = None
        for f in os.listdir(geno_dir):
            name = os.path.split(f)[1]
            if CULFile.matches_file(name) and name.startswith(self.crop):
                self.cult_file = CULFile(os.path.join(geno_dir, f))
            elif ECOFile.matches_file(name) and name.startswith(self.crop):
                self.eco_file = ECOFile(os.path.join(geno_dir, f))

            if self.eco_file is not None and self.cult_file is not None:
                break

        if self.cult_file is None:
            raise ValueError('No cultivar file (.CUL) found for crop "{}".'.format(self.crop))

        eco_codes = self.cult_file.get_val('ECO#')
        cult_codes = self.cult_file.get_val('VAR#')
        eco = eco_codes[cult_codes == self.cult]

        self.eco_n = np.where(self.eco_file.get_val('ECO#') == eco)
        self.cult_n = np.where(cult_codes == cult)

    def get_val(self, var):
        if var in self.cult_file.variables():
            return self.cult_file.get_val(var)
        elif self.eco_file is not None and var in self.eco_file.variables():
            return self.eco_file.get_val(var)
        else:
            raise ValueError('No genetic variable named "{}" was found.'.format(var))

    def set_val(self, var, val):
        if var in self.cult_file.variables():
            return self.cult_file.set_val(var, val)
        elif self.eco_file is not None and var in self.eco_file.variables():
            return self.eco_file.set_val(var, val)
        else:
            raise ValueError('No genetic variable named "{}" was found.'.format(var))

    def variables(self):
        vars_ = {*self.cult_file.variables()}
        if self.eco_file is not None:
            vars_.update(self.eco_file.variables())

        return vars_


_crop_models = {
    'AL': ['ALFRM'],
    'BA': ['BACER', 'BACRP'],
    'BH': ['BHGRO'],
    'BM': ['BMFRM', 'BMGRO'],
    'BN': ['BNGRO'],
    'BR': ['BRFRM', 'BRGRO'],
    'BS': ['BSCER'],
    'CB': ['CBGRO'],
    'CH': ['CHGRO'],
    'CN': ['CNGRO'],
    'CO': ['COGRO'],
    'CP': ['CPGRO'],
    'CS': ['CSCAS', 'CSYCA'],
    'FB': ['FBGRO'],
    'G0': ['G0GRO'],
    'GB': ['GBGRO'],
    'ML': ['MLCER'],
    'MZ': ['MZCER', 'MZIXM'],
    'PI': ['PIALO'],
    'PN': ['PNGRO'],
    'PP': ['PPGRO'],
    'PR': ['PRGRO'],
    'PT': ['PTSUB'],
    'RI': ['RICER', 'RIORZ'],
    'SB': ['SBGRO'],
    'SC': ['SCCAN', 'SCCSP'],
    'SF': ['SFGRO'],
    'SG': ['SGCER'],
    'SU': ['SUGRO'],
    'SW': ['SWCER'],
    'TM': ['TMGRO'],
    'TN': ['TNARO'],
    'VB': ['VBGRO'],
    'WH': ['WHAPS', 'WHCER', 'WHCRP']
}


def get_model(crop, mod):
    try:
        m = _crop_models[crop]
    except KeyError:
        raise ValueError('No model defined for crop "{}" in traDSSAT.'.format(crop))
    if mod in m:
        return mod
    else:
        return m[0]
