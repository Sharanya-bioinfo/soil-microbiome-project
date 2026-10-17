# ============================================================
# PROJECT: SOIL MICROBIOME ANALYSIS ACROSS TROPICAL LAND USES
# Language: Python
# Editor: VS Code
# Input: Two original Excel datasets-soil_chemistry.xlsx,taxonomic_profile.xlsx
# Output: Graphs, summary tables, and exploratory analysis
# ============================================================

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



DATA_FOLDER = Path("data")
RESULTS_FOLDER = Path("results")

RESULTS_FOLDER.mkdir(exist_ok=True)

SOIL_FILE = DATA_FOLDER / "soil_chemistry.xlsx"
TAXA_FILE = DATA_FOLDER / "taxonomic_profile.xlsx"

# Check that both input files exist.
for file in [SOIL_FILE, TAXA_FILE]:
    if not file.exists():
        raise FileNotFoundError(
            f"File not found: {file}\n"
            "Check the data folder and Excel filenames."
        )



print("\n" + "=" * 60)
print("SOIL MICROBIOME ANALYSIS")
print("=" * 60)

soil = pd.read_excel(SOIL_FILE, sheet_name="Sheet1")
taxa = pd.read_excel(TAXA_FILE, sheet_name="spe")

# Rename the first column to Sample_ID.
soil = soil.rename(columns={"Unnamed: 0": "Sample_ID"})
taxa = taxa.rename(columns={"Unnamed: 0": "Sample_ID"})

# Remove accidental spaces from sample IDs.
soil["Sample_ID"] = soil["Sample_ID"].astype(str).str.strip()
taxa["Sample_ID"] = taxa["Sample_ID"].astype(str).str.strip()

# Standardise land-use labels.
soil["Landuse"] = soil["Landuse"].astype(str).str.strip()

print("\nSOIL DATA SHAPE:", soil.shape)
print("TAXONOMIC DATA SHAPE:", taxa.shape)

print("\nFIRST FIVE SOIL SAMPLES:")
print(soil.head().to_string(index=False))

print("\nFIRST FIVE TAXONOMIC SAMPLES:")
print(taxa.iloc[:, :6].head().to_string(index=False))

# Save an overview of the source data.
with open(RESULTS_FOLDER / "data_overview.txt", "w",
          encoding="utf-8") as report:
    report.write("SOIL DATA\n")
    report.write(f"Shape: {soil.shape}\n")
    report.write(f"Columns: {soil.columns.tolist()}\n\n")
    report.write("TAXONOMIC DATA\n")
    report.write(f"Shape: {taxa.shape}\n")
    report.write(f"Number of taxonomic categories: {taxa.shape[1] - 1}\n")



if soil["Sample_ID"].duplicated().any():
    raise ValueError("Duplicate sample IDs found in soil data.")

if taxa["Sample_ID"].duplicated().any():
    raise ValueError("Duplicate sample IDs found in taxonomic data.")

if set(soil["Sample_ID"]) != set(taxa["Sample_ID"]):
    soil_ids = set(soil["Sample_ID"])
    taxa_ids = set(taxa["Sample_ID"])

    raise ValueError(
        f"Sample IDs do not match.\n"
        f"Only in soil file: {soil_ids - taxa_ids}\n"
        f"Only in taxonomy file: {taxa_ids - soil_ids}"
    )

# Put both files in the same sample order.
taxa = (
    taxa.set_index("Sample_ID")
    .loc[soil["Sample_ID"]]
    .reset_index()
)

print("\nSAMPLES PER LAND-USE GROUP:")
print(soil["Landuse"].value_counts().to_string())

print("\nNUMBER OF SAMPLES:", len(soil))
print("NUMBER OF TAXONOMIC CATEGORIES:", taxa.shape[1] - 1)



taxon_columns = [
    column for column in taxa.columns
    if column != "Sample_ID"
]

taxa[taxon_columns] = taxa[taxon_columns].apply(
    pd.to_numeric, errors="coerce"
)

if taxa[taxon_columns].isna().any().any():
    raise ValueError(
        "Missing or non-numeric taxonomic counts were found."
    )

if (taxa[taxon_columns] < 0).any().any():
    raise ValueError("Negative taxonomic counts were found.")

sample_totals = taxa[taxon_columns].sum(axis=1)

if (sample_totals == 0).any():
    raise ValueError("At least one sample has a total count of zero.")

print("\nDATA QUALITY CHECK PASSED.")


# Formula:
# Relative abundance (%) =
# (Count for one category / Total counts in that sample) * 100

relative = taxa[taxon_columns].div(
    sample_totals, axis=0
) * 100

relative.insert(0, "Sample_ID", taxa["Sample_ID"])

# Attach the correct land-use group to each sample.
relative = relative.merge(
    soil[["Sample_ID", "Landuse"]],
    on="Sample_ID",
    validate="one_to_one"
)

# Save sample-level percentages.
relative.to_csv(
    RESULTS_FOLDER / "relative_abundance_by_sample.csv",
    index=False
)

print("\nRELATIVE ABUNDANCE CALCULATED.")
print("Example: first five samples and selected categories")
print(relative.iloc[:, :7].head().to_string(index=False))


# Calculate mean relative abundance in each land-use group.
mean_abundance = relative.groupby("Landuse")[taxon_columns].mean()

# Rank categories by their average across the four groups.
overall_mean = mean_abundance.mean(axis=0)
top_taxa = overall_mean.nlargest(10).index.tolist()

top_table = (
    overall_mean[top_taxa]
    .sort_values(ascending=False)
    .reset_index()
)
top_table.columns = ["Taxonomic_category", "Mean_relative_abundance_percent"]

print("\nTOP 10 TAXONOMIC CATEGORIES:")
print(top_table.to_string(index=False))

