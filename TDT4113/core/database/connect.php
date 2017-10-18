<?php
    include("dbconfig.php");
    $conn = mysqli_connect($host, $user, $pswd);
    mysqli_select_db($conn, $db);
?>