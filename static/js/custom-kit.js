function updateOverlayHeight() {
  const chatBody = document.querySelector('.chat-body');
  const chatBodyHeight = chatBody.scrollHeight;
  document.documentElement.style.setProperty('--overlay-height', chatBodyHeight + 'px');
}

function formatResponse(response) {
    // 将文本开头的换行符删除掉
    if (response.startsWith('\n')) {
    response = response.replace(/^\n/, '');
    }

    // 正则表达式将匹配以 "'''" 开头和以 "'''" 结尾的文本，然后将其替换为 <pre><code> 和 </code></pre>。
    // 使用 "gm" 修饰符以匹配每一个 "'''"，而不是仅匹配第一个。
    response = response.replace(/```(.+?)```/gm, '<pre><code>$1</code></pre>');

    // 将文本中的换行符替换为<br>元素
    response = response.replace(/(\r\n|\n|\r)/gm, '<br />');

    return response;
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
    var user_input = $('#user-input').val();
    if (!user_input.length) return;
    user_input = formatResponse(user_input);
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
        data: {user_input: user_input},
        success: function (response) {
            // 将返回文本格式化成HTML元素
            var formattedResponse = formatResponse(response);
            if (!formattedResponse.length) return;
            $('#chat_content').append('<div class="bubble-received">' + formattedResponse + '<span class="copy-icon left">&nbsp;</span></div>');
            chat_content.scrollTop = chat_content.scrollHeight;
            updateOverlayHeight();
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log(errorThrown);
            $('#chat_content').append('<div class="bubble-received">我开小差了，没听清你的问题，请再说一次。</div>');
            chat_content.scrollTop = chat_content.scrollHeight;
            updateOverlayHeight();
        }
    });
    $('#user-input').height(25);
}
