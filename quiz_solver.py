"""
Quiz solver orchestrator using Gemini API.
Coordinates browser automation, data processing, and answer submission.
"""

import asyncio
import logging
import time
import json
import re
from typing import Any, Dict, Optional, List
from pathlib import Path

import google.generativeai as genai
import aiohttp

from config import settings
from browser_handler import BrowserHandler
from data_processor import DataProcessor
from visualizer import Visualizer

logger = logging.getLogger(__name__)


class QuizSolver:
    """
    Main quiz solving orchestrator.
    Uses Gemini API to understand questions and determine solution strategies.
    """

    def __init__(self):
        self.browser_handler = BrowserHandler()
        self.data_processor = DataProcessor()
        self.visualizer = Visualizer()
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def initialize(self) -> None:
        """Initialize all components."""
        logger.info("Initializing QuizSolver...")
        await self.browser_handler.initialize()
        logger.info("QuizSolver initialized successfully")

    async def cleanup(self) -> None:
        """Clean up all components."""
        logger.info("Cleaning up QuizSolver...")
        await self.browser_handler.cleanup()

    async def solve_quiz_chain(self, email: str, secret: str, initial_url: str) -> None:
        """
        Solve a chain of quiz questions starting from initial_url.

        Args:
            email: Student email
            secret: Student secret
            initial_url: Starting quiz URL
        """
        start_time = time.time()
        current_url = initial_url
        attempt_count = 0

        try:
            logger.info(f"Starting quiz chain from {initial_url}")

            while current_url and (time.time() - start_time) < settings.QUIZ_TIMEOUT:
                attempt_count += 1
                logger.info(f"Attempt #{attempt_count}: Solving quiz at {current_url}")

                try:
                    # Solve the quiz
                    answer = await self.solve_single_quiz(current_url)

                    # Submit the answer
                    result = await self.submit_answer(
                        email=email,
                        secret=secret,
                        url=current_url,
                        answer=answer
                    )

                    logger.info(f"Submission result: {result}")

                    # Check if correct and get next URL
                    if result.get('correct'):
                        logger.info(f"✓ Answer correct for {current_url}")
                        next_url = result.get('url')
                        if next_url:
                            current_url = next_url
                            logger.info(f"Moving to next quiz: {next_url}")
                        else:
                            logger.info("Quiz chain completed successfully!")
                            break
                    else:
                        reason = result.get('reason', 'Unknown reason')
                        logger.warning(f"✗ Answer incorrect: {reason}")

                        # Check if we should retry or move to next
                        next_url = result.get('url')
                        if next_url and next_url != current_url:
                            logger.info(f"Skipping to next quiz: {next_url}")
                            current_url = next_url
                        elif attempt_count < settings.MAX_RETRIES:
                            logger.info("Retrying same quiz with improved analysis...")
                            continue
                        else:
                            logger.error("Max retries reached, moving on or stopping")
                            break

                except Exception as e:
                    logger.error(f"Error solving quiz at {current_url}: {e}", exc_info=True)
                    break

            elapsed = time.time() - start_time
            logger.info(f"Quiz chain finished. Total time: {elapsed:.2f}s, Attempts: {attempt_count}")

        except Exception as e:
            logger.error(f"Fatal error in quiz chain: {e}", exc_info=True)

    async def solve_single_quiz(self, url: str) -> Any:
        """
        Solve a single quiz question.

        Args:
            url: Quiz URL to solve

        Returns:
            The answer to submit (could be number, string, boolean, object, or base64 image)
        """
        try:
            # Step 1: Get quiz content using browser
            quiz_data = await self.browser_handler.get_quiz_content(url)

            # Step 2: Extract and parse the question using Gemini
            question_analysis = await self.analyze_question(quiz_data)

            logger.info(f"Question analysis: {question_analysis}")

            # Step 3: Execute the solution strategy
            answer = await self.execute_solution(question_analysis, quiz_data)

            logger.info(f"Computed answer: {answer}")

            return answer

        except Exception as e:
            logger.error(f"Error solving quiz: {e}", exc_info=True)
            raise

    async def analyze_question(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini to analyze the quiz question and determine solution strategy.

        Args:
            quiz_data: Data extracted from quiz page

        Returns:
            Analysis including task type, required operations, and strategy
        """
        try:
            # Prepare content for Gemini
            analysis_prompt = f"""
Analyze this quiz question and determine how to solve it.

QUIZ PAGE CONTENT:
{quiz_data['text']}

RESULT ELEMENT TEXT:
{quiz_data['result_text']}

AVAILABLE LINKS:
{json.dumps(quiz_data['links'], indent=2)}

Your task is to:
1. Identify what the question is asking
2. Determine what data needs to be retrieved (if any files need to be downloaded)
3. Identify required processing steps (data cleaning, analysis, calculations)
4. Determine the expected answer format (number, string, boolean, JSON object, base64 image URI)
5. Extract the submit URL from the question

Provide your analysis in JSON format:
{{
    "question_summary": "Brief description of what is being asked",
    "task_type": "data_retrieval|data_analysis|visualization|text_processing|calculation",
    "download_required": true/false,
    "download_url": "URL to download if needed",
    "file_type": "pdf|csv|json|xlsx|image|other",
    "operations": ["list of operations needed: sum, mean, filter, sort, aggregate, etc."],
    "target_column": "column name if analyzing tabular data",
    "target_page": page number if PDF,
    "answer_type": "number|string|boolean|object|base64_image",
    "submit_url": "extracted submit URL from the question",
    "solution_strategy": "step by step approach to solve this"
}}
"""

            # Use Gemini to generate analysis
            response = await asyncio.to_thread(
                self.model.generate_content,
                analysis_prompt
            )

            response_text = response.text

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                # Fallback parsing
                analysis = {
                    "question_summary": "Could not parse question",
                    "task_type": "unknown",
                    "answer_type": "string",
                    "submit_url": self.extract_submit_url(quiz_data['text'])
                }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing question: {e}")
            raise

    async def execute_solution(self, analysis: Dict[str, Any], quiz_data: Dict[str, Any]) -> Any:
        """
        Execute the solution strategy based on analysis.

        Args:
            analysis: Question analysis from Claude
            quiz_data: Original quiz data

        Returns:
            The computed answer
        """
        try:
            # Download file if needed
            if analysis.get('download_required') and analysis.get('download_url'):
                file_path = await self.browser_handler.download_file(analysis['download_url'])
                file_type = analysis.get('file_type', 'unknown')

                # Process the file based on type
                if file_type == 'pdf':
                    data = self.data_processor.read_pdf(
                        file_path,
                        page_number=analysis.get('target_page')
                    )
                elif file_type == 'csv':
                    data = self.data_processor.read_csv(file_path)
                elif file_type == 'json':
                    data = self.data_processor.read_json(file_path)
                elif file_type in ['xlsx', 'xls']:
                    data = self.data_processor.read_excel(file_path)
                else:
                    data = None

                # Use Gemini to compute the answer based on the data
                answer = await self.compute_answer_with_gemini(analysis, data)

            else:
                # No file download needed, answer might be in the page content
                answer = await self.compute_answer_with_gemini(analysis, quiz_data)

            # Format answer according to expected type
            answer = self.format_answer(answer, analysis.get('answer_type', 'string'))

            return answer

        except Exception as e:
            logger.error(f"Error executing solution: {e}")
            raise

    async def compute_answer_with_gemini(self, analysis: Dict[str, Any], data: Any) -> Any:
        """
        Use Gemini to compute the final answer based on data.

        Args:
            analysis: Question analysis
            data: Processed data (could be DataFrame, dict, list, etc.)

        Returns:
            The computed answer
        """
        try:
            # Convert data to string representation for Gemini
            if hasattr(data, 'to_dict'):  # pandas DataFrame
                data_str = f"DataFrame with {len(data)} rows:\n{data.head(20).to_string()}\n\nSummary:\n{data.describe().to_string()}"
            elif isinstance(data, dict):
                if 'tables' in data and len(data['tables']) > 0:
                    # PDF with tables
                    table_info = []
                    for table in data['tables']:
                        df = table['dataframe']
                        table_info.append(f"Page {table['page']}, Table {table['table_index']}:\n{df.to_string()}")
                    data_str = "\n\n".join(table_info)
                else:
                    data_str = json.dumps(data, indent=2, default=str)
            else:
                data_str = str(data)

            computation_prompt = f"""
Based on this question analysis and data, compute the exact answer.

QUESTION: {analysis['question_summary']}

OPERATIONS NEEDED: {', '.join(analysis.get('operations', []))}

DATA:
{data_str[:10000]}  # Limit to avoid token overflow

ANSWER TYPE: {analysis.get('answer_type')}

TARGET COLUMN: {analysis.get('target_column', 'N/A')}

Provide ONLY the final answer value. No explanation, no formatting, just the raw answer.
If it's a number, provide just the number.
If it's a string, provide just the string.
If it's a boolean, provide true or false.
If it's a JSON object, provide the valid JSON.
"""

            # Use Gemini to generate answer
            response = await asyncio.to_thread(
                self.model.generate_content,
                computation_prompt
            )

            answer_text = response.text.strip()

            # Try to parse as JSON first
            try:
                answer = json.loads(answer_text)
            except json.JSONDecodeError:
                # Not JSON, return as is
                answer = answer_text

            return answer

        except Exception as e:
            logger.error(f"Error computing answer with Gemini: {e}")
            raise

    def format_answer(self, answer: Any, answer_type: str) -> Any:
        """Format answer according to expected type."""
        try:
            if answer_type == 'number':
                # Try to convert to number
                if isinstance(answer, str):
                    answer = answer.replace(',', '')  # Remove commas
                    try:
                        answer = int(answer)
                    except ValueError:
                        answer = float(answer)
            elif answer_type == 'boolean':
                if isinstance(answer, str):
                    answer = answer.lower() in ['true', 'yes', '1']
            elif answer_type == 'object':
                if isinstance(answer, str):
                    answer = json.loads(answer)

            return answer

        except Exception as e:
            logger.warning(f"Error formatting answer: {e}, returning as-is")
            return answer

    async def submit_answer(self, email: str, secret: str, url: str, answer: Any) -> Dict[str, Any]:
        """
        Submit answer to the quiz endpoint.

        Args:
            email: Student email
            secret: Student secret
            url: Quiz URL
            answer: The computed answer

        Returns:
            Response from the server
        """
        try:
            # Extract submit URL from the question text if available
            # For now, assume it's in the format shown in the example
            # The submit URL should have been extracted during analysis
            # As fallback, derive from quiz URL
            submit_url = url.replace('/quiz-', '/submit')

            payload = {
                "email": email,
                "secret": secret,
                "url": url,
                "answer": answer
            }

            logger.info(f"Submitting answer to {submit_url}: {json.dumps(payload, indent=2, default=str)}")

            async with aiohttp.ClientSession() as session:
                async with session.post(submit_url, json=payload) as response:
                    result = await response.json()
                    logger.info(f"Submit response ({response.status}): {result}")
                    return result

        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            raise

    @staticmethod
    def extract_submit_url(text: str) -> Optional[str]:
        """Extract submit URL from question text."""
        # Look for URL patterns
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)

        # Find submit URL
        for url in urls:
            if 'submit' in url.lower():
                return url

        return None
