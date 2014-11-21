# genetic optimization of stats for rearrange
#Copyright (c) 2010, pete@weargoggles.co.uk
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the <organization> nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL pete@weargoggles.co.uk BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import random, math, os, sys

skills = {
#covert
            'co.st': 'DDDIS',
            'co.hi': 'DDIIS',
            'co.lo': 'DDDDI',
            'co.ma': 'DDISS',
            'co.ca': 'DIIWW',
            'co.it': 'DIIII',
            'co.po': 'DDIIC',
# faith   
            'fa.ri.of': 'ISSWW',
            'fa.ri.de': 'DDIWW',
            'fa.ri.cu': 'CCIWW',
            'fa.ri.mi': 'IIWWW',
            'fa.ri.sp': 'ISWWW',
            'fa.it':     'DIIWW',
            'fa.po':    'CIIWW',
            
            'ma.sp.of': 'SSIIW',
            'ma.sp.de': 'CCIIW',
            'ma.sp.mi': 'DDIIW',
            'ma.sp.sp': 'IIWWW',
            'ma.me.el': 'CCCII',
            'ma.me.me': 'IIIII',
            'ma.me.ph': 'DDDII',
            'ma.me.sp': 'IIWWW',
            'ma.it':    'DIIWW',
            'ma.po':    'IISWW',
            
            'fi.me.da': 'DDDDS',
            'fi.me.sw': 'DDDSS',
            'fi.me.po': 'CCSSS',
            'fi.me.he': 'CDSSS',
            'fi.me.ma': 'CCDSS',
            'fi.ra.th': 'DDDSS',
            'fi.ra.fi': 'DDDDS',
            'fi.de.do': 'DDDDW',
            'fi.de.pa': 'DDDSW',
            'fi.de.bl': 'DDSSW',
            'fi.sp.we': 'SDIII',
            'fi.sp.ta': 'WWIII',
            'fi.po':    'DSSCC',
            'fi.un':    'DDSSW',

            'ad.pe':    'IIWWW',
            'ad.he':    'CCCCS',
            
            'utility':     'SSCCC',
            'test':     'SSSSS',
}

GENERATIONS = 5000
POP_LEN = 40
MUTATIONS = 2
CARRY_TARGET = 160
AT_LEVEL = 200

blank = [ 13, 13, 13, 13, 13 ]

skills_to_optimise = [
'fa.ri.cu',

'fa.ri.de',

'fi.me.po',
'fi.de.pa',

]

gp_skill = 'fa.po'

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

stats = [ 'C', 'D', 'I', 'S', 'W' ]

### bonus calculation
def R( skill_level ):
    return math.floor( 0.5 * (skill_level - 60) + 170 )

def M( skill_weighting, stat_a ):
    values = [ stat_a[stats.index(i)] for i in skill_weighting ]
    product = 1
    for i in values:
        product *= i
    return (1/9.8) * math.log(product) - 0.25

def bonus( skill, level, stat_a ):
    return math.floor( M( skills[skill], stat_a ) * R( level ) )

def gp_regen( stat_a ):
    return math.floor(
        math.sqrt(
            175 * M( skills[gp_skill], stat_a ) )
        - 10 )

def carrying_capacity( stat_a ):
    s = stat_a[ stats.index('S') ]
    return math.floor( 1.89 * (20 + s + s**2/5 ) )

min_bonus = bonus( 'test', AT_LEVEL, [0, 0, 0, 8, 0] )
max_bonus = bonus( 'test', AT_LEVEL, [0,0,0,23,0] )
bonus_diff = max_bonus - min_bonus

class Skills(object):
    pass

