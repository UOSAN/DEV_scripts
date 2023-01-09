import socket
import os
from sklearn.model_selection import GroupKFold
import yaml
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.metrics import precision_recall_fscore_support


def read_yaml_for_host(file_path):
    hostname = socket.gethostname()
    #print full current working directory
    #print("current working directory: " + os.getcwd())
    #read yaml file
    with open(file_path, 'r') as f:
        yaml_full = yaml.safe_load(f)
    
    if hostname in yaml_full:
        yaml_host = yaml_full[hostname]
    else:
        print("yaml file does not contain host-specific settings for this host. Using default settings.")
        yaml_host = yaml_full['default']
    
    return(yaml_host)


def get_2DX_from_4DX(nifti_X):

    #rotate my array so that the last dimension is first
    print(nifti_X.shape)
    nifti_X=np.moveaxis(nifti_X,-1,0)
    print(nifti_X.shape)
    pre_reshaped_shape = nifti_X.shape
    #now flatten dims 2-4 into a single dimension
    arr2d_full=nifti_X.reshape([nifti_X.shape[0],np.prod(nifti_X.shape[1:4])])
    print("this is the form of the data that the decoder wants, (n_samples, n_features)")
    print(arr2d_full.shape)
    return(arr2d_full)


def get_4DX_from_2DX(arr2d,pre_reshaped_shape):
    #now undo the above operations to get the original matrix
    arr4d=arr2d.reshape(pre_reshaped_shape)
    print(arr4d.shape)
    arr4d=np.moveaxis(arr4d,0,-1)
    print(arr4d.shape)
    return(arr4d)


