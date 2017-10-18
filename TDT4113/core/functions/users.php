<?php

function user_exists($username, $conn) {
    $username = sanitize($username, $conn);
    $query = mysqli_query($conn, "SELECT COUNT(`user_id`) FROM `standard_users` WHERE `username` = '$username'");
    return (mysqli_result($query, 0) == 1) ? true : false;
}

function login($username, $password, $conn) {
    $user_id = user_id_from_username($username, $conn);
    $salt = salt_from_username($username, $conn);
    $username = sanitize($username, $conn);
    //$password = md5($password);
    $password = hash_pbkdf2("sha256", $password, $salt, 1000, 32);

    $query = mysqli_query($conn, "SELECT COUNT(`user_id`) FROM `standard_users` WHERE `username` = '$username' AND `password` = '$password'");
    return (mysqli_result($query, 0) == 1) ? $user_id : false;
}


function user_id_from_username($username, $conn) {
    $username = sanitize($username, $conn);
    $query = mysqli_query($conn, "SELECT `user_id` FROM `standard_users` WHERE `username` = '$username'");
    return mysqli_result($query, 0, 'user_id');
}

function salt_from_username($username, $conn) {
    $username = sanitize($username, $conn);
    $query = mysqli_query($conn, "SELECT `salt` FROM `standard_users` WHERE `username` = '$username'");
    return mysqli_result($query, 0, 'salt');
}

function get_all_users($conn) {
    $query = mysqli_query($conn, "SELECT `username` FROM `standard_users`");
    return $query;
}

function user_data($conn, $user_id) {
    $data = array();
    $user_id = (int)$user_id;

    $func_num_args = func_num_args();
    $func_get_args = func_get_args();
    if ($func_num_args > 0){
        unset($func_get_args[0]);

        $fields = '`' . implode('`, `', $func_get_args) . '`';
        $query = "SELECT $fields FROM `standard_users` WHERE `user_id` = $user_id";
        $data = mysqli_fetch_assoc(mysqli_query($conn, $query));
        return $data;
    }
}

function register_user($register_data, $conn, $salt) {
    array_walk($register_data, 'array_sanitize');
//  $register_data['password'] = md5($register_data['password']);

    $register_data['password'] = hash_pbkdf2("sha256", $register_data['password'], $salt, 1000, 32);

    $fields = '`' . implode('`, `', array_keys($register_data)) . '`';
    $data = '\'' . implode('\', \'', $register_data) . '\'';

    $query = "INSERT INTO `standard_users` ($fields) VALUES ($data)";
    mysqli_query($conn, $query);
}

function logged_in() {
    return (isset($_SESSION['user_id'])) ? true : false;
}


?>