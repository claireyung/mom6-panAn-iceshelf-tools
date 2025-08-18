#!/bin/bash
#PBS -N mom6_swmt
#PBS -P e14
#PBS -q hugemem
#PBS -l walltime=04:00:00
#PBS -l mem=1400GB
#PBS -l ncpus=48
#PBS -l storage=gdata/v45+gdata/hh5+gdata/cj50+gdata/ik11+scratch/x77+gdata/x77+gdata/e14+gdata/g40+gdata/xp65+gdata/gv90+gdata/ol01

export dir_path=/g/data/gv90/fbd581/access-om3-iceshelves/mom6-panAn-iceshelf-tools/Hackathon_evaluation/mom6-panAn-iceshelf-tools/evaluation

cd $dir_path

module use /g/data/xp65/public/modules
module load conda/analysis3-25.07

# run
python3 SWMT_mom6.py > $PBS_JOBID.log
