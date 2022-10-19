from flask import Flask, send_file, request, Response
from prometheus_client import start_http_server, Counter, generate_latest, Gauge ,Enum ,Info
import logging
import pingparsing
 
logger = logging.getLogger(__name__)
 
app = Flask(__name__)
 
CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')
g = Gauge('rtt_node01', 'Latency')


def rtt_ue_app_link(ue_ip="12.2.1.2"):
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination = ue_ip
    transmitter.count = 5
    result = transmitter.ping()
    result = ping_parser.parse(result).as_dict()
    g.set(result["rtt_avg"]) 
    
      
@app.route('/metrics', methods=['GET'])
def get_data():
    """Returns all data as plaintext."""
    rtt_ue_app_link()
    return Response(generate_latest(g), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port= 9888)

