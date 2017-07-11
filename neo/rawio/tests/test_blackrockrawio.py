# -*- coding: utf-8 -*-
"""
Tests of neo.rawio.examplerawio
"""

# needed for python 3 compatibility
from __future__ import unicode_literals, print_function, division, absolute_import

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from  neo.rawio.blackrockrawio import BlackrockRawIO
from neo.rawio.tests.common_rawio_test import BaseTestRawIO

import numpy as np
from numpy.testing import assert_equal

try:
    import scipy.io
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False


class TestBlackrockRawIO(BaseTestRawIO, unittest.TestCase, ):
    rawioclass = BlackrockRawIO
    files_to_test = ['FileSpec2.3001']

    files_to_download = [
        'FileSpec2.3001.nev',
        'FileSpec2.3001.ns5',
        'FileSpec2.3001.ccf',
        'FileSpec2.3001.mat']

    @unittest.skipUnless(HAVE_SCIPY, "requires scipy")
    def test_compare_blackrockio_with_matlabloader(self):
        """
        This test compares the output of ReachGraspIO.read_block() with the
        output generated by a Matlab implementation of a Blackrock file reader
        provided by the company. The output for comparison is provided in a
        .mat file created by the script create_data_matlab_blackrock.m.
        The function tests LFPs, spike times, and digital events on channels
        80-83 and spike waveforms on channel 82, unit 1.
        For details on the file contents, refer to FileSpec2.3.txt
        
        Ported to the rawio API by Samuel Garcia.
        """

        # Load data from Matlab generated files
        ml = scipy.io.loadmat(self.get_filename_path('FileSpec2.3001.mat'))
        
        lfp_ml = ml['lfp']  # (channel x time) LFP matrix
        ts_ml = ml['ts']  # spike time stamps
        elec_ml = ml['el']  # spike electrodes
        unit_ml = ml['un']  # spike unit IDs
        wf_ml = ml['wf']  # waveform unit 1 channel 1
        mts_ml = ml['mts']  # marker time stamps
        mid_ml = ml['mid']  # marker IDs

        # Load data in channels 1-3 from original data files using the Neo
        # BlackrockIO
        reader = BlackrockIO(filename=self.get_filename_path('FileSpec2.3001'))
        reader.parse_header()
        
        # Check if analog data on channels 1-8 are equal
        self.assertGreater(reader.signal_channels_count(), 0)
        for c in range(0, 8):
            raw_sigs = reader.get_analogsignal_chunk(channel_indexes=[c])
            raw_sigs = raw_sigs.flatten()
            assert_equal(raw_sigs[:-1], lfp_ml[c, :])
        
        # Check if spikes in channels are equal
        nb_unit = reader.unit_channels_count()
        for unit_index in range(nb_unit):
            unit_name = reader.header['unit_channels'][unit_index]['name']
            # name is chXX#YY where XX is channel_id and YY is unit_id
            channel_id, unit_id = unit_name.split('#')
            channel_id = int(channel_id.replace('ch', ''))
            unit_id = int(unit_id)
            
            matlab_spikes = ts_ml[(elec_ml == channel_id) & (unit_ml == unit_id)]
            
            io_spikes = reader.spike_timestamps(unit_index=unit_index)
            assert_equal(io_spikes, matlab_spikes)

            # Check waveforms of channel 1, unit 0
            if channel_id == 1 and unit_id == 0:
                io_waveforms = reader.spike_raw_waveforms(unit_index=unit_index)
                io_waveforms = io_waveforms[:, 0, :]#remove dim 1
                assert_equal(io_waveforms, wf_ml)
        
        
        # Check if digital input port events are equal
        nb_ev_chan = reader.event_channels_count()
        #~ print(reader.header['event_channels'])
        for ev_chan in range(nb_ev_chan):
            name = reader.header['event_channels']['name'][ev_chan]
            #~ print(name)
            if name == 'digital_input_port':
                all_timestamps, _, labels = reader.event_timestamps(event_channel_index=ev_chan)
                
                for label in np.unique(labels):
                    python_digievents = all_timestamps[labels==label]
                    matlab_digievents = mts_ml[mid_ml==int(label)]
                    assert_equal(python_digievents, matlab_digievents)
        


import neo
#~ import neo.rawio.blackrockrawio
from  neo.rawio.blackrockrawio import BlackrockRawIO
from neo.io import BlackrockIO


import time

