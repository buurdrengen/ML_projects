# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 11:25:39 2022

@author: s196140
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat
import torch
import pandas as pd
from sklearn import model_selection
from toolbox_02450 import train_neural_net, draw_neural_net
from scipy import stats
from inner_loop import ANN_validate

#%% IMPORT DATA
filename = 'data.csv'
df = pd.read_csv(filename)

raw_data = df.values  

cols = range(1, 10) 
X = raw_data
y = X[:,[10]]
X = X[:,:10]            # CHD Target
N, M = X.shape
C = 2
#attributeNames = np.asarray(df.columns[cols])

# Normalize data
X = stats.zscore(X) 


#%% ANN MODEL
K = 10
CV = model_selection.KFold(K, shuffle=True)

# Parameters for neural network classifier
hidden_units = [1, 2, 3]   # number of hidden units
n_replicates = 1        # number of networks trained in each k-fold
max_iter = 10000

# Initialize variables
Error_train_ANN = np.empty((K,1))
Error_test_ANN = np.empty((K,1))
errors = [] # make a list for storing generalizaition error in each loop


k=0
for (k, (train_index, test_index)) in enumerate(CV.split(X,y)): 
    print('\nCrossvalidation fold: {0}/{1}'.format(k+1,K))    
    
    # Extract training and test set for current CV fold, convert to tensors
    X_train = torch.Tensor(X[train_index,:])
    y_train = torch.Tensor(y[train_index])
    X_test = torch.Tensor(X[test_index,:])
    y_test = torch.Tensor(y[test_index])
    
    errors = ANN_validate(X_train, y_train,hidden_units,K)
    h_idx = np.argmin(errors)
    opt_h = hidden_units[h_idx]
    
    model = lambda: torch.nn.Sequential(
                        torch.nn.Linear(M, opt_h), #M features to n_hidden_units
                        torch.nn.Tanh(),   # 1st transfer function,
                        torch.nn.Linear(opt_h, 1), # n_hidden_units to 1 output neuron
                        # no final tranfer function, i.e. "linear output"
                        )
    loss_fn = torch.nn.MSELoss()
    
    # Train the net on training data
    net, final_loss, learning_curve = train_neural_net(model,
                                                       loss_fn,
                                                       X=X_train,
                                                       y=y_train,
                                                       n_replicates=n_replicates,
                                                       max_iter=max_iter)

    
    # Determine estimated class labels for test set
    y_test_est = net(X_test)
    
    # Determine errors and errors
    se = (y_test_est.float()-y_test.float())**2 # squared error
    mse = (sum(se).type(torch.float)/len(y_test)).data.numpy() #mean
    errors.append(mse) # store error rate for current CV fold 

print(se)

