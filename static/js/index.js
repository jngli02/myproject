$(document).ready(function() {
    // 当鼠标悬停在用户名上时，显示下拉菜单
    $('.user-info').hover(function() {
        $('#dropdown-menu').show();
    }, function() {
        $('#dropdown-menu').hide();
    });
});