class Character(object):
    def __init__(self, stat_a ):
        self.stat_a = stat_a
    
    def burden( self, percent ):
        s = self.stat_a[ stats.index('S') ]
        return percent * math.floor( 1.89 * (20 + s + s**2/5 ) )
    
    def gp_regen( self ):
        return math.floor(
            math.sqrt(
                175 * M( skills[gp_skill], self.stat_a ) )
            - 10 )
    ### bonus calculation
    def R( skill_level ):
        return math.floor( 0.5 * (skill_level - 60) + 170 )
    
    def M( skill_weighting, stat_a ):
        values = [ stat_a[stats.index(i)] for i in skill_weighting ]
        product = 1
        for i in values:
            product *= i
        return (1/9.8) * math.log(product) - 0.25
    
    def bonus( skill, level, stat_a ):
        return math.floor( M( skills[skill], stat_a ) * R( level ) )
    
    
    
# da heart of da whole fing, da fitness function. should return 1 (ish) at neutral stats.
# NEEDS TUNING FOR GP AND CARRYING CAP
def fitness( stat_a ):
    bs = [ bonus( skill, AT_LEVEL, stat_a ) for skill in skills_to_optimise ]
    bs = [ 90 * ( bon - min_bonus ) / bonus_diff for bon in bs ]
    bs_avg = sum(bs)/len(bs)
    gpr = 25.0 * gp_regen( stat_a )
    cc = 100. * ( 1 - ( abs(CARRY_TARGET - carrying_capacity( stat_a )) / CARRY_TARGET )/4. )
    
    r = [ gpr, cc, bs_avg ]
    return sum(r)/len(r)-1
    
def print_and_replace( format, data , replace=1):
   # if type(data) is not type([]):
   #     raise TypeError, "Format string arguments in an array please."
    per_cents = format.count('%')
    while len(data) != per_cents:
        data.append(0)
    data = tuple(data)
    output = format % data
    if replace:
        sys.stdout.write( '\b' * len( output ))
    else:
        output = '\n'+output
    sys.stdout.write(output)

frmt = "Iteration %5d : Fitness %.3f : Gp %d [ Con %2d Dex %2d Int %2d Str %2d Wis %2d ]"

def main():
    sorting = {}
    pop = []
    new_pop = []
    leader_ = [ fitness(blank), list(blank) ]
    leader = list(leader_)
    
    print "Starting..."
    print "\n"
    print_and_replace( frmt, [0] + [1.] + [3] + list(blank) , replace=0 )
    
    for i in xrange(POP_LEN):
        pop.append( list(blank) )
    
    for i in xrange(GENERATIONS):
        for j in pop[:int(len(pop)/4)]:
            sorting[ fitness(j) ] = list(j)
        for j in pop[int(len(pop)/4):-1]:
            # pick between 0 and MUTATIONS pairs of stats, modify them 
            # by up to 2 if that won't take them out of allowed ranges
            for k in xrange(random.randint(0,MUTATIONS)):
                x = random.randint(0,4)
                y = x
                while y == x:
                    y = random.randint(0,4)
                change = random.randint(1,2)
                if (j[x]-change) >= 8 and (j[y]+change <= 23):
                    j[x] -= change
                    j[y] += change
            # add j to the sorting dict with its fitness as the key
            sorting[ fitness( j ) ] = list(j)
        sorting
        
        # get the keys of the sorting dict (the fitnesses)
        k = sorting.keys()
        #print len(k), len(pop)
        # sort for highest first
        k.sort()
        k.reverse()
        # take the first 3/4 and put them into the next generation
        for z in k:
            new_pop.append( sorting[z] )
        # make sure new_pop is full of members
        while len(new_pop) < POP_LEN:
            new_pop.append( list(blank) )
        #while len(new_pop) > POP_LEN:
        #    new_pop.pop()
        
        
        # best ever?
        if k[0] > leader[0]:
            leader = k[0], sorting[k[0]]
            #print "Iteration", i,"Score", leader[0],"||", leader[1], gp_regen( leader[1] )
        
        da = [ i, leader[0], gp_regen( leader[1] ) ] + leader[ 1 ]
        print_and_replace( frmt, da )
        if not i % int(GENERATIONS/10):
            da = [ i, k[0], gp_regen( sorting[k[0]] ) ] + sorting[k[0]]
            print_and_replace( frmt, da, replace=0 )
        
        pop = list(new_pop)
        new_pop = []
        sorting = {}
    print ""

if __name__ == "__main__":
    main()
