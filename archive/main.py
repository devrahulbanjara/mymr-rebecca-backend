import sys
from pathlib import Path

from document_processor import DocumentProcessor
from loguru import logger


def main():
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
    )

    logger.add(
        "processing.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation="10 MB",
    )

    # right now it is this, it might change later
    input_dir = Path("Patients report raw data")

    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        logger.error("Please ensure the 'Patients report raw data' directory exists")
        return 1

    if not input_dir.is_dir():
        logger.error(f"Input path is not a directory: {input_dir}")
        return 1

    processor = DocumentProcessor()

    if not processor.is_available:
        logger.error("Docling is not available. Please install it")
        return 1

    results = processor.process_directory_parallel(
        input_dir=input_dir,
        file_extensions=[".pdf"],
        max_workers=4,
        recursive=True,
    )

    processor.print_summary(results)

    failed_files = [
        (str(path), error) for path, (success, error) in results.items() if not success
    ]

    if failed_files:
        failed_log_path = Path("failed_files.log")
        with open(failed_log_path, "w", encoding="utf-8") as f:
            f.write("Failed Files Report\n")
            f.write("=" * 80 + "\n\n")
            for file_path, error in failed_files:
                f.write(f"File: {file_path}\n")
                f.write(f"Error: {error}\n")
                f.write("-" * 80 + "\n\n")

        logger.info(f"Failed files log saved to: {failed_log_path}")

    summary = processor.get_summary(results)
    if summary["failed"] > 0:
        logger.warning(f"Completed with {summary['failed']} failures")
        return 1
    else:
        logger.success("All files processed successfully!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
