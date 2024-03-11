from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
import seaborn as sns
from factor_analyzer import FactorAnalyzer
import matplotlib.pyplot as plt
import pandas as pd

class DevCvExploratoryTools:

    
    @staticmethod
    def calculate_fa_validity(df):
        #drop TESQ_E_sum because it's gonna be too highly correlated with otehr variables


        chi_square_value,p_value=calculate_bartlett_sphericity(df)
        print("Bartlett's test of sphericity chisq, p-value:")
        print(chi_square_value, p_value)

        from factor_analyzer.factor_analyzer import calculate_kmo
        kmo_all,kmo_model=calculate_kmo(df)
        print("KMO test of sampling adequacy:")
        print(kmo_model)


    @staticmethod
    def do_diagnostic_fa(df):
        test_fa = FactorAnalyzer(n_factors = 25, rotation=None)
        test_fa.fit(df)
        ev,v=test_fa.get_eigenvalues()
        DevCvExploratoryTools.screeplot(df,ev)

    @staticmethod
    def screeplot(df,ev):
        print("generating screeplot....")
        # Create scree plot using matplotlib
        plt.scatter(range(1,df.shape[1]+1),ev)
        #number each even point on the plot consecutively from left to right
        for i in range(1,df.shape[1]+1):
            if i % 2 == 0:
                plt.annotate(i, (i,ev[i-1]))
        plt.plot(range(1,df.shape[1]+1),ev)
        plt.title('Scree Plot')
        plt.xlabel('Factors')
        plt.ylabel('Eigenvalue')
        plt.grid()
        plt.show()

    @staticmethod
    def do_factor_analysis(df,n_factors):
        # Create factor analysis object and perform factor analysis using 5 factors
        fa = FactorAnalyzer(n_factors = n_factors, rotation="varimax")
        fa.fit(df)
        print(fa.loadings_.shape)
        return(fa.loadings_)


    @staticmethod
    def label_factor_loadings(fa_loadings, df):
        factor_loadings_labelled = pd.DataFrame(
            data=fa_loadings,
            index=df.columns,
            columns=['Factor ' + str(i) for i in range(1,fa_loadings.shape[1]+1)]
        )
        return(factor_loadings_labelled)

    @staticmethod
    def display_factor_loadings_in_plot(labelled_factor_loadings):
        # do a heatmap of the factor loadings using seaborn's clustermap feature
        #put row labels in a small font
        plt.figure(figsize=(10,10))
        g = sns.clustermap(labelled_factor_loadings, cmap='coolwarm', annot=True, vmin=-1, vmax=1,yticklabels=True)
        plt.setp(g.ax_heatmap.get_yticklabels(), fontsize=8)  # Adjust fontsize for y-tick labels
        plt.title('Factor Loadings')
        plt.show()

    @staticmethod
    def do_cov_mat(df):
        #print a covariance matrix of data_behavioral
        cov_mat = df.cov()
        #display as a heatmap
        #make the figure pretty big
        plt.figure(figsize=(15,15))
        #plot the heatmap, with covariances printed in each cell
        sns.heatmap(cov_mat, annot = True)

    @staticmethod
    def do_corr_mat(df):
        #now do a plain old correlation matrix
        corr_mat = df.corr()
        #display as a heatmap
        plt.figure(figsize=(15,15))
        #plot the heatmap
        sns.heatmap(corr_mat, annot = True)
