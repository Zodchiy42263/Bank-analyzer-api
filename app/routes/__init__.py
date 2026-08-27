from app.routes.users import users_bp
from app.routes.banks import banks_bp
from app.routes.debit_cards import debit_card_bp
from app.routes.deposits import deposits_bp
from app.routes.saving_accounts import saving_accounts_bp
from app.routes.minimum_balance_accounts import minimum_balance_accounts_bp
from app.routes.credit_cards import credit_cards_bp
from app.routes.loans import loans_bp
from app.routes.overviews import overview_bp
from app.routes.transactions import transactions_bp

BLUEPRINTS = (
    users_bp,
    banks_bp,
    debit_card_bp,
    deposits_bp,
    saving_accounts_bp,
    minimum_balance_accounts_bp,
    credit_cards_bp,
    loans_bp,
    overview_bp,
    transactions_bp,
)
