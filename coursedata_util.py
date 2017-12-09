#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 12:57:56 2017

@author: chuntley

A utility for scaping Fairfield U course data from text scraped from PDF files.
"""

import re

# A set of tags that appear in the Notes field of a course_spec string
tags = [
    'By Permission',
    'CRNST',
    'WDiv',
    'USDiv',
    'ResColl',
    'JUHAN',
    'Water',
    'NS Only',
    'English Core',
    'History Core',
    'SerL Opt',
    'SerL',
    'RNNU',
    'SDNU',
    'Nicaragua',
    'Hybrid',
    'Jan.'
]


def parse_course_spec(spec):
    '''
    Parses a course spec string into a JSON-style dict/list tree. 
    '''

    # Pick off the easy fields at the start of the spec
    spec_tokens = spec.split(' ')
    fields = {'CatalogID':spec_tokens[0]+spec_tokens[1],'Section':spec_tokens[2],'CRN':spec_tokens[3],'Credits':spec_tokens[4]}


    # The rest of the field will require special handling because of the spaces
    spec_unparsed = ' '.join(spec_tokens[5:])

    # Parse out the tags at the end of the spec
    spec_tags = []
    for tag in tags:
        pos = spec_unparsed.lower().rfind(tag.lower())
        if pos > -1:
            spec_tags += [tag]
            spec_unparsed = spec_unparsed[:pos]+' '+spec_unparsed[pos+len(tag):]
    fields['Tags'] = spec_tags
    spec_unparsed = spec_unparsed.rstrip(' ,')

    # Parse out the class timecodes
    timecode = re.compile('(TBA)|([Bb]y [Aa]rrangement)|([Oo]nline)|([MTWRFSU]+ [0-9]{4}-[0-9]{4}[PpAa][Mm])')
    timecodes=[]
    m = timecode.search(spec_unparsed)
    while (m):
        timecodes += [m.group()]
        spec_unparsed = spec_unparsed[0:m.start()]+"__"+spec_unparsed[m.end():]
        m = timecode.search(spec_unparsed)
    fields['Timecodes']=timecodes

    # Parse out the instructor(s) and course title
    instructors = spec_unparsed[spec_unparsed.rfind('__')+3:]
    fields['Instructor']=instructors
    fields['Title'] = spec_unparsed[:spec_unparsed.find('__')-1]

    return fields

def parse_schedule(filename):
    '''
    Returns a list of course spec trees, one per line of the input file. 
    '''
    course_specs = []
    for spec in open(filename).read().splitlines():
        course_specs.append(parse_course_spec(spec))
    return course_specs

    
def parse_catalog(filename):
    '''
    Returns a list of course descriptions grouped by program
    '''
    
    rawtxt = open(filename,encoding="utf-8").read().replace('\xa0',' ')
    # print(rawtxt)

    # parse out the program names and abbreviations
    program_re = re.compile('(CONTENTS|[0-9])([A-Z][a-z,A-Z\s]+)\s+\(([A-Z]+)\)')
    programs = [{'name':p[1],'prog_id':p[2]} for p in program_re.findall(rawtxt)]
    print(programs)
    print('+++',programs[0])
    
    # strip out the front matter before the course descriptions
    #start = rawtxt.find(programs[0]['name']+" ("+programs[0])
    first_program_re = re.compile('('+programs[0]['name']+'\s*\('+programs[0]['prog_id']+'\))')
    rawtxt = first_program_re.split(rawtxt)[3] + first_program_re.split(rawtxt)[4]
    
    # split the file by program; each program will still have its courses
    programs_split_re_pattern = ""
    for p in programs:
        programs_split_re_pattern += '|'+p['name']+'\s*\('+p['prog_id']+'\)'
    programs_split_re_pattern = "("+programs_split_re_pattern[1:]+")"
    print(programs_split_re_pattern)
    
    programs_split_re = re.compile(programs_split_re_pattern)
    programs_courses_raw = programs_split_re.split(rawtxt)[1:]
    print('---',programs_courses_raw[0])

    print('%%%'+programs_courses_raw[2])
    
    for i in range(0,int(len(programs_courses_raw)/2)):
        print('---',i, programs[i],programs_courses_raw[2*i])

#parse_catalog("CourseCatalogScrape.txt")
