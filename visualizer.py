"""
Visualization utilities for creating charts and images.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

from config import settings

logger = logging.getLogger(__name__)

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100


class Visualizer:
    """Handles data visualization and chart generation."""

    @staticmethod
    def create_bar_chart(
        data: Union[pd.DataFrame, Dict],
        x_column: str,
        y_column: str,
        title: str = "Bar Chart",
        output_path: Optional[Path] = None
    ) -> Path:
        """Create a bar chart."""
        try:
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                df = data

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(df[x_column], df[y_column])
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            ax.set_title(title)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            if output_path is None:
                output_path = settings.TEMP_DIR / "bar_chart.png"

            plt.savefig(output_path)
            plt.close()

            logger.info(f"Bar chart saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error creating bar chart: {e}")
            raise

    @staticmethod
    def create_line_chart(
        data: Union[pd.DataFrame, Dict],
        x_column: str,
        y_columns: Union[str, List[str]],
        title: str = "Line Chart",
        output_path: Optional[Path] = None
    ) -> Path:
        """Create a line chart."""
        try:
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                df = data

            if isinstance(y_columns, str):
                y_columns = [y_columns]

            fig, ax = plt.subplots(figsize=(10, 6))
            for y_col in y_columns:
                ax.plot(df[x_column], df[y_col], marker='o', label=y_col)

            ax.set_xlabel(x_column)
            ax.set_ylabel('Value')
            ax.set_title(title)
            ax.legend()
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            if output_path is None:
                output_path = settings.TEMP_DIR / "line_chart.png"

            plt.savefig(output_path)
            plt.close()

            logger.info(f"Line chart saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error creating line chart: {e}")
            raise

    @staticmethod
    def create_scatter_plot(
        data: Union[pd.DataFrame, Dict],
        x_column: str,
        y_column: str,
        title: str = "Scatter Plot",
        output_path: Optional[Path] = None
    ) -> Path:
        """Create a scatter plot."""
        try:
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                df = data

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(df[x_column], df[y_column], alpha=0.6)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            ax.set_title(title)
            plt.tight_layout()

            if output_path is None:
                output_path = settings.TEMP_DIR / "scatter_plot.png"

            plt.savefig(output_path)
            plt.close()

            logger.info(f"Scatter plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error creating scatter plot: {e}")
            raise

    @staticmethod
    def create_histogram(
        data: Union[pd.DataFrame, pd.Series, List],
        column: Optional[str] = None,
        bins: int = 30,
        title: str = "Histogram",
        output_path: Optional[Path] = None
    ) -> Path:
        """Create a histogram."""
        try:
            if isinstance(data, pd.DataFrame):
                if column is None:
                    raise ValueError("column must be specified for DataFrame")
                values = data[column]
            elif isinstance(data, pd.Series):
                values = data
            else:
                values = data

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(values, bins=bins, edgecolor='black', alpha=0.7)
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
            ax.set_title(title)
            plt.tight_layout()

            if output_path is None:
                output_path = settings.TEMP_DIR / "histogram.png"

            plt.savefig(output_path)
            plt.close()

            logger.info(f"Histogram saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error creating histogram: {e}")
            raise

    @staticmethod
    def create_pie_chart(
        data: Union[pd.DataFrame, Dict],
        labels_column: str,
        values_column: str,
        title: str = "Pie Chart",
        output_path: Optional[Path] = None
    ) -> Path:
        """Create a pie chart."""
        try:
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                df = data

            fig, ax = plt.subplots(figsize=(10, 8))
            ax.pie(
                df[values_column],
                labels=df[labels_column],
                autopct='%1.1f%%',
                startangle=90
            )
            ax.set_title(title)
            plt.tight_layout()

            if output_path is None:
                output_path = settings.TEMP_DIR / "pie_chart.png"

            plt.savefig(output_path)
            plt.close()

            logger.info(f"Pie chart saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error creating pie chart: {e}")
            raise

    @staticmethod
    def create_heatmap(
        data: pd.DataFrame,
        title: str = "Heatmap",
        output_path: Optional[Path] = None
    ) -> Path:
        """Create a heatmap (useful for correlation matrices)."""
        try:
            fig, ax = plt.subplots(figsize=(12, 10))
            sns.heatmap(data, annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
            ax.set_title(title)
            plt.tight_layout()

            if output_path is None:
                output_path = settings.TEMP_DIR / "heatmap.png"

            plt.savefig(output_path)
            plt.close()

            logger.info(f"Heatmap saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error creating heatmap: {e}")
            raise

    @staticmethod
    def create_box_plot(
        data: Union[pd.DataFrame, Dict],
        columns: Union[str, List[str]],
        title: str = "Box Plot",
        output_path: Optional[Path] = None
    ) -> Path:
        """Create a box plot."""
        try:
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                df = data

            if isinstance(columns, str):
                columns = [columns]

            fig, ax = plt.subplots(figsize=(10, 6))
            df[columns].boxplot(ax=ax)
            ax.set_title(title)
            ax.set_ylabel('Value')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            if output_path is None:
                output_path = settings.TEMP_DIR / "box_plot.png"

            plt.savefig(output_path)
            plt.close()

            logger.info(f"Box plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error creating box plot: {e}")
            raise
