function changeSubscribe(id) {
    var elem = document.getElementById("subscribeButton");
    var sub_count = document.getElementById("subCount");
    if (elem.innerHTML == "Отписаться") {
        elem.innerHTML = "Подписаться";
        sub_count.innerHTML = parseInt(sub_count.innerHTML, 10) - 1;
        fetch('/api/users/' + id + '/unfollow');
    } else {
        elem.innerHTML = "Отписаться";
        sub_count.innerHTML = parseInt(sub_count.innerHTML, 10) + 1;
        fetch('/api/users/' + id + '/follow');
    }
}
