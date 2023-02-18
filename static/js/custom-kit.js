function updateOverlayHeight() {
  const chatBody = document.querySelector('.chat-body');
  const chatBodyHeight = chatBody.scrollHeight;
  document.documentElement.style.setProperty('--overlay-height', chatBodyHeight + 'px');
  leftDiv.classList.add('active');
  rightDiv.classList.remove('active');
}

function formatPrompt(prompt) {
    // 将文本开头的换行符删除掉
    if (prompt.startsWith('\n')) {
    prompt = prompt.replace(/^\n/, '');
    }

    // 正则表达式将匹配以 "'''" 开头和以 "'''" 结尾的文本，然后将其替换为 <pre><code> 和 </code></pre>。
    // 使用 "gm" 修饰符以匹配每一个 "'''"，而不是仅匹配第一个。
    prompt = prompt.replace(/```(.+?)```/gm, '<pre><code>$1</code></pre>');

    // 将文本中的换行符替换为<br>元素
    prompt = prompt.replace(/(\r\n|\n|\r)/gm, '<br />');

    return prompt;
}

function formatClipboard(text) {
    // 将文本中的<br>替换为换行符元素
    text = text.replace(/<br ?\/?>/ig,"\r\n");
    var pos = text.indexOf("<span class=\"copy-icon left\"")
    text = text.substring(0, pos);

    return text;
}

function submitContent(event){
    event.preventDefault();
    var chat_content = document.getElementById('chat_content');
    var prompt_id_value = $('#prompt_id').val();
    var user_input_original = $('#user-input').val();
    if (!user_input_original.length) return;
        user_input = formatPrompt(user_input_original);
    // $('#chat_content').append('<div class="bubble-sent"><span class="copy-icon right">&nbsp;</span>' + user_input + '</div>');
    $('#chat_content').append('<div class="bubble-sent">' + user_input + '</div>');
    $('#user-input').replaceWith($('#user-input').clone(true));
    $('#user-input').val('');
    $('#user-input').height(28);
    chat_content.scrollTop = chat_content.scrollHeight;
    updateOverlayHeight();
    $.ajax({
        type: 'POST',
        url: '/get_response',
        data: {
            user_input: user_input_original,
            prompt_id: prompt_id_value
        },
        success: function (data) {
            // 将返回文本格式化成HTML元素
            var prompt_id = data.prompt_id;
            var prompt = data.prompt;
            var formattedPrompt = formatPrompt(prompt);
            if (!formattedPrompt.length) return;
            $('#chat_content').append('<div class="bubble-received">' + formattedPrompt + '<span class="copy-icon left">&nbsp;</span></div>');
            chat_content.scrollTop = chat_content.scrollHeight;
            updateOverlayHeight();
            $('#prompt_id').val(prompt_id);
            get_prompts();
        },
        error: function (xhr, textStatus, errorThrown) {
            console.error(errorThrown);
            $('#chat_content').append('<div class="bubble-received">我开小差了，没听清你的问题，请再说一次。</div>');
            chat_content.scrollTop = chat_content.scrollHeight;
            updateOverlayHeight();
        }
    });
    $('#user-input').height(25);
}

function get_prompts(){
    var svgHtml = '<svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="30px" xmlns="http://www.w3.org/2000/svg"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';
    var promptIdValue = $('#prompt_id').val();
    $.ajax({
    url: '/prompts',
    dataType: 'json',
    success: function(data) {
        $('#list').empty();  //清空列表元素中的内容
        $.each(data, function(index, row) {
            var prompt = row[1];
            var prompt_id = row[0];
            var promptHTML = '<div class="prompt" id="' + prompt_id + '">' + prompt + '</div>';
            $('#list').append(promptHTML);
            var containerElem = $('.chat-container');
            var promptElem = $('#' + prompt_id);
            var promptWidth = containerElem.width() * 0.8 - 20;
            var promptFontSize = parseInt(promptElem.css('font-size'));
            var promptChars = prompt.length;
            var promptMaxWidth = Math.floor(promptWidth / promptFontSize - 4);
            if (promptChars > promptMaxWidth) {
                var truncatedPrompt = svgHtml + prompt.substr(0, promptMaxWidth) + '...';
                // var truncatedPrompt = svgHtml + '...' + prompt.slice(-promptMaxWidth) ;
                promptElem.empty();
                promptElem.append(truncatedPrompt);
            }else{
                promptElem.empty();
                promptElem.append(svgHtml+prompt);
            }
            if (promptIdValue == prompt_id)
                $('#' + prompt_id).addClass('active');
        });
    }
    });
}

//复制操作
$(document).on('click', '.copy-icon', function() {
    const copyIcons = document.querySelectorAll('.copy-icon');
    // 遍历 copy-icon 元素，给它们添加 click 事件监听器
    for (const copyIcon of copyIcons) {
        // 移除之前点击过的.copy-icon的title
        $(copyIcon).removeAttr('title');
        $(copyIcon).removeAttr('data-original-title');
    }
    // 获取要复制的文本
    const div = this.parentElement;
    const text = formatClipboard(div.innerHTML);
    if (text) {
        // 将文本内容复制到系统剪贴板中
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text)
            .then(() => {
                $(this).attr('title', '已复制').tooltip('fixTitle').tooltip('show');
                })
            .catch(err => {
                $(this).attr('title', '复制失败').tooltip('fixTitle').tooltip('show');
            });
        } else {
            console.error('浏览器不支持navigator操作');
            // 创建textarea
            const textArea = document.createElement('textarea');
            textArea.value = text;
            // 使textarea不在viewport，同时设置不可见
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            $(this).attr('title', '已复制').tooltip('fixTitle').tooltip('show');
            return new Promise((res, rej) => {
                // 执行复制命令并移除文本框
                document.execCommand('copy', false, text) ? res() : rej()
                textArea.remove()
            })
        }
    } else {
        console.error('要复制的文本为空或未定义');
    }
});



