# Questo file contiene le classi che rappresentano i servizi esterni.
# Nella nostra suite di test, non useremo queste implementazioni,
# ma le sostituiremo con dei mock.

class ProductDatabase:
    """Simula l'interazione con un database di prodotti."""
    def get_product_details(self, product_id):
        print(f"DATABASE: Reperimento dettagli per {product_id}")
        pass

    def check_product_availability(self, product_id, quantity):
        print(f"DATABASE: Controllo disponibilità di {quantity} pezzi per {product_id}")
        pass

    def update_product_price(self, product_id, new_price):
        print(f"DATABASE: Aggiornamento prezzo per {product_id} a {new_price}")
        pass


class InventorySystem:
    """Simula l'interazione con un sistema di gestione dell'inventario."""
    def update_stock(self, product_id, quantity_change):
        print(f"INVENTORY: Aggiornamento stock per {product_id} di {quantity_change}")
        pass


class PaymentGateway:
    """Simula l'interazione con un gateway di pagamento."""
    def process_payment(self, amount, card_details):
        print(f"PAYMENT: Processo pagamento di {amount} EUR")
        pass

    def process_refund(self, amount, transaction_id):
        print(f"PAYMENT: Processo rimborso di {amount} EUR per la transazione {transaction_id}")
        pass


class PromoCodeValidator:
    """Simula la validazione di codici promozionali."""
    def validate_code(self, promo_code):
        print(f"PROMO: Validazione del codice {promo_code}")
        pass

class NotificationService:
    """Simula l'invio di notifiche ai clienti (es. email, SMS)."""
    def send_order_confirmation(self, customer_email, product_id, quantity):
        print(f"NOTIFICATION: Invio conferma a {customer_email} per ordine di {quantity}x {product_id}")
        pass


class ShippingService:
    """Simula l'interazione con un sistema di logistica e spedizioni."""
    def schedule_shipment(self, product_id, quantity, address):
        print(f"SHIPPING: Pianificazione spedizione di {quantity}x {product_id} a {address}")
        pass


class AuditLogger:
    """Simula un servizio di logging per audit e tracciabilità."""
    def log_event(self, event_type, details: dict):
        print(f"AUDIT LOG: Evento '{event_type}' - Dettagli: {details}")
        pass

class FraudDetectionService:
    """Simula un servizio di analisi anti-frode."""
    def is_fraudulent(self, customer_info, card_details):
        print("FRAUD: Analisi dell'ordine...")
        return False # Default a non fraudolento

class TaxCalculatorService:
    """Simula un servizio esterno per il calcolo delle tasse."""
    def calculate_tax(self, amount, address):
        print(f"TAX: Calcolo tasse per {amount} EUR all'indirizzo {address}")
        return amount * 0.22 # Simula una tassa fissa del 22%

class LoyaltyProgramManager:
    """Simula la gestione di un programma fedeltà."""
    def award_points(self, customer_id, purchase_amount):
        points = int(purchase_amount) # 1 punto per ogni euro speso
        print(f"LOYALTY: Assegnati {points} punti al cliente {customer_id}")
        pass

class AnalyticsTracker:
    """Simula un servizio di analytics per il tracciamento delle vendite."""
    def track_sale(self, product_id, quantity, amount):
        print(f"ANALYTICS: Tracciata vendita per prodotto {product_id} - Importo: {amount}")
        pass

class CurrencyConverter:
    """Simula un servizio di conversione valuta."""
    def get_rate(self, from_currency, to_currency):
        print(f"CURRENCY: Richiesta tasso di cambio da {from_currency} a {to_currency}")
        # Logica di esempio
        if from_currency == "EUR" and to_currency == "USD":
            return 1.08
        return None

class CRMSystem:
    """Simula l'interazione con un sistema di Customer Relationship Management."""
    def update_customer_history(self, customer_id, transaction_id, amount):
        print(f"CRM: Aggiornamento cronologia cliente {customer_id} con transazione {transaction_id}")
        pass

class GiftOptionsService:
    """Simula un servizio per calcolare i costi delle opzioni regalo."""
    def get_gift_wrap_price(self, option_details):
        print(f"GIFT: Calcolo costo per opzioni: {option_details}")
        return 5.00 # Costo fisso per confezione regalo

class DigitalAssetManager:
    """Simula la gestione di asset digitali e link per il download."""
    def generate_download_link(self, product_id, customer_id):
        print(f"DIGITAL: Generazione link per prodotto {product_id} per cliente {customer_id}")
        return f"https://my.store/download/{product_id}/{uuid.uuid4()}"

class RMAManager:
    """Simula un sistema di gestione delle autorizzazioni al reso (RMA)."""
    def create_rma_ticket(self, product_id, transaction_id):
        ticket_id = f"RMA-{random.randint(1000, 9999)}"
        print(f"RMA: Creato ticket {ticket_id} per la transazione {transaction_id}")
        return ticket_id

class ComplianceChecker:
    """Simula un servizio che controlla la conformità normativa per le spedizioni."""
    def verify_shipment(self, product_id, address):
        print(f"COMPLIANCE: Verifica spedizione di {product_id} a {address}")
        return True # Default a conforme