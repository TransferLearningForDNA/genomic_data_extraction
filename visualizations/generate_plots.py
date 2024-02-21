import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from sklearn.metrics import r2_score
import os
import mlflow
import warnings

def plot_scatter_line_of_best_fit(df: pd.DataFrame, save_directory: str = os.getcwd()) -> None:
    """
    Plot a scatter plot with a line of best fit for real values vs predicted values.

    Args:
        df (pd.DataFrame): DataFrame containing 'Real Values' and 'Predicted Values' columns.
        save_directory (str, optional): The directory to save the generated plot. Defaults to the current working directory.

    Returns:
        None
    """
    # Scatter plot
    df.plot(kind='scatter', x='Real Values', y='Predicted Values', s=32, alpha=.8)
    plt.gca().spines[['top', 'right']].set_visible(False)

    # Line of best fit
    real_values = df['Real Values'].values
    predicted_values = df['Predicted Values'].values
    fit = np.polyfit(real_values, predicted_values, 1)
    fit_fn = np.poly1d(fit)
    plt.plot(real_values, fit_fn(real_values), color='red', label='Line of Best Fit')

    # R^2 value
    r_squared = r2_score(predicted_values, fit_fn(real_values))
    plt.text(plt.xlim()[1] - 2, 2, f'$R^2 = {r_squared:.2f}$', fontsize=10, ha='center')

    # Set plot properties
    plt.xlabel('Real Values')
    plt.ylabel('Predicted Values')
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.legend()
    # plt.show()

    if not os.path.isdir(save_directory):
        os.makedirs(save_directory, exist_ok=True)

    save_path = f"{save_directory}/scatter_plot.png"
    plt.savefig(save_path)

def plot_species_scatter_line_of_best_fit(df: pd.DataFrame, species_col: str = 'Species', save_directory: str = os.getcwd()) -> None:
    """
    Plot scatter plots with a line of best fit for each species.

    Args:
        df (pd.DataFrame): DataFrame containing 'Real Values', 'Predicted Values', and 'Species' columns.
        species_col (str, optional): Name of the column containing species information. Defaults to 'Species'.
        save_directory (str, optional): The directory to save the generated plot. Defaults to the current working directory.

    Returns:
        None
    """
    species = df[species_col].unique()
    fig, axes = plt.subplots(nrows=len(species), ncols=1, figsize=(6, 12), sharex=True, sharey=True)

    for i, species_name in enumerate(species):
        group = df[df[species_col] == species_name]

        # Scatter plot
        ax = axes[i]
        ax.scatter(group['Real Values'], group['Predicted Values'], s=32, alpha=0.8)

        # Line of best fit
        fit = np.polyfit(group['Real Values'], group['Predicted Values'], 1)
        fit_fn = np.poly1d(fit)
        ax.plot(group['Real Values'], fit_fn(group['Real Values']), color='red')

        # R^2 value
        r_squared = r2_score(group['Predicted Values'], fit_fn(group['Real Values']))

        # Title with species name and R^2 value
        ax.set_title(f'{species_name} - $R^2 = {r_squared:.2f}$')

        # Set plot properties
        ax.set_xlabel('Real Values')
        ax.set_ylabel('Predicted Values')
        ax.spines[['top', 'right']].set_visible(False)

        # Show x-axis tick labels in all plots
        ax.tick_params(axis='x', which='both', labelbottom=True)

    # Adjust layout to prevent overlapping
    plt.tight_layout()
    # plt.show()

    if not os.path.isdir(save_directory):
        os.makedirs(save_directory, exist_ok=True)

    save_path = f"{save_directory}/scatter_plot.png"
    plt.savefig(save_path)


