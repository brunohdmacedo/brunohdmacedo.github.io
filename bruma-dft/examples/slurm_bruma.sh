#!/bin/bash
# Exemplo de job SLURM para rodar o Bruma depois de um cálculo CASTEP.
# Envie com:  sbatch slurm_bruma.sh mgh2_Fe
#SBATCH --job-name=bruma
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=bruma_%j.log

SEED="${1:-mgh2_Fe}"
cd "$SLURM_SUBMIT_DIR"
# module load python/3.11        # descomente/ajuste conforme o cluster
export MPLBACKEND=Agg            # sem display
python3 bruma.py "$SEED" -e Mg,H,Fe --planes todos --vesta --quiet
# com o Bruma instalado via pip:   bruma "$SEED" -e Mg,H,Fe --planes todos --vesta
