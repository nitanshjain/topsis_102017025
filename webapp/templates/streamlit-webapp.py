import streamlit as st
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import numpy as np
from detect_delimiter import detect
import scipy.stats as ss
import sys
import os

def solve_topsis(input_file, weights, impacts):
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print('Please check the path to the file')
    
    if df.shape[1]<3:
        print('Input sile should\'ve 3 or more columns')
        exit()
    #n 
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


PASSWORD = "zayden@3004"
st.set_page_config(page_title="Topsis - Nitansh Jain - 102017025", page_icon=":guardsman:", layout="wide")

in_file = st.file_uploader("Input File Name", type=["csv"])
out_file = st.text_input("Output File Name")
weights = st.text_input("Weights")
impacts = st.text_input("Impacts")
email_id = st.text_input("Email ID", key='email')

if st.button("Submit"):
    if in_file and out_file and weights and impacts and email:
        st.success("Form submitted successfully!")

        topsis_df = solve_topsis(in_file, weights, impacts)
        topsis_df.to_csv(out_file, index=False)
        
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "nitanshtopsis@gmail.com"  # Enter your address
        receiver_email = email_id  # Enter receiver address

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Topsis Final CSV Attachment"

        # Add body to email
        message.attach(MIMEText("Please find the attached CSV file.", "plain"))

        # Open PDF file in bynary
        with open(out_file, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload((attachment).read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header with pdf name
        part.add_header(
            "Content-Disposition",
            f"attachment; filename=data.csv",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, PASSWORD)
            server.sendmail(sender_email, receiver_email, text)

        print("Email sent!")

        
    else:
        st.warning("Please fill all the fields")