top_table.to_csv(
    RESULTS_FOLDER / "top_10_taxonomic_categories.csv",
    index=False
)

# Prepare plotting data.
plot_data = relative.melt(
    id_vars=["Sample_ID", "Landuse"],
    value_vars=top_taxa,
    var_name="Taxonomic_category",
    value_name="Relative_abundance_percent"
)

# Draw a grouped bar plot.
sns.set_theme(style="whitegrid")

plt.figure(figsize=(14, 7))

sns.barplot(
    data=plot_data,
    x="Taxonomic_category",
    y="Relative_abundance_percent",
    hue="Landuse",
    errorbar=None
)

plt.title("Top 10 Taxonomic Categories Across Land Uses")
plt.xlabel("Taxonomic category")
plt.ylabel("Mean relative abundance (%)")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Land use")
plt.tight_layout()

plt.savefig(
    RESULTS_FOLDER / "microbial_composition_top10.png",
    dpi=300
)
plt.close()

# Save mean relative abundance for all categories and groups.
taxonomic_summary = mean_abundance.reset_index().melt(
    id_vars="Landuse",
    var_name="Taxonomic_category",
    value_name="Mean_relative_abundance_percent"
)

taxonomic_summary.to_csv(
    RESULTS_FOLDER / "taxonomic_summary_by_landuse.csv",
    index=False
)



chemistry_columns = [
    "pH",
    "Total nitrogen (%)",
    "Total carbon (%)",
    "Available phosphorus (mg/kg)"
]

# Convert chemistry measurements to numeric values.
for column in chemistry_columns:
    soil[column] = pd.to_numeric(
        soil[column], errors="coerce"
    )

if soil[chemistry_columns].isna().any().any():
    raise ValueError(
        "Missing or non-numeric soil chemistry values were found."
    )

# Calculate descriptive statistics for each land-use group.
chemistry_summary = (
    soil.groupby("Landuse")[chemistry_columns]
    .agg(["count", "mean", "median", "std", "min", "max"])
)

chemistry_summary.to_csv(
    RESULTS_FOLDER / "soil_chemistry_summary.csv"
)

print("\nSOIL CHEMISTRY SUMMARY:")
print(chemistry_summary.round(3).to_string())


for variable in chemistry_columns:

    plt.figure(figsize=(9, 6))

    sns.boxplot(
        data=soil,
        x="Landuse",
        y=variable
    )

    sns.stripplot(
        data=soil,
        x="Landuse",
        y=variable,
        color="black",
        alpha=0.65,
        jitter=True
    )

    plt.title(f"{variable} Across Land-Use Groups")
    plt.xlabel("Land-use group")
    plt.ylabel(variable)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()

    safe_name = (
        variable.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "_")
    )

    plt.savefig(
        RESULTS_FOLDER / f"soil_{safe_name}.png",
        dpi=300
    )

    plt.close()


detected_categories = (taxa[taxon_columns] > 0).sum(axis=1)

richness_data = soil[
    ["Sample_ID", "Landuse", "pH"]
].copy()

richness_data["Detected_categories"] = detected_categories

richness_data.to_csv(
    RESULTS_FOLDER / "pH_and_detected_categories.csv",
    index=False
)

# Scatter plot.
plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=richness_data,
    x="pH",
    y="Detected_categories",
    hue="Landuse",
    s=100
)

plt.title("Soil pH vs Detected Taxonomic Categories")
plt.xlabel("Soil pH")
plt.ylabel("Number of detected categories")
plt.tight_layout()

plt.savefig(
    RESULTS_FOLDER / "pH_vs_detected_categories.png",
    dpi=300
)

plt.close()

# Calculate Pearson correlation as a simple exploratory measure.
# Correlation does not establish causation.

pearson_r = richness_data["pH"].corr(
    richness_data["Detected_categories"],
    method="pearson"
)

print("\nPEARSON CORRELATION:")
print("Soil pH vs detected taxonomic categories:", round(pearson_r, 4))

with open(
    RESULTS_FOLDER / "exploratory_correlation.txt",
    "w",
    encoding="utf-8"
) as report:
    report.write("Exploratory Pearson correlation\n")
    report.write("Variables: soil pH and detected taxonomic categories\n")
    report.write(f"Pearson r: {pearson_r:.4f}\n")
    report.write(
        "This correlation is exploratory and does not establish causation.\n"
    )



summary_text = f"""
SOIL MICROBIOME ANALYSIS: PROJECT SUMMARY

Number of soil samples: {len(soil)}
Number of taxonomic categories: {len(taxon_columns)}

Land-use groups:
{soil['Landuse'].value_counts().to_string()}

Research question:
How does soil taxonomic composition vary across the land-use groups?

Analyses completed:
1. Sample ID matching and data quality checks.
2. Sample-level relative abundance calculations.
3. Top 10 taxonomic category comparison.
4. Soil pH, nitrogen, carbon and phosphorus summaries.
5. Soil chemistry graphs.
6. Soil pH versus detected-category scatter plot.
7. Exploratory Pearson correlation.

Pearson correlation between soil pH and detected categories:
{pearson_r:.4f}

Interpretation caution:
Relative abundance represents proportions of recorded counts,
not absolute numbers of microorganisms. Observational patterns
do not establish causation.
"""

(RESULTS_FOLDER / "project_summary.txt").write_text(
    summary_text,
    encoding="utf-8"
)

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE!")
print("=" * 60)

print("\nYour results are saved in:")
print(RESULTS_FOLDER.resolve())

print("\nFILES CREATED:")

for file in sorted(RESULTS_FOLDER.iterdir()):
    print("-", file.name)

print("\nNext: open the results folder in VS Code and inspect the graphs.")