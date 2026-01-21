#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from setuptools import setup
from setuptools.command.build_ext import build_ext
import numpy as np

F90FLAGS_COMMON = "-Ofast -march=native -funroll-loops -ffast-math -fno-signed-zeros -fno-trapping-math"
F90FLAGS_OMP = f"-fopenmp {F90FLAGS_COMMON}"

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
PYTHON_MAJOR = sys.version_info.major
PYTHON_MINOR = sys.version_info.minor

if PYTHON_MAJOR == 3 and PYTHON_MINOR >= 12:
    F2PY_CMD = [sys.executable, "-m", "numpy.f2py"]
else:
    F2PY_CMD = ["f2py"]

class FortranBuild(build_ext):
    def run(self):
        print(f"Python {PYTHON_VERSION}, using {' '.join(F2PY_CMD)}")
        print("Compiling Fortran modules...")
        
        self.clean_previous()
        self.compile_all_modules()
        
        print("Build complete!")
    
    def clean_previous(self):
        src_dir = "src"
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith(('.so', '.mod', '.o')):
                    os.remove(os.path.join(root, file))
    
    def compile_all_modules(self):
        """编译所有Fortran模块，并将它们保留在原始目录结构中"""
        
        # 编译Constants模块
        print("Building Constants...")
        subprocess.run(F2PY_CMD + ["-m", "Constants", "-c", "src/Constants.f90"], 
                      check=True, capture_output=True)
        
        # 编译Dynamics模块
        print("Building Dynamics modules...")
        subprocess.run(F2PY_CMD + ["-m", "Dynamics_reverse", "-c", "src/Constants.f90", 
                                   "src/Dynamics/Dynamics_reverse.f90", 
                                   f"--f90flags={F90FLAGS_COMMON}"], 
                      check=True, capture_output=True)
        subprocess.run(F2PY_CMD + ["-m", "Dynamics_forward", "-c", "src/Constants.f90", 
                                   "src/Dynamics/Dynamics_forward.f90",
                                   f"--f90flags={F90FLAGS_COMMON}"], 
                      check=True, capture_output=True)
        
        # 编译Electron模块
        print("Building Electron modules...")
        subprocess.run(F2PY_CMD + ["-m", "FS_electron_weno5", "-c", "src/Constants.f90",
                                   "src/Electron/FS_electron_weno5.f90",
                                   f"--f90flags={F90FLAGS_OMP}"], 
                      check=True, capture_output=True)
        subprocess.run(F2PY_CMD + ["-m", "FS_electron_fullhide", "-c", "src/Constants.f90",
                                   "src/Electron/calling_modules.f90", 
                                   "src/Electron/FS_electron_fullhide.f90",
                                   f"--f90flags={F90FLAGS_OMP}"], 
                      check=True, capture_output=True)
        
        # 编译Interpolation模块
        print("Building Interpolation modules...")
        subprocess.run(F2PY_CMD + ["-m", "SED_interpolation", "-c", "src/Constants.f90",
                                   "src/Interpolation/SED_interpolation.f90",
                                   f"--f90flags={F90FLAGS_OMP}"], 
                      check=True, capture_output=True)
        subprocess.run(F2PY_CMD + ["-m", "SED_interpolation_structured", "-c", "src/Constants.f90",
                                   "src/Interpolation/SED_interpolation_structured.f90",
                                   f"--f90flags={F90FLAGS_OMP}"], 
                      check=True, capture_output=True)
        
        # 编译Radiation模块
        print("Building Radiation modules...")
        subprocess.run(F2PY_CMD + ["-m", "Annihilation", "-c", "src/Constants.f90",
                                   "src/Radiation/Annihilation.f90",
                                   f"--f90flags={F90FLAGS_OMP}"], 
                      check=True, capture_output=True)
        subprocess.run(F2PY_CMD + ["-m", "Seed_reverse", "-c", "src/Constants.f90",
                                   "src/Radiation/Seed_reverse.f90",
                                   f"--f90flags={F90FLAGS_OMP}"], 
                      check=True, capture_output=True)
        subprocess.run(F2PY_CMD + ["-m", "SSC_spec", "-c", "src/Constants.f90",
                                   "src/Radiation/SSC_spec.f90",
                                   f"--f90flags={F90FLAGS_OMP}"], 
                      check=True, capture_output=True)

def check_dependencies():
    print("Checking dependencies...")
    
    try:
        subprocess.run(["gfortran", "--version"], capture_output=True, check=True)
        print("✓ gfortran found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Error: gfortran not installed")
        import platform
        if platform.system() == "Darwin":
            print("Install with: brew install gcc")
        elif platform.system() == "Linux":
            print("Ubuntu/Debian: sudo apt-get install gfortran")
            print("CentOS/RHEL: sudo yum install gcc-gfortran")
        sys.exit(1)
    
    try:
        import numpy
        print(f"✓ numpy {numpy.__version__} found")
    except ImportError:
        print("✗ Error: numpy not installed")
        print("Install with: pip install numpy")
        sys.exit(1)

def main():
    print(f"Python {PYTHON_VERSION} detected")
    check_dependencies()
    
    # 创建包结构
    os.makedirs("ASGARD", exist_ok=True)
    
    # 创建 __init__.py
    init_content = '''
"""
ASGARD - Astrophysical Simulation and GRB Analysis with Radiative Dynamics
"""
import os
import sys

# 将src目录添加到Python路径，以便直接导入编译的模块
src_path = os.path.join(os.path.dirname(__file__), "src")
if os.path.exists(src_path):
    sys.path.insert(0, src_path)
'''
    
    with open(os.path.join("ASGARD", "__init__.py"), "w") as f:
        f.write(init_content)
    
    # 创建包内的src目录结构
    asgard_src = os.path.join("ASGARD", "src")
    os.makedirs(asgard_src, exist_ok=True)
    os.makedirs(os.path.join(asgard_src, "Dynamics"), exist_ok=True)
    os.makedirs(os.path.join(asgard_src, "Electron"), exist_ok=True)
    os.makedirs(os.path.join(asgard_src, "Interpolation"), exist_ok=True)
    os.makedirs(os.path.join(asgard_src, "Radiation"), exist_ok=True)
    
    # 复制Fortran源文件到包内（可选）
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith('.f90'):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, "src")
                dest_dir = os.path.join(asgard_src, rel_path)
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, file)
                shutil.copy2(src_path, dest_path)
    
    setup(
        name="ASGARD",
        version="4.2.1",
        author="ASGARD Development Team",
        description="Astrophysical Simulation and GRB Analysis with Radiative Dynamics",
        packages=["ASGARD"],
        package_dir={"ASGARD": "ASGARD"},
        package_data={
            "ASGARD": [
                "src/*.so",
                "src/*/*.so",
                "src/*.f90",
                "src/*/*.f90"
            ]
        },
        include_package_data=True,
        python_requires=">=3.8",
        install_requires=["numpy>=1.19.0"],
        cmdclass={"build_ext": FortranBuild},
        ext_modules=[],  # 空的，因为我们使用自定义构建
        zip_safe=False,
    )

if __name__ == "__main__":
    main()
