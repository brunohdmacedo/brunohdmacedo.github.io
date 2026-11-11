#!/bin/bash
# Exemplo: rodar o CASTEP e, na sequência, o Bruma no mesmo job SLURM.
#SBATCH --job-name=castep+bruma
#SBATCH --ntasks=32
#SBATCH --time=24:00:00
SEED=mgh2_Fe
cd "$SLURM_SUBMIT_DIR"
srun castep.mpi "$SEED"                         # ajuste ao executável do seu cluster
export MPLBACKEND=Agg
python3 bruma.py "$SEED" -e Mg,H,Fe --quiet     # figuras e .dat em ${SEED}_plots/
