function changeLike(id) {
    var elem = document.getElementById("likeButton_svg");
    var heart_type = elem.getAttribute("href");
    var like_count = document.getElementById("likeCount");
    if (heart_type == "#heart") {
        elem.setAttribute("href", "#heart-fill");
        like_count.innerHTML = parseInt(like_count.innerHTML, 10) + 1;
        fetch('/api/videos/' + id + '/like');
    } else {
        elem.setAttribute("href", "#heart");
        like_count.innerHTML = parseInt(like_count.innerHTML, 10) - 1;
        fetch('/api/videos/' + id + '/unlike');
    }
}

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

function commentVideo(id) {
    var text = document.getElementById("commentInput").value.trim();
    if (text) {
        fetch("/api/comment", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({video_id: id, text: text})
        })
        location.reload();
    }

}