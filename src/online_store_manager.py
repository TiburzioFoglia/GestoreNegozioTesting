from src.external_dependencies import (
    ProductDatabase, InventorySystem, PaymentGateway, PromoCodeValidator,
    NotificationService, ShippingService, AuditLogger,
    FraudDetectionService, TaxCalculatorService, LoyaltyProgramManager, AnalyticsTracker,
    CurrencyConverter, CRMSystem, GiftOptionsService,
    DigitalAssetManager, RMAManager, ComplianceChecker
)


class OnlineStoreManager:
    """
    Gestisce le operazioni di un negozio online, orchestrando le interazioni
    tra database prodotti, inventario, pagamenti e altri servizi.
    """

    def __init__(
            self,
            product_db: ProductDatabase, inventory_sys: InventorySystem, payment_gw: PaymentGateway,
            promo_validator: PromoCodeValidator, notification_service: NotificationService,
            shipping_service: ShippingService, audit_logger: AuditLogger,
            fraud_detector: FraudDetectionService, tax_calculator: TaxCalculatorService,
            loyalty_manager: LoyaltyProgramManager, analytics_tracker: AnalyticsTracker,
            currency_converter: CurrencyConverter, crm_system: CRMSystem,
            gift_options_service: GiftOptionsService, digital_asset_manager: DigitalAssetManager,
            rma_manager: RMAManager, compliance_checker: ComplianceChecker
    ):
        # Il controllo delle dipendenze diventa sempre più cruciale
        dependencies = [
            product_db, inventory_sys, payment_gw, promo_validator, notification_service,
            shipping_service, audit_logger, fraud_detector, tax_calculator,
            loyalty_manager, analytics_tracker, currency_converter, crm_system,
            gift_options_service, digital_asset_manager, rma_manager, compliance_checker
        ]
        if not all(dependencies):
            raise ValueError("Tutte le dipendenze devono essere fornite.")

        self.product_db = product_db
        self.inventory_sys = inventory_sys
        self.payment_gw = payment_gw
        self.promo_validator = promo_validator
        self.notification_service = notification_service
        self.shipping_service = shipping_service
        self.audit_logger = audit_logger
        self.fraud_detector = fraud_detector
        self.tax_calculator = tax_calculator
        self.loyalty_manager = loyalty_manager
        self.analytics_tracker = analytics_tracker
        self.currency_converter = currency_converter
        self.crm_system = crm_system
        self.gift_options_service = gift_options_service
        self.digital_asset_manager = digital_asset_manager
        self.rma_manager = rma_manager
        self.compliance_checker = compliance_checker

    def get_product_info(self, product_id):
        """Recupera e restituisce le informazioni di un prodotto."""
        if not product_id:
            return None
        return self.product_db.get_product_details(product_id)

    def check_availability(self, product_id, quantity):
        """Controlla se una certa quantità di un prodotto è disponibile."""
        if quantity <= 0:
            return False
        return self.product_db.check_product_availability(product_id, quantity)

    def process_order(self, product_id, quantity, card_details, customer_info, gift_options=None):
        """
        Elabora un ordine completo per un prodotto fisico, orchestrando tutti i servizi.

        Args:
            product_id (str): L'ID del prodotto da ordinare.
            quantity (int): Il numero di unità da ordinare.
            card_details (dict): I dettagli della carta di credito per il pagamento.
            customer_info (dict): Le informazioni sul cliente (ID, email, indirizzo).
            gift_options (dict, optional): Dettagli su eventuali opzioni regalo. Default a None.

        Returns:
            dict: Un dizionario con lo stato dell'ordine e un messaggio.
        """
        # Log iniziale per tracciabilità
        self.audit_logger.log_event("ORDER_PROCESS_STARTED", {"product_id": product_id, "quantity": quantity})

        # 1. Validazione input di base
        if not isinstance(quantity, int) or quantity <= 0:
            return {"status": "error", "message": "La quantità deve essere un intero positivo."}

        # 2. Recupero dettagli prodotto
        product_details = self.product_db.get_product_details(product_id)
        if not product_details:
            self.audit_logger.log_event("ORDER_FAILED", {"reason": "Product not found"})
            return {"status": "error", "message": "Prodotto non trovato."}

        # 3. Controllo anti-frode
        if self.fraud_detector.is_fraudulent(customer_info, card_details):
            self.audit_logger.log_event("ORDER_FAILED",
                                        {"reason": "Fraud detected", "customer_id": customer_info.get("id")})
            return {"status": "error", "message": "L'ordine è stato bloccato per sospetta frode."}

        # 4. Verifica conformità spedizione
        if not self.compliance_checker.verify_shipment(product_id, customer_info["address"]):
            self.audit_logger.log_event("ORDER_FAILED",
                                        {"reason": "Compliance check failed", "address": customer_info["address"]})
            return {"status": "error",
                    "message": "Prodotto non spedibile a questo indirizzo per restrizioni normative."}

        # 5. Controllo disponibilità inventario
        if not self.product_db.check_product_availability(product_id, quantity):
            self.audit_logger.log_event("ORDER_FAILED", {"reason": "Stock not available"})
            return {"status": "error", "message": "Quantità non disponibile."}

        # 6. Calcolo del prezzo base
        price_before_options = product_details.get("price", 0) * quantity
        if price_before_options <= 0:
            self.audit_logger.log_event("ORDER_FAILED", {"reason": "Invalid price"})
            return {"status": "error", "message": "Prezzo non valido o nullo."}

        # 7. Aggiunta costi opzioni regalo
        gift_cost = 0
        if gift_options:
            gift_cost = self.gift_options_service.get_gift_wrap_price(gift_options)

        price_with_gift = price_before_options + gift_cost

        # 8. Calcolo delle tasse
        try:
            tax = self.tax_calculator.calculate_tax(price_with_gift, customer_info["address"])
        except Exception as e:
            self.audit_logger.log_event("ORDER_FAILED", {"reason": "Tax calculation error", "error": str(e)})
            return {"status": "error", "message": f"Impossibile calcolare le tasse: {e}"}

        total_price = round(price_with_gift + tax, 2)

        # 9. Elaborazione del pagamento
        try:
            payment_result = self.payment_gw.process_payment(total_price, card_details)
        except Exception as e:
            self.audit_logger.log_event("ORDER_FAILED", {"reason": "Payment gateway exception", "error": str(e)})
            return {"status": "error", "message": f"Errore del gateway di pagamento: {e}"}

        # 10. Gestione del risultato del pagamento
        if payment_result and payment_result.get("status") == "success":
            transaction_id = payment_result.get("transaction_id")

            # --- Inizio delle operazioni post-pagamento ---

            # 10a. Aggiornamento inventario
            self.inventory_sys.update_stock(product_id, -quantity)

            # 10b. Pianificazione spedizione
            self.shipping_service.schedule_shipment(product_id, quantity, customer_info["address"])

            # 10c. Invio notifica al cliente
            self.notification_service.send_order_confirmation(customer_info["email"], transaction_id)

            # 10d. Aggiornamento cronologia cliente nel CRM
            self.crm_system.update_customer_history(customer_info["id"], transaction_id, total_price)

            # 10e. Assegnazione punti fedeltà
            self.loyalty_manager.award_points(customer_info["id"], total_price)

            # 10f. Tracciamento vendita per analytics
            self.analytics_tracker.track_sale(product_id, quantity, total_price)

            # 10g. Log di successo finale
            self.audit_logger.log_event("ORDER_SUCCESS", {"transaction_id": transaction_id, "amount": total_price})

            return {"status": "success", "message": "Ordine completato.", "transaction_id": transaction_id,
                    "total_paid": total_price}
        else:
            # Se il pagamento fallisce
            self.audit_logger.log_event("ORDER_FAILED",
                                        {"reason": "Payment failed", "gateway_message": payment_result.get("message")})
            return {"status": "error", "message": "Pagamento fallito."}



    def add_stock(self, product_id, quantity):
        """Aggiunge una quantità di un prodotto all'inventario."""
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("La quantità deve essere un intero positivo.")
        self.inventory_sys.update_stock(product_id, quantity)
        self.audit_logger.log_event("STOCK_ADDED", {"product_id": product_id, "quantity": quantity})
        return {"status": "success", "message": f"Aggiunti {quantity} pezzi per il prodotto {product_id}."}

    def apply_discount(self, product_id, discount_percentage):
        """Applica uno sconto al prezzo di un prodotto e restituisce il nuovo prezzo."""
        if not (0 < discount_percentage <= 100):
            raise ValueError("La percentuale di sconto deve essere tra 1 e 100.")

        product_details = self.product_db.get_product_details(product_id)
        if not product_details or "price" not in product_details:
            return None

        original_price = product_details["price"]
        new_price = original_price * (1 - discount_percentage / 100)
        return round(new_price, 2)

    def process_refund(self, product_id, quantity, transaction_id):
        """Gestisce il rimborso per un prodotto, ripristinando lo stock."""
        self.audit_logger.log_event("REFUND_PROCESS_STARTED", {"transaction_id": transaction_id})
        if quantity <= 0:
            return {"status": "error", "message": "La quantità da rimborsare deve essere positiva."}

        product_details = self.product_db.get_product_details(product_id)
        if not product_details:
            self.audit_logger.log_event("REFUND_FAILED", {"reason": "Product not found"})
            return {"status": "error", "message": "Prodotto non trovato per il rimborso."}

        refund_amount = product_details.get("price", 0) * quantity
        refund_result = self.payment_gw.process_refund(refund_amount, transaction_id)

        if refund_result and refund_result.get("status") == "success":
            self.inventory_sys.update_stock(product_id, quantity)
            self.audit_logger.log_event("REFUND_SUCCESS", {"transaction_id": transaction_id})
            return {"status": "success", "message": "Rimborso completato."}
        else:
            self.audit_logger.log_event("REFUND_FAILED", {"reason": "Gateway refund failed"})
            return {"status": "error", "message": "Rimborso fallito."}

    def get_price_with_promo_code(self, product_id, promo_code):
        """Calcola il prezzo di un prodotto applicando un codice promozionale valido."""
        product_details = self.product_db.get_product_details(product_id)
        if not product_details:
            return {"status": "error", "message": "Prodotto non trovato."}

        validation_result = self.promo_validator.validate_code(promo_code)
        if validation_result and validation_result.get("is_valid"):
            discount = validation_result.get("discount_percentage", 0)
            new_price = product_details["price"] * (1 - discount / 100)
            return {"status": "success", "new_price": round(new_price, 2)}
        else:
            return {"status": "error", "message": "Codice promozionale non valido o scaduto."}

    def get_product_price_in_currency(self, product_id, currency_code):
        """
        Converte il prezzo di un prodotto in una valuta specifica.
        """
        product_details = self.product_db.get_product_details(product_id)
        if not product_details:
            return None
        base_price = product_details["price"]

        if currency_code.upper() == "EUR":
            return base_price

        rate = self.currency_converter.get_rate("EUR", currency_code)
        if rate is None:
            return None

        return round(base_price * rate, 2)

    def process_digital_order(self, product_id, card_details, customer_info):
        """
        Gestisce l'acquisto di un prodotto digitale.
        """
        product_details = self.product_db.get_product_details(product_id)
        if not product_details or not product_details.get("is_digital"):
            return {"status": "error", "message": "Prodotto non digitale."}

        total_price = product_details["price"]  # Senza tasse o spedizione per semplicità
        payment_result = self.payment_gw.process_payment(total_price, card_details)

        if payment_result and payment_result.get("status") == "success":
            download_link = self.digital_asset_manager.generate_download_link(product_id, customer_info["id"])
            return {"status": "success", "download_link": download_link}
        else:
            return {"status": "error", "message": "Pagamento fallito."}

    def request_return(self, product_id, transaction_id):
        """
        Inizia una richiesta di reso (RMA) per un acquisto.
        """
        product_details = self.product_db.get_product_details(product_id)
        if not product_details:
            return {"status": "error", "message": "Prodotto non trovato."}

        if not product_details.get("is_returnable"):
            return {"status": "error", "message": "Questo prodotto non può essere restituito."}

        rma_ticket = self.rma_manager.create_rma_ticket(product_id, transaction_id)
        return {"status": "success", "rma_ticket": rma_ticket}