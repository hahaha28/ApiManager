const projectId = UrlParam.paramValues("id")[0]

$(function () {
    const url = "/find/project?id=" + projectId

    var updatePermissionMemberAccount

    // 发送请求获取项目基本信息
    httpGET(url, function (data) {
        const projectName = data["name"];
        const leaderName = data["creatorName"];
        const leaderAccount = data["creatorAccount"];
        $("#project-name").text(projectName)
        $("#leaderName").text(leaderName)
        $("#leaderAccount").text(leaderAccount)
        for (let i = 0; i < data["members"].length; ++i) {
            const memberData = data["members"][i];
            const userName = memberData["userName"];
            const userAccount = memberData["userAccount"];
            let permission;
            if (memberData["permission"] === 0) {
                permission = "只读权限"
            } else {
                permission = "读写权限"
            }
            const html = getMemberHtml(userName, userAccount, permission);
            $("#members").append(html)

            // 点击修改权限
            $("#" + userAccount + "edit").click(function () {
                console.log(userAccount + "edit")
                updatePermissionMemberAccount = userAccount
                $("#updatePermissionModal").modal('show')
            })
            // 点击删除成员
            $("#" + userAccount + "delete").click(function () {
                deleteMember(projectId,userAccount)
            })
        }
    })

    // 添加项目成员
    $("#newProjectMember").click(function () {
        const account = $("#memberAccount").val()
        const permission = parseInt($("#permissionSelect").val())

        var data = {
            "projectId": projectId,
            "account": account,
            "permission": permission
        }
        httpPost("/new/project/member", data,
            function (responseData) {
                console.log(responseData)
                location.reload()
            },
            function (code, responseData) {
                console.log(responseData)
                $('#newMemberModal').modal('hide')
                alert(responseData['msg'])
            })
    })

    // 删除项目成员
    function deleteMember(projectId,account) {
        const data = {
            "projectId": projectId,
            "account": account
        }
        httpPost("/delete/project/member",data,
            function () {
                $("#"+account+"member").hide()
            }),
            function (code,responseData) {
                alert(responseData['msg'])
            }
    }

    // 点击修改权限的确定按钮
    $("#updatePermission").click(function () {
        const permission = parseInt($("#updatePermissionSelect").val())
        updateMemberPermission(projectId,updatePermissionMemberAccount,permission)
    })

    // 修改成员权限
    function updateMemberPermission(projectId,account,permission) {
        let data = {
            "projectId": projectId,
            "account": account,
            "permission": permission
        }
        httpPost('/update/member/permission',data,
            function () {
                let text;
                if(permission === 0){
                    text = "只读权限"
                }else{
                    text = "读写权限"
                }
                $("#"+updatePermissionMemberAccount+"permission").text(text)
                $("#updatePermissionModal").modal('hide')
            },function (code,responseData) {
                alert(code+","+responseData['msg'])
            })
    }

});

function getMemberHtml(name, account, permission) {
    var html = '<div class="member-container" id="'+account+'member">\n' +
        '                <div>\n' +
        '                    <div class="name">' + name + '</div>\n' +
        '                    <div class="account">' + account + '</div>\n' +
        '                </div>\n' +
        '                <div style="display: flex">\n' +
        '                    <div>\n' +
        '                    <span class="badge badge-pill badge-primary" id="'+account+'permission">\n' +
        '                        ' + permission + '\n' +
        '                    </span>\n' +
        '                    </div>\n' +
        '                    <div type="button" class="svg-btn" id="' + account + 'edit">\n' +
        '                        <svg height="16" width="16" class="octicon octicon-pencil" viewBox="0 0 16 16" version="1.1"\n' +
        '                             aria-hidden="true">\n' +
        '                            <path fill-rule="evenodd"\n' +
        '                                  d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L10.811 3.75l1.439 1.44 1.263-1.263a.25.25 0 000-.354l-1.086-1.086zM11.189 6.25L9.75 4.81l-6.286 6.287a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.249.249 0 00.108-.064l6.286-6.286z"></path>\n' +
        '                        </svg>\n' +
        '                    </div>\n' +
        '                    <div type="button" class="svg-btn" id="' + account + 'delete">\n' +
        '                        <svg class="octicon octicon-trashcan" viewBox="0 0 16 16" version="1.1" width="16" height="16"\n' +
        '                             aria-hidden="true">\n' +
        '                            <path fill-rule="evenodd"\n' +
        '                                  d="M6.5 1.75a.25.25 0 01.25-.25h2.5a.25.25 0 01.25.25V3h-3V1.75zm4.5 0V3h2.25a.75.75 0 010 1.5H2.75a.75.75 0 010-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75zM4.496 6.675a.75.75 0 10-1.492.15l.66 6.6A1.75 1.75 0 005.405 15h5.19c.9 0 1.652-.681 1.741-1.576l.66-6.6a.75.75 0 00-1.492-.149l-.66 6.6a.25.25 0 01-.249.225h-5.19a.25.25 0 01-.249-.225l-.66-6.6z"></path>\n' +
        '                        </svg>\n' +
        '                    </div>\n' +
        '                </div>\n' +
        '            </div>'
    return html
}