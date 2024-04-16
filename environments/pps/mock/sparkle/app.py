from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys

MODE = sys.argv[1]


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    '''
    This is a simple HTTP server to mock responses for Sparkle connector.
    It takes 0, 1, 2 as parameter and returns data accordingly.
    '''

    def do_GET(self):
        # Set response status code
        self.send_response(200)
        # Set headers
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Process the data as needed
        # For demonstration, simply echo the received data in the response
        if MODE == '0':
            response = []
        elif MODE == '1':
            response = [{
                "iscorporate": "0",
                "firstname": "myhyppas ypzveas Vessav",
                "investmentspecialist": "Unknown",
                "intermediaryno": "106D67-27",
                "internalidentifier": "mock",
                "idnumber": "123456",
                "cellphonenumber": "12312312",
                "brokerageno": "Unknown",
                "registrationcode": "106D71-51",
                "title": "",
                "userid": "12893",
                "clientnumber": "Unknown",
                "memberno": "",
                "idtype": "RSAIDNumber",
                "newbieinvestor": "Unknown",
                "surname": "adsawd",
                "dob": "3/29/2017 10:45:03 AM",
                "regionalmanager": "Unknown",
                "roletype": "Intermediary",
                "email": "ppsinvestmentsbpm@pps.co.za",
                "ismultimapped": True,
                "dfmmanager": "Unknown"
            }]
        elif MODE == '2':
            response = [
                    {
                        "iscorporate": "0",
                        "firstname": "myhyppas ypzveas Vessav",
                        "investmentspecialist": "Unknown",
                        "intermediaryno": "106D67-27",
                        "internalidentifier": "mock",
                        "idnumber": "6003075059087",
                        "cellphonenumber": "12312312",
                        "brokerageno": "Unknown",
                        "registrationcode": "106D71-51",
                        "title": "",
                        "userid": "12893",
                        "clientnumber": "Unknown",
                        "memberno": "",
                        "idtype": "RSAIDNumber",
                        "newbieinvestor": "Unknown",
                        "surname": "adsawd",
                        "dob": "3/29/2017 10:45:03 AM",
                        "regionalmanager": "Unknown",
                        "roletype": "Intermediary",
                        "email": "ppsinvestmentsbpm@pps.co.za",
                        "ismultimapped": True,
                        "dfmmanager": "Unknown"
                    },
                    {
                        "iscorporate": "0",
                        "firstname": "myhyppas ypzveas Vessav",
                        "investmentspecialist": "Unknown",
                        "intermediaryno": "106D67-27VM",
                        "internalidentifier": "mock",
                        "idnumber": "123456",
                        "cellphonenumber": "12312312",
                        "brokerageno": "Unknown",
                        "registrationcode": "106D71-51",
                        "title": "",
                        "userid": "12893",
                        "clientnumber": "Unknown",
                        "memberno": "",
                        "idtype": "RSAIDNumber",
                        "newbieinvestor": "Unknown",
                        "surname": "werwerw",
                        "dob": "3/29/2017 10:45:03 AM",
                        "regionalmanager": "Unknown",
                        "roletype": "Intermediary",
                        "email": "ppsinvestmentsbpm@pps.co.za",
                        "ismultimapped": True,
                        "dfmmanager": "Unknown"
                    }
            ]

        # Send the JSON response
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == '__main__':
    # Specify the server address and port
    server_address = ('', 8700)

    # Create an HTTP server with the custom request handler
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

    print('Server running on port 8700...')

    # Start the server
    httpd.serve_forever()