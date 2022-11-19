import pandas as pd
import numpy as np
import os

def extract_properties_from_log(log_file_path):
    data = []
    search_token = 'TotEng'
    df_head = None
    with open(log_file_path, 'r') as f:
        for line in f:
            if search_token in line:
                df_head = line.split()
            try:
                properties = list(map(float, line.split()))
                data.append(properties)
            except:
                continue

    # There is some [] at the end of the data for some reason so I'm removing it
    while [] in data:
        del data[data.index([])]

    # Dropna because if we got some other numeric row we need to eliminate it.
    df = pd.DataFrame(data, columns=df_head).dropna(axis=0)
    return df

def get_data_eq2(file, warmup=1501):
    ''' Equation 2 : Using the Variance of internal energy '''
    common_path = file # path of the lammps log file
    data = extract_properties_from_log(common_path)

    var_u = np.var(data['PotEng'][warmup:]) # Variance of potential energy kcal/mol
    var_e = np.var(data['TotEng'][warmup:]) # Variance of total energy kcal/mol

    k_b = 3.29983031e-27 # kcal/K
    T = np.mean(data['Temp'][warmup:]) # K
    N_A = 6.022e23 # mol

    C_v_u = var_u/(N_A*k_b*T*T) # kcal^2*K
                                # -----------
                                # kcal*mol^2*K^2 
    C_v_e = var_e/(N_A*k_b*T*T) # kcal^2*K
                                # -----------
                                # kcal*mol^2*K^2 
    
    E = np.mean(data['TotEng'][warmup:])
    U = np.mean(data['PotEng'][warmup:])
    T = np.mean(data['Temp'][warmup:])

    tmp = {}
    tmp[f'var_u'] = var_u
    tmp[f'var_e'] = var_e
    tmp[f'var_t'] = np.var(data['Temp'][warmup:])
    tmp[f'C_v_u'] = C_v_u
    tmp[f'C_v_e'] = C_v_e
    tmp[f'E']     = E
    tmp[f'U']     = U
    tmp[f'T']     = T
    
    df = pd.DataFrame([tmp])

    return df


def get_data_eq1(file, warmup=1501):
    ''' Equation 1 : dU/dT '''

    common_path = file # path of the lammps log file
    data = extract_properties_from_log(common_path)

    T = np.array(data["Temp"][warmup:])
    dT  = T[1:] - T[:-1]

    E = np.array(data["TotEng"][warmup:])
    dE  = E[1:] - E[:-1]
    
    U = np.array(data["PotEng"][warmup:])
    dU  = U[1:] - U[:-1]

    C_V_E = dE/dT

    C_V_U = dU/dT

    tmp = {}
    tmp[f'var_u'] = np.var(U)
    tmp[f'var_e'] = np.var(E)
    tmp[f'var_t'] = np.var(T)
    tmp[f'C_v_u'] = np.mean(C_V_U)
    tmp[f'C_v_e'] = np.mean(C_V_E)
    tmp[f'E']     = np.mean(E)
    tmp[f'U']     = np.mean(U)
    tmp[f'T']     = np.mean(T)

    df = pd.DataFrame([tmp])

    return df

if __name__ == "__main__":


    LJ_dir = "data/LJ/"
    ReaxFF_dir = "data/ReaxFF/"

    LJ_files = os.listdir(LJ_dir)
    ReaxFF_files = os.listdir(ReaxFF_dir)

    # Data for LJ simulations
    df = pd.DataFrame()

    for file in LJ_files:
        df = pd.concat([df, get_data_eq2(LJ_dir+file)])

    df.to_csv(f"csv/LJdata_eq2.csv")

    # Data for ReaxFF Simulations
    df = pd.DataFrame()

    for file in ReaxFF_files:
        df = pd.concat([df, get_data_eq2(ReaxFF_dir+file)])

    df.to_csv(f"csv/ReaxFFdata_eq2.csv")

    #############
    ## Equation 1

    # Data for LJ simulations
    df = pd.DataFrame()

    for file in LJ_files:
        df = pd.concat([df, get_data_eq1(LJ_dir+file)])

    df.to_csv(f"csv/LJdata_eq1.csv")

    # Data for ReaxFF Simulations
    df = pd.DataFrame()

    for file in ReaxFF_files:
        df = pd.concat([df, get_data_eq1(ReaxFF_dir+file)])

    df.to_csv(f"csv/ReaxFFdata_eq1.csv")
