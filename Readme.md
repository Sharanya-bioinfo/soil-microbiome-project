Soil Microbiome Analysis Across Tropical Land Uses



**Project overview**

This project explores soil microbial taxonomic composition and soil chemical measurements across tropical land-use groups using publicly available data



**Research question**

How does soil microbial taxonomic composition vary across forest logging histories and oil-palm plantation land use?



**Dataset**

Tripathi et al. (2016), \*The impact of tropical forest logging and oil palm agriculture on the soil microbiome.\*



Dataset: https://doi.org/10.5061/dryad.17n4d



Research paper: https://doi.org/10.1111/mec.13620



xlsx files used from zipped folder downloaded-

1)M5NR taxonomic profile at class level.xlsx

2)Soil chemical variables.xlsx



Project Directory Structure

soil-microbiome-project/

│

├── data/                               Input directory 

│   ├── soil\_chemistry.xlsx             # Soil chemical metadata (pH, C, N, P)

│   └── taxonomic\_profile.xlsx          # Taxonomic read counts matrix

│

├── results/                            

│   ├── relative\_abundance\_by\_sample.csv

│   ├── top\_10\_taxonomic\_categories.csv

│   ├── taxonomic\_summary\_by\_landuse.csv

│   ├── soil\_chemistry\_summary.csv

│   ├── pH\_and\_detected\_categories.csv

│   ├── exploratory\_correlation.txt

│   ├── project\_summary.txt

│   ├── microbial\_composition\_top10.png

│   ├── soil\_ph.png

│   ├── soil\_total\_nitrogen\_%.png

│   ├── soil\_total\_carbon\_%.png

│   ├── soil\_available\_phosphorus\_mgkg.png

│   └── pH\_vs\_detected\_categories.png

│

├── analyze\_soil.py                     # Main script

└── README.md                           # Project documentation



Tools

\- Python

\- pandas

\- Matplotlib

\- Seaborn



Workflow

1\. Load and match soil samples across two Excel datasets

2\. Calculate sample-level relative abundance from taxonomic counts

3\. Compare major taxonomic categories across land-use groups

4\. Summarise and visualise soil chemical measurements

5\. Explore the relationship between soil pH and detected taxonomic categories



&#x20;Limitations

This is just an  exploratory analysis of already published data  whereas Relative abundance is not a direct measure of absolute microbial abundance and this analysis does not establish causation or directly measure microbial activity



Reproducibility

Install the required packages and run `python analyze_soil.py

Author-sharanya-bioinfo

Bioinformatics and Biotechnology student



