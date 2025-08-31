"""
Exploratory Data Analysis helpers for the Gold World Happiness dataset.

This module provides a lightweight, teaching-friendly EDA utility with:
- concise preview/summary helpers,
- common plots (histograms, boxplots, correlations, simple geo scatter),
- and a small configuration object to control seaborn/matplotlib styling.

The emphasis is readability and intent — comments explain *why* each step exists.
"""

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------------------------------------------------------------
# Configuration (style, saving, figure quality)
# ----------------------------------------------------------------------

@dataclass
class EDAConfig:
    """
    Simple configuration for EDA output.
    
    Parameters
    ----------
    save_dir:pathlib.Path or None, optional
        If provided, figures are saved into this folder; otherwise they are shown.
    style: str, optional
        Seaborn style name, e.g., "whitegrid" (default).
    context: str, optional
        Seaborn context, e.g., "notebook" (default).
    fig_dpi: int, optional
        Figure DPI for saved/shown images (default 110).
    palette: str or None, optional
        Optional seaborn palette name (e.g., "mako", "viridis"). If invalid, the default
        is seaborn palette is kept.
    use_theme: bool, optional
        If True, call 'sns.set_theme()' for modern seaborn defaults (default True).
    """

    save_dir: Optional[Path] = None
    style: str = "whitegrid"
    context: str = "notebook"
    fig_dpi: int = 110
    palette: Optional[str] = "viridis"
    use_theme: bool = True

# ----------------------------------------------------------------------
# Core Explorer
# ----------------------------------------------------------------------

