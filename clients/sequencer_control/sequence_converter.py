import os
import sys
import json

channel_map = {
        '3D MOT AOM': '3D MOT AOM@A00',
        '3D MOT Shutter': '3D MOT Shutter@A01',
        'Fluores. AOM': 'Fluores. AOM@A02',
        'Fluores. Shutter': 'Fluores. Shutter@A03',
        'Abs. AOM': 'Abs. AOM@A04',
        'Abs. Shutter': 'Abs Shutter@A05',
        '2D Mot Shutter': '2D MOT Shutter@A06',
        'Zeeman Shutter': 'Zeeman Shutter@A07',
        'AH Enable': 'AH Enable@A08',
        'AH Bottom Enable': 'AH Bottom Enable@A09',
        'TTLA10': 'V Camera Trig.@A10',
        'TTLA11': 'H Camera Trig@A11',
        'TTLA12': 'Dimple AOM@A12',
        'TTLA13': 'HODT AOM@A13',
        'TTLA14': 'VODT AOM@A14',
        'Spec. Lock Enable': 'Spec. Lock Enable@A15',

        'TTLB00': 'Tickle Enable@B00',
        'TTLB01': 'TTLB01@B01',
        'TTLB02': 'Spin Pol. Drive sw@B02',
        'TTLB03': 'LC Wave@B03',
        'TTLB04': 'TTLB04@B04',
        'TTLB05': 'TTLB05@B05',
        'TTLB06': 'HODT Shutter@B06',
        'TTLB07': 'VODT Shutter@B07',
        'TTLB08': 'Dimple Shutter@B08',
        'TTLB09': '813 H1 AOM@B09',
        'TTLB10': '813 H2 AOM@B10',
        'TTLB11': '813 V AOM@B11',
        'TTLB12': 'TTLB12@B12',
        'TTLB13': 'TTLB13@B13',
        'TTLB14': 'TTLB14@B14',
        'TTLB15': 'TTLB15@B15',
        
        'TTLC00': 'RM Gain Switch@C00',
        'TTLC01': 'TTLC01@C01',
        'TTLC02': 'TTLC02@C02',
        'TTLC03': 'TTLC03@C03',
        'TTLC04': 'TTLC04@C04',
        'TTLC05': 'TTLC05@C05',
        'TTLC06': 'TTLC06@C06',
        'TTLC07': 'TTLC07@C07',
        'TTLC08': 'TTLC08@C08',
        'TTLC09': 'TTLC09@C09',
        'TTLC10': 'TTLC10@C10',
        'TTLC11': 'TTLC11@C11',
        'TTLC12': 'TTLC12@C12',
        'TTLC13': 'TTLC13@C13',
        'TTLC14': 'TTLC14@C14',
        'TTLC15': 'ODT Servo Enable@C15',
        
        'Alpha AOM': 'Alpha AOM@D00',
        'Alpha Shutter': 'Alpha Shutter@D01',
        'Beta AOM': 'Beta AOM@D02',
        'Beta Shutter': 'Beta Shutter@D03',
        'Spin Pol. AOM': 'Spin Pol. AOM@D04',
        'Spin Pol. Shutter': 'Spin Pol. Shutter@D05',
        '679 AOM': '679 AOM@D06',
        '707 AOM': '707 AOM@D07',
        'Repump Shutter': 'Repump Shutter@D08',
        'TTLD09': 'RM FM Trigger@D09',
        'TTLD10': 'TTLD10@D10',
        'TTLD11': 'TTLD11@D11',
        'TTLD12': 'TTLD12@D12',
        'TTLD13': 'TTLD13@D13',
        'Aosense Heater Enable': 'AOSence Heater Enable@D14',
        'E Trigger': 'Trigger@D15',

        'Alpha Intensity': 'Alpha Intensity@E00',
        'Beta Intensity': 'Beta Intensity@E01',
        'X Comp. Coil': 'X Comp. Coil@E02',
        'Y Comp. Coil': 'Y Comp. Coil@E03',
        'Z Comp. Coil': 'Z Comp. Coil@E04',
        'MOT Coil': 'MOT Coil@E05',
        'DACE06': 'HODT Intensity@E06',
        'DACE07': 'Dimple Intensity@E07',
    }

new_channels = [
        'VODT Intensity@F00',
        '813 H1 Intensity@F01',
        '813 H2 Intensity@F02',
        '813 V Intensity@F03',
        'DACF04@F04',
        'DACF05@F05',
        'DACF06@F06',
        'DACF07@F07',
        ]

def replace_file(filename):
    with open(filename, 'r') as infile:
        old_sequence = [eval(line.split('\n')[:-1][0]) for line in infile.readlines()]
    new_sequence = {}
    for ok, nk in channel_map.items():
        new_sequence[nk] = [os[1][ok] for os in old_sequence]
    for nc in new_channels:
        new_sequence[nc] = [{'type': 'lin', 'vf': 0} for os in old_sequence]
    new_sequence['digital@T'] = [os[0] for os in old_sequence]
    with open(filename+'.new', 'w') as outfile:
        json.dump(new_sequence, outfile)



if __name__ == '__main__':
    filenames = os.listdir('.')
    for fn in filenames:
        try:
            replace_file(fn)
        except:
            print 'could not fix {}'.format(fn)
