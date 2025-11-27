"""Main entry point for batch image denoising."""
import logging
from config_loader import load_config
from processor import ImageProcessor
from metrics import save_metrics_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """Main execution function."""
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = load_config('config.ini')
        
        logger.info(f"Input folder: {config.input_path}")
        logger.info(f"Output folder: {config.output_path}")
        
        # Process images
        processor = ImageProcessor(config)
        processed_count, metrics_list = processor.process_batch()
        
        # Save metrics
        if processed_count > 0:
            csv_file = save_metrics_to_csv(metrics_list, config.output_path)
            logger.info(f"📊 Metrics saved to: {csv_file}")
            logger.info(f"✓ Successfully processed {processed_count} images")
        else:
            logger.warning("No images were processed")
    
    except FileNotFoundError as e:
        logger.error(str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
