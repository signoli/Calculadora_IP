from flask import Flask, render_template, request
import ipaddress

class CalculadoraRed:
    def __init__(self, ip, mascara):
        self.ip = ip
        self.mascara = mascara
        self.red = self._crear_red()

    def _crear_red(self):
        try:
            return ipaddress.IPv4Network(f"{self.ip}/{self.mascara}", strict=False)
        except ValueError:
            return None
                        
    def es_ip_privada(self):
    	try:
        	return ipaddress.ip_address(self.ip).is_private
    	except ValueError:
        	return False

    def calcular_datos(self):
        if not self.red:
            return None

        return {
            "address": self.ip,
            "netmask": str(self.red.netmask),
            "wildcard": str(ipaddress.IPv4Address(int(self.red.hostmask))),
            "network": str(self.red.network_address),
            "broadcast": str(self.red.broadcast_address),
            "host_min": str(list(self.red.hosts())[0]) if self.red.num_addresses > 2 else "N/A",
            "host_max": str(list(self.red.hosts())[-1]) if self.red.num_addresses > 2 else "N/A",
            "hosts_count": self.red.num_addresses - 2 if self.red.num_addresses > 2 else 0,
            "class": self.calcular_clase(),
            "es_privada": "Privada" if self.es_ip_privada() else "Pública",
        }

    def calcular_clase(self):
        octeto = int(self.ip.split('.')[0])
        if 0 <= octeto <= 127:
            return 'A'
        elif 128 <= octeto <= 191:
            return 'B'
        elif 192 <= octeto <= 223:
            return 'C'
        elif 224 <= octeto <= 239:
            return 'D (Multicast)'
        elif 240 <= octeto <= 255:
            return 'E (Reservada)'
        else:
            return 'Desconocida'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    ip = request.form.get('ip')
    mascara = request.form.get('mascara')
    try:
        mascara = int(mascara)
        calculadora = CalculadoraRed(ip, mascara)
        resultado = calculadora.calcular_datos()
        if resultado:
            return render_template('index.html', resultado=resultado)
        else:
            return render_template('index.html', error="Dirección IP o máscara no válida.")
    except (ValueError, TypeError):
        return render_template('index.html', error="Entrada no válida. Asegúrate de ingresar una IP y una máscara correctas.")

if __name__ == '__main__':
    app.run(debug=True, port=8000)
