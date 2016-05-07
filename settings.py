#/usr/bin/python
# coding=utf-8

config = {

        # X time axe period
        'time_axe_range': 12,
        
        # File which contains list with offsets
        'off_filename': 'offsets',

        # Offsets buffer size
        'o_buffer': 1500,

        # Offsets period. Every n-th sample for offsets
        'p_offsets': 5,

        # Server ip
        'host': '188.244.51.15',

        # Server port
        'port': 5000,

        # Serial link data length
        'data_l': 67,

        # X axe time format
        'time_format': '%H:%M:%S',

        # Minimum stack size for plotting
        'min_stack_size': 700

}
