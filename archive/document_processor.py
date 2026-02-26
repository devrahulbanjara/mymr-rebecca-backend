import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from docling.document_converter import DocumentConverter
from loguru import logger
from tqdm import tqdm


class DocumentProcessor:
    def __init__(self):
        try:
            self.converter = DocumentConverter()
            self.is_available = True
            logger.success("Docling initialized successfully")
        except ImportError:
            logger.warning("Docling not installed. Install with: pip install docling")
            self.is_available = False

    def extract_text(self, file_path: Path) -> str:
        """Extract text from a single file"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = file_path.suffix.lower()

        if file_extension == ".txt":
            return file_path.read_text(encoding="utf-8")

        if self.is_available and file_extension in [
            ".pdf",
            ".docx",
            ".doc",
            ".png",
            ".jpg",
            ".jpeg",
        ]:
            return self._extract_with_docling(file_path)

        logger.warning(
            f"Unsupported file format: {file_extension}. Attempting to read as text."
        )

        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ValueError(
                f"Unable to read file {file_path}. Format may not be supported."
            )

    def _extract_with_docling(self, file_path: Path) -> str:
        """Extract text using Docling"""
        try:
            logger.info(f"Processing {file_path.name} with Docling")
            result = self.converter.convert(str(file_path))
            markdown_text = result.document.export_to_markdown()
            logger.success(f"Successfully extracted text from {file_path.name}")
            return markdown_text
        except Exception as e:
            logger.error(f"Docling extraction failed for {file_path}: {e}")
            if file_path.suffix.lower() == ".txt":
                return file_path.read_text(encoding="utf-8")
            raise ValueError(f"Failed to extract text from {file_path}: {e}")

    def process_single_file(
        self, file_path: Path, output_path: Optional[Path] = None
    ) -> Tuple[Path, bool, Optional[str]]:
        try:
            text = self.extract_text(file_path)

            if output_path is None:
                output_path = file_path.with_suffix(".md")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            output_path.write_text(text, encoding="utf-8")

            logger.success(f"✓ Saved: {output_path}")
            return (file_path, True, None)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"✗ Failed: {file_path.name} - {error_msg}")
            return (file_path, False, error_msg)

    def process_directory_parallel(
        self,
        input_dir: Path,
        file_extensions: List[str] = None,
        max_workers: int = None,
        recursive: bool = True,
    ) -> Dict[Path, Tuple[bool, Optional[str]]]:
        if file_extensions is None:
            file_extensions = [".pdf"]

        if max_workers is None:
            max_workers = min(multiprocessing.cpu_count(), 10)

        file_paths = []
        if recursive:
            for ext in file_extensions:
                file_paths.extend(input_dir.rglob(f"*{ext}"))
        else:
            for ext in file_extensions:
                file_paths.extend(input_dir.glob(f"*{ext}"))

        if not file_paths:
            logger.warning(
                f"No files found with extensions {file_extensions} in {input_dir}"
            )
            return {}

        logger.info(f"Found {len(file_paths)} files to process")
        logger.info(f"Using {max_workers} workers")

        results = {}

        # Process files in parallel with progress bar
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(self.process_single_file, path): path
                for path in file_paths
            }

            # Process completed tasks with progress bar
            with tqdm(total=len(file_paths), desc="Processing files") as pbar:
                for future in as_completed(future_to_path):
                    file_path = future_to_path[future]
                    try:
                        original_path, success, error = future.result()
                        results[original_path] = (success, error)
                    except Exception as e:
                        results[file_path] = (False, str(e))
                        logger.error(f"Unexpected error processing {file_path}: {e}")

                    pbar.update(1)

        return results

    def get_summary(self, results: Dict[Path, Tuple[bool, Optional[str]]]) -> Dict:
        """Generate a summary of processing results"""
        total = len(results)
        successful = sum(1 for success, _ in results.values() if success)
        failed = total - successful

        summary = {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
        }

        # Group failures by error type
        if failed > 0:
            error_types = {}
            for file_path, (success, error) in results.items():
                if not success and error:
                    error_types[error] = error_types.get(error, 0) + 1
            summary["error_types"] = error_types

        return summary

    def print_summary(self, results: Dict[Path, Tuple[bool, Optional[str]]]):
        """Print a formatted summary of results"""
        summary = self.get_summary(results)

        logger.info("=" * 60)
        logger.info("PROCESSING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total files: {summary['total']}")
        logger.info(
            f"Successful: {summary['successful']} ({summary['success_rate']:.1f}%)"
        )
        logger.info(f"Failed: {summary['failed']}")

        if summary.get("error_types"):
            logger.info("\nError breakdown:")
            for error, count in summary["error_types"].items():
                logger.info(f"  - {error}: {count} files")

        logger.info("=" * 60)
