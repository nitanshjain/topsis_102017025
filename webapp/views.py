from flask import Blueprint, render_template, request, jsonify, redirect, url_for


views = Blueprint(__name__, "views")

def solve_topsis(input_file, weights, impacts, output_file):
    import pandas as pd
    import numpy as np
    from detect_delimiter import detect
    import scipy.stats as ss
    import sys
    
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
    
    # df.to_csv(output_file, index=False)
    
    return df

@views.route("/views")
def home():
    return render_template("index.html")

@views.route("/data/", methods = ['POST'] )
def topsis_solve():
    
    if request.method == 'POST':
        input_user_file = request.files("in_file")
        output_user_file = request.form.get("out_file")
        weights_user = request.form.get("weights")
        impacts_user= request.form.get("impacts")
        email_user= request.form.get("email")
        # topsis_df = solve_topsis(input_user_file, weights_user, impacts_user, output_user_file)
        
        return render_template('data.html', 
                              email_user=email_user,
                              weights_user=weights_user
                              )
        

    #gathering file from form
    

