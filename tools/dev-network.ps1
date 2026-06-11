# dev-network.ps1
param([switch]$Stop)

$wslIp = "192.168.53.76"
$port = 8501

if ($Stop) {
    netsh interface portproxy delete v4tov4 listenport=$port listenaddress=192.168.1.154 connectport=$port connectaddress=$wslIp
    Remove-NetFirewallRule -DisplayName "Streamlit WSL" -ErrorAction SilentlyContinue
    usbipd detach --wsl --busid 2-9
    Write-Host "Rules removed."
} else {
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=192.168.1.154 connectport=$port connectaddress=$wslIp
    New-NetFirewallRule -DisplayName "Streamlit WSL" -Direction Inbound -Action Allow -Protocol TCP -LocalPort $port | Out-Null
    Write-Host "Port forwarding and firewall rules added."
    usbipd attach --wsl --busid 2-9
    Write-Host "zigbee device attached to WSL."
}