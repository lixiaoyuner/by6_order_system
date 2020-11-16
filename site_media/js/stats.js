$(document).ready(function(){

    $('.show-pay').click(function(event){
        event.preventDefault();
        var id = this.getAttribute('value')
        queryHelp(id);
    })

    function queryHelp(id) {
        $.ajax({
            url : "/myapt/",
            async : true,
            type : "post",
            data : {
                "id" : id
            },
            // 成功后开启模态框
            success : showQuery,
            error : function() {
                alert("请求失败");
            },
            dataType : "json"
        });
    }
    
    // 查询成功后向模态框插入数据并开启模态框。data是返回的JSON对象
    function showQuery(data) {
        $("#pay-content").html(data.data);
        // 显示模态框
        $('#payModal').modal('show');
    }

    $('input[name="start_time"]').datetimepicker({
        language: 'zh-CN',
        format: 'yyyy-mm-dd',
        minView: "month", 
        autoclose: true,
    });
    $('input[name="end_time"]').datetimepicker({
        language: 'zh-CN',
        format: 'yyyy-mm-dd',
        minView: "month",
        autoclose: true,
    });

    $('#export').click(function(){
        event.preventDefault();
        location.href='/export/?start_time=' + $('#start_time').val() + '&end_time=' + $('#end_time').val() + '&user_id=' + $('#user_select').val();
    })
})