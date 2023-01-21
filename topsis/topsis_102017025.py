import pandas as pd
import numpy as np
from detect_delimiter import detect
import scipy.stats as ss
import sys


def check_input():
    input_arguments = sys.argv
    
    try:
        input_file = input_arguments[1]
        weights = input_arguments[2]
        impacts = input_arguments[3]
        output_file = input_arguments[4]
    
    except IndexError:
        print('Number of input paramters provided are incomplete.')
    
    return input_file, weights, impacts, output_file

def read_data(input_file, weights, impacts):
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print('Please check the path to the file')
    
    if df.shape[1]<3:
        print('Input sile should\'ve 3 or more columns')
        exit()
        
    num_col_post1 = df.iloc[:,1:].shape[1]
    num_col_numeric = df.select_dtypes(include='number').shape[1]
    if num_col_numeric < num_col_post1:
        print('Please make sure that the 2nd to the last columns have only numeric values')
        exit()
        
    if(detect(impacts)!=',' or detect(weights)!=','):
        print('Please make sure you are using \',\' as your delimiter')
    
    weights = list(map(float, weights.split(',')))
    impacts = impacts.split(',')
    
    if num_col_numeric!=len(weights) or num_col_numeric!=len(impacts):
        print('Please make sure that number of weights and impacts is equal to number of feature columns')
    
    if any(element not in ['+','-'] for element in impacts):
        print('Make sure your weights are either \'+\' or \'-\'')
        
    return df, weights, impacts
    
        
def topsis_solve(df, weights, impacts, out_data_file):
    
    # Step1 - Converting Pandas Dataframe to Numpy Matrix
    num = df.iloc[:,1:].to_numpy()
    
    # Step2 - Dividing every column value by its root of sum of squares
    num = num / np.sqrt(np.sum(np.square(num), axis=0))
    
    # Step3 - Calculate weight * normalized performance value
    num = np.multiply(num, np.array(weights))
    
    # Step4 - Selecting ideal best
    id_best = list()
    for i in range(len(impacts)):
        if impacts[i]=='+':
            id_best.append(max(num[:,i]))
        else:
            id_best.append(min(num[:,i]))
    
    # Step5 - Selecting ideal worst
    id_worst = list()
    for i in range(len(impacts)):
        if impacts[i]=='+':
            id_worst.append(min(num[:,i]))
        else:
            id_worst.append(max(num[:,i]))
            
    # Step6 - Calculate Euclidean Distance between all points from Ideal Best and Ideal Worst row-wise
    eucl_dist_id_best = list()
    for i in range(df.shape[0]):
        eucl_dist_id_best.append(np.sqrt(np.sum(np.square(num[i,:]-id_best))))
        
    eucl_dist_id_worst = list()
    for i in range(df.shape[0]):
        eucl_dist_id_worst.append(np.sqrt(np.sum(np.square(num[i,:]-id_worst))))
        
    # Step7 - Calculate Performance Score
    perf_score = np.array(eucl_dist_id_worst) / (np.array(eucl_dist_id_best) + np.array(eucl_dist_id_worst))
    
    # Step8 - Assigning Topsis Rank
    df['Topsis Score'] = perf_score
    rank = len(perf_score) - ss.rankdata(perf_score).astype(int) + 1
    df['Rank'] = rank
    
    df.to_csv(out_data_file, index=False)
    
    return df
