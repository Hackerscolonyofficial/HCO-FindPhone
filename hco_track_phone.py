    # Install requirements
    if not install_requirements():
        print(f"{RED}Failed to install requirements. Exiting.{RESET}")
        sys.exit(1)
    
    # Clear screen after YouTube redirect
    os.system(CLEAR)
    print(f"{GREEN}Starting HCO Track Phone tool...{RESET}")
    print(f"{YELLOW}Using port: {SERVER_PORT}{RESET}")
    
    # Start Flask server
    print(f"{YELLOW}Starting server...{RESET}")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    server_start_time = time.time()
    server_ready = False
    while time.time() - server_start_time < 30:
        if check_server_running():
            server_ready = True
            break
        time.sleep(1)
    
    if not server_ready:
        print(f"{RED}Server failed to start. Trying different port...{RESET}")
        # Try to force kill anything on the port
        try:
            subprocess.run(["fuser", "-k", f"{SERVER_PORT}/tcp"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        time.sleep(2)
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        time.sleep(5)
    
    print(f"{GREEN}Server started successfully on port {SERVER_PORT}!{RESET}")
    
    # Start ngrok tunnel
    print(f"{YELLOW}Creating internet tunnel...{RESET}")
    if start_ngrok(SERVER_PORT):
        print(f"{GREEN}Internet access enabled!{RESET}")
    else:
        print(f"{RED}Failed to create internet tunnel. Using local network only.{RESET}")
        LOCAL_IP = socket.gethostbyname(socket.gethostname())
        TRACKING_URL = f"http://{LOCAL_IP}:{SERVER_PORT}"
        print(f"{YELLOW}Local URL: {TRACKING_URL}{RESET}")
        print(f"{YELLOW}Note: Both devices must be on same WiFi network{RESET}")
    
    # Generate QR code
    print(f"{YELLOW}Generating QR code...{RESET}")
    generate_qr_code()
    time.sleep(2)
    
    # Display banner with the link
    display_banner()
    
    # Live location printing in Termux
    last_location_time = 0
    connection_wait_time = time.time()
    display_refresh_time = time.time()
    
    while True:
        # Refresh display every 15 seconds to prevent clutter
        current_time = time.time()
        if current_time - display_refresh_time > 15:
            os.system(CLEAR)
            display_banner()
            display_refresh_time = current_time
            
        if locations and 'last_update' in locations:
            current_time = time.time()
            # Only update if we have a new location
            if locations['last_update'] > last_location_time:
                last_location_time = locations['last_update']
                time_str = time.strftime('%H:%M:%S', time.localtime(locations['last_update']))
                print(f"{GREEN}📍 LIVE LOCATION {time_str}{RESET}")
                print(f"{GREEN}Latitude: {locations.get('lat')}{RESET}")
                print(f"{GREEN}Longitude: {locations.get('lon')}{RESET}")
                print(f"{GREEN}Accuracy: {locations.get('accuracy', 'N/A')}m{RESET}")
                
                # Show Google Maps link
                lat = locations.get('lat')
                lon = locations.get('lon')
                if lat and lon:
                    maps_url = f"https://maps.google.com/?q={lat},{lon}"
                    print(f"{GREEN}Google Maps: {maps_url}{RESET}")
                
                print(f"{BLUE}{'-'*40}{RESET}")
        else:
            # Show waiting message with elapsed time
            elapsed = int(current_time - connection_wait_time)
            print(f"{YELLOW}Waiting for target phone to connect ({elapsed}s)...{RESET}")
            print(f"{YELLOW}Scan the QR code or open: {CYAN}{TRACKING_URL}{RESET}")
            print(f"{YELLOW}On target phone, click 'SHARE LOCATION' button{RESET}")
            print(f"{BLUE}{'-'*40}{RESET}")
        
        time.sleep(3)
        
except KeyboardInterrupt:
    print(f"\n{RED}Shutting down...{RESET}")
    print(f"{GREEN}Thank you for using HCO Track Phone!{RESET}")
    
    # Kill ngrok process if running
    if ngrok_process:
        ngrok_process.terminate()
        
except Exception as e:
    print(f"{RED}Error: {e}{RESET}")
    print(f"{YELLOW}Please make sure you have installed all requirements:{RESET}")
    print(f"{CYAN}pkg install python curl -y{RESET}")
    print(f"{CYAN}pip install flask requests qrcode[pil] pyngrok{RESET}")
