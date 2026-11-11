#!/bin/bash
# Exemplo de job PBS/Torque. Envie com:  qsub -v SEED=mgh2_Fe pbs_bruma.sh
#PBS -N bruma
#PBS -l nodes=1:ppn=1,walltime=00:30:00,mem=4gb
#PBS -j oe
cd "$PBS_O_WORKDIR"
export MPLBACKEND=Agg
python3 bruma.py "${SEED:-mgh2_Fe}" -e Mg,H,Fe --planes todos --vesta --quiet
