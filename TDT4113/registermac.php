<?php

include 'core/init.php';

$mac_eth = $_POST['mac_eth'];
$mac_wlan0 = $_POST['mac_wlan0'];
$ip_eth = $_POST['ip_eth'];
$ip_wlan0 = $_POST['ip_wlan0'];

if (empty($_POST) === false) {
    if (empty($mac_eth) == false && empty($ip_eth) == false) {
        if (mac_exists($mac_eth, $conn)) {
            update_ip_of_mac($mac_eth, $ip_eth, $conn);
        }
        else {
            insert_mac_ip($mac_eth, $ip_eth, $conn);
        }
        echo "eth\n";
        echo "mac: " , $mac_eth, "\n";
        echo "ip: " , $ip_eth, "\n";
    }
    else{
        echo "eth not connected\n";
    }
    if (empty($mac_wlan0) == false && empty($ip_wlan0) == false) {
        if (mac_exists($mac_wlan0, $conn)) {
            update_ip_of_mac($mac_wlan0, $ip_wlan0, $conn);
        }
        else {
            insert_mac_ip($mac_wlan0, $ip_wlan0, $conn);
        }
        echo "wlan0\n";
        echo "mac: " , $mac_wlan0, "\n";
        echo "ip: " , $ip_wlan0;
    }
    else{
        echo "wlan0 not connected";
    }
}

?>