/**
 * Created by zhangxiaogui on 16/7/15.
 */
var InterValObj;
var count = 60;
var curCount;

var heightWindow = $(window).height();
var widthWindow = $(window).width();

$(".messageimg").css("height",heightWindow);
$(".messageimg").css("width",widthWindow);
function sendMessage(id) {
    var phoneNum = $(".phoneNum").val();
    var regexp = /^[0-9]{11}$/;
    if(!regexp.test(phoneNum)){
        var pwd = $(".Tips");
        pwd.text("请填写正确的手机号");
        GeneralTips(pwd);
        pwd.slideDown(300);
        setTimeout(function(){
            pwd.slideUp(300);
        },1500);
    }else{
        //向后台发送处理数据
        $.ajax({
            url:"https://dhui100.com/api/activity/redbag/msg",
            type: "post",
            data: "mobile="+phoneNum+"&type=ACT001&id="+id,
            dataType: "json",
            headers : { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
            success: function (res) {
                if (res.response.success == 1){
                    console.log(res);
                }else{
                    alert(res.response.return_code);
                }
            }
        });
        $(".validate").hide();
        curCount = count;
        $(".count").show().text(curCount);
        InterValObj = window.setInterval(SetRemainTime, 1000);
    }
}

//timer处理函数
function SetRemainTime() {
    if (curCount == 0) {
        window.clearInterval(InterValObj);//停止计时器
        $(".validate").show();
        $(".count").text("60").hide();
    }
    else {
        curCount--;
        $(".count").text(curCount);
    }
}
function GeneralTips(GeneralTips){
    var screenHeight = $(window).height();
    var screenWidth = $(window).width();
    var height = parseInt(GeneralTips.css("height").split("px")[0])+50;
    var width = parseInt(GeneralTips.css("width").split("px")[0])+16;

    var endTop = (screenHeight-height)/2;
    var endLeft = (screenWidth-width)/2;

    GeneralTips.css("top",endTop);
    GeneralTips.css("left",endLeft);
}

function blurInputphone(){
    $(".messageimg").css("top","0");
}
function blurInputcode(){
     $(".messageimg").css("top","0");


}
function focusInputphone(){
    $(".messageimg").css("height",heightWindow);
}
function focusInputcode(){
    $(".messageimg").css("height",heightWindow);
}