def sklearn_nested_cross_validate(X, y, estimator_set, groups=None):
    # a function to do a group k-fold cross-validation
    # do a group k-fold to estimate *performance*
    # within each group, 
    # do an inner cross-validation
    # go through each candidate estimator and do a gridsearch to find the best parameters for that estimator
    # record the results from the cumulative inner-CV for each estimator and parameter combination
    # identify the best estimator/parameter combination
    # then, do a group k-fold to estimate *performance/generalization* of the best estimator/parameter combination

    #assert X, y, and groups are all numpy arrays
    #so we know for sure how e.g., the indexing will behave.
    assert isinstance(X, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert isinstance(groups, np.ndarray)

    #create a dataframe to store the results of the inner CV
    #first three columns should be integers; score should be a float
    estimator_performance_df =pd.DataFrame(
        columns=['outer_fold_i','inner_fold_j','estimator_i','score']
    )

    outer_cv = GroupKFold(n_splits=3)
    inner_cv = GroupKFold(n_splits=3)

    outer_cv_split=[split_tuple for split_tuple in outer_cv.split(X,groups=groups)]
    y_pred_inner = np.zeros(len(y))

    #https://machinelearningmastery.com/nested-cross-validation-for-machine-learning-with-python/
    for i, (train_i,validate_i) in enumerate(outer_cv_split):
        print("generalization test group " + str(i))
        
        print(len(train_i))
        print(len(validate_i))

        X_train_i=X[train_i]
        y_train_i=y[train_i]
        groups_train_i=groups[train_i]


        #now do inner CV
        for j, (train_j,validate_j) in enumerate(inner_cv.split(X_train_i,groups=groups_train_i)):
            print("hyper-parameter search group " + str(j) + "; ",end=" ")
        
            #print(len(train_j))
            #print(len(validate_j))
            #do a grid search using  to find the best parameters for each estimator

            for estimator_i, estimator in enumerate(estimator_set):
                print("est...",end="")
                #for now, don't implement the gridsearch because we don't need it; 
                # I just want to comapre the performance of the different estimators
                estimator.fit(X_train_i[train_j],y=y_train_i[train_j])
                #now, evaluate the performance of the estimator on the validation set
                inner_y_pred = estimator.predict(X_train_i[validate_j])
                y_pred_inner[train_i][validate_j] = inner_y_pred
                # get the score of the estimator on the test data
                inner_score = roc_auc_score(y_train_i[validate_j], inner_y_pred)
                #print the score for this estimator
                print("est " + str(estimator_i) + "; ROC AUC: " + str(inner_score) + "; ")
                #add an entry to the dataframe
                estimator_performance_df.loc[len(estimator_performance_df)] = [i,j,estimator_i,inner_score]
            
        print("\n")

    #now, we have a list of lists of lists of scores for each estimator
    #we can select the best estimator for each fold from the estimators df
    #then, we can do a group k-fold to estimate *performance/generalization* of the best estimator/parameter combination
    estimator_performance_df = estimator_performance_df.convert_dtypes({'score':float,'outer_fold_i':int,'inner_fold_j':int,'estimator_i':int})
    overall_est_performance = estimator_performance_df.groupby(['estimator_i'])['score'].mean().sort_values(ascending=False,inplace=False)
    top_est_i = overall_est_performance.index[0]
    print(overall_est_performance)
    print("chose estimator " + str(top_est_i))
    #now we can do a group k-fold to estimate *performance/generalization* of the best estimator/parameter combination
    best_estimator = estimator_set[top_est_i]
    outer_y_pred = np.zeros(len(y))

    for i, (train_i,validate_i) in enumerate(outer_cv_split):
        print("generalization test group " + str(i))
        best_estimator.fit(X[train_i],y=y[train_i])
        #now, evaluate the performance of the estimator on the validation set
        outer_y_pred[validate_i] = best_estimator.predict(X[validate_i])
        # get the score of the estimator on the test data
        #outer_score = roc_auc_score(selected_subjs['y_int'][validate_i], outer_y_pred)

    # get the cross-validated score of the estimator on the test data
    outer_score = roc_auc_score(y, outer_y_pred)
    print("cross-validated score is: " + str(outer_score))

    print("precision, recall, fscore, support:")
    print(precision_recall_fscore_support(y, outer_y_pred))
    #now we can return the best estimator and the cross-validated score
    best_estimator.fit(X,y=y)
    print("raw (overfit) score is: " + str(roc_auc_score(y, best_estimator.predict(X))))

    return({
        'y_predict_final':outer_y_pred,
        'model_final':best_estimator
    })

def sklearn_simple_cross_validate(X, y, estimator, groups=None,scoring_function=roc_auc_score):

    #assert X, y, and groups are all numpy arrays
    #so we know for sure how e.g., the indexing will behave.
    assert isinstance(X, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert isinstance(groups, np.ndarray)

    outer_cv = GroupKFold(n_splits=3)
    outer_cv_split=outer_cv.split(X,groups=groups)

    outer_y_pred = np.zeros(len(y))

    for i, (train_i,validate_i) in enumerate(outer_cv_split):
        print("generalization test group " + str(i), end=", ")
        print('estimating... ', end="")
        estimator.fit(X[train_i],y=y[train_i])
        print('estimated; predicting... ')
        #now, evaluate the performance of the estimator on the validation set
        prediction = estimator.predict(X[validate_i])
        outer_y_pred[validate_i] = prediction
        # get the score of the estimator on the test data
        outer_score = scoring_function(y[validate_i], prediction)

    # get the cross-validated score of the estimator on the test data
    outer_score = scoring_function(y, outer_y_pred)
    print("cross-validated score is: " + str(outer_score))

    print("precision, recall, fscore, support:")
    print(precision_recall_fscore_support(y, outer_y_pred))
    #now we can return the best estimator and the cross-validated score
    estimator.fit(X,y=y)
    print("raw (overfit) score is: " + str(scoring_function(y, estimator.predict(X))))

    return({
        'y_predict_final':outer_y_pred,
        'model_final':estimator
    })



def filter_dev_data(test_train_df_raw, nonbids_data_path,dropbox_datapath):
    #mark subjects in nsc_subject_exclusions (not sure where this came from)
    include_exclude_list = pd.read_csv("../nsc_subject_exclusions.csv")
    #mark subjects with bad data at scan time
    #check if file exists
#     if os.path.isfile(dropbox_datapath + "/DEV-Session1DataQualityC_DATA.xlsx"):
#         data_quality = pd.read_excel(dropbox_datapath + "/DEV-Session1DataQualityC_DATA.xlsx", engine = 'openpyxl')
#     else:
    data_quality = pd.read_csv(dropbox_datapath + "/DEV-Session1DataQualityC_DATA.csv")
    data_quality_sst = data_quality.loc[data_quality.SST.isna()==False,]

    #remove each of hte above categories
    test_train_df_raw = test_train_df_raw.merge(include_exclude_list[include_exclude_list.Task=='SST'],left_on='sub_label',right_on='SubjectId',how='left')
    test_train_df_raw.loc[test_train_df_raw.Include.isna(),'Include'] = True
    test_train_df_raw = test_train_df_raw.merge(data_quality_sst[['dev_id','SST']],left_on='sub_label',right_on='dev_id',how='left')
    test_train_df = test_train_df_raw[(test_train_df_raw.Include==True) & (test_train_df_raw.SST=="No reported problems")]

    #remove subjects noted with bad or missign data eitehr here or elsewhere
    exclude_subjects = [
    'DEV012','DEV018', 'DEV068', 'DEV073','DEV159', #excluded during the conversion process for reasons I'm not sure about

    'DEV061','DEV185','DEV187',
    'DEV189','DEV190','DEV192',
    'DEV198','DEV203','DEV220','DEV221',
    'DEV312']
    #2022-01-06 added DEV157 because of an error
    #2023-01-02 to -03 added DEV068, DEV101 because of an error

    #we have data missing fro mthese subjects below. not enstirely sure yet; see 
    #https://docs.google.com/document/d/1EB0ACA6qhMkDEgv-zqNTepPCe_x41fRQHaeqT47vazM/edit#heading=h.60rb13rlxkrq
    train_subjs = test_train_df.loc[test_train_df.SplitGroup_75_25=='Train','sub_label'].tolist()#only get the train subjects; ignore those previously marked hold-out
    train_subjs_selected = [ts for ts in train_subjs if (ts not in exclude_subjects)]

    return(train_subjs_selected)