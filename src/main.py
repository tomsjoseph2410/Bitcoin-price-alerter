import os
import time
import yaml
from btc_tracker import get_btc_data, get_percentage_difference_from_ath
from cache_object import AlertCache
from email_notifier import send_email
from logger_config import setup_logger

logger = setup_logger(__name__)


def main():
    # Load configuration from environment variable if available, else from file
    config_yaml = os.environ.get("CONFIG_YAML")
    if config_yaml:
        config = yaml.safe_load(config_yaml)
    else:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        with open(config_path) as f:
            config = yaml.safe_load(f)

    scheduler_interval_minutes = config["scheduler_interval_minutes"]
    thresholds = sorted(
        config["alert_threshold_percents"], reverse=True
    )
    email_cfg = config["email"]
    alert_cache = AlertCache()
    logger.info("Starting BTC price tracker service...")

    while True:
        try:
            btc_data = get_btc_data()
            price, ath = btc_data["price"], btc_data["ath"]
            logger.info(f"BTC: ${price} (ATH: ${ath})")

            for threshold in thresholds:
                percentage_fall_from_ath = get_percentage_difference_from_ath(price, ath)

                # Trigger alert if the drop percentage crosses the threshold and hasn't been alerted this week
                if alert_cache.last_alerted_threshold < threshold <= percentage_fall_from_ath:
                    logger.info(
                        f"BTC price has dropped more than {threshold}% from its all-time high. Actual drop: {percentage_fall_from_ath:.2f}%"
                    )
                    subject = f"Bitcoin Price Alert: Price Down More Than {threshold}% from ATH"
                    body = (
                        f"Alert: Bitcoin price has dropped by {percentage_fall_from_ath:.2f}% from its all-time high.\n"
                        f"Current price: ${price}\n"
                        f"All-time high: ${ath}\n\n\n"
                        f"This is an automated notification from your BTC tracker."
                    )
                    alert_cache.last_alerted_threshold = threshold
                    if email_cfg["is_feature_enabled"] is True:
                        logger.info("Email feature enabled, email will be sent for alert")
                        send_email(email_cfg, subject, body)
                    else:
                        logger.info("Email feature disabled, no email will be sent for alert")

                    # Stop checking further thresholds since the highest breached threshold (sorted descending) has been handled
                    break

        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")

        logger.info(f"Sleeping for {scheduler_interval_minutes} minutes")
        time.sleep(scheduler_interval_minutes * 60)


if __name__ == "__main__":
    main()
