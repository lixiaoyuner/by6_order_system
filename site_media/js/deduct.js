$(document).ready(function(){
    
    $('#deduct-submit').click(function(event){
        event.preventDefault()
        if($('#datetimepicker-start').val() == ''){
            Swal.fire('输入时间不能为空');
            return
        }else if($('#datetimepicker-end').val() == ''){
            Swal.fire('输入时间不能为空');
            return
        }else{
            Swal.fire({
                title: 'Are you sure?',
                text: '您确认手动修改吗？',
                type: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: '充值'
              }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: '/order/pay/deduct/',
                        type: "POST",
                        data: {
                            "user_id": $('#user-select').val(),
                            "start_time": $('#datetimepicker-start').val(),
                            "end_time": $('#datetimepicker-end').val(),
                            "remark": $('#deduct-remark').val(),
                            "csrfmiddlewaretoken": $('[name="csrfmiddlewaretoken"]').val(),
                        },
                        datatype: "json",
                        success: function (data) {
                            if(data.ok){
                                Swal.fire(
                                    data.msg,
                                ).then((result) => {
                                    window.location.href = '/stats/';
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

    $(function () {
        $('#datetimepicker-start').datetimepicker({
            language: 'zh-CN',
        });
    });

    $(function () {
        $('#datetimepicker-end').datetimepicker({
            language: 'zh-CN',
        });
    });

    
});