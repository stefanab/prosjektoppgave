<?php

function sanitize($data, $conn) {
    return mysqli_real_escape_string($conn, $data);
}

function mysqli_result($res,$row=0,$col=0){
    $numrows = mysqli_num_rows($res);
    if ($numrows && $row <= ($numrows-1) && $row >=0){
        mysqli_data_seek($res,$row);
        $resrow = (is_numeric($col)) ? mysqli_fetch_row($res) : mysqli_fetch_assoc($res);
        if (isset($resrow[$col])){
            return $resrow[$col];
        }
    }
    return false;
}

function mac_exists($mac, $conn) {
    $username = sanitize($mac, $conn);
    $query = mysqli_query($conn, "SELECT COUNT(`mac`) FROM `mac_ip` WHERE `mac` = '$mac'");
    return (mysqli_result($query, 0) == 1) ? true : false;
}

function update_ip_of_mac($mac, $ip, $conn){
    $query = "UPDATE `mac_ip` SET `ip` = '$ip', `update_time` = DEFAULT WHERE `mac` = '$mac'";
    mysqli_query($conn, $query);
}

function insert_mac_ip($mac, $ip, $conn){
    $query = "INSERT INTO `mac_ip` (`mac`, `ip`) VALUES ('$mac', '$ip')";
    mysqli_query($conn, $query);
}

function ip_from_mac($mac, $conn) {
    $mac = sanitize($mac, $conn);
    $query = mysqli_query($conn, "SELECT `ip` FROM `mac_ip` WHERE `mac` = '$mac'");
    return mysqli_result($query, 0, 'ip');
}

function get_all($conn) {
     return mysqli_query($conn, "SELECT `ip`, `mac`, `update_time` FROM `mac_ip` ORDER By `update_time` DESC");
}

?>