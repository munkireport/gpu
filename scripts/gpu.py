#!/usr/local/munkireport/munkireport-python3


"""
GPU  info for munkireport.
Will return all details about connected GPUs and video cards
"""

import subprocess
import os
import plistlib
import sys

sys.path.insert(0, '/usr/local/munki')
sys.path.insert(0, '/usr/local/munkireport')

from munkilib import FoundationPlist

def get_gpu_info():
    '''Uses system profiler to get GPU info for this machine.'''
    cmd = ['/usr/sbin/system_profiler', 'SPDisplaysDataType', '-xml']
    proc = subprocess.Popen(cmd, shell=False, bufsize=-1,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, unused_error) = proc.communicate()
    try:
        try:
            plist = plistlib.readPlistFromString(output)
        except AttributeError as e:
            plist = plistlib.loads(output)
        # system_profiler xml is an array
        sp_dict = plist[0]
        items = sp_dict['_items']
        return items
    except Exception:
        return {}

def flatten_gpu_info(array, localization):
    '''Un-nest GPUs, return array with objects with relevant keys'''
    out = []
    for obj in array:
        device = {'model': '','metal': 0}
        for item in obj:
            if item == '_items':
                out = out + flatten_gpu_info(obj['_items'])
            elif item == 'spdisplays_device-id':
                device['device_id'] = obj[item]
            elif item == 'spdisplays_gmux-version':
                device['gmux_version'] = obj[item]
            elif item == 'spdisplays_efi-version':
                device['efi_version'] = obj[item]
            elif item == 'spdisplays_pcie_width':
                device['pcie_width'] = obj[item]
            elif item == 'spdisplays_revision-id':
                device['revision_id'] = obj[item]
            elif item == 'spdisplays_rom-revision':
                device['rom_revision'] = obj[item]
            elif item == 'spdisplays_vendor':
                device['vendor'] = obj[item]
            elif item == 'spdisplays_vram_shared':
                device['vram_shared'] = obj[item]
            elif item == 'spdisplays_vram':
                device['vram'] = obj[item]
            elif item == 'sppci_model':
                device['model'] = obj[item]
            elif item == 'sppci_cores':
                device['num_cores'] = obj[item]
            elif item == 'sppci_slot_name':
                device['slot_name'] = obj[item]
            elif item == 'spdisplays_ndrvs':
                device['ndrvs'] = obj[item]
            elif item == 'spdisplays_metalfamily' and obj[item] == 'spdisplays_mtlgpufamilymac1':
                device['metal_version'] = get_metal_version(obj[item], localization)
                device['metal'] = 8
            elif item == 'spdisplays_metalfamily' and obj[item] == 'spdisplays_mtlgpufamilyapple7':
                device['metal_version'] = get_metal_version(obj[item], localization)
                device['metal'] = 7
            elif item == 'spdisplays_metalfamily' and obj[item] == 'spdisplays_mtlgpufamilymac2':
                device['metal_version'] = get_metal_version(obj[item], localization)
                device['metal'] = 6
            elif item == 'spdisplays_metal' and obj[item] == 'spdisplays_metalfeaturesetfamily21':
                device['metal_version'] = get_metal_version(obj[item], localization)
                device['metal'] = 5
            elif item == 'spdisplays_metal' and obj[item] == 'spdisplays_metalfeaturesetfamily14':
                device['metal_version'] = get_metal_version(obj[item], localization)
                device['metal'] = 4
            elif item == 'spdisplays_metal' and obj[item] == 'spdisplays_metalfeaturesetfamily13':
                device['metal_version'] = get_metal_version(obj[item], localization)
                device['metal'] = 3 
            elif item == 'spdisplays_metal' and obj[item] == 'spdisplays_metalfeaturesetfamily12':
                device['metal_version'] = get_metal_version(obj[item], localization)
                device['metal'] = 2
            elif item == 'spdisplays_metal' and (obj[item] == 'spdisplays_supported' or obj[item] == 'spdisplays_metalfeaturesetfamily11'):
                device['metal_version'] = get_metal_version(obj[item], localization)
                device['metal'] = 1
            elif item == 'spdisplays_mtlgpufamilysupport' :
                try:
                    device['metal_version'] = localization[obj[item]].strip()
                except KeyError as error:
                    device['metal_version'] = obj[item].strip() 
        out.append(device)
    return out
    
def get_metal_version(metal_version, localization):
    try:
        return localization[metal_version].strip()
    except KeyError as error:
        return metal_version.strip() 

def main():
    """Main"""

    # Get results
    result = dict()
    info = get_gpu_info()

    # Read in English localizations from SystemProfiler
    if os.path.isfile('/System/Library/SystemProfiler/SPDisplaysReporter.spreporter/Contents/Resources/en.lproj/Localizable.strings'):
        localization = FoundationPlist.readPlist('/System/Library/SystemProfiler/SPDisplaysReporter.spreporter/Contents/Resources/en.lproj/Localizable.strings')
    elif os.path.isfile('/System/Library/SystemProfiler/SPDisplaysReporter.spreporter/Contents/Resources/English.lproj/Localizable.strings'):
        localization = FoundationPlist.readPlist('/System/Library/SystemProfiler/SPDisplaysReporter.spreporter/Contents/Resources/English.lproj/Localizable.strings')
    elif os.path.isfile('/System/Library/SystemProfiler/SPDisplaysReporter.spreporter/Contents/Resources/Localizable.loctable'):
        localization_dict = FoundationPlist.readPlist('/System/Library/SystemProfiler/SPDisplaysReporter.spreporter/Contents/Resources/Localizable.loctable')
        if "en" in localization_dict:
            localization = localization_dict["en"]
        elif "English" in localization_dict:
            localization = localization_dict["English"]
        else:
            localization = {}
    else:
        localization = {}

    result = flatten_gpu_info(info, localization)
    
    # Write GPU results to cache
    cachedir = '%s/cache' % os.path.dirname(os.path.realpath(__file__))
    output_plist = os.path.join(cachedir, 'gpuinfo.plist')
    try:
        plistlib.writePlist(result, output_plist)
    except:
        with open(output_plist, 'wb') as fp:
            plistlib.dump(result, fp, fmt=plistlib.FMT_XML)

if __name__ == "__main__":
    main()
