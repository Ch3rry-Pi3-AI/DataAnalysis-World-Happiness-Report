from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class EDAConfig:
    """Simple configuration for EDA output."""
    save_dir: Optional[Path] = None
    style: str = "whitegrid"
    context: str = "notebook"
    fig_dpi: int = 110
    palette: Optional[str] = None 

class EDAExplorer:
    """Lightweight EDA helper for the Gold World Happiness dataset."""
    def __init__(
            self,
            df: pd.DataFrame,
            config: Optional[EDAConfig] = None,
            lat_col: str = "latitude",
            lon_col: str = "longitude"
    ) -> None:
        
        self.df = df.copy()
        self.config = config or EDAConfig()
        self.lat_col = lat_col
        self.lon_col = lon_col

        sns.set_style(self.config.style)
        sns.set_context(self.config.context)
        if self.config.palette:
            try:
                sns.set_palette(self.config.palette)
            except:
                pass

    def preview(self, n: int = 5) -> None:
        """Show head and tail"""
        print(f"\nFirst {n} rows\n")
        print(self.df.head(n))
        print(f"\nLast {n} rows\n")
        print(self.df.tail(n))
        
    def info(self) -> None:
        """Print shape, dtypes, memory usage, and basic null summary"""
        print("\nShape:\n")
        print(self.df.shape)
        print("\nDtypes:\n")
        print(self.df.dtypes.sort_index())

        memory_mb = self.df.memory_usage(deep=True).sum() / (1024 ** 2)
        print(f"Memory usage: {memory_mb} MB\n")

        na = self.df.isna().sum().sort_values(ascending=False)
        print("Missing values\n")
        print(na[na > 0])

    def describe_numeric(
            self, 
            exclude: Optional[Sequence[str]] = None
    ) -> pd.DataFrame:
        """Return numeric summary, excluding specific columns"""

        exclude = set(exclude or [])

        num = self.df.select_dtypes(include="number")
        num = num.drop(columns=[c for c in exclude if c in num.columns], errors="ignore")

        if num.empty:
            print("No numeric columns to describe after exclusion.")

        desc = num.describe().T
        print(desc)
        return desc
    
    def describe_categorical(self, top_n: int = 10) -> pd.DataFrame:
        "Show top frequencies for object/category columns"

        cats = self.df.select_dtypes(include=["object", "category"]).columns
        rows = []
        for col in cats:
            vc = self.df[col].value_counts(dropna=False).head(top_n)
            for index, count in vc.items():
                rows.append({"column": col, "value": index, "count": int(count)})
        out = pd.DataFrame(rows)
        print(out)
        return out
    
    def missing(self, plot: bool = True) -> pd.DataFrame:
        """Tabulate missing values; optionally plot a horizontal bar chart"""
        missing = self.df.isna().sum().sort_values(ascending=False)
        missing = missing[missing > 0]
        if plot and not missing.empty:
            fig, ax = plt.subplots(
                figsize = (8, 0.3 * len(missing)),
                dpi = self.config.fig_dpi
            )
            missing.sort_values().plot.barh(ax=ax)
            ax.set_title("Missing values by column")
            ax.set_xlabel("Count")
            self._finalise(fig, "missing.png")
        print(missing.to_frame(name="missing"))
        return missing.to_frame(name="missing")

    def histograms(
        self,
        columns: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        bins: int = 30,
    ) -> None:
        """Plot histograms for numeric columns (or a subset)."""
        num_cols = list(self.df.select_dtypes(include="number").columns)
        if exclude:
            ex = set(exclude)
            num_cols = [c for c in num_cols if c not in ex]

        cols = [c for c in (columns or num_cols) if c in self.df.columns]
        if not cols:
            print("No numeric columns selected.")
            return

        n = len(cols)
        ncols = 3
        nrows = (n + ncols - 1) // ncols

        fig, axes = plt.subplots(
            nrows=nrows, ncols=ncols,
            figsize=(4 * ncols, 2.8 * nrows),
        )
        axes = axes.ravel() if n > 1 else [axes]

        for ax, col in zip(axes, cols):
            sns.histplot(self.df[col].dropna(), bins=bins, ax=ax)
            ax.set_title(col)

        for ax in axes[len(cols):]:
            ax.axis("off")

        fig.suptitle("Numeric distributions", y=1.02)
        plt.tight_layout()


    def boxplots(
        self,
        columns: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        showfliers: bool = True,
    ) -> None:
        """Horizontal boxplots for numeric columns, with optional exclusion."""
        num_cols = list(self.df.select_dtypes(include="number").columns)
        if exclude:
            ex = set(exclude)
            num_cols = [c for c in num_cols if c not in ex]

        cols = [c for c in (columns or num_cols) if c in self.df.columns]
        if not cols:
            print("No numeric columns selected")
            return

        # Long-form for reliable horizontal layout
        df_long = self.df[cols].melt(var_name="Feature", value_name="Value").dropna(subset=["Value"])

        fig_h = max(3, 0.45 * len(cols) + 1.5)  # taller if many features
        fig, ax = plt.subplots(figsize=(8, fig_h))
        sns.boxplot(data=df_long, x="Value", y="Feature", order=cols, showfliers=showfliers, ax=ax)
        ax.set_title("Boxplots (horizontal)")
        ax.set_xlabel("Value")
        ax.set_ylabel("")

        plt.tight_layout()
        plt.show()

    def correlations(self, method: str = "pearson", top_k: Optional[int] = None) -> pd.DataFrame:
        """Compute and (optionally) plot a correlation heatmap for numeric columns."""
        num_df = self.df.select_dtypes(include="number")
        if top_k is not None and top_k < len(num_df.columns):
            # keep columns with largest variance to reduce clutter
            variances = num_df.var().sort_values(ascending=False)
            keep = variances.head(top_k).index
            num_df = num_df[keep]

        corr = num_df.corr(method=method)
        if corr.empty:
            print("No numeric correlations to plot.")
            return corr

        fig, ax = plt.subplots(figsize=(0.6 * len(corr.columns) + 3, 0.6 * len(corr.columns) + 1.5))
        sns.heatmap(corr, cmap="coolwarm", center=0, annot=False, linewidths=0.5, ax=ax)
        ax.set_title(f"Correlation heatmap ({method})")
        plt.tight_layout()
        return corr
    
    def geo_scatter(self, hue: Optional[str] = None, alpha: float = 0.8, s: int = 40) -> None:
        """Very simple lat/long scatter (no basemap), to eyeball coverage."""
        if self.lat_col not in self.df.columns or self.lon_col not in self.df.columns:
            print(f"Latitude/longitude not found (expected '{self.lat_col}', '{self.lon_col}').")
            return

        plot_df = self.df[[self.lat_col, self.lon_col] + ([hue] if hue and hue in self.df.columns else [])].dropna()
        if plot_df.empty:
            print("No rows with latitude/longitude to plot.")
            return

        fig, ax = plt.subplots(figsize=(8, 4.5))
        if hue and hue in plot_df.columns:
            sns.scatterplot(
                data=plot_df, x=self.lon_col, y=self.lat_col, hue=hue, s=s, edgecolor="none", alpha=alpha, ax=ax
            )
            ax.legend(title=hue, bbox_to_anchor=(1.02, 1), loc="upper left")
        else:
            ax.scatter(plot_df[self.lon_col], plot_df[self.lat_col], s=s, alpha=alpha)
        ax.set_title("Geographic scatter (lon vs lat)")
        ax.set_xlabel(self.lon_col)
        ax.set_ylabel(self.lat_col)
        plt.tight_layout()

    def _finalise(self, fig: plt.figure, filename: str) -> None:
        """Show or save figure depending on config."""
        if self.config.save_dir:
            self.config.save_dir.mkdir(parents=True, exist_ok=True)
            out_path = self.config.save_dir / filename
            fig.savefig(out_path, bbox_inches="tight")
            print(f"Saved: {out_path}")
            plt.close()
        else:
            plt.show()

if __name__ == "__main__":

    from load_gold_data import load_gold_happiness_data

    gold_df = load_gold_happiness_data()

    exp = EDAExplorer(df = gold_df)
    exp.preview()
    exp.info()
    exp.describe_numeric(exclude=["year", "latitude", "longitude"])
    exp.describe_categorical()
    exp.missing(plot=False)