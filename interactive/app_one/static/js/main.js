
// Gallery
$(document).ready(function() {
	$('.popup-gallery').magnificPopup({
		delegate: 'a',
		type: 'image',
		tLoading: 'Loading image #%curr%...',
		mainClass: 'mfp-img-mobile',
		gallery: {
			enabled: true,
			navigateByImgClick: true,
			preload: [0,1] // Will preload 0 - before current, and 1 after the current image
		},
		image: {
			tError: '<a href="%url%">The image #%curr%</a> could not be loaded.',
			titleSrc: function(item) {
				return item.el.attr('title') + '<small>by Marsel Van Oosten</small>';
			}
		}
	});
});

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




// Add Comment to post
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


// $('body').on('click','#like',function(e){
//     e.preventDefault()
//     post_id=$(this).attr('post_id')
//     $.ajax({
//         url:`/like/${post_id}`,
//         method:'get',
//         success: function(response)
//         {
//             console.log(response);
//             $('.all_posts_container').html(response)
//         }
//     })
// })
// $('body').on('click', '#unlike',function(e){
//     e.preventDefault()
//     post_id=$(this).attr('post_id')
//     $.ajax({
//         url:`/unlike/${post_id}`,
//         method:'get',
//         success: function(response)
//         {
//             console.log(response);
//             $('.all_posts_container').html(response)
//         }
//     })
// })



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