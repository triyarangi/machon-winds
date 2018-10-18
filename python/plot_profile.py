import matplotlib.pyplot as plt

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
    if outdir is not None:
        plt.savefig(outdir+label+'.png')
    plt.show()
