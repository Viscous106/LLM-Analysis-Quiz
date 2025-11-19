"""
Data processing utilities for various formats (PDF, CSV, JSON, Excel, etc.)
"""

import logging
import json
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import PyPDF2
import pdfplumber
from PIL import Image

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data processing for various file formats and data types."""

    @staticmethod
    def read_pdf(file_path: Path, page_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Read PDF file and extract text and tables.

        Args:
            file_path: Path to PDF file
            page_number: Specific page to extract (1-indexed), None for all pages

        Returns:
            Dict containing text and tables from the PDF
        """
        try:
            logger.info(f"Reading PDF: {file_path}")
            result = {
                'text': [],
                'tables': [],
                'num_pages': 0
            }

            # Extract text using PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                result['num_pages'] = len(pdf_reader.pages)

                if page_number:
                    pages_to_process = [page_number - 1]  # Convert to 0-indexed
                else:
                    pages_to_process = range(len(pdf_reader.pages))

                for page_idx in pages_to_process:
                    if 0 <= page_idx < len(pdf_reader.pages):
                        page = pdf_reader.pages[page_idx]
                        text = page.extract_text()
                        result['text'].append({
                            'page': page_idx + 1,
                            'content': text
                        })

            # Extract tables using pdfplumber
            with pdfplumber.open(file_path) as pdf:
                if page_number:
                    pages_to_process = [page_number - 1]
                else:
                    pages_to_process = range(len(pdf.pages))

                for page_idx in pages_to_process:
                    if 0 <= page_idx < len(pdf.pages):
                        page = pdf.pages[page_idx]
                        tables = page.extract_tables()
                        for table_idx, table in enumerate(tables):
                            if table:
                                # Convert to DataFrame
                                df = pd.DataFrame(table[1:], columns=table[0])
                                result['tables'].append({
                                    'page': page_idx + 1,
                                    'table_index': table_idx,
                                    'data': df.to_dict('records'),
                                    'dataframe': df
                                })

            logger.info(f"Extracted {len(result['text'])} pages and {len(result['tables'])} tables")
            return result

        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            raise

    @staticmethod
    def read_csv(file_path: Path) -> pd.DataFrame:
        """Read CSV file into a pandas DataFrame."""
        try:
            logger.info(f"Reading CSV: {file_path}")
            df = pd.read_csv(file_path)
            logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {e}")
            raise

    @staticmethod
    def read_excel(file_path: Path, sheet_name: Optional[str] = None) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Read Excel file into pandas DataFrame(s)."""
        try:
            logger.info(f"Reading Excel: {file_path}")
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                logger.info(f"Loaded sheet '{sheet_name}' with {len(df)} rows")
                return df
            else:
                dfs = pd.read_excel(file_path, sheet_name=None)
                logger.info(f"Loaded {len(dfs)} sheets")
                return dfs
        except Exception as e:
            logger.error(f"Error reading Excel {file_path}: {e}")
            raise

    @staticmethod
    def read_json(file_path: Path) -> Union[Dict, List]:
        """Read JSON file."""
        try:
            logger.info(f"Reading JSON: {file_path}")
            with open(file_path, 'r') as file:
                data = json.load(file)
            logger.info(f"Loaded JSON data")
            return data
        except Exception as e:
            logger.error(f"Error reading JSON {file_path}: {e}")
            raise

    @staticmethod
    def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform basic analysis on a DataFrame.

        Returns:
            Dict containing analysis results
        """
        try:
            analysis = {
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'summary_stats': {},
                'sample_data': df.head(5).to_dict('records')
            }

            # Numerical columns summary
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                analysis['summary_stats'] = df[numeric_cols].describe().to_dict()

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing DataFrame: {e}")
            raise

    @staticmethod
    def compute_aggregations(df: pd.DataFrame, operations: Dict[str, Any]) -> Any:
        """
        Compute various aggregations on DataFrame.

        Args:
            df: DataFrame to analyze
            operations: Dict specifying operations like {'sum': 'column_name', 'mean': 'column_name'}

        Returns:
            Results of the operations
        """
        try:
            results = {}

            for operation, column in operations.items():
                if column not in df.columns:
                    logger.warning(f"Column '{column}' not found in DataFrame")
                    continue

                if operation == 'sum':
                    results[f'sum_{column}'] = df[column].sum()
                elif operation == 'mean':
                    results[f'mean_{column}'] = df[column].mean()
                elif operation == 'median':
                    results[f'median_{column}'] = df[column].median()
                elif operation == 'count':
                    results[f'count_{column}'] = df[column].count()
                elif operation == 'min':
                    results[f'min_{column}'] = df[column].min()
                elif operation == 'max':
                    results[f'max_{column}'] = df[column].max()
                elif operation == 'std':
                    results[f'std_{column}'] = df[column].std()

            return results

        except Exception as e:
            logger.error(f"Error computing aggregations: {e}")
            raise

    @staticmethod
    def image_to_base64(image_path: Path) -> str:
        """Convert image to base64 string for embedding."""
        try:
            with open(image_path, 'rb') as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                # Detect image type
                ext = image_path.suffix.lower()
                mime_type = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }.get(ext, 'image/png')

                return f"data:{mime_type};base64,{encoded}"
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            raise

    @staticmethod
    def extract_numbers_from_text(text: str) -> List[float]:
        """Extract all numbers from text."""
        import re
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        return [float(m) for m in matches if m]

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by handling common issues.

        - Remove completely empty rows/columns
        - Strip whitespace from string columns
        - Convert numeric strings to numbers
        """
        try:
            # Remove empty rows and columns
            df = df.dropna(how='all')
            df = df.dropna(axis=1, how='all')

            # Strip whitespace from string columns
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]

            # Try to convert numeric strings to numbers
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass

            return df

        except Exception as e:
            logger.error(f"Error cleaning DataFrame: {e}")
            raise
