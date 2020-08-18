// $('#color_teal').click(function(){
//     let css_1_Path = $('#css_style').attr('href'); 
//     $('#css_style').attr('href', css_1_Path)
// })

// $('#color_blue').click(function(){
//     let css_2_Path = $('#css_style').attr('alt_src2');
//     $('#css_style').attr('href', css_2_Path)
// })




// Show Form for submitt post
$('#image_post_btn').click(function(){
    $('#video_post').hide();
    $('#text_post').hide();
    $('#music_post').hide();
    $('#image_post').show();
})

$('#song_post_btn').click(function(){
    $('#video_post').hide();
    $('#text_post').hide();
    $('#image_post').hide();
    $('#music_post').show();
})

$('#video_post_btn').click(function(){
    $('#image_post').hide();
    $('#text_post').hide();
    $('#music_post').hide();
    $('#video_post').show();
})

$('#text_post_btn').click(function(){
    $('#image_post').hide();
    $('#video_post').hide();
    $('#music_post').hide();
    $('#text_post').show();
})

$('#cancel_post_btn').click(function(){
    $('#image_post').hide();
    $('#text_post').hide();
    $('#music_post').hide();
    $('#video_post').hide();
})



// Add Comment to post
$(".comment_container").on('submit', '.comment_form', function(e){
    e.preventDefault();
    let post_id = $(this).attr('post_id')
    let data = $(this).serialize();
    var thisForm = $(this);
    $.ajax({
        method: 'POST',
        data: data,
        url: '/post_comment'
    }).done(function(res){
        $('.display_comments_container').html(res)
        $(`.${post_id}display`).show()
        $(`.${post_id}paragraph`).html("Hide comments")
        thisForm[0].reset();
    })
})


// Show Comments on the post
$('.show_comments').click(function(){
    let pContent=$(this).html()
    let post_id = $(this).attr('post_id')

    if(pContent == 'Hide comments'){
        $(this).html('Show comments...')
        $(`.${post_id}display`).hide()
    }
    else{
        $(this).html('Hide comments')
        $(`.${post_id}display`).show()
    }
})



// Likes
$('body').on('click','.unlike',function(e){
    e.preventDefault()
    let path = $(this).attr('href')
    var this_var = $(this)
    var needed_html = $(this).html()
    var post_id = $(this).attr('post_id')
    if(needed_html == 'Unlike'){
        $(this).html('Like')
    }else{
        $(this).html('Unlike')
    }
    $.ajax({
        url:path,
        method:'get',
        success: function(response){
            console.log(response);
            this_var.attr('href',  this_var.attr('href2'))
            this_var.attr('href2', path)
            $(`.${post_id}`).html(response)
        }
    })
})
$('body').on('submit','.chat_form',function(e){
    e.preventDefault()
    var thisForm = $(this);
    var conversation=$(this).attr('conversation')
    var receiver=$(this).attr('receiver')
    $.ajax({
        url: `/chat/${conversation}/${receiver}`,
        data: $(this).serialize(),
        method:'post',
        success: (response) => {
            response = JSON.parse(response)
            $('.last').attr('class', "chat_message_container")
            $('#chat_container').append(
                `<div class="chat_message_container last" mess_id ="{{message.id}}">
                    <div class="chat_message">
                        <div class="chat_avatar">
                            <a href="/user/${response.poster_id}/profile" ><img src="/media/${response.avatar}" alt=""></a>
                        </div>
                        <div class="chat_content_container">
                            <div class="chat_content_header">
                                <a href="/user/${response.poster_id}/profile">${response.name}</a>
                                <small>${response.time}</small>
                            </div>
                            <div class="chat_content_body">
                                <p>${response.message}</p>
                            </div>
                        </div>
                    </div>
                </div>`
            )
            thisForm[0].reset();
            updateScroll()
        }
    })
})

// Ajax check for new messages
// $('body').on('submit','.chat_form',function(e){
function check_for_mess(){
    var mess_id = $('.last').attr('mess_id')
    // console.log(mess_id);
    $.ajax({
        url: `/check_mess/${mess_id}`,
        method:'get',
        async: false,
        success: function(response){
            response = JSON.parse(response)

            for(mess of response){
                var name = mess['name'][0]
                var avatar = mess['avatar'][0]
                var message = mess['message'][0]
                var time = mess['time'][0]
                var poster_id = mess['poster_id']
                var mess_id = mess['mess_id']

                $('.last').attr('class', "chat_message_container")
                $('#chat_container').append(
                    `<div class="chat_message_container last" mess_id =${mess_id}>
                        <div class="chat_message">
                            <div class="chat_avatar">
                                <a href="/user/${poster_id}/profile" ><img src="/media/${avatar}" alt=""></a>
                            </div>
                            <div class="chat_content_container">
                                <div class="chat_content_header">
                                    <a href="/user/${poster_id}/profile">${name}</a>
                                    <small>${time}</small>
                                </div>
                                <div class="chat_content_body">
                                    <p>${message}</p>
                                </div>
                            </div>
                        </div>
                    </div>`
                )
                updateScroll()
            }
        }
    })
}

window.setInterval(function(){
    check_for_mess()
}, 1000);

// Delete post comment
$('body').on('click','#delete_com',function(e){
    e.preventDefault()
    let path = $(this).attr('href')
    $.ajax({
        url:path,
        method:'get',
        success: function(response){
            $('.display_comments_container').html(response)
        }
    })
})


// Chat keep scrolled down
function updateScroll(){
    var element = document.getElementById("chat_container");
    element.scrollTop = element.scrollHeight;
}
updateScroll()



// Emoji
var input = document.querySelector('#content');
var emoji_btn = document.querySelector('#add_emoji');
var picker = new EmojiButton({
    position: 'right-end' 
})
picker.on('emoji', function(emoji){
    input.value += emoji;
})
emoji_btn.addEventListener('click', function(){
    picker.pickerVisible ? picker.hidePicker() : picker.showPicker(emoji_btn);
})



// [{
//     "name": ["Veta Romanchenko"], 
//     "avatar": ["avatars/veta.jpg-32411016f1194067905bc758b1dd819f.jpg"], 
//     "message": ["dsgfgsdf"], 
//     "time": ["Aug 18, 02:43AM"], 
//     "poster_id": "2"
// }]