class EDAExplorer:
    """
    Lightweight EDA helper for the Gold World Happiness dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        The gold dataset to explore (copied internally)
    config : EDAConfig or None, optional
        Configuration for styling and saving (default: 'EDAConfig()')
    lat_col : str, optional
        Latitude column name for simple geo plots (default: "latitude")
    lon_col : str, optional
        Longitude column name for simple geo plots (default: "longitude")
    """

    def __init__(
        self,
        df: pd.DataFrame,
        config: Optional[EDAConfig] = None,
        lat_col: str = "latitude",
        lon_col: str = "longitude",
    ) -> None:
        
        # Keep defensive copy so EDA never mutates caller's DataFrame. 
        self.df = df.copy()

        # Initialise configuration and geolocation columns
        self.config = config or EDAConfig()
        self.lat_col = lat_col
        self.lon_col = lon_col


        # Apply seaborn styling/context (teaching-friendly, consistent visuals).
        if self.config.use_theme:
            sns.set_theme()
        sns.set_style(self.config.style)
        sns.set_context(self.config.context)

        # Try to set a named palette if provided; keep defaults if invalid.
        if self.config.palette:
            try:
                sns.set_palette(self.config.palette)
            except Exception:
                # If invalid palette name, keep seaborn default.
                pass
    
    # ------------------------------------------------------------------
    # Step 1: Summary Statics
    # ------------------------------------------------------------------

    def preview(self, n: int = 5, console: bool = True) -> None:
        """
        Show head/tail snapshot for quick inspection
        
        Parameters
        ----------
        n : int, optional
            Number of rows to show (default: 5)
        console : bool, optional
            If True, print to console; otherwise, use rich display for notebook.
            
        """
        
        # Print first N rows.
        print(f"\nFirst {n} rows\n")
        if console:
            print(self.df.head(n))
        else:
            display(self.df.head(n))

        # Print last N rows.
        print(f"\nLast {n} rows\n")
        if console:
            print(self.df.tail(n))
        else:
            display(self.df.tail(n))
        

    def info(self) -> None:
        """
        Print shape, dtypes, and memory usage.
        """

        # Basic shape (rows, columns).
        print("\nShape:\n")
        print(self.df.shape)

        # Data types sorted.
        print("\nDtypes:")
        print(self.df.dtypes.sort_index())

        # Approximate memory footprint using 'deep=True' option
        memory_mb = self.df.memory_usage(deep=True).sum() / (1024 ** 2)
        print(f"\nMemory usage: {memory_mb:,.2f} MB\n")

    def describe_numeric(
            self, 
            exclude: Optional[Sequence[str]] = None, 
            console: bool = True
            ) -> pd.DataFrame:
        """
        Return numeric summary, excluding specific columns.
        
        Parameters
        ----------
        exclude: Sequence[str], optional
            Column names to exclude from description.
        console : bool, optional
            If True, print to console; otherwise, use rich display for notebook.
        """
        
        # Select numeric columns after optional exclusion.
        num = self._select_numeric(columns=None, exclude=exclude)

        # Fall-back if nothing remains after exclusion.
        if num.empty:
            print("No numeric columns to describe after exclusion.")
            return pd.DataFrame()
        
        # Describe and transpose.
        desc = num.describe().T

        # Print to console or display for notebook.
        if console:
            print(desc)
        else:
            display(desc)

    
    def describe_categorical(self, top_n: int = 10, console: bool = True) -> pd.DataFrame:
        """
        Summarise top value frequencies for object/category columns.
        
        Parameters
        ----------
        top_n: int, optional
            Top N values to show per column (default: 10).
        console : bool, optional
            If True, print to console; otherwise, return DataFrame.

        Returns
        -------
        pandas.DataFrame or None
            Returns a summary table when 'console=False', else prints.
        """
        
        # Identify object and category columns.
        cats = self.df.select_dtypes(include=["object", "category"]).columns
        if len(cats) == 0:
            print("No categorical/object columns found.")
            return pd.DataFrame()
        
        # Build a list of columns (column, value, count).
        rows: List[dict] = []
        for col in cats:
            vc = self.df[col].value_counts(dropna=False).head(top_n)
            for val, cnt in vc.items():
                rows.append({"column": col, "value": val, "count": int(cnt)})

        # Convert to DataFrame
        out = pd.DataFrame(rows)
        if out.empty:
            print("No categorical frequencies to show.")
            return out

        # Sort by column (ascending) then count (descending)
        out = out.sort_values(["column", "count"], ascending=[True, False], ignore_index=True)
        
        # Print to console or display for notebook.
        if console:
            print(out)
        else:
            return out
    
    def missing(self, plot: bool = True) -> pd.DataFrame:
        """
        Tabulate missing values; optionally plot a horizontal bar chart.
        
        Parameters
        ----------
        plot: bool, optional
            If True, show/save a horizontal bar chart; else, returns a table.

        Returns
        -------
        pandas.DataFrame or None
            Table with counts when 'console=False'; else, None.
        """

        # Compute NA counts per column, sorted by missing value count.
        missing = self.df.isna().sum().sort_values(ascending=False)
        missing = missing[missing > 0]

        # If 'plot=True' and DataFrame is not empty.
        if plot and not missing.empty:

            # Height set to scale with number of missing columns.
            fig, ax = plt.subplots(
                figsize=(8, max(1.8, 0.3 * len(missing))),
                dpi=self.config.fig_dpi,
            )

            # Output simple  horizontal bar chart.
            missing.sort_values().plot.barh(ax=ax)
            ax.set_title("Missing values by column")
            ax.set_xlabel("Count")
            ax.set_ylabel("")

            # Save/show bar chart.
            self._finalise(fig, "missing.png")

        # Otherwise return a tidy table.
        return missing.to_frame(name="missing")

    # ------------------------------------------------------------------
    # Step 2: Plots
    # ------------------------------------------------------------------

    def histograms(
        self,
        columns: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        bins: int = 30,
    ) -> None:
        """
        Plot histograms for numeric columns (or a filtered subset).

        Parameters
        ----------
        columns : Sequence[str] or None, optional
            Inclusion list of columns to plot. If None, use all numeric columns.
        exclude : Sequence[str] or None, optional
            Columns to exclude prior to plotting.
        bins : int, optional
            Number of bins for each histogram (default 30).
        """

        # Select numeric columns with include/exclude filters. 
        num = self._select_numeric(columns=columns, exclude=exclude)
        if num.empty:
            print("No numeric columns selected.")
            return

        # Compute grid to hold subplots
        cols = list(num.columns)
        n = len(cols)
        ncols = 3
        nrows = (n + ncols - 1) // ncols

        # Allocate a figure with enough room for all histograms.
        fig, axes = plt.subplots(
            nrows=nrows,
            ncols=ncols,
            figsize=(4 * ncols, 3 * nrows),
            dpi=self.config.fig_dpi,
        )
        axes = axes.ravel() if n > 1 else [axes]

        # Generate each histogram in its own axis.
        for ax, col in zip(axes, cols):
            sns.histplot(num[col].dropna(), bins=bins, ax=ax)
            ax.set_title(col)

        # Hide leftover axes    
        for ax in axes[len(cols):]:
            ax.axis("off")

        # Add supertitle and save/show plot
        fig.suptitle("Numeric distributions", y=1.02)
        plt.tight_layout()
        self._finalise(fig, "histograms.png")

    def boxplots(
        self,
        columns: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        show_outliers: bool = True,
    ) -> None:
        """
        Draw horizontal boxplots for numeric columns (optionally filtered).

        Parameters
        ----------
        columns : Sequence[str] or None, optional
            Inclusion list of columns to plot. If None, use all numeric columns.
        exclude : Sequence[str] or None, optional
            Columns to exclude prior to plotting.
        show_outliers : bool, optional
            Whether to show outliers (default: True)
        """

        # Select numeric subset.
        num = self._select_numeric(columns=columns, exclude=exclude)
        if num.empty:
            print("No numeric columns selected.")
            return

        # Melt to long format: Feature, Value.
        cols = list(num.columns)
        df_long = num.melt(var_name="Feature", value_name="Value").dropna(subset=["Value"])

        # Height scales with the number of features.
        fig_h = max(3, 0.45 * len(cols) + 1.5)
        fig, ax = plt.subplots(figsize=(8, fig_h), dpi=self.config.fig_dpi)

        # Draw plot containing the boxplots.
        sns.boxplot(data=df_long, x="Value", y="Feature", order=cols, showfliers=show_outliers, ax=ax)
        ax.set_title("Boxplots (horizontal)")
        ax.set_xlabel("Value")
        ax.set_ylabel("")
        plt.tight_layout()
        self._finalise(fig, "boxplots.png")

    def correlations(
        self,
        method: str = "pearson",
        top_k: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Compute and plot a correlation heatmap for numeric columns.
        
        Parameters
        ----------
        method : {"pearson", "spearman", "kendall"}, optional
            Correlation method to use (default: "pearson")
        top_k : int or None, optional
            If provided, keep only the top 'k' columns by variance.

        Returns
        -------
        pandas.DataFrame
            The correlation matrix for plotting.
        """

        # Work on numeric-only subset.
        num_df = self.df.select_dtypes(include="number")
        if num_df.empty:
            print("No numeric columns available for correlation.")
            return pd.DataFrame()

        # Optional variance-based pruning to declutter heatmap.
        if top_k is not None and 0 < top_k < len(num_df.columns):
            variances = num_df.var(numeric_only=True).sort_values(ascending=False)
            keep = variances.head(top_k).index
            num_df = num_df[keep]

        # Compute correlation
        corr = num_df.corr(method=method, numeric_only=True)
        if corr.empty:
            print("No numeric correlations to plot.")
            return corr

        # Size heatmap relative to number of features.
        size = 0.6 * len(corr.columns) + 3
        fig, ax = plt.subplots(figsize=(size, size), dpi=self.config.fig_dpi)

        # Create heatmap with diverging palette.
        sns.heatmap(corr, cmap="coolwarm", center=0, annot=False, linewidths=0.5, ax=ax)
        ax.set_title(f"Correlation heatmap ({method})")
        plt.tight_layout()
        self._finalise(fig, f"correlations_{method}.png")
        
    def geo_scatter(
        self,
        hue: Optional[str] = None,
        alpha: float = 0.8,
        s: int = 40,
    ) -> None:
        """
        Very simple lat/long scatter (no basemap), to eyeball coverage.
        
        Parameters
        ----------
        hue : str or None, optional
            Optional column name to colour points by.
        alpha : float, optional
            Alter transparency (default: 0.8)
        s : int, optional
            Marker size (default: 40)
        """

        # Ensure the expected geolocation columns exist.
        if self.lat_col not in self.df.columns or self.lon_col not in self.df.columns:
            print(f"Latitude/longitude not found (expected '{self.lat_col}', '{self.lon_col}').")
            return

        # Build a minimal DataFrame for plotting
        cols = [self.lat_col, self.lon_col]
        if hue and hue in self.df.columns:
            cols.append(hue)
        plot_df = self.df[cols].dropna()

        # If no rows have valid coordinates
        if plot_df.empty:
            print("No rows with latitude/longitude to plot.")
            return

        # Create the scatterplot figure
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=self.config.fig_dpi)
        
        # Use seaborn when hue column is provided.
        if hue and hue in plot_df.columns:
            sns.scatterplot(
                data=plot_df,
                x=self.lon_col, y=self.lat_col,
                hue=hue, s=s, edgecolor="none", alpha=alpha, ax=ax,
            )
            ax.legend(title=hue, bbox_to_anchor=(1.02, 1), loc="upper left")
        else:
            ax.scatter(plot_df[self.lon_col], plot_df[self.lat_col], s=s, alpha=alpha)

        ax.set_title("Geographic scatter (lon vs lat)")
        ax.set_xlabel(self.lon_col)
        ax.set_ylabel(self.lat_col)
        plt.tight_layout()
        self._finalise(fig, "geo_scatter.png")
    
    # ------------------------------------------------------------------
    # Step 3: Helpers
    # ------------------------------------------------------------------

    def _select_numeric(
            self,
            columns: Optional[Sequence[str]] = None,
            exclude: Optional[Sequence[str]] = None,
    ) -> pd.DataFrame:
        """
        Return numeric subset after applying optional include/exclude filters.
        
        Parameters
        ----------
        columns : Sequence[str] or None, optional
            If provided, restrict to these columns.
        exclude : Sequence[str] or None, optional
            Remove these columns from numeric set.

        Returns
        -------
        pandas.DataFrame
            The filtered numeric DataFrame.
        """
        
        # Start from numeric-only columns.
        num = self.df.select_dtypes(include="number")
        
        # Apply exclude filter to avoid later reselection.
        if exclude:
            ex = set(exclude)
            num = num[[c for c in num.columns if c not in ex]]

        # Apply inclusion list.    
        if columns:
            keep = [c for c in columns if c in num.columns]
            num = num[keep]
        return num

    def _finalise(self, fig: plt.figure, filename: str) -> None:
        """
        Show or save figure depending on configuration.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure to display or save.
        filename : str
            Output filename when 'save_dir' is configured.
        """
        
        # Save to disk if a folder has been configured; else, just show
        if self.config.save_dir:
            self.config.save_dir.mkdir(parents=True, exist_ok=True)
            out_path = self.config.save_dir / filename
            fig.savefig(out_path, bbox_inches="tight")
            print(f"Saved: {out_path}")
            plt.show()
            plt.close()
        else:
            plt.show()