def plot_residuals_by_promoter_bin(df: pd.DataFrame, species_col: str = 'Species',
                                    amount_promoter_col: str = 'Amount Promoter',
                                    real_values_col: str = 'Real Values',
                                    predicted_values_col: str = 'Predicted Values',
                                    save_directory: str = os.getcwd()) -> None:
    """
    Plot mean residuals for different promoter bins across species.

    Args:
        df (pd.DataFrame): DataFrame containing columns 'Species', 'Amount Promoter', 'Real Values',
                           'Predicted Values', and 'Residuals'.
        species_col (str, optional): Name of the column containing species information. Defaults to 'Species'.
        amount_promoter_col (str, optional): Name of the column containing the amount of promoter information.
                                            Defaults to 'Amount Promoter'.
        real_values_col (str, optional): Name of the column containing real values. Defaults to 'Real Values'.
        predicted_values_col (str, optional): Name of the column containing predicted values.
                                              Defaults to 'Predicted Values'.
        save_directory (str, optional): The directory to save the generated plot. Defaults to the current working directory.

    Returns:
        None
    """

    if not os.path.isdir(save_directory):
        os.makedirs(save_directory, exist_ok=True)


    # Calculate residuals
    df['Residuals'] = df[real_values_col] - df[predicted_values_col]

    # Calculate min and max values of 'Amount Promoter'
    min_amount = df[amount_promoter_col].min()
    max_amount = df[amount_promoter_col].max()

    # Create a new column 'Promoter Bin' based on 'Amount Promoter'
    df['Promoter Bin'], _ = pd.cut(df[amount_promoter_col], bins=np.linspace(min_amount, max_amount, 10), include_lowest=True, retbins=True)

    species_list = df[species_col].unique()

    for species_name in species_list:
        # Filter data for the specific species
        species_data = df[df[species_col] == species_name]

        plt.figure(figsize=(6, 4))
        species_data.groupby('Promoter Bin')['Residuals'].mean().plot(kind='bar', color='skyblue')
        plt.title(f'{species_name}')
        plt.xlabel('Promoter Bin')
        plt.ylabel('Mean Residuals')
        plt.xticks(rotation=45, ha='right')
        # plt.show()

        save_path = f"{save_directory}/residuals_{species_name}.png"
        plt.savefig(save_path)


def plot_top_x_clustered_bar_chart(df: pd.DataFrame, top_x_value: int = 5, save_directory: str = os.getcwd()) -> None:
    """
    Create a clustered bar chart for each species with the top-X results based on Real Values.

    Args:
        df (pd.DataFrame): DataFrame containing 'Real Values', 'Predicted Values', 'Species', and 'Gene' columns.
        top_x_value (int, optional): Number of top results to display. Defaults to 5.
        save_directory (str, optional): The directory to save the generated plot. Defaults to the current working directory.

    Returns:
        None
    """
    if not os.path.isdir(save_directory):
        os.makedirs(save_directory, exist_ok=True)

    # Create a clustered bar chart for each species
    for species_name, group in df.groupby('Species'):
        plt.figure(figsize=(10, 6))

        top_x_group = group.nlargest(top_x_value, 'Real Values')  # Select the top-X based on Real Values

        # Set the width of the bars
        bar_width = 0.35

        # Set the x-axis positions for real values and predicted values
        x_positions_real = np.arange(len(top_x_group['Gene']))
        x_positions_pred = x_positions_real + bar_width

        # Plotting real values
        plt.bar(x_positions_real, top_x_group['Real Values'], label=f'Real', alpha=0.7, width=bar_width)

        # Plotting predicted values
        plt.bar(x_positions_pred, top_x_group['Predicted Values'], label=f'Predicted', alpha=0.7, width=bar_width)

        plt.yscale('log')  # Log-scaled y-axis
        plt.title(f'Top-{top_x_value} results for {species_name}')
        plt.xlabel('Gene')
        plt.ylabel('Expression level (log scale)')
        plt.xticks(x_positions_real + bar_width / 2, top_x_group['Gene'])  # Set x-axis ticks at the center of the clustered bars
        plt.legend()
        # plt.show()

        save_path = f"{save_directory}/top_{top_x_value}_{species_name}.png"
        plt.savefig(save_path)


