import json
from django.shortcuts import render
import requests
import socket
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import os
from groq import Groq
# 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
client = Groq(api_key='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')
       

def lookup_view(request):
    context = {"data": None, "error": None}
    
    if request.method == "POST":
        ip_or_url = request.POST.get("ip_or_url", "").strip()
        api_url = f"http://ip-api.com/json/{ip_or_url}"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                context["data"] = {
                    "ip": data.get("query"),
                    "nation": data.get("country"),
                    "nation_code": data.get("countryCode"),
                    "region_code": data.get("region"),
                    "region_name": data.get("regionName"),
                    "city": data.get("city"),
                    "timezone": data.get("timezone"),
                    "isp": data.get("isp"),
                    "org": data.get("org"),
                    "as": data.get("as"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "zip": data.get("zip"),
                    "google_maps": f"https://www.google.com/maps/place/{data.get('lat')},{data.get('lon')}",
                }
            else:
                context["error"] = f"Unable to fetch details for {ip_or_url} (Reason: {data.get('message')})"
        
        except requests.exceptions.RequestException as e:
            context["error"] = f"Error: {e}"
    
    return render(request, "lookup.html", context)

def dashboard_view(request):
    return render(request, "dashboard/index.html")


def lookup(request):
    context = {"data": None, "error": None}
    
    if request.method == "POST":
        ip_or_url = request.POST.get("ip_or_url", "").strip()
        api_url = f"http://ip-api.com/json/{ip_or_url}"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                context["data"] = {
                    "ip": data.get("query"),
                    "nation": data.get("country"),
                    "nation_code": data.get("countryCode"),
                    "region_code": data.get("region"),
                    "region_name": data.get("regionName"),
                    "city": data.get("city"),
                    "timezone": data.get("timezone"),
                    "isp": data.get("isp"),
                    "org": data.get("org"),
                    "as": data.get("as"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "zip": data.get("zip"),
                    "google_maps": f"https://www.google.com/maps/place/{data.get('lat')},{data.get('lon')}",
                }
            else:
                context["error"] = f"Unable to fetch details for {ip_or_url} (Reason: {data.get('message')})"
        
        except requests.exceptions.RequestException as e:
            context["error"] = f"Error: {e}"
    
    return render(request, "dashboard/lookup.html", context)

@csrf_exempt 
def ports(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hostname = data.get('hostname')
            if not hostname:
                return JsonResponse({"status": "error", "message": "Hostname is required."})

            scan_option = data.get('scan_option')
            port_range = data.get('port_range')
            selected_ports = data.get('selected_ports')

            # Try to resolve the server IP from the hostname
            server_ip = socket.gethostbyname(hostname)
            open_ports = []

            # Determine which ports to scan
            if scan_option == 'all':
                ports_to_scan = range(1, 65536)
            elif scan_option == 'range' and port_range:
                start, end = map(int, port_range.split('-'))
                ports_to_scan = range(start, end + 1)
            elif scan_option == 'selected' and selected_ports:
                ports_to_scan = map(int, selected_ports.split(','))

            # Scan the ports
            for port in ports_to_scan:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((server_ip, port))
                    if result == 0:
                        open_ports.append(port)

            return JsonResponse({"status": "success", "open_ports": open_ports})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return render(request, 'dashboard/ports.html')

JSON_FILE_PATH = 'data.json'
@require_POST
@csrf_exempt 
def store_data(request):
    try:
        # Parse the incoming JSON data from the request body
        data = json.loads(request.body)
        # print(data)
        data=data['open_ports']
        print("sender data filtered",data)
        # Check if the JSON file exists, if not, create it with an empty list
        if not os.path.exists(JSON_FILE_PATH):
            with open(JSON_FILE_PATH, 'w') as f:
                json.dump([], f)

        # Overwrite the data in the file with the new data
        with open(JSON_FILE_PATH, 'w') as f:
            json.dump(data, f)
        with open('data.json', 'r') as f:
            ports = json.load(f)
        return JsonResponse({"message": "http://127.0.0.1:8000/view-data","sd":ports}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


def view_data(request):
    try:
     
       
        with open('data.json', 'r') as f:
            ports = json.load(f)
        with open('details.json', 'r') as f:
            details = json.load(f)
        port_data = {}

        for port in ports:
            str_port = str(port)
            if str_port in details:
                port_data[str_port] = details[str_port]
            else:
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                     messages=[
                        {
                            "role": "system",
                            "content": f"\nports:{port}"+"\ngive me the one lines of these for the above port in the below variable json\nvulnarability:\"\",\ndisadvantage\"\",\nsolution:\"\",\nusage:\"\""
                        }
                    ],
                    temperature=0.88,
                    max_tokens=1024,
                    top_p=1,
                    stream=False,
                    response_format={"type": "json_object"},
                    stop=None,
                )
                
                # Parse the response and map the values
                # response_data = completion.choices[0].message.content

                # print(response_data['vulnerability'])
                # print(response_data['disadvantage'])
                # print(response_data['solution'])
                # print(response_data['usage'])
                # # response_data))
                # print("\n\n")
                port_data[str_port] = {
                    "vulnerability": "Not specified",
                    "disadvantage": "Not specified",
                    "solution": "Not specified",
                    "usage": "Not specified"
                }
        return render(request, 'dashboard/view_data.html', {'data': port_data})

    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)