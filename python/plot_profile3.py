import matplotlib.pyplot as plt


def LetterChanges(x):
    # code goes here
    import string
    xnew = x 
    xnew = list(xnew)
     
    
   
    for l in range(len(x)):
        
        if x[l] == " ":
           xnew[l]="_"
    xnew = "".join(xnew) # Change the list back to string, by using 'join' method of strings.    
    return xnew



def plot_profile( line_profiles, scatter_profiles ,outdir,title=""):
    if line_profiles is not None:
        for label in sorted(line_profiles.values.iterkeys()):
            profile = line_profiles.values[label]
            plt.plot( profile, line_profiles.heights, label=label)
    if scatter_profiles is not None:
        for label in sorted(scatter_profiles.values.iterkeys()):
            profile = scatter_profiles.values[label]
            plt.scatter( profile, scatter_profiles.heights, label=label)

    plt.title(title)
    plt.legend(loc='best')
        # padding outfile name
    label1=LetterChanges(label)
    if outdir is not None:
        plt.savefig(outdir+label1+'.png')
    plt.show()
