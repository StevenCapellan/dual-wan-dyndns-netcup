# Dual WAN DynDNS Netcup script
A simple python script to update the DNS settings at netcup to make two wan connections available from the public internet. 
Ready to deploy via docker compose on any server.

**Why would you want it?**  
You want to connect to your home network via VPN or make a server accessible from the outside. But you also happen to have two WAN connections, e.g. Cable and DSL and want to make use of the increased availability of these two connections.  
Additionally, you don't want to use any publicly available DynDS service .

**Requirements**
- A public Domain registered at [Netcup](https://www.netcup.de/)
- A local firewall e.g. [OPNsense](https://opnsense.org/)
- An always-online device/server to host the script

**Usage**
1. Clone git repository

        git clone https://github.com/StevenCapellan/dual-wan-dyndns-netcup
2. Rename ".env.example" to ".env"

        mv .env.example .env
3. Replace the placeholders with your own data

| Placeholder           | Description                |
| :-------------------- | :------------------------- |
| `domain_name`         | Your Domain Name |
| `customer_number`     | Your customer number at netcup |
| `api_key`             | Your API key at netcup (see [Netcup Wiki](https://www.netcup-wiki.de/wiki/CCP_API) for details) |
| `client_request_id`   | A client request id. Can be set individually. Only for tracking of multiple requests |
| `api_password`        | Your API password. (see [Netcup Wiki](https://www.netcup-wiki.de/wiki/CCP_API) for details)  |
| `public_ip_url`       | A link to a site where you can retrieve your public IP (e.g. "ipinfo.io/ip") |
| `subdomain_one`       | The subdomain for your first WAN connection |
| `subdomain_two`       | The subdomain for your seconds WAN connection |

4. Run the docker container

        docker-compose -d

5. Configure your firewall to route requests with the local port range 55000-55019 through the first WAN and the range 55020-55039 through the second WAN
