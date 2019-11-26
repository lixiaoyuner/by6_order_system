$(document).ready(function(){

    $('#help').click(function(event){
        event.preventDefault();
        queryHelp();
    })

    function queryHelp() {
        $.ajax({
            url : "/doc/help/",
            async : true,
            type : "get",
            // data : {
            //     "type" : "query",
            //     "id" : id
            // },
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
        $("#content").html(data.content);
        // 显示模态框
        $('#helpModal').modal('show');
    }
})