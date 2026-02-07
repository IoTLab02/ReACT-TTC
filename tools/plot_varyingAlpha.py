import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams
from pathlib import Path
import os



# Avoid type 3 fonts
rcParams["pdf.fonttype"] = 42
rcParams["ps.fonttype"]  = 42
rcParams["text.usetex"]  = False

in_path = Path("../results/results_varying_alpha.csv")
out_dir = Path("../results")
out_dir.mkdir(parents=True, exist_ok=True)



df = pd.read_csv(in_path)

df.columns = df.columns.str.strip()

# Filter out rows where Method == 'PCL'
df_filtered = df[df['Method'].str.strip() != 'PCL']




# Set seaborn style and color palette
sns.set(style="whitegrid", palette="Set1")  # colorblind is clean and distinct

# Plot
to_plot = ['Total satisfaction PT']



for _y in to_plot:
    plt.figure(figsize=(8, 6))
    sns.lineplot(
        data=df_filtered,
        x='alpha',
        y= _y,
        hue='Method',
        marker='o'
    )
    
    # Customize axes and title
    plt.xlabel(r'$\alpha$', fontsize=20)
    plt.ylabel(_y, fontsize=20)
    # plt.title('Assigned Indices vs Total EV (Excl. PCL)')
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.legend(title_fontsize=18, fontsize=18)
    plt.tight_layout()
    out_file_name = _y + '_vs_alpha.pdf'
    plt.savefig(out_dir/out_file_name, dpi=300, format='pdf')
    plt.show()


    
    


    
    
    
    

