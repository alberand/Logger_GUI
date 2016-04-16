#!/usr/bin/env python
# coding=utf-8

def calculateDensity(period):
    result = period*3600/800
    
    if result < 1:
        return 1
    else: 
        return int(result)