def test_BlackrockRawIO():
    #~ filename = '/media/sgarcia/SamCNRS/DataSpikeSorting/elodie/Dataset 3/20161124-112218-001'
    #~ filename = '/media/sgarcia/SamCNRS/DataSpikeSorting/elodie/Nouveaux_datasets/micro_VS10_SAB 1 600ms/20160627-155334-001'
    #~ filename = '/media/sgarcia/SamCNRS/DataSpikeSorting/elodie/Nouveaux_datasets/micro_VS10_SAB 1 600ms/20160627-155334-001'
    #~ filename = '/home/samuel/Documents/projet/DataSpikeSorting/elodie/Dataset 3/20161124-112218-001.ns5'
    #~ filename = '/home/sgarcia/Documents/projet/tridesclous_examples/20160627-161211-001'
    #~ filename = '/home/sgarcia/Documents/files_for_testing_neo/blackrock/FileSpec2.3001.ns5'
    filename = '/home/samuel/Documents/files_for_testing_neo/blackrock/FileSpec2.3001.ns5'
    
    
    
    reader = BlackrockRawIO(filename=filename, nsx_to_load=5)
    reader.parse_header()
    print(reader)
    
    assert reader.block_count()==1
    
    assert reader.segment_count(0)==1
    
    # Acces 10000 chunk of 1024 samples for 10 channels
    nb_chunk = 10000
    chunksize = 1024
    #~ channel_indexes = np.arange(20,30)
    channel_indexes = np.arange(5,10)
    
    t0 = time.perf_counter()
    for i in range(nb_chunk):
        i_start = i*chunksize
        i_stop = (i+1)*chunksize
        raw_chunk = reader.get_analogsignal_chunk(block_index=0, seg_index=0,
                            i_start=i_start, i_stop=i_stop,  channel_indexes=channel_indexes)
        #~ print(sig_chunk.shape)
    t1 = time.perf_counter()
    print('acces {} chunk of {} samples in {:0.3f} s'.format(nb_chunk,chunksize, t1-t0))
    
    sig_shape = reader.analogsignal_shape(0,0)
    #~ print('sig_shape', sig_shape)
    
    channel_names = reader.header['signal_channels']['name'][[1,4,3,7]]
    #~ print(channel_names)
    
    raw_chunk = reader.get_analogsignal_chunk(block_index=0, seg_index=0,
                            i_start=0, i_stop=1024,  channel_names=channel_names)
    
    float_chunk = reader.rescale_signal_raw_to_float(raw_chunk, dtype='float64', channel_names=channel_names)
    
    
    #~ import matplotlib.pyplot as plt
    #~ fig, axs = plt.subplots(nrows=2, sharex=True)
    #~ axs[0].plot(raw_chunk)
    #~ axs[1].plot(float_chunk)
    #~ plt.show()
    print(reader.header['unit_channels'])
    nb_unit = reader.unit_channels_count()
    for unit_index in range(nb_unit):
        print()
        print(reader.header['unit_channels'][unit_index])
        
        nb =  reader.spike_count(unit_index=unit_index)
        print('nb', nb)
        spike_timestamp = reader.spike_timestamps(unit_index=unit_index, t_start=None, t_stop=None)
        print(spike_timestamp.shape)
        print(spike_timestamp[:10])
        spike_times = reader.rescale_spike_timestamp(spike_timestamp, 'float64')
        print(spike_times[:10])
        
        raw_waveforms = reader.spike_raw_waveforms(block_index=0, seg_index=0, unit_index=unit_index, t_start=None, t_stop=None)
        print(raw_waveforms.shape, raw_waveforms.dtype)
        
        float_waveforms = reader.rescale_waveforms_to_float(raw_waveforms, dtype='float32', unit_index=unit_index)
        print(float_waveforms.shape, float_waveforms.dtype)
        
    
    
    print(reader.header['event_channels'])
    nb = reader.event_channels_count()
    for i in range(nb):
        nb_event = reader.event_count(block_index=0, seg_index=0, event_channel_index=i)
        print('i', i, 'nb_event', nb_event)
        ev_timestamps, ev_durations, ev_labels = reader.event_timestamps(block_index=0, seg_index=0, event_channel_index=i)
        print(ev_timestamps)
        print(ev_durations)
        print('ev_labels', ev_labels)
        ev_times = reader.rescale_event_timestamp(ev_timestamps, dtype='float64')
        print(ev_times)
        
    
    
    
    
    


def test_BlackrockIO():
    #~ filename = '/home/samuel/Documents/projet/DataSpikeSorting/elodie/Dataset 3/20161124-112218-001.ns5'
    #~ filename = '/home/sgarcia/Documents/projet/tridesclous_examples/20160627-161211-001'
    #~ filename = '/home/samuel/Téléchargements/files_for_testing_neo/blackrock/FileSpec2.3001.ns5'
    #~ filename = '/home/sgarcia/Documents/files_for_testing_neo/blackrock/FileSpec2.3001.ns5'
    filename = '/home/samuel/Documents/files_for_testing_neo/blackrock/FileSpec2.3001.ns5'
    
    reader = BlackrockIO(filename=filename, nsx_to_load=5)
    
    #~ blocks = reader.read(lazy=True, signal_group_mode='group-by-same-units')
    blocks = reader.read(lazy=False, signal_group_mode='group-by-same-units')
    #~ blocks = reader.read(lazy=False, signal_group_mode='split-all')
    
    for bl in blocks:
        print()
        print(bl)
        for seg in bl.segments:
            print(seg)
            print(seg.analogsignals)
            for anasig in seg.analogsignals:
                print(anasig.name, anasig.shape)
            #~ print(len(seg.spiketrains))
            for sptr in seg.spiketrains:
                print(sptr.name, sptr.shape)
            
            for ev in seg.events:
                print(ev.name)
                #~ print(ev.labels)
                print('yep')
            
            for ep in seg.epochs:
                print(ep)

    
if __name__ == '__main__':
    #~ test_BlackrockRawIO()
    #~ test_BlackrockIO()
    unittest.main()

