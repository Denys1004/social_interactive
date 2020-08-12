// Show Form for submitt post
$('#image_post_btn').click(function(){
    $('#video_post').hide();
    $('#text_post').hide();
    $('#image_post').show();
})

$('#video_post_btn').click(function(){
    $('#image_post').hide();
    $('#text_post').hide();
    $('#video_post').show();
})

$('#text_post_btn').click(function(){
    $('#image_post').hide();
    $('#video_post').hide();
    $('#text_post').show();
})

$('#cancel_post_btn').click(function(){
    $('#image_post').hide();
    $('#text_post').hide();
    $('#video_post').hide();
})





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



$(".comment_container").on('submit', '.comment_form', function(e){
    e.preventDefault();
    let post_id = $(this).attr('post_id')
    let data = $(this).serialize();
    let thisForm = $(this);
    $.ajax({
        method: 'POST',
        data: data,
        url: '/post_comment'
    }).done(function(res){
        thisForm.siblings('.display_comments_container').html(res)
        $(`.${post_id}display`).show()
        $(`.${post_id}paragraph`).html("Hide comments")
        thisForm[0].reset();
    })
})