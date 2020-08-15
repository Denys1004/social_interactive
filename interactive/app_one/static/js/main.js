
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
    if(needed_html == 'Unlike'){
        $(this).html('Like')
    }else{
        $(this).html('Unlike')
    }
    $.ajax({
        url:path,
        method:'get',
        success: function(response)
{
            this_var.attr('href',  this_var.attr('href2'))
            this_var.attr('href2', path)
            $('.likess').html(response)
        }
    })
})


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