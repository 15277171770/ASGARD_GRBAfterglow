#!/bin/bash

F2PY_CMD="python3 -m numpy.f2py"

F90FLAGS_COMMON="-Ofast -march=native -funroll-loops -ffast-math -fno-signed-zeros -fno-trapping-math"
F90FLAGS_OMP="-fopenmp $F90FLAGS_COMMON -flto"
LIBS="-lgomp"
echo "Compile start"

cd ./src
rm -f *.so *.mod *.o

$F2PY_CMD -m Constants -c Constants.f90 --quiet

cd ./Dynamics
rm -f *.so *.mod *.o
FFLAGS="$F90FLAGS_COMMON" $F2PY_CMD -m Dynamics_reverse -c ../Constants.f90 Dynamics_reverse.f90 --quiet
FFLAGS="$F90FLAGS_COMMON" $F2PY_CMD -m Dynamics_forward -c ../Constants.f90 Dynamics_forward.f90 --quiet

cd ../Electron
rm -f *.so *.mod *.o
FFLAGS="$F90FLAGS_OMP" $F2PY_CMD -m FS_electron_weno5 -c ../Constants.f90 calling_modules.f90 FS_electron_weno5.f90 $LIBS --quiet
FFLAGS="$F90FLAGS_OMP" $F2PY_CMD -m FS_electron_fullhide -c ../Constants.f90 calling_modules.f90 FS_electron_fullhide.f90 $LIBS --quiet
FFLAGS="$F90FLAGS_OMP" $F2PY_CMD -m FS_electron_t2g1 -c ../Constants.f90 calling_modules.f90 FS_electron_t2g1.f90 $LIBS --quiet

cd ../Interpolation
rm -f *.so *.mod *.o
FFLAGS="$F90FLAGS_OMP" $F2PY_CMD -m SED_interpolation -c ../Constants.f90 SED_interpolation.f90 $LIBS --quiet
FFLAGS="$F90FLAGS_OMP" $F2PY_CMD -m SED_interpolation_structured -c ../Constants.f90 SED_interpolation_structured.f90 $LIBS --quiet

cd ../Radiation
rm -f *.so *.mod *.o
FFLAGS="$F90FLAGS_OMP" $F2PY_CMD -m Annihilation -c ../Constants.f90 Annihilation.f90 $LIBS --quiet
FFLAGS="$F90FLAGS_OMP" $F2PY_CMD -m Seed_reverse -c ../Constants.f90 Seed_reverse.f90 $LIBS --quiet
FFLAGS="$F90FLAGS_OMP" $F2PY_CMD -m SSC_spec -c ../Constants.f90 SSC_spec.f90 $LIBS --quiet

cd ../..
echo "Compile complete!"
