import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

HOTMART_URL = os.environ.get("HOTMART_URL", "https://developers.hotmart.com/payments/api/v1/subscriptions")
TOKEN_URL = os.environ.get("TOKEN_URL", "https://api-sec-vlc.hotmart.com/security/oauth/token")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
BASIC_TOKEN = os.environ.get("BASIC_TOKEN")

class HotmartAPI:
    def __init__(self):
        self.access_token = None
        self.token_expiry = 0

    def get_access_token(self):
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token

        # Parâmetros como query string
        params = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {BASIC_TOKEN}"
        }
        try:
            response = requests.post(TOKEN_URL, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expiry = time.time() + token_data.get("expires_in", 3600) - 60
            return self.access_token
        except requests.RequestException as e:
            print(f"Erro ao obter access token: {e}")
            return None

    def _encode_basic_auth(self):
        import base64
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        return base64.b64encode(auth_str.encode()).decode()

    def get_active_subscriptions(self, accession_date: int = 1546308000000):
        token = self.get_access_token()
        if not token:
            print("Não foi possível obter o access token.")
            return None

        params = {
            "status": "ACTIVE",
            "accession_date": accession_date
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        try:
            response = requests.get(HOTMART_URL, headers=headers, params=params, timeout=15)
            if response.status_code == 401:
                # Token expirado ou inválido, tentar renovar e refazer a chamada
                print("Token expirado ou inválido. Renovando token e tentando novamente...")
                self.access_token = None  # Forçar renovação
                token = self.get_access_token()
                if not token:
                    print("Não foi possível renovar o access token.")
                    return None
                headers['Authorization'] = f'Bearer {token}'
                response = requests.get(HOTMART_URL, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            self.parse_subscriptions_summary(data)
            return data
        except requests.RequestException as e:
            print(f"Erro ao consultar Hotmart: {e}")
            return None

    def parse_subscriptions_summary(self, data):
        if not data or "items" not in data:
            return "Nenhum dado encontrado."

        items = data["items"]
        page_info = data.get("page_info", {})
        total_results = page_info.get("total_results", 0)

        summary = f"**Resumo de Assinaturas Atrasadas**\n"
        summary += f"**Total de assinaturas:** {total_results}\n\n"

        if total_results == 0:
            return summary + "Nenhuma assinatura atrasada encontrada."

        plans_summary = {}
        total_value = 0

        for item in items:
            subscriber = item.get("subscriber", {})
            plan = item.get("plan", {})
            price = item.get("price", {})

            name = subscriber.get("name", "N/A")
            email = subscriber.get("email", "N/A")
            plan_name = plan.get("name", "N/A")
            value = price.get("value", 0)
            currency = price.get("currency_code", "BRL")

            total_value += value

            if plan_name not in plans_summary:
                plans_summary[plan_name] = {
                    "count": 0,
                    "value": value,
                    "subscribers": []
                }

            plans_summary[plan_name]["count"] += 1
            plans_summary[plan_name]["subscribers"].append({
                "name": name,
                "email": email
            })

        summary += "**Por Planos:**\n"
        for plan_name, info in plans_summary.items():
            plan_total = info["value"] * info["count"]
            summary += f"• {plan_name}: {info['count']} assinantes (R$ {info['value']:.2f} cada = R$ {plan_total:.2f})\n"

        summary += f"\n**Valor total em atraso:** R$ {total_value:.2f}\n"

        summary += "\n**Todos os assinantes em atraso:**\n"
        for item in items:
            subscriber = item.get("subscriber", {})
            plan = item.get("plan", {})
            name = subscriber.get("name", "N/A")
            email = subscriber.get("email", "N/A")
            plan_name = plan.get("name", "N/A")
            summary += f"• {name} ({email}) - {plan_name}\n"

        return summary

    def get_delayed_subscriptions(self, accession_date: int = 1546308000000):
        token = self.get_access_token()
        if not token:
            print("Não foi possível obter o access token.")
            return None

        params = {
            "status": "DELAYED",
            "accession_date": accession_date
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        try:
            response = requests.get(HOTMART_URL, headers=headers, params=params, timeout=15)
            if response.status_code == 401:
                # Token expirado ou inválido, tentar renovar e refazer a chamada
                print("Token expirado ou inválido. Renovando token e tentando novamente...")
                self.access_token = None  # Forçar renovação
                token = self.get_access_token()
                if not token:
                    print("Não foi possível renovar o access token.")
                    return None
                headers['Authorization'] = f'Bearer {token}'
                response = requests.get(HOTMART_URL, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            summary = self.parse_subscriptions_summary(data)
            print(summary)
            return summary
        except requests.RequestException as e:
            print(f"Erro ao consultar Hotmart: {e}")
            return None

    def get_active_and_delayed_summary(self, accession_date: int = 1546308000000):
        """Busca assinaturas ACTIVE e DELAYED da Hotmart e retorna resumo consolidado"""
        token = self.get_access_token()
        if not token:
            return {"error": "Não foi possível obter o access token."}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        def make_request(status):
            params = {"status": status, "accession_date": accession_date}
            try:
                response = requests.get(HOTMART_URL, headers=headers, params=params, timeout=15)
                if response.status_code == 401:
                    # Token expirado, renovar
                    self.access_token = None
                    new_token = self.get_access_token()
                    if not new_token:
                        return None
                    headers['Authorization'] = f'Bearer {new_token}'
                    response = requests.get(HOTMART_URL, headers=headers, params=params, timeout=15)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                print(f"Erro ao consultar Hotmart ({status}): {e}")
                return None

        # Buscar assinaturas ativas e atrasadas
        active_data = make_request("ACTIVE")
        delayed_data = make_request("DELAYED")

        if not active_data and not delayed_data:
            return {"error": "Erro ao consultar dados da Hotmart"}

        # Processar dados
        active_items = active_data.get("items", []) if active_data else []
        delayed_items = delayed_data.get("items", []) if delayed_data else []
        
        active_total = active_data.get("page_info", {}).get("total_results", 0) if active_data else 0
        delayed_total = delayed_data.get("page_info", {}).get("total_results", 0) if delayed_data else 0

        return {
            "active": {"items": active_items, "total": active_total},
            "delayed": {"items": delayed_items, "total": delayed_total}
        }

if __name__ == "__main__":
    api = HotmartAPI()
    # api.get_active_subscriptions()
    api.get_delayed_subscriptions()
