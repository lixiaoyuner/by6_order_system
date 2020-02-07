$(document).ready(function(){
    
    $('#charge-submit').click(function(event){
        event.preventDefault()
        if($('#input-money').val() == ''){
            Swal.fire('输入金额不能为空');
            return
        }else if($('#input-contract').val() == ''){
            Swal.fire('合同编号不能为空');
            return
        }else if($('#input-project').val() == ''){
            Swal.fire('输入项目名称不能为空');
            return
        }else if($('#input-负责人').val() == ''){
            Swal.fire('输入负责人不能为空');
            return
        }else{
            Swal.fire({
                title: 'Are you sure?',
                text: "您将充值" + $('#input-money').val() + '元到账户' + $('#user-select option:selected').html(),
                type: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: '充值'
              }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: '/order/charge/',
                        type: "POST",
                        data: {
                            "user_id": $('#user-select').val(),
                            "type_id": $('#type-select').val(),
                            "money": $('#input-money').val(),
                            "contract": $('#input-contract').val(),
                            "project": $('#input-project').val(),
                            "header": $('#input-header').val(),
                            "remark": $('#charge-remark').val(),
                            "csrfmiddlewaretoken": $('[name="csrfmiddlewaretoken"]').val(),
                        },
                        datatype: "json",
                        success: function (data) {
                            if(data.ok){
                                Swal.fire(
                                    data.msg,
                                ).then((result) => {
                                    window.location.href = '/order/charge/record/';
                                })
                            }else{
                                Swal.fire(
                                    data.msg,
                                )
                            } 
                        },
                        error: function () {
                            swal({
                                    type: 'error',
                                    title: '服务出错',
                                    text: '当前服务不可用',
                                })
                            return false;
                        },
                        headers: {'X-Requested-With': 'XMLHttpRequest'},
                    })
                }
            })
        }
    })

    $('.show-appointment').click(function(event){
        event.preventDefault();
        var id = this.id
        queryHelp(id);
    })

    function queryHelp(id) {
        $.ajax({
            url : "/order/charge/myrecord/",
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
        $("#appointment-content").html(data.data);
        // 显示模态框
        $('#appointmentModal').modal('show');
    }

    $('#charge-table').on('page-change.bs.table', function (e,number, size) {
        $('.show-appointment').click(function(event){
            event.preventDefault();
            var id = this.id
            queryHelp(id);
        })
    });
});