def plot_gene_expression_per_gene(df: pd.DataFrame, max_y: float = None, save_directory: str = os.getcwd(), save_to_mlflow: bool = False) -> None:
    """
    Plot gene expression per gene using an interactive line plot for each species.

    Args:
        df (pd.DataFrame): DataFrame containing 'Gene', 'Real Values', 'Predicted Values', and 'Species' columns.
        max_y (float, optional): Maximum y-axis value for the plot. If not provided, it will be determined from the data.
        save_directory (str, optional): The directory to save the generated plot. Defaults to the current working directory.
    Returns:
        None
    """

    if not os.path.isdir(save_directory):
        os.makedirs(save_directory, exist_ok=True)

    if max_y is None:
        max_y = max(df['Predicted Values'].max(), df['Real Values'].max())

    grouped_data = df.groupby('Species').apply(lambda x: {
        'genes': x['Gene'].tolist(),
        'real_values': x['Real Values'].tolist(),
        'predicted_values': x['Predicted Values'].tolist()
    }).reset_index()

    for species in df['Species'].unique():
        df_signal_species = pd.DataFrame({
            "real_values": grouped_data[grouped_data.Species == species][0].values[0]['real_values'],
            "genes": grouped_data[grouped_data.Species == species][0].values[0]['genes'],
            "predicted_values": grouped_data[grouped_data.Species == species][0].values[0]['predicted_values']
        })

        df_signal_species = df_signal_species.sort_values("real_values", ascending=False).reset_index()

        # multiple unpivot columns
        melted_signal = pd.melt(df_signal_species, id_vars=['genes'], value_vars=['real_values', 'predicted_values'],
                                var_name='Expression')

        # Create an interactive plot using Plotly Express
        fig = px.line(melted_signal, x='genes', y='value', color="Expression",
                      title=f'{species} - Gene Expression per gene',
                      line_shape='linear')
        fig.update_yaxes(title="Expression")
        fig.update_layout(xaxis_title='Gene', width=1000, height=400, template="none")
        fig.update_layout(yaxis_range=[0, max_y])
        # fig.show()

        fig.write_html(f"{save_directory}/expression_signal_{species}.html")

        if save_to_mlflow:
            mlflow.log_figure(fig, f'expression_signal_{species}.html')


# Filter out FutureWarnings related to groupby
warnings.simplefilter(action='ignore', category=FutureWarning)

if __name__ == "__main__":
    
    # Create fake data
    np.random.seed(42)  # for reproducibility
    # Assuming three species: Species A, Species B, Species C
    species = ['Species A'] * 50 + ['Species B'] * 50 + ['Species C'] * 50
    real_values = np.concatenate([
        np.random.normal(10, 2, 50),   # Species A
        np.random.normal(15, 3, 50),   # Species B
        np.random.normal(5, 1, 50)     # Species C
    ])
    predicted_values = real_values + np.random.normal(0, 2, 150)
    # Create DataFrame
    df = pd.DataFrame({'Species': species, 'Real Values': real_values, 'Predicted Values': predicted_values})
    amount_promoter = np.random.randint(0, 10, size=150)
    # Create DataFrame
    df['Amount Promoter']= amount_promoter


    save_directory = "visualizations/sample_plots"

    # Plot scatter plot with line of best fit
    plot_scatter_line_of_best_fit(df, save_directory=save_directory)

    # Plot scatter plot with line of best fit for each species
    plot_species_scatter_line_of_best_fit(df, save_directory=save_directory)

    # Plot mean residuals for different promoter bins across species
    plot_residuals_by_promoter_bin(df, save_directory=save_directory)



    # Creating fake data for testing
    np.random.seed(42)
    species = np.random.choice(['Species A', 'Species B', 'Species C'], size=500)
    genes = [f'Gene_{i}' for i in range(1, 501)]
    real_values = np.random.rand(500) * 10
    predicted_values = real_values + np.random.randn(500)

    # Create DataFrame
    df = pd.DataFrame({'Species': species, 'Gene': genes, 'Real Values': real_values, 'Predicted Values': predicted_values})

    # Plot top-X clustered bar chart for each species
    plot_top_x_clustered_bar_chart(df, top_x_value=5, save_directory=save_directory)

    # Plot gene expression per gene
    plot_gene_expression_per_gene(df, save_directory=save_directory, save_to_mlflow=False)