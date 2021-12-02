# from HiLITDECoreLibraries.Utilities.decorator import scrape_data

# @scrape_data
def doseunit_validation(unit):
    unit_list = ['%', '% (V/V)', '% (W/V)', '% (W/W)', '/min', '/µl', 'A', 'ATU', 'AU/ml',
                 'AgU', 'AgU/ml', 'Bq', 'Bq/g', 'Bq/kg', 'Bq/l', 'Bq/mg', 'Bq/ml', 'Bq/µg',
                 'Bq/µl', 'C', 'CCID50', 'CCID50/dose', 'CFU/g', 'CFU/ml', 'Ci', 'Ci/g', 'Ci/kg',
                 'Ci/l', 'Ci/mg', 'Ci/ml', 'Ci/µg', 'Ci/µl', 'Co', 'DAgU', 'DAgU/ml', 'DF', 'EID50',
                 'EID50/dose', 'ELISA unit', 'ELISA unit/dose', 'ELISA unit/ml', 'F', 'FAI50',
                 'FAI50/dose', 'GBq', 'GBq/Kg', 'GBq/g', 'GBq/l', 'GBq/mg', 'GBq/ml', 'GBq/µg',
                 'GBq/µl', 'GM/DL', 'GM/L', 'Gtt', 'Gy', 'H', 'Hz', 'IOU', 'IU', 'IU/g', 'IU/kg',
                 'IU/l', 'IU/mg', 'IU/ml', 'J', 'K', 'KBq/kg', 'KIU/ml', 'LB', 'LU', 'LU/g', 'LU/ml',
                 'LacU', 'LfU', 'LfU/ml', 'MBq', 'MBq/g', 'MBq/kg', 'MBq/l', 'MBq/mg', 'MBq/ml', 'MBq/µg',
                 'MBq/µl', 'MICROGRAM/L', 'MICROMOLE/L', 'MUSP units', 'N', 'N/A', 'NIH units/cm2', 'OZ',
                 'P', 'PFU', 'PFU e.1000 mouse LD50', 'PFU/dose', 'PFU/ml', 'PNU/ml', 'PPM', 'QS', 'S', 'SEC',
                 'Sv', 'T', 'TCID50/dose', 'Torr', 'U', 'U/L', 'U/g', 'U/ml', 'USP unit', 'V', 'W', 'Wb', 'ad',
                 'anti-Xa IU', 'anti-Xa IU/ml', 'billion CFU', 'billion CFU/g', 'billion CFU/ml', 'billion organisms',
                 'billion organisms/g', 'billion organisms/mg', 'billion organisms/ml', 'cd', 'cm2', 'd', 'fL', 'g',
                 'g (titre)', 'g/dL', 'g/g', 'g/l', 'g/m2', 'g/m3', 'g/ml', 'g/mmol', 'g/mol', 'h', 'kBq', 'kBq/g',
                 'kBq/l', 'kBq/mg', 'kBq/ml', 'kBq/µg', 'kBq/µl', 'kIU', 'kUSP units', 'kat', 'kg', 'kg/l', 'kg/m2',
                 'kg/m3', 'kunits', 'l', 'lm', 'log10 CCID50', 'log10 CCID50/dose', 'log10 EID50', 'log10 EID50/dose',
                 'log10 ELISA unit', 'log10 ELISA unit/dose', 'log10 FAI50', 'log10 FAI50/dose', 'log10 PFU',
                 'log10 PFU/dose', 'log10 TCID50', 'log10 TCID50/dose', 'log10/ml', 'lx', 'm', 'm2', 'm3',
                 'mCi', 'mCi/g', 'mCi/kg', 'mCi/l', 'mCi/mg', 'mCi/ml', 'mCi/µg', 'mCi/µl', 'mEq', 'mEq/g', 'mEq/kg',
                 'mEq/l', 'mEq/mg', 'mEq/ml', 'mEq/µg', 'mEq/µl', 'mL/min/1.73m2', 'mOsm/kg', 'mg', 'mg (titer)',
                 'mg/L', 'mg/dL', 'mg/day', 'mg/g', 'mg/kg', 'mg/l', 'mg/m2', 'mg/m3', 'mg/mg', 'mg/ml', 'mg/mmol',
                 'million CFU', 'million CFU/g', 'million CFU/ml', 'million IU', 'million USP units',
                 'million organisms', 'million organisms/g', 'million organisms/mg', 'million organisms/ml',
                 'million unit', 'min', 'mkat', 'ml', 'ml/cm2', 'mm', 'mmHg', 'mmol', 'mmol/g', 'mmol/kg', 'mmol/l',
                 'mmol/ml', 'mol', 'mol/g', 'mol/kg', 'mol/l', 'mol/mg', 'mol/ml', 'nCi', 'ng', 'ng/mL', 'nkat', 'nl',
                 'nmol', 'nmol/ml', 'ohm', 'per thousand', 'pg', 'pkat', 'pock forming unit', 'pressor units/ml',
                 'r/min', 's', 't', 'thousand CFU', 'thousand CFU/g', 'thousand CFU/mL', 'thousand organisms',
                 'thousand organisms/g', 'thousand organisms/ml', 'titre', 'tuberculin unit', 'tuberculin unit/ml',
                 'umol/L', 'ut', 'x104 /µl', '°', '°C', 'µCi', 'µCi/g', 'µCi/kg', 'µCi/l', 'µCi/mg', 'µCi/ml',
                 'µCi/µg', 'µCi/µl', 'µg', 'µg/kg', 'µg/l', 'µg/m2', 'µg/m3', 'µg/ml', 'µg/µl', 'µkat', 'µl', 'µl/ml',
                 'µmol', 'µmol/l', 'µmol/ml']
    if unit in unit_list:
        return unit
    else:
        return ""

# @scrape_data
def split_combdata(data):
    data = data.split('||')[4:]
    data = ' '.join(data)
    return data
