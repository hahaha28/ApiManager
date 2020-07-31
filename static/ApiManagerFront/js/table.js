/**
 * 在第index行下添加一行
 * @param index 行数，从0开始
 * @param leftBodyId 左侧伸缩表格的body的id
 * @param tbodyId 右侧正常表格的tbody的id
 */
function addOneLine(index,leftBodyId,tbodyId) {
    var leftCell; // 被添加的左侧单元格
    // 首先把这之后的行数先+1
    addOneIndex(index);
    // 如果index = -1 直接在根添加
    if(index === -1){
        // 添加左侧的伸缩表格
        leftCell = createCell(index+1,0)
        $("#"+leftBodyId).prepend(leftCell);
        // 添加右侧的正常表格
        $("#"+tbodyId).prepend(createRightTableLine(index+1));
    }else{
        // 如果index != 0 则查找元素，再之后添加
        const condition = "line='"+index+"'"
        // 添加左侧的伸缩表格
        var el = $(".out-border["+condition+"]");
        const level = parseInt(el.attr('level'));
        leftCell = createCell(index+1,level)
        el.after(leftCell);
        // 添加右侧的正常表格
        el = $(".flex-tr["+condition+"]");
        el.after(createRightTableLine(index+1))
    }
    // 绑定点击事件
    bindInputListener(leftCell.find('input'));
}

/**
 * 在第index行下添加一子行
 * @param index 行数，从0开始
 */
function addSubLine(index) {
    // 首先把这之后的行数先+1
    addOneIndex(index);
    // 添加子行
    const condition = "line='"+index+"'"
    var el = $(".out-border["+condition+"]")
    const level = parseInt(el.attr('level'))
    const leftCell = createCell(index+1,level+1)
    el.after(leftCell)
    // 右侧添加正常表格
    el = $(".flex-tr["+condition+"]");
    el.after(createRightTableLine(index+1))

    // 绑定点击事件
    bindInputListener(leftCell.find('input'));
}

/**
 * 把第index行之后的行数都加一
 * @param index 从0开始
 */
function addOneIndex(index) {
    // 先处理左侧的伸缩表格
    var els = $(".out-border");
    for(let i=0;i<els.length;++i){
        let el = els.eq(i);
        let elIndex = parseInt(el.attr('line'));
        if(elIndex > index){
            el.attr('line',elIndex+1);
        }
    }
    // 再处理右侧的正常表格
    els = $(".flex-tr");
    for(let i=0;i<els.length;++i){
        let el = els.eq(i);
        let elIndex = parseInt(el.attr('line'));
        if(elIndex > index){
            el.attr('line',elIndex+1);
        }
    }
}

/**
 * 删除某行，同时会删除他的子行
 * @param index
 */
function deleteLine(index) {
    // 找到自己
    var chooseLine = $(".out-border[line='"+index+"']");
    const level = parseInt(chooseLine.attr('level'));

    var els = $(".out-border");
    var maxIndex = index; // 被删除的最大的索引
    // 记录要删除自己和所以子行的索引
    var deleteIndex = [index]
    for(let i=index+1;i<els.length;++i){
        console.log('i='+i)
        let el = els.eq(i);
        let elIndex = parseInt(el.attr('line'));
        let elLevel = parseInt(el.attr('level'))

        if(elLevel <= level){
            break;
        }
        console.log(elIndex)
        deleteIndex[deleteIndex.length] = elIndex;
        maxIndex = elIndex
    }
    // 先把后续的行数修改
    const diffIndex = maxIndex-index+1; // 应该扣掉的索引
    for(let i = maxIndex+1;i<els.length;++i){
        let el = els.eq(i);
        el.attr('line',i-diffIndex)
    }
    // 修改右侧正常表格的行数
    var normalTableEls = $(".flex-tr");
    for(let i = maxIndex+1;i<els.length;++i){
        let el = normalTableEls.eq(i);
        el.attr('line',i-diffIndex);
    }

    // 再删除自己和子行
    for(let i =deleteIndex.length-1;i>=0;i=i-1){
        console.log('remove '+deleteIndex[i])
        els.eq(deleteIndex[i]).remove();
        // 删除右侧正常表格
        normalTableEls.eq(deleteIndex[i]).remove();
    }

}

/**
 * 构造单元格
 * @param level 单元格的级数，0为正常
 * @param index 单元格的行数，从0开始
 */
function createCell(index,level){
    const outBorder = $("<div></div>")
        .attr('line',index)
        .attr('level',level)
        .addClass('out-border');
    const inputContainer = $("<div></div>").addClass('input-container');
    const input = $("<input >")
        .attr('type','text')
        .addClass('form-control')
        .addClass('left-input');
    inputContainer.append(input);

    if(level === 0){
        outBorder.append(inputContainer);
    }else{
        var div = $("<div></div>").addClass('line-container').append(inputContainer);
        var temp
        for(;level>1;level=level-1){
            temp = $("<div></div>").addClass('line-container');
            temp.append(div);
            div = temp;
        }
        outBorder.append(div);
    }
    return outBorder
}

/**
 * 构造右侧正常表格的一行
 * @param index
 */
function createRightTableLine(index){
    const tr = $("<tr class='flex-tr'></tr>").attr('line',index);

    const td1 = $("<td></td>");
    const input1 = $("<input>").attr('type','text').addClass('form-control');
    td1.append(input1);

    const td2 = $("<td></td>");
    const input2 = $("<input>").attr('type','text').addClass('form-control');
    td2.append(input2);

    const td3 = $("<td></td>");
    const a1 = $("<a></a>")
        .attr('href','javascript::;')
        .attr('onclick','onclickAddSubLine(this)')
        .attr('line',index)
        .text('添加子字段');
    const span = $("<span style=\"color: #dee2e6\">&nbsp;|&nbsp;</span>");
    const a2 = $("<a></a>")
        .attr('href','javascript::;')
        .attr('line',index)
        .attr('onclick','onclickDeleteLine(this)')
        .text('删除');
    td3.append(a1);
    td3.append(span);
    td3.append(a2);

    tr.append(td1);
    tr.append(td2);
    tr.append(td3);
    return tr
}

/**
 * 添加子字段的点击事件
 * @param a
 */
function onclickAddSubLine(a){
    const aEle = $(a)
    var line = aEle.parent().parent().attr('line')
    line = parseInt(line)
    addSubLine(line)
}

/**
 * 删除的点击事件
 * @param a
 */
function onclickDeleteLine(a){
    const aEle = $(a)
    var line = aEle.parent().parent().attr('line')
    line = parseInt(line)
    console.log('line='+line)
    deleteLine(line)
}

/**
 * 给input绑定监听
 * @param element
 */
function bindInputListener(element){
    // 左侧伸缩表格的输入框的监听，判断是否要自动添加一行
    element.bind("input propertychange",function (event) {
        const value = $(this).val();
        var els = $(this).parentsUntil('.out-border')
        const border = els.eq(els.length-1).parent()
        const next = border.next()
        console.log('border.level='+border.attr('level'))
        console.log('next.level='+next.attr('level'))
        const nowLine = parseInt(border.attr('line'))
        const nowLevel = border.attr('level')
        const nextLevel = next.attr('level')
        if(nextLevel === undefined || nextLevel < nowLevel){
            if(value.length === 1){
                // 即时同级别最后一个，又是第一次输入，则添加一行
                addOneLine(nowLine)
                // 解除监听，因为只有一次机会
                element.unbind("input propertychange")
            }
        }
    })
}

$(function () {
    // addOneLine(2,'table')
    addOneLine(-1,'flex-table-body','right-body')


})