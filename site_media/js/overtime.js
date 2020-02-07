$(document).ready(function(){
    
    $('#overtime-submit').click(function(event){
        event.preventDefault()
        if($('#datetimepicker-overtime').val() == ''){
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
                confirmButtonText: '设置'
              }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: '/order/set_overtime/',
                        type: "POST",
                        data: {
                            "overtime_value": $('#overtime-select').val(),
                            "date": $('#datetimepicker-overtime').val(),
                            "csrfmiddlewaretoken": $('[name="csrfmiddlewaretoken"]').val(),
                        },
                        datatype: "json",
                        success: function (data) {
                            if(data.ok){
                                Swal.fire(
                                    data.msg,
                                )
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
        $('#datetimepicker-overtime').datetimepicker({
            language: 'zh-CN',
            format: 'yyyy-mm-dd',
            minView: "month",
            autoclose: true,
        });
    });

    
});