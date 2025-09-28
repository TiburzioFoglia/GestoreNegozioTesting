import unittest
from unittest.mock import MagicMock, patch, call

from src.online_store_manager import OnlineStoreManager
# Assumiamo che le classi di dipendenza siano in external_dependencies.py
from src.external_dependencies import (ProductDatabase, InventorySystem, PaymentGateway, PromoCodeValidator,
                                       NotificationService, ShippingService, AuditLogger, FraudDetectionService,
                                       TaxCalculatorService, LoyaltyProgramManager, AnalyticsTracker,
                                       CurrencyConverter, CRMSystem, GiftOptionsService, DigitalAssetManager,
                                       RMAManager, ComplianceChecker)


class TestOnlineStoreManager(unittest.TestCase):

    def setUp(self):
        """Configura un ambiente di test pulito prima di ogni test."""
        self.mock_product_db = MagicMock(spec=ProductDatabase)
        self.mock_inventory_sys = MagicMock(spec=InventorySystem)
        self.mock_payment_gw = MagicMock(spec=PaymentGateway)
        self.mock_promo_validator = MagicMock(spec=PromoCodeValidator)
        self.mock_notification_service = MagicMock(spec=NotificationService)
        self.mock_shipping_service = MagicMock(spec=ShippingService)
        self.mock_audit_logger = MagicMock(spec=AuditLogger)
        self.mock_fraud_detector = MagicMock(spec=FraudDetectionService)
        self.mock_tax_calculator = MagicMock(spec=TaxCalculatorService)
        self.mock_loyalty_manager = MagicMock(spec=LoyaltyProgramManager)
        self.mock_analytics_tracker = MagicMock(spec=AnalyticsTracker)
        self.mock_currency_converter = MagicMock(spec=CurrencyConverter)
        self.mock_crm_system = MagicMock(spec=CRMSystem)
        self.mock_gift_options = MagicMock(spec=GiftOptionsService)
        self.mock_digital_manager = MagicMock(spec=DigitalAssetManager)
        self.mock_rma_manager = MagicMock(spec=RMAManager)
        self.mock_compliance_checker = MagicMock(spec=ComplianceChecker)

        self.store_manager = OnlineStoreManager(
            self.mock_product_db, self.mock_inventory_sys, self.mock_payment_gw,
            self.mock_promo_validator, self.mock_notification_service, self.mock_shipping_service,
            self.mock_audit_logger, self.mock_fraud_detector, self.mock_tax_calculator,
            self.mock_loyalty_manager, self.mock_analytics_tracker,
            self.mock_currency_converter, self.mock_crm_system, self.mock_gift_options,
            self.mock_digital_manager, self.mock_rma_manager, self.mock_compliance_checker
        )
        self.customer_info = {"id": "CUST001", "email": "test@example.com", "address": "123 Via Prova"}
        self.card_details = "valid_card_details"

    # --- Test per __init__ ---
    def test_init_raises_error_if_any_dependency_is_none(self):
        with self.assertRaises(ValueError):
            OnlineStoreManager(self.mock_product_db, self.mock_inventory_sys, self.mock_payment_gw,
                               self.mock_promo_validator, self.mock_notification_service, None, self.mock_audit_logger)

    # --- Test per get_product_info ---
    def test_get_product_info_success(self):
        self.mock_product_db.get_product_details.return_value = {"id": "P123", "name": "Test Product"}
        result = self.store_manager.get_product_info("P123")
        self.assertEqual(result["name"], "Test Product")

    def test_get_product_info_not_found(self):
        self.mock_product_db.get_product_details.return_value = None
        self.assertIsNone(self.store_manager.get_product_info("P999"))

    def test_get_product_info_with_empty_id(self):
        self.assertIsNone(self.store_manager.get_product_info(""))
        self.mock_product_db.get_product_details.assert_not_called()

    # --- Test per check_availability ---
    def test_check_availability_is_available(self):
        self.mock_product_db.check_product_availability.return_value = True
        self.assertTrue(self.store_manager.check_availability("P123", 10))
        self.mock_product_db.check_product_availability.assert_called_once_with("P123", 10)

    def test_check_availability_is_not_available(self):
        self.mock_product_db.check_product_availability.return_value = False
        self.assertFalse(self.store_manager.check_availability("P123", 100))

    def test_check_availability_with_zero_quantity(self):
        self.assertFalse(self.store_manager.check_availability("P123", 0))
        self.mock_product_db.check_product_availability.assert_not_called()

    def test_check_availability_with_negative_quantity(self):
        self.assertFalse(self.store_manager.check_availability("P123", -5))
        self.mock_product_db.check_product_availability.assert_not_called()

    # --- Test per process_order ---
    def test_process_order_success(self):
        self.mock_product_db.get_product_details.return_value = {"price": 25.50}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_payment_gw.process_payment.return_value = {"status": "success", "transaction_id": "TXYZ"}

        result = self.store_manager.process_order("P123", 2, "valid_card")

        self.assertEqual(result["status"], "success")
        self.mock_payment_gw.process_payment.assert_called_once_with(51.00, "valid_card")
        self.mock_inventory_sys.update_stock.assert_called_once_with("P123", -2)

    def test_process_order_product_not_found(self):
        self.mock_product_db.get_product_details.return_value = None
        result = self.store_manager.process_order("P999", 1, "card")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Prodotto non trovato.")
        self.mock_payment_gw.process_payment.assert_not_called()

    def test_process_order_not_available(self):
        self.mock_product_db.get_product_details.return_value = {"price": 10}
        self.mock_product_db.check_product_availability.return_value = False
        result = self.store_manager.process_order("P123", 10, "card")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Quantità non disponibile.")

    def test_process_order_payment_fails(self):
        self.mock_product_db.get_product_details.return_value = {"price": 10}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_payment_gw.process_payment.return_value = {"status": "failed"}
        result = self.store_manager.process_order("P123", 1, "invalid_card")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Pagamento fallito.")
        self.mock_inventory_sys.update_stock.assert_not_called()

    def test_process_order_with_zero_quantity(self):
        result = self.store_manager.process_order("P123", 0, "card")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "La quantità deve essere positiva.")

    def test_process_order_product_with_zero_price(self):
        self.mock_product_db.get_product_details.return_value = {"price": 0}
        self.mock_product_db.check_product_availability.return_value = True
        result = self.store_manager.process_order("P123", 1, "card")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Prezzo non valido o nullo.")

    def test_process_order_payment_gateway_raises_exception(self):
        self.mock_product_db.get_product_details.return_value = {"price": 10}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_payment_gw.process_payment.side_effect = ConnectionError("Timeout")
        result = self.store_manager.process_order("P123", 1, "card")
        self.assertEqual(result["status"], "error")
        self.assertIn("Timeout", result["message"])

    def test_process_order_product_details_missing_price(self):
        self.mock_product_db.get_product_details.return_value = {"name": "Test Product"}  # No price
        self.mock_product_db.check_product_availability.return_value = True
        result = self.store_manager.process_order("P123", 1, "card")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Prezzo non valido o nullo.")

    def test_process_order_success_with_all_services(self):
        self.mock_product_db.get_product_details.return_value = {"price": 25.50}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_payment_gw.process_payment.return_value = {"status": "success", "transaction_id": "TXYZ"}

        result = self.store_manager.process_order("P123", 2, "valid_card", self.customer_info)

        self.assertEqual(result["status"], "success")
        # Verifica chiamate ai servizi esistenti
        self.mock_payment_gw.process_payment.assert_called_once_with(51.00, "valid_card")
        self.mock_inventory_sys.update_stock.assert_called_once_with("P123", -2)
        # Verifica chiamate ai nuovi servizi
        self.mock_shipping_service.schedule_shipment.assert_called_once_with("P123", 2, self.customer_info["address"])
        self.mock_notification_service.send_order_confirmation.assert_called_once_with(self.customer_info["email"],
                                                                                       "P123", 2)
        # Verifica che il log di successo sia stato chiamato
        self.mock_audit_logger.log_event.assert_called_with("ORDER_SUCCESS", {"transaction_id": "TXYZ"})

    def test_process_order_payment_fails_logs_error_and_does_not_ship(self):
        self.mock_product_db.get_product_details.return_value = {"price": 10}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_payment_gw.process_payment.return_value = {"status": "failed"}

        result = self.store_manager.process_order("P123", 1, "invalid_card", self.customer_info)

        self.assertEqual(result["status"], "error")
        # Assicura che i servizi post-pagamento non siano stati chiamati
        self.mock_inventory_sys.update_stock.assert_not_called()
        self.mock_shipping_service.schedule_shipment.assert_not_called()
        self.mock_notification_service.send_order_confirmation.assert_not_called()
        # Verifica che il fallimento sia stato loggato
        self.mock_audit_logger.log_event.assert_called_with("ORDER_FAILED", {"reason": "Payment failed"})

    def test_process_order_success_even_if_notification_fails(self):
        """Verifica che un ordine vada a buon fine anche se la notifica fallisce."""
        self.mock_product_db.get_product_details.return_value = {"price": 25.50}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_payment_gw.process_payment.return_value = {"status": "success", "transaction_id": "TXYZ"}
        # Simula un'eccezione dal servizio di notifica
        self.mock_notification_service.send_order_confirmation.side_effect = ConnectionError("SMTP server down")

        result = self.store_manager.process_order("P123", 2, "valid_card", self.customer_info)

        # L'ordine deve comunque risultare completato
        self.assertEqual(result["status"], "success")
        # Spedizione e stock devono essere aggiornati
        self.mock_shipping_service.schedule_shipment.assert_called_once()
        self.mock_inventory_sys.update_stock.assert_called_once()
        # Deve essere stato fatto un tentativo di inviare la notifica
        self.mock_notification_service.send_order_confirmation.assert_called_once()
        # Il fallimento della notifica e il successo dell'ordine devono essere loggati
        expected_log_calls = [
            call("ORDER_PROCESS_STARTED", {"product_id": "P123", "quantity": 2}),
            call("NOTIFICATION_FAILED", {"email": self.customer_info["email"], "error": "SMTP server down"}),
            call("ORDER_SUCCESS", {"transaction_id": "TXYZ"})
        ]
        self.mock_audit_logger.log_event.assert_has_calls(expected_log_calls, any_order=True)

    def test_process_order_not_found_logs_error(self):
        self.mock_product_db.get_product_details.return_value = None
        self.store_manager.process_order("P999", 1, "card", self.customer_info)
        self.mock_audit_logger.log_event.assert_called_with("ORDER_FAILED", {"reason": "Product not found"})

    def test_process_order_fails_if_fraud_is_detected(self):
        """Verifica che l'ordine venga bloccato se il servizio anti-frode lo segnala."""
        self.mock_product_db.get_product_details.return_value = {"price": 100}
        self.mock_fraud_detector.is_fraudulent.return_value = True  # Simula rilevamento frode

        result = self.store_manager.process_order("P123", 1, self.card_details, self.customer_info)

        self.assertEqual(result["status"], "error")
        self.assertIn("sospetta frode", result["message"])
        self.mock_fraud_detector.is_fraudulent.assert_called_once_with(self.customer_info, self.card_details)
        # Assicura che il processo si interrompa e non si proceda al pagamento
        self.mock_payment_gw.process_payment.assert_not_called()
        self.mock_audit_logger.log_event.assert_called_with("ORDER_FAILED", {"reason": "Fraud detected"})

    def test_process_order_includes_taxes_in_final_price(self):
        """Verifica che le tasse calcolate vengano aggiunte al prezzo finale pagato."""
        self.mock_product_db.get_product_details.return_value = {"price": 100}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_fraud_detector.is_fraudulent.return_value = False
        self.mock_tax_calculator.calculate_tax.return_value = 22.0  # Tassa fissa per il test
        self.mock_payment_gw.process_payment.return_value = {"status": "success", "transaction_id": "TXYZ"}

        self.store_manager.process_order("P123", 1, self.card_details, self.customer_info)

        # Il prezzo base è 100, la tassa è 22. Il pagamento deve essere di 122.
        self.mock_tax_calculator.calculate_tax.assert_called_once_with(100.0, self.customer_info["address"])
        self.mock_payment_gw.process_payment.assert_called_once_with(122.0, self.card_details)

    def test_process_order_awards_loyalty_points_on_success(self):
        """Verifica che i punti fedeltà vengano assegnati dopo un ordine andato a buon fine."""
        self.mock_product_db.get_product_details.return_value = {"price": 150}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_fraud_detector.is_fraudulent.return_value = False
        self.mock_tax_calculator.calculate_tax.return_value = 33.0
        self.mock_payment_gw.process_payment.return_value = {"status": "success", "transaction_id": "TXYZ"}

        self.store_manager.process_order("P123", 1, self.card_details, self.customer_info)

        # Il totale è 150 + 33 = 183. Vengono assegnati punti in base a questo totale.
        self.mock_loyalty_manager.award_points.assert_called_once_with("CUST001", 183.0)
        # Assicura che non vengano assegnati punti se il pagamento fallisce
        self.mock_loyalty_manager.reset_mock()
        self.mock_payment_gw.process_payment.return_value = {"status": "failed"}
        self.store_manager.process_order("P123", 1, self.card_details, self.customer_info)
        self.mock_loyalty_manager.award_points.assert_not_called()

    def test_process_order_tracks_sale_in_analytics_on_success(self):
        """Verifica che una vendita andata a buon fine sia tracciata dal servizio di analytics."""
        self.mock_product_db.get_product_details.return_value = {"price": 50}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_fraud_detector.is_fraudulent.return_value = False
        self.mock_tax_calculator.calculate_tax.return_value = 11.0
        self.mock_payment_gw.process_payment.return_value = {"status": "success", "transaction_id": "TXYZ"}

        self.store_manager.process_order("P456", 2, self.card_details, self.customer_info)

        # Prezzo totale: (50 * 2) + 11 = 111.0
        self.mock_analytics_tracker.track_sale.assert_called_once_with("P456", 2, 111.0)

    def test_process_order_handles_tax_service_exception(self):
        """Verifica che un'eccezione dal servizio tasse venga gestita correttamente."""
        self.mock_product_db.get_product_details.return_value = {"price": 100}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_fraud_detector.is_fraudulent.return_value = False
        self.mock_tax_calculator.calculate_tax.side_effect = ValueError("Servizio tasse non disponibile")

        result = self.store_manager.process_order("P123", 1, self.card_details, self.customer_info)

        self.assertEqual(result["status"], "error")
        self.assertIn("Impossibile calcolare le tasse", result["message"])
        self.mock_payment_gw.process_payment.assert_not_called()

    # --- Test per add_stock ---
    def test_add_stock_success(self):
        result = self.store_manager.add_stock("P456", 50)
        self.assertEqual(result["status"], "success")
        self.mock_inventory_sys.update_stock.assert_called_once_with("P456", 50)

    def test_add_stock_raises_error_for_zero_quantity(self):
        with self.assertRaisesRegex(ValueError, "La quantità deve essere un intero positivo."):
            self.store_manager.add_stock("P456", 0)

    def test_add_stock_raises_error_for_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.store_manager.add_stock("P456", -10)

    def test_add_stock_raises_error_for_float_quantity(self):
        with self.assertRaises(ValueError):
            self.store_manager.add_stock("P456", 10.5)

    def test_add_stock_success_logs_event(self):
        result = self.store_manager.add_stock("P456", 50)
        self.assertEqual(result["status"], "success")
        self.mock_inventory_sys.update_stock.assert_called_once_with("P456", 50)
        self.mock_audit_logger.log_event.assert_called_once_with("STOCK_ADDED", {"product_id": "P456", "quantity": 50})

    # --- Test per apply_discount ---
    def test_apply_discount_success(self):
        self.mock_product_db.get_product_details.return_value = {"price": 100.0}
        self.assertEqual(self.store_manager.apply_discount("P789", 20), 80.0)

    def test_apply_discount_with_rounding(self):
        self.mock_product_db.get_product_details.return_value = {"price": 99.99}
        self.assertEqual(self.store_manager.apply_discount("P789", 10), 89.99)

    def test_apply_discount_product_not_found(self):
        self.mock_product_db.get_product_details.return_value = None
        self.assertIsNone(self.store_manager.apply_discount("P999", 20))

    def test_apply_discount_product_missing_price(self):
        self.mock_product_db.get_product_details.return_value = {"name": "No Price Product"}
        self.assertIsNone(self.store_manager.apply_discount("P999", 20))

    def test_apply_discount_raises_error_for_zero_percentage(self):
        with self.assertRaises(ValueError):
            self.store_manager.apply_discount("P789", 0)

    def test_apply_discount_raises_error_for_negative_percentage(self):
        with self.assertRaises(ValueError):
            self.store_manager.apply_discount("P789", -10)

    def test_apply_discount_raises_error_for_over_100_percentage(self):
        with self.assertRaises(ValueError):
            self.store_manager.apply_discount("P789", 101)

    def test_apply_discount_at_100_percent(self):
        self.mock_product_db.get_product_details.return_value = {"price": 50}
        self.assertEqual(self.store_manager.apply_discount("P789", 100), 0.0)

    # --- Test per process_refund ---
    def test_process_refund_success(self):
        self.mock_product_db.get_product_details.return_value = {"price": 50}
        self.mock_payment_gw.process_refund.return_value = {"status": "success"}
        result = self.store_manager.process_refund("P123", 2, "TXYZ")
        self.assertEqual(result["status"], "success")
        self.mock_payment_gw.process_refund.assert_called_once_with(100, "TXYZ")
        self.mock_inventory_sys.update_stock.assert_called_once_with("P123", 2)

    def test_process_refund_product_not_found(self):
        self.mock_product_db.get_product_details.return_value = None
        result = self.store_manager.process_refund("P999", 1, "TXYZ")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Prodotto non trovato per il rimborso.")
        self.mock_payment_gw.process_refund.assert_not_called()

    def test_process_refund_gateway_fails(self):
        self.mock_product_db.get_product_details.return_value = {"price": 50}
        self.mock_payment_gw.process_refund.return_value = {"status": "failed"}
        result = self.store_manager.process_refund("P123", 1, "TXYZ")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Rimborso fallito.")
        self.mock_inventory_sys.update_stock.assert_not_called()

    def test_process_refund_with_zero_quantity(self):
        result = self.store_manager.process_refund("P123", 0, "TXYZ")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "La quantità da rimborsare deve essere positiva.")

    def test_process_refund_with_negative_quantity(self):
        result = self.store_manager.process_refund("P123", -1, "TXYZ")
        self.assertEqual(result["status"], "error")

    def test_process_refund_success_logs_event(self):
        self.mock_product_db.get_product_details.return_value = {"price": 50}
        self.mock_payment_gw.process_refund.return_value = {"status": "success"}
        self.store_manager.process_refund("P123", 2, "TXYZ")

        expected_log_calls = [
            call("REFUND_PROCESS_STARTED", {"transaction_id": "TXYZ"}),
            call("REFUND_SUCCESS", {"transaction_id": "TXYZ"})
        ]
        self.mock_audit_logger.log_event.assert_has_calls(expected_log_calls)

    def test_process_refund_gateway_fails_logs_error(self):
        self.mock_product_db.get_product_details.return_value = {"price": 50}
        self.mock_payment_gw.process_refund.return_value = {"status": "failed"}
        self.store_manager.process_refund("P123", 1, "TXYZ")

        self.mock_inventory_sys.update_stock.assert_not_called()
        self.mock_audit_logger.log_event.assert_called_with("REFUND_FAILED", {"reason": "Gateway refund failed"})

    # --- Test per get_price_with_promo_code ---
    def test_get_price_with_promo_code_success(self):
        self.mock_product_db.get_product_details.return_value = {"price": 200}
        self.mock_promo_validator.validate_code.return_value = {"is_valid": True, "discount_percentage": 15}
        result = self.store_manager.get_price_with_promo_code("P123", "WINTER15")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["new_price"], 170.0)
        self.mock_promo_validator.validate_code.assert_called_once_with("WINTER15")

    def test_get_price_with_promo_code_invalid_code(self):
        self.mock_product_db.get_product_details.return_value = {"price": 200}
        self.mock_promo_validator.validate_code.return_value = {"is_valid": False}
        result = self.store_manager.get_price_with_promo_code("P123", "INVALIDCODE")
        self.assertEqual(result["status"], "error")
        self.assertIn("non valido", result["message"])

    def test_get_price_with_promo_code_product_not_found(self):
        self.mock_product_db.get_product_details.return_value = None
        result = self.store_manager.get_price_with_promo_code("P999", "ANYCODE")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Prodotto non trovato.")
        self.mock_promo_validator.validate_code.assert_not_called()

    def test_get_price_with_promo_code_validator_returns_none(self):
        self.mock_product_db.get_product_details.return_value = {"price": 200}
        self.mock_promo_validator.validate_code.return_value = None
        result = self.store_manager.get_price_with_promo_code("P123", "ANYCODE")
        self.assertEqual(result["status"], "error")

    def test_get_price_with_promo_code_no_discount_in_payload(self):
        self.mock_product_db.get_product_details.return_value = {"price": 200}
        self.mock_promo_validator.validate_code.return_value = {"is_valid": True}  # No discount percentage
        result = self.store_manager.get_price_with_promo_code("P123", "FREESHIP")
        self.assertEqual(result["new_price"], 200.0)

    def test_process_order_inventory_update_fails(self):
        """Simula un fallimento durante l'aggiornamento dello stock DOPO il pagamento."""
        self.mock_product_db.get_product_details.return_value = {"price": 10}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_payment_gw.process_payment.return_value = {"status": "success", "transaction_id": "TXYZ"}
        self.mock_inventory_sys.update_stock.side_effect = IOError("Impossibile connettersi al sistema di inventario")
        # In uno scenario reale, questo richiederebbe una logica di rollback/compensazione.
        # Qui verifichiamo solo che l'eccezione venga sollevata se non gestita.
        with self.assertRaises(IOError):
            self.store_manager.process_order("P123", 1, "card")

    def test_process_refund_inventory_update_fails(self):
        """Simula un fallimento durante il ripristino dello stock DOPO il rimborso."""
        self.mock_product_db.get_product_details.return_value = {"price": 50}
        self.mock_payment_gw.process_refund.return_value = {"status": "success"}
        self.mock_inventory_sys.update_stock.side_effect = IOError("DB inventario non disponibile")
        with self.assertRaises(IOError):
            self.store_manager.process_refund("P123", 1, "TXYZ")

    def test_check_availability_db_raises_exception(self):
        self.mock_product_db.check_product_availability.side_effect = TimeoutError("DB connection timed out")
        with self.assertRaises(TimeoutError):
            self.store_manager.check_availability("P123", 1)

    def test_get_product_price_in_currency_converts_correctly(self):
        """Verifica la corretta conversione di valuta."""
        self.mock_product_db.get_product_details.return_value = {"price": 100.0}
        self.mock_currency_converter.get_rate.return_value = 1.08

        price_usd = self.store_manager.get_product_price_in_currency("P123", "USD")

        self.assertEqual(price_usd, 108.0)
        self.mock_currency_converter.get_rate.assert_called_once_with("EUR", "USD")

    def test_process_order_updates_crm_on_success(self):
        """Verifica che il CRM venga aggiornato dopo un ordine completato."""
        self._setup_successful_order_mocks()  # Metodo helper per ridurre la ripetizione
        self.store_manager.process_order("P123", 1, self.card_details, self.customer_info)

        self.mock_crm_system.update_customer_history.assert_called_once_with("CUST001", "TXYZ", 122.0)

    def test_process_order_adds_gift_wrap_cost(self):
        """Verifica che il costo della confezione regalo venga aggiunto al totale."""
        self._setup_successful_order_mocks()
        self.mock_gift_options.get_gift_wrap_price.return_value = 5.00

        self.store_manager.process_order("P123", 1, self.card_details, self.customer_info, gift_options={"wrap": True})

        # Prezzo 100 + Tasse 22 + Regalo 5 = 127
        self.mock_payment_gw.process_payment.assert_called_once_with(127.0, self.card_details)

    def test_process_digital_order_generates_download_link(self):
        """Verifica che un ordine digitale generi un link e non attivi la spedizione."""
        self.mock_product_db.get_product_details.return_value = {"price": 20.0, "is_digital": True}
        self.mock_payment_gw.process_payment.return_value = {"status": "success"}
        self.mock_digital_manager.generate_download_link.return_value = "http://fake.link"

        result = self.store_manager.process_digital_order("D200", self.card_details, self.customer_info)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["download_link"], "http://fake.link")
        self.mock_shipping_service.schedule_shipment.assert_not_called()

    def test_request_return_creates_rma_ticket(self):
        """Verifica che venga creato un ticket RMA per un prodotto restituibile."""
        self.mock_product_db.get_product_details.return_value = {"is_returnable": True}
        self.mock_rma_manager.create_rma_ticket.return_value = "RMA-1234"

        result = self.store_manager.request_return("P123", "TXYZ")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rma_ticket"], "RMA-1234")
        self.mock_rma_manager.create_rma_ticket.assert_called_once_with("P123", "TXYZ")

    def test_process_order_fails_if_compliance_check_fails(self):
        """Verifica che un ordine venga bloccato da un controllo di conformità negativo."""
        self.mock_product_db.get_product_details.return_value = {"price": 100}
        self.mock_compliance_checker.verify_shipment.return_value = False

        result = self.store_manager.process_order("P123", 1, self.card_details, self.customer_info)

        self.assertEqual(result["status"], "error")
        self.assertIn("non spedibile", result["message"])
        self.mock_payment_gw.process_payment.assert_not_called()

    def _setup_successful_order_mocks(self):
        """Metodo helper per non ripetere il setup di un ordine base."""
        self.mock_product_db.get_product_details.return_value = {"price": 100}
        self.mock_product_db.check_product_availability.return_value = True
        self.mock_fraud_detector.is_fraudulent.return_value = False
        self.mock_compliance_checker.verify_shipment.return_value = True
        self.mock_tax_calculator.calculate_tax.return_value = 22.0
        self.mock_payment_gw.process_payment.return_value = {"status": "success", "transaction_id": "TXYZ"}
        self.mock_gift_options.get_gift_wrap_price.return_value = 0.0  # Default a zero se non specificato

    def test_process_order_raises_exception_if_crm_update_fails_after_payment(self):
        """Verifica che un'eccezione venga sollevata se l'aggiornamento del CRM fallisce."""
        self._setup_successful_order_mocks()

        self.mock_crm_system.update_customer_history.side_effect = ConnectionError("CRM non raggiungibile")

        with self.assertRaises(ConnectionError):
            self.store_manager.process_order("P123", 1, self.card_details, self.customer_info)

        self.mock_payment_gw.process_payment.assert_called_once()
        self.mock_inventory_sys.update_stock.assert_called_once()
        self.mock_shipping_service.schedule_shipment.assert_called_once()

        self.mock_crm_system.update_customer_history.assert_called_once()

if __name__ == '__main__':
    unittest.main(verbosity=2)