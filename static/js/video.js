function changeLike() {
    var elem = document.getElementById("likeButton_svg");
    var heart_type = elem.getAttribute("href");
    var like_count = document.getElementById("likeCount");
    if (heart_type == "#heart") {
        elem.setAttribute("href", "#heart-fill");
        like_count.innerHTML = parseInt(like_count.innerHTML, 10) + 1;
    } else {
        elem.setAttribute("href", "#heart");
        like_count.innerHTML = parseInt(like_count.innerHTML, 10) - 1;
    }
}

function changeSubscribe() {
    var elem = document.getElementById("subscribeButton");
    var sub_count = document.getElementById("subCount");
    if (elem.innerHTML == "Отписаться") {
        elem.innerHTML = "Подписаться";
        sub_count.innerHTML = parseInt(sub_count.innerHTML, 10) - 1;
    } else {
        elem.innerHTML = "Отписаться";
        sub_count.innerHTML = parseInt(sub_count.innerHTML, 10) + 1;
    }
}
