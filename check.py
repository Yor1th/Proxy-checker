import requests
import re
import pyfiglet
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.auth import HTTPProxyAuth

# Инициализация colorama
init(autoreset=True)

def print_banner():
    """Выводит ASCII-арт заголовок."""
    ascii_art = pyfiglet.figlet_format("PROXY Checker Fast")
    by_text = "By https://t.me/sukhanovhennadii"
    print(f"\n{Fore.YELLOW}{ascii_art}{by_text.center(80)}\n")

def load_proxies(file_path):
    """Загружает прокси из файла."""
    with open(file_path, encoding="utf-8") as f:
        return f.read().splitlines()

def parse_proxy(proxy):
    """Парсит прокси в нужный формат."""
    match = re.match(r'(?:(?P<protocol>https?|socks4|socks5)://)?(?:(?P<user>[^:@]+):(?P<pass>[^:@]+)@)?(?P<host>[^:@]+):(?P<port>\d+)', proxy)
    
    if match:
        protocol = match.group('protocol') or 'http'
        user = match.group('user')
        password = match.group('pass')
        host = match.group('host')
        port = match.group('port')
        
        formatted_proxy = f"{protocol}://{user}:{password}@{host}:{port}" if user and password else f"{protocol}://{host}:{port}"
        proxy_without_protocol = f"{user}:{password}@{host}:{port}" if user and password else f"{host}:{port}"
        auth = (user, password) if user and password else None
        
        return formatted_proxy, proxy_without_protocol, auth
    return None, None, None

def check_proxy(proxy, auth, session, test_url):
    """Проверяет прокси на работоспособность."""
    proxies = {"http": proxy, "https": proxy}
    
    try:
        response = session.get(test_url, proxies=proxies, auth=HTTPProxyAuth(*auth) if auth else None, timeout=3)
        if response.status_code == 200:
            print(f"{Fore.GREEN}[+] {proxy} работает")
            return proxy, True
    except requests.RequestException:
        pass
    
    print(f"{Fore.RED}[-] {proxy} не работает")
    return proxy, False

def save_proxies(file_path, proxies):
    """Сохраняет список прокси в файл."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(proxies))

def main():
    print_banner()
    input(f"{Fore.CYAN}Нажмите Enter, чтобы запустить проверку прокси...")

    # Параметры
    proxy_file = "proxies.txt"
    test_url = "http://httpbin.org/ip"
    output_files = {
        "with_protocol": "working_proxies_with_protocol.txt",
        "without_protocol": "working_proxies_without_protocol.txt",
    }

    proxies_list = load_proxies(proxy_file)
    
    working_proxies_with_protocol = []
    working_proxies_without_protocol = []

    session = requests.Session()
    
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = []
        for proxy in proxies_list:
            parsed_proxy, proxy_without_protocol, auth = parse_proxy(proxy)
            if parsed_proxy:
                futures.append(executor.submit(check_proxy, parsed_proxy, auth, session, test_url))

        for future in as_completed(futures):
            proxy, is_working = future.result()
            if is_working:
                working_proxies_with_protocol.append(proxy)
                working_proxies_without_protocol.append(proxy.split('://')[-1])

    save_proxies(output_files["with_protocol"], working_proxies_with_protocol)
    save_proxies(output_files["without_protocol"], working_proxies_without_protocol)

    print(f"\n{Fore.YELLOW}Готово! Найдено {len(working_proxies_with_protocol)} рабочих прокси.")

if __name__ == "__main__":
    main()
