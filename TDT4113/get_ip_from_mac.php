<?php
include 'core/init.php';

if (empty($_POST) == false && isset($_POST['mac'])) {
    $mac = $_POST['mac'];
    $ip = ip_from_mac($mac, $conn);
}
else if (empty($_POST) == false && isset($_POST['all'])) {
    $all = get_all($conn);
}

?>


<html>
<head lang="en">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP from MAC</title>

</head>
<body>
    <form action="get_ip_from_mac.php" method="post">
        <div class="form-group">
            <label for="mac">MAC address: </label>
            <input class="form-control" type="text" id="mac" name="mac" placeholder="mac">
        </div>
        <button type="submit" style="margin-top: 10px">Get your IP address</button>
    </form>
    <form action="get_ip_from_mac.php" method="post">
        <input type="hidden" class="form-control" type="text" id="all" name="all" value="true">
        <button type="submit">Get all IP addresses</button>
    </form>

    <?php
        if (isset($ip)) {
            echo "IP address: ", $ip;
        }
        else if (isset($all)) {
            while ($row = mysqli_fetch_array($all, MYSQLI_ASSOC)) {
                echo $row['mac']. "   -   " . $row['ip'] . "   -   " . $row['update_time'] . "</br>";
            }
        }
    ?>
</body>
</html>
