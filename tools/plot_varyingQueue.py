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

in_path = Path("../results/results_varying_q.csv")
out_dir = Path("../results")
out_dir.mkdir(parents=True, exist_ok=True)



df = pd.read_csv(in_path)

df.columns = df.columns.str.strip()

# Filter out rows where Method == 'PCL'
df_filtered = df[df['Method'].str.strip() != 'PCL']

# Avoid floats in X-axis
df_filtered['CP Queue'] = df_filtered['CP Queue'].astype(int)



# Set seaborn style and color palette
sns.set(style="whitegrid", palette="Set1")  # colorblind is clean and distinct

# Plot
to_plot = ['Sum of assigned indices', 'Total satisfaction PT']


df_filtered1 = df_filtered[df_filtered['ratio'] == 0.8]

# for _y in to_plot:
#     plt.figure(figsize=(8, 6))
#     sns.lineplot(
#         data=df_filtered1,
#         x='CP Queue',
#         y= _y,
#         hue='Method',
#         marker='o'
#     )
    
#     # Customize axes and title
#     plt.xlabel('CP Queue', fontsize=20)
#     plt.ylabel(_y, fontsize=20)
#     # plt.title('Assigned Indices vs Total EV (Excl. PCL)')
#     plt.xticks(ticks=sorted(df_filtered1['CP Queue'].unique()), labels=sorted(df_filtered1['CP Queue'].unique()))
#     plt.xticks(fontsize=18)
#     plt.yticks(fontsize=18)
#     plt.legend(title_fontsize=18, fontsize=18)
#     plt.tight_layout()
#     out_file_name = _y + '_vs_Queue_ratio0.8.pdf'
#     plt.savefig(out_dir/out_file_name, dpi=300, format='pdf')
#     plt.show()


    
    

df_filtered2 = df_filtered[df_filtered['CP Queue'] == 3]
    
for _y in to_plot:
    plt.figure(figsize=(8, 6))
    sns.lineplot(
        data=df_filtered2,
        x='ratio',
        y= _y,
        hue='Method',
        marker='o'
    )
    
    # Customize axes and title
    plt.xlabel('EV to charging slot ratio', fontsize=20)
    plt.ylabel(_y, fontsize=20)
    # plt.title('Assigned Indices vs Total EV (Excl. PCL)')
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.legend(title_fontsize=18, fontsize=18)
    plt.tight_layout()
    out_file_name = _y + '_vs_ratio_Q3.pdf'
    plt.savefig(out_dir/out_file_name, dpi=300, format='pdf')
    plt.show()
    
    
    
    

df_filtered1['CP Queue'] = df_filtered1['CP Queue'].astype(int).astype(str)
df_filtered1['CP Queue'] = pd.Categorical(df_filtered1['CP Queue'], ordered=True)
    
for _y in to_plot:
    plt.figure(figsize=(8, 6))
    sns.barplot(
    data=df_filtered1,
    x='CP Queue',
    y=_y,
    hue='Method',
    ci='sd',
    dodge=True
)
    
    # Customize axes and appearance
    plt.xlabel('CP Queue', fontsize=20)
    plt.ylabel(_y, fontsize=20)
    # plt.xticks(ticks=sorted(df_filtered1['CP Queue'].unique()), labels=sorted(df_filtered1['CP Queue'].unique()), fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.legend(title='Method', title_fontsize=18, fontsize=18)
    plt.tight_layout()

    # Save plot
    out_file_name = _y + '_bar_vs_Queue_ratio0.8.pdf'
    plt.savefig(out_dir / out_file_name, dpi=300, format='pdf')
    plt.